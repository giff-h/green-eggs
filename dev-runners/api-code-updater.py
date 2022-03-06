# -*- coding: utf-8 -*-
import builtins
from itertools import zip_longest
import keyword
from pathlib import Path
import re
from typing import Dict, Generator, Iterable, List, Optional, Tuple, Union
from urllib.request import urlopen

from lxml.html import HtmlElement, fromstring

nbsp = re.compile(r' *\xa0 *')
has_possible_multi_param = re.compile(r'\b(?:Maximum|Limit): (\d+)(?! characters)(?=\D|$)')
url_extractor = re.compile(r'^`(?P<url_method>[A-Z]+ )?(?:https://api\.twitch\.tv/)?helix/(?P<url_path>[^?`]+)[^`]*`$')
illegal_endpoint_field_variables = set(dir(builtins)) | set(keyword.kwlist) | {'params', 'data'}
sections_xpath = '//section[@class = "left-docs"]/h2[position() = 1]/..'
section_child_xpath = '*[not(name() = "a" and @class = "editor-link") and not(position() = 1)]'
url_triggers = ['URL', 'URLs']
parameter_triggers = [
    'Body Parameter',
    'Query Parameter',
    'Query Paramater',
    'Body Value',
    'Request Body',
]
table_header_parameter_columns = ['Field', 'Fields', 'Name', 'Paramater', 'Parameter']
type_value_lookup: Dict[str, Union[str, Dict[str, str]]] = {
    'array': {
        'update_drops_entitlements.entitlement_ids': 'List[str]',
        'send_extension_pubsub_message.target': 'List[str]',
    },
    'boolean': 'bool',
    'condition': 'Dict[str, Any]',  # https://dev.twitch.tv/docs/eventsub/eventsub-reference#conditions
    'integer': 'int',
    'object': 'Dict[str, Any]',
    'object[]': 'List[Dict[str, Any]]',
    'string': 'str',
    'string array': 'List[str]',
    'transport': 'Dict[str, Any]',  # https://dev.twitch.tv/docs/eventsub/eventsub-reference#transport
}
object_types = ['object', 'object[]']
url_method_fallbacks = {
    'get_stream_key': 'GET',
}
spelling_fixes = {
    'doesn’t': "doesn't",
    'requestion': 'request',
    'invalide': 'invalid',
    'Invalide': 'Invalid',
    'Minumum': 'Minimum',
    'undertermined': 'undetermined',
    'uesrs': 'users',
    'Paramater': 'Parameter',
    'currenty': 'currently',
    'coutry': 'country',
}


def clean_reserved(s: str) -> str:
    return s + '_' if s in illegal_endpoint_field_variables else s


def indent(lines: Iterable[str]) -> List[str]:
    return [f'    {line}' for line in lines]


def split_table_row_lines(row: List[str]) -> List[Tuple[str, ...]]:
    return list(zip_longest(*[map(str.strip, cell.split('\n')) for cell in row], fillvalue=''))


def format_table(table_rows: List[List[str]]) -> List[str]:
    expanded_rows = [split_table_row_lines(row) for row in table_rows]

    max_lengths = [
        max(len(inner_row[i]) for row in expanded_rows for inner_row in row) for i in range(len(expanded_rows[0][0]))
    ]
    middle = '-+-'.join('-' * length for length in max_lengths)
    horizontal = f'+-{middle}-+'

    formatted = [horizontal]
    for row in expanded_rows:
        for inner_row in row:
            middle = ' | '.join(cell.ljust(length, ' ') for cell, length in zip(inner_row, max_lengths))
            formatted_row = f'| {middle} |'
            formatted.append(formatted_row)
        formatted.append(horizontal)
    return formatted


def node_text_iter(node: HtmlElement) -> Generator[str, None, None]:
    if node.tag == 'code':
        yield f'`{node.text}`'
    elif node.tag == 'li':
        yield f'\n- {node.text}'
    else:
        yield node.text

    for child in node:
        if child.tag == 'br':
            yield '\n'
        else:
            yield from node_text_iter(child)
        yield child.tail


def node_text(node: HtmlElement, do_strip=True) -> str:
    text = nbsp.sub(' ', ''.join(text or '' for text in node_text_iter(node)))
    return text.strip() if do_strip else text


