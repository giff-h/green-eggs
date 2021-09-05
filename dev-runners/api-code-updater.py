# -*- coding: utf-8 -*-
import builtins
from itertools import chain, zip_longest
import keyword
from pathlib import Path
import re
from urllib.request import urlopen

from lxml.html import fromstring

nbsp = re.compile(r' *\xa0 *')
has_possible_multi_param = re.compile(r'\b(?:Maximum|Limit): (\d+)(?! characters)(?=\D|$)')
url_extractor = re.compile(r'^`(?P<url_method>[A-Z]+ )?(?:https://api\.twitch\.tv/)?helix/(?P<url_path>[^?`]+)[^`]*`$')
reserved = set(dir(builtins)) | set(keyword.kwlist)
sections_xpath = '//section[@class = "left-docs"]/h2[position() = 1]/..'
section_child_xpath = '*[not(name() = "a" and @class = "editor-link") and not(position() = 1)]'
url_triggers = ['URL', 'URLs']
parameter_triggers = [
    'Body Parameter',
    'Query Parameter',
    'Query Paramater',
    'Body Value',
]
table_header_parameter_columns = ['Field', 'Fields', 'Name', 'Paramater', 'Parameter']
type_value_lookup = {
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


def clean_reserved(s):
    return s + '_' if s in reserved else s


def indent(lines):
    return [f'    {line}' for line in lines]


def split_table_row_lines(row):
    return list(zip_longest(*[map(str.strip, cell.split('\n')) for cell in row], fillvalue=''))


def format_table(table_rows):
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


def node_text_iter(node):
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


def node_text(node):
    return nbsp.sub(' ', ''.join(text or '' for text in node_text_iter(node))).strip()


def function_param(pair, required):
    param, annotation = pair

    param_repr = f'{clean_reserved(param)}: {annotation}'
    return param_repr if required else param_repr + ' = _empty'


def function_from_section(section):
    function_name = section.xpath('h2[1]/@id')[0].replace('-', '_')
    required_parameters = dict(url=[], body=[])
    optional_parameters = dict(url=[], body=[])
    url_method = ''
    url_path = ''
    is_under_url_header = False
    is_parameter_for_body = False
    is_under_parameter_header = False
    is_in_parameter_table = False
    is_parameter_required_by_header = False
    is_parameter_requirement_in_table = False

    documentation_lines = ['"""']
    for child in section.xpath(section_child_xpath):
        # TAGS {'div', 'h2', 'h3', 'p', 'table', 'ul'}
        if child.tag == 'div':
            div_content = node_text(child).split('\n')
            documentation_lines.extend(indent(filter(len, map(str.strip, div_content))))
            documentation_lines.append('')
        elif child.tag == 'h2' or child.tag == 'h3':
            header_text = node_text(child)
            is_under_url_header = header_text in url_triggers
            is_under_parameter_header = any(p in header_text for p in parameter_triggers)
            is_parameter_for_body = is_under_parameter_header and 'Body' in header_text
            is_parameter_required_by_header = header_text.startswith('Required')
            documentation_lines.append(f'# {header_text}:')
        elif child.tag == 'p':
            text_lines = node_text(child).split('\n')
            is_empty = len(text_lines) == 0 or (len(text_lines) == 1 and not len(text_lines[0]))
            if not is_empty:
                if is_under_url_header:
                    match = url_extractor.match(text_lines[0])
                    if match:
                        url_strings = match.groupdict()
                        url_method = url_strings.get('url_method') or url_method_fallbacks.get(function_name, '')
                        url_path = url_strings.get('url_path') or ''
                documentation_lines.extend(text_lines)
                documentation_lines.append('')
            is_under_url_header = False
        elif child.tag == 'table':
            type_column_index = None
            table_trs = child.xpath('*/tr')
            table_text = []

            header_row = table_trs[0]
            header_text = [node_text(th) for th in header_row]
            if is_under_parameter_header:
                if header_text[0] in table_header_parameter_columns:
                    is_in_parameter_table = True
                    type_column_index = header_text.index('Type')
                    if header_text[1] == 'Required':
                        is_parameter_requirement_in_table = True
            table_text.append(header_text)

            for body_row in table_trs[1:]:
                row_text = [node_text(td) for td in body_row]
                if is_in_parameter_table:
                    required = is_parameter_required_by_header or (
                        is_parameter_requirement_in_table and row_text[1] == 'yes'
                    )
                    parameters_key = 'body' if is_parameter_for_body else 'url'
                    if '.' not in row_text[0]:
                        param = row_text[0].strip('`')
                        param_type = type_value_lookup[row_text[type_column_index].lower()]
                        if isinstance(param_type, dict):
                            param_type = param_type[f'{function_name}.{param}']
                        param_multi_limit = has_possible_multi_param.search(row_text[-1])
                        if param_multi_limit and param_multi_limit.group(1) != '1':
                            # Including first which is usually an int is necessary here for a
                            # few functions where it's typed as string, probably incorrectly
                            is_type_naturally_counted = (
                                any(param_type.lower().startswith(predicate) for predicate in ('int', 'list'))
                                or param == 'first'
                            )
                            if not is_type_naturally_counted:
                                param_type = f'Union[{param_type}, List[{param_type}]]'

                        if required:
                            required_parameters[parameters_key].append((param, param_type))
                        else:
                            optional_parameters[parameters_key].append((param, param_type))
                table_text.append(row_text)

            documentation_lines.extend(format_table(table_text))
            documentation_lines.append('')

            is_under_parameter_header = False
            is_in_parameter_table = False
            is_parameter_required_by_header = False
            is_parameter_requirement_in_table = False
        elif child.tag == 'ul':
            documentation_lines.extend(node_text(child).split('\n'))
            documentation_lines.append('')
        else:
            raise Exception(f'Unhandled tag {child.tag!r} in section {section.xpath("h2[1]/text()")[0]!r}')
    documentation_lines.append('"""')

    parameter_parts = [
        [function_param(pair, True) for pair in required_parameters['url']],
        [function_param(pair, False) for pair in optional_parameters['url']],
        [function_param(pair, True) for pair in required_parameters['body']],
        [function_param(pair, False) for pair in optional_parameters['body']],
    ]
    function_parameters = ', '.join(chain(*parameter_parts))
    if len(function_parameters):
        function_parameters = ', *, ' + function_parameters
    function_def = f'async def {function_name}(self{function_parameters}):'
    function_lines = [function_def]
    function_lines.extend(indent(documentation_lines))

    code_lines = []

    return_line = f'return await self._request({url_method.strip()!r}, {url_path!r}'

    url_params = required_parameters['url'] + optional_parameters['url']
    if len(url_params):
        params_kwargs = ', '.join(f'{param}={clean_reserved(param)}' for param, _ in url_params)
        params_constructor = f'params = exclude_non_empty({params_kwargs})'
        code_lines.append(params_constructor)
        return_line += ', params=params'

    body_params = required_parameters['body'] + optional_parameters['body']
    if len(body_params):
        body_kwargs = ', '.join(f'{param}={clean_reserved(param)}' for param, _ in body_params)
        body_constructor = f'data = exclude_non_empty({body_kwargs})'
        code_lines.append(body_constructor)
        return_line += ', data=data'

    code_lines.append(return_line + ')')
    function_lines.extend(indent(code_lines))

    return function_lines


def parse_document(document):
    sections = document.xpath(sections_xpath)
    functions_lines = []

    for section in sections:
        functions_lines.append('')
        functions_lines.extend(function_from_section(section))

    return indent(functions_lines)


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

    template = (this_dir / 'api.py.template').read_text()
    full_file = template + '\n'.join(generated_lines) + '\n'
    for misspelled, corrected in spelling_fixes.items():
        full_file = full_file.replace(misspelled, corrected)
    (this_dir.parent / 'green_eggs' / 'api.py').write_text(full_file)