class EndpointField:
    FIELD_NAME_ATTR = '_field_name'
    REQUIRED_VALUE_ATTR = '_required_value'
    FIELD_TYPE_ATTR = '_field_type'
    DESCRIPTION_ATTR = '_description'

    def __init__(
        self,
        field_name: str,
        required_value: str,
        field_type: str,
        description: str,
        ordering: List[str],
        is_required: bool,
    ):
        self._field_name = field_name
        self._required_value = required_value
        self._field_type = field_type
        self._description = description
        self._ordering = ordering
        self._is_required = is_required

        self.parent_field: Optional['EndpointField'] = None
        self.is_object_list = self._field_type.lower() == 'object[]'
        self.inner_fields: List['EndpointField'] = []

    @property
    def documentation(self) -> List[List[str]]:
        self_line = [getattr(self, attr) for attr in self._ordering]
        documentation = [self_line]
        for field in self.inner_fields:
            documentation.extend(field.documentation)
        return documentation

    @property
    def field_name(self) -> str:
        return self._field_name.replace('`', '').split('.')[-1].strip()

    @property
    def local_variable(self):
        return clean_reserved(self._field_name.replace('`', '').replace('.', '_').strip())

    @property
    def local_variable_with_part(self):
        return f'_{self.field_name}_part'

    def annotation(self, function_name: str):
        type_value = type_value_lookup[self._field_type.lower()]
        if isinstance(type_value, dict):
            annotation = type_value[f'{function_name}.{self.field_name}']
        else:
            annotation = type_value

        param_multi_limit = has_possible_multi_param.search(self._description)
        if param_multi_limit and param_multi_limit.group(1) != '1':
            is_type_naturally_counted = (
                any(annotation.lower().startswith(predicate) for predicate in ('int', 'list'))
                or self.field_name == 'first'
            )
            if not is_type_naturally_counted:
                annotation = f'Union[{annotation}, List[{annotation}]]'

        return f'List[{annotation}]' if self.parent_field and self.parent_field.is_object_list else annotation

    def function_parameter(self, function_name: str) -> str:
        parameter_string = f'{self.local_variable}: {self.annotation(function_name)}'
        return parameter_string if self._is_required else parameter_string + ' = _empty'

    def as_kwarg(self, is_in_comprehension=False) -> Tuple[str, List[str]]:
        """
        Returns the kwarg of the current field for use in the `exclude_non_empty` function call in the body of the
        endpoint function.

        The first tuple item is the string `field_name=local_variable` The second tuple item is the list of other full
        code lines that should run first, can be empty
        """
        additional_code: List[str] = []
        inner_fields = sorted(self.inner_fields, key=lambda f: f.local_variable)

        if inner_fields:
            lv = f'_{self.local_variable}'
            inner_kwarg_results = [field.as_kwarg() for field in inner_fields]
            inner_kwargs = ', '.join(kwarg for kwarg, _ in inner_kwarg_results)
            for _, additional_codes in inner_kwarg_results:
                additional_code.extend(additional_codes)

            if self.is_object_list:
                inner_kwargs_from_lists = f', '.join(field.as_kwarg(True)[0] for field in inner_fields)
                inner_parts = ', '.join(field.local_variable_with_part for field in inner_fields)
                inner_locals = ', '.join(field.local_variable for field in inner_fields)
                loop_iterator = (
                    f'zip_longest({inner_locals}, fillvalue=_empty)' if len(inner_fields) > 1 else inner_locals
                )
                loop = f'for {inner_parts} in {loop_iterator}'
                comprehension = f'[exclude_non_empty({inner_kwargs_from_lists}) {loop}]'
                # instance_check = f'if isinstance({inner_fields[0].local_variable}, list) else'
                # singular = f'exclude_non_empty({inner_kwargs})'
                additional_code.append(f'{lv} = {comprehension}')
            else:
                additional_code.append(f'{lv} = exclude_non_empty({inner_kwargs})')

        else:
            lv = self.local_variable_with_part if is_in_comprehension else self.local_variable

        kwarg = f'{self.field_name}={lv}'
        if inner_fields:
            kwarg = f'{kwarg} or _empty'
        return kwarg, additional_code


class EndpointFieldTable:
    def __init__(self, node: HtmlElement, is_parameter_required_by_header: bool):
        self._node = node

        self._fields: List[EndpointField] = []
        self._header_row: List[str] = []

        self._parse_node(is_parameter_required_by_header)

    def _parse_node(self, is_parameter_required_by_header: bool):
        is_parameter_requirement_in_table = False
        table_trs = self._node.xpath('*/tr')

        self._header_row = [node_text(th) for th in table_trs[0]]
        type_column_index = self._header_row.index('Type')
        if self._header_row[1] == 'Required':
            ordering = [
                EndpointField.FIELD_NAME_ATTR,
                EndpointField.REQUIRED_VALUE_ATTR,
                EndpointField.DESCRIPTION_ATTR,
            ]
            is_parameter_requirement_in_table = True
        else:
            ordering = [EndpointField.FIELD_NAME_ATTR, EndpointField.DESCRIPTION_ATTR]
        ordering.insert(type_column_index, EndpointField.FIELD_TYPE_ATTR)

        for body_row in table_trs[1:]:
            row_text = [node_text(td, do_strip=False) for td in body_row]
            field_name = row_text[0]
            required_value = row_text[1] if is_parameter_requirement_in_table else ''
            field_type = row_text[type_column_index]
            description = row_text[-1]
            is_required = is_parameter_required_by_header or (
                is_parameter_requirement_in_table and row_text[1].lower() == 'yes'
            )
            field = EndpointField(field_name, required_value, field_type, description, ordering, is_required)
            if '.' in field_name or field_name.replace('`', '').startswith(' '):
                field.parent_field = self._fields[-1]
                if all(field.local_variable != f.local_variable for f in self._fields[-1].inner_fields):
                    self._fields[-1].inner_fields.append(field)
            else:
                if all(field.local_variable != f.local_variable for f in self._fields):
                    self._fields.append(field)

    @property
    def documentation(self) -> List[str]:
        lines = [self._header_row]
        for field in self._fields:
            lines.extend(field.documentation)
        return format_table(lines)

    def function_parameters(self, function_name: str) -> List[str]:
        parameters = []

        for field in self._fields:
            if field.inner_fields:
                for inner_field in field.inner_fields:
                    parameters.append(inner_field.function_parameter(function_name))
            else:
                parameters.append(field.function_parameter(function_name))

        return parameters

    @property
    def code_lines(self) -> Tuple[List[str], List[str]]:
        """
        Returns a tuple of two lists.

        The first is a list of code that needs to be run before the kwargs are compiled for the request call. The second
        is the list of kwargs from this table.
        """
        if not self._fields:
            return [], []

        kwargs_and_code = [field.as_kwarg() for field in sorted(self._fields, key=lambda f: f.local_variable)]
        code = []
        for _, additional_code in kwargs_and_code:
            code.extend(additional_code)
        return code, [kwarg for kwarg, _ in kwargs_and_code]


class EndpointFunction:
    def __init__(self, node: HtmlElement):
        self._node = node

        self._url_params_tables: List[EndpointFieldTable] = []
        self._request_body_tables: List[EndpointFieldTable] = []

        self._documentation_lines: List[str] = []

        self._url_method = ''
        self._url_path = ''

        self._is_under_url_header = False
        self._is_parameter_for_body = False
        self._is_under_parameter_header = False
        self._is_parameter_required_by_header = False

        self._parse_node()

    def _parse_div(self, node: HtmlElement):
        div_content = node_text(node).split('\n')
        self._documentation_lines.extend(indent(line for line in map(str.strip, div_content) if line))
        self._documentation_lines.append('')

    def _parse_header(self, node: HtmlElement):
        header_text = node_text(node)
        self._is_under_url_header = header_text in url_triggers
        self._is_under_parameter_header = any(p in header_text for p in parameter_triggers)
        self._is_parameter_for_body = self._is_under_parameter_header and 'Body' in header_text
        self._is_parameter_required_by_header = header_text.startswith('Required')
        self._documentation_lines.append(f'# {header_text}:')

    def _parse_paragraph(self, node: HtmlElement):
        text_lines = node_text(node).split('\n')
        is_empty = len(text_lines) == 0 or (len(text_lines) == 1 and not len(text_lines[0]))
        if not is_empty:
            if self._is_under_url_header:
                match_result = url_extractor.match(text_lines[0])
                if match_result:
                    url_strings: Dict[str, str] = match_result.groupdict()
                    url_method = url_strings.get('url_method') or url_method_fallbacks.get(self.function_name, '')
                    assert url_method is not None
                    self._url_method = url_method
                    self._url_path = url_strings.get('url_path') or ''
            self._documentation_lines.extend(text_lines)
            self._documentation_lines.append('')
        self._is_under_url_header = False

    def _parse_table(self, node: HtmlElement):
        table_trs = node.xpath('*/tr')
        header_row = table_trs[0]
        header_text = [node_text(th) for th in header_row]
        is_in_parameter_table = self._is_under_parameter_header and header_text[0] in table_header_parameter_columns

        if is_in_parameter_table:
            table = EndpointFieldTable(node, self._is_parameter_required_by_header)
            if self._is_parameter_for_body:
                self._request_body_tables.append(table)
            else:
                self._url_params_tables.append(table)
            documentation = table.documentation
        else:
            table_text = [[node_text(td) for td in body_row] for body_row in table_trs]
            documentation = format_table(table_text)

        self._documentation_lines.extend(documentation)
        self._documentation_lines.append('')
        self._is_under_parameter_header = False
        self._is_parameter_required_by_header = False

    def _parse_list(self, node: HtmlElement):
        self._documentation_lines.extend(node_text(node).split('\n'))
        self._documentation_lines.append('')

    def _parse_node(self):
        for child in self._node.xpath(section_child_xpath):
            if child.tag == 'div':
                self._parse_div(child)
            elif child.tag == 'h2' or child.tag == 'h3':
                self._parse_header(child)
            elif child.tag == 'p':
                self._parse_paragraph(child)
            elif child.tag == 'table':
                self._parse_table(child)
            elif child.tag == 'ul':
                self._parse_list(child)
            else:
                raise Exception(f'Unhandled tag {child.tag!r} in section {self._node.xpath("h2[1]/text()")[0]!r}')

    @property
    def function_name(self) -> str:
        return self._node.xpath('h2[1]/@id')[0].replace('-', '_')

    @property
    def function_parameters(self) -> str:
        url_params = []
        for table in self._url_params_tables:
            url_params.extend(table.function_parameters(self.function_name))
        body_params = []
        for table in self._request_body_tables:
            body_params.extend(table.function_parameters(self.function_name))
        params_string = ', '.join(sorted(url_params) + sorted(body_params))
        return f', *, {params_string}' if params_string else ''

    @property
    def function_docstring(self) -> List[str]:
        return ['"""'] + self._documentation_lines + ['"""']

    @property
    def function_body(self) -> List[str]:
        code_lines = []
        return_line = f'return await self._request({self._url_method.strip()!r}, {self._url_path!r}'

        if self._url_params_tables:
            all_kwargs = []
            for table in self._url_params_tables:
                table_code, table_kwargs = table.code_lines
                code_lines.extend(table_code)
                all_kwargs.extend(table_kwargs)
            kwargs = ', '.join(sorted(all_kwargs))
            code_lines.append(f'params = exclude_non_empty({kwargs})')
            return_line += ', params=params'

        if self._request_body_tables:
            all_kwargs = []
            for table in self._request_body_tables:
                table_code, table_kwargs = table.code_lines
                code_lines.extend(table_code)
                all_kwargs.extend(table_kwargs)
            kwargs = ', '.join(sorted(all_kwargs))
            code_lines.append(f'data = exclude_non_empty({kwargs})')
            return_line += ', data=data'

        code_lines.append(return_line + ')')
        return code_lines

    @property
    def function_code(self) -> List[str]:
        def_line = f'async def {self.function_name}(self{self.function_parameters}):'
        return [def_line] + indent(self.function_docstring + self.function_body)


def parse_document(document: HtmlElement) -> List[str]:
    sections = document.xpath(sections_xpath)
    functions_lines = []

    for section in sections:
        functions_lines.append('')
        function = EndpointFunction(section)
        functions_lines.extend(indent(function.function_code))

    return functions_lines


if __name__ == '__main__':
    this_dir = Path(__file__).resolve().parent
    possible_file = this_dir / 'reference.html'
    if possible_file.exists():
        source = possible_file.read_text()
    else:
        with urlopen('https://dev.twitch.tv/docs/api/reference') as response:
            source = response.read()
            if isinstance(source, bytes):
                possible_file.write_bytes(source)
            else:
                possible_file.write_text(source)

    markup = fromstring(source)
    generated_lines = parse_document(markup)

    template = (this_dir / 'direct.py.template').read_text()
    full_file = template + '\n'.join(generated_lines) + '\n'
    for misspelled, corrected in spelling_fixes.items():
        full_file = full_file.replace(misspelled, corrected)
    (this_dir.parent / 'green_eggs' / 'api' / 'direct.py').write_text(full_file)
