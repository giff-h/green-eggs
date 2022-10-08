# -*- coding: utf-8 -*-
import re
from itertools import zip_longest
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Optional, Tuple, Union
from urllib.request import urlopen

from lxml.html import HtmlElement, fromstring

nbsp = re.compile(r' *\xa0 *')
has_possible_multi_param = re.compile(r'\b(?:(?:Maximum|Limit):|a maximum of) (\d+)(?! characters)(?=\D|$)')
url_extractor = re.compile(r'^`(?P<url_method>[A-Z]+ )?(?:https://api\.twitch\.tv/)?helix/(?P<url_path>[^?`]+)[^`]*`$')
starting_spaces = re.compile(r'^ +')
null_word = re.compile(r'\bnull\b')
data_array_check = re.compile(r'"data": ?(\[ ?)?(?:\.+ ?)?{')
pagination_string_check = re.compile(r'"pagination": ?"')
sections_xpath = '//section[@class = "left-docs"]/h2[position() = 1]/..'
response_example_xpath = 'following-sibling::section[@class = "right-code"]/h3[contains(text(), "Response")]/following-sibling::div[1]//code'
section_child_xpath = '*[not(name() = "a" and @class = "editor-link") and not(position() = 1)]'
url_triggers = ['URL', 'URLs']
parameter_triggers = [
    'Body Parameter',
    'Query Parameter',
    'Query Paramater',
    'Body Value',
    'Request Body',
]
response_triggers = [
    'Response Fields',
    'Response Body',
    'Return Values',
]
table_header_parameter_columns = ['Field', 'Fields', 'Name', 'Paramater', 'Parameter']
type_value_lookup: Dict[str, Union[str, Dict[str, str]]] = {
    'array': {
        'updateDropsEntitlements.`entitlement_ids`': 'string[]',
        'updateDropsEntitlements.`ids`': 'string[]',
        'sendExtensionPubsubMessage.`target`': 'string[]',
        'getExtensions.`screenshot_urls`': 'string[]',
        'getExtensions.`allowlisted_config_urls`': 'string[]',
        'getExtensions.`allowlisted_panel_urls`': 'string[]',
        'getReleasedExtensions.`screenshot_urls`': 'string[]',
        'getReleasedExtensions.`allowlisted_config_urls`': 'string[]',
        'getReleasedExtensions.`allowlisted_panel_urls`': 'string[]',
    },
    'object': {
        'getCheermotes.`images`': 'Record<"dark" | "light", Record<"animated" | "static", Record<"1" | "1.5" | "2" | "3" | "4", string>>>',
        'createCustomRewards.`image`': 'Record<"url_1x" | "url_2x" | "url_4x", string> | null',
        'createCustomRewards.`default_image`': 'Record<"url_1x" | "url_2x" | "url_4x", string>',
        'createCustomRewards.`max_per_stream_setting`': '{ is_enabled: boolean; max_per_stream: number; }',
        'createCustomRewards.`max_per_user_per_stream_setting`': '{ is_enabled: boolean; max_per_user_per_stream: number; }',
        'createCustomRewards.`global_cooldown_setting`': '{ is_enabled: boolean; global_cooldown_seconds: number; }',
        'getCustomReward.`image`': 'Record<"url_1x" | "url_2x" | "url_4x", string> | null',
        'getCustomReward.`default_image`': 'Record<"url_1x" | "url_2x" | "url_4x", string>',
        'getCustomReward.`max_per_stream_setting`': '{ is_enabled: boolean; max_per_stream: number; }',
        'getCustomReward.`max_per_user_per_stream_setting`': '{ is_enabled: boolean; max_per_user_per_stream: number; }',
        'getCustomReward.`global_cooldown_setting`': '{ is_enabled: boolean; global_cooldown_seconds: number; }',
        'getCustomRewardRedemption.`reward`': '{ id: string; title: string; prompt: string; cost: number; }',
        'updateCustomReward.`image`': 'Record<"url_1x" | "url_2x" | "url_4x", string> | null',
        'updateCustomReward.`default_image`': 'Record<"url_1x" | "url_2x" | "url_4x", string>',
        'updateCustomReward.`max_per_stream_setting`': '{ is_enabled: boolean; max_per_stream: number; }',
        'updateCustomReward.`max_per_user_per_stream_setting`': '{ is_enabled: boolean; max_per_user_per_stream: number; }',
        'updateCustomReward.`global_cooldown_setting`': '{ is_enabled: boolean; global_cooldown_seconds: number; }',
        'updateRedemptionStatus.`reward`': '{ id: string; title: string; prompt: string; cost: number; }',
        'getExtensions.`icon_urls`': 'Record<string, string>',
        'getExtensions.`views`': 'Record<string, Record<string, string | number | boolean>>',  # FIXME
        'getReleasedExtensions.`icon_urls`': 'Record<string, string>',
        'getReleasedExtensions.`subscriptions_support_level`': 'string',
        'getReleasedExtensions.`views`': 'Record<string, Record<string, string | number | boolean>>',  # FIXME
        'getTopGames.`box_art_url`': 'string',
        'getGames.`box_art_url`': 'string',
        'getVideos.`url`': 'string',
        'getVideos.`thumbnail_url`': 'string',
    },
    'integer': 'number',
    'int': 'number',
    'float': 'number',
    'map[string,string]': 'Record<string, string>',
    'string array': 'string[]',
    'condition': 'EventSubCondition',  # https://dev.twitch.tv/docs/eventsub/eventsub-reference#conditions
    'transport': 'EventSubTransport',  # https://dev.twitch.tv/docs/eventsub/eventsub-reference#transport
}
url_method_fallbacks = {
    'getStreamKey': 'GET',
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
set_inner_field_level_before = {
    'getHypeTrainEvents.`last_contribution`': (1, 1),
}
set_inner_field_level_after = {
    'getCheermotes.`tiers`': 1,
    'getCheermotes.`show_in_bits_card`': 0,
    'getExtensionTransactions.`data`': 1,
    'getExtensionTransactions.`broadcast`': 0,
    'getDropsEntitlements.`data`': 1,
    'getDropsEntitlements.`updated_at`': 0,
    'updateDropsEntitlements.`data`': 1,
    'getPredictions.`outcome.top_predictors`': -1,
    'getPredictions.`outcome.top_predictors.user.channel_points_won`': 0,
    'createPrediction.`outcome.top_predictors`': -1,
    'createPrediction.`outcome.top_predictors.user.channel_points_won`': 0,
    'endPrediction.`outcome.top_predictors`': -1,
    'endPrediction.`outcome.top_predictors.user.channel_points_won`': 0,
}


def format_documentation(lines: Iterable[str]) -> List[str]:
    return ['/**'] + [f' * {line}' for line in lines] + [' */']


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
        yield '`'
    elif node.tag == 'li':
        yield '\n- '

    yield node.text or ''

    for child in node:
        if child.tag == 'br':
            yield '\n'
        else:
            yield from node_text_iter(child)
        yield child.tail or ''

    if node.tag == 'code':
        yield '`'


def node_text(node: HtmlElement, do_strip=True) -> str:
    text = nbsp.sub(' ', ''.join(text for text in node_text_iter(node)))
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
        self.is_object_list = self._field_type.lower() in ('object[]', 'array of objects')
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

    def annotation(self, function_name: str) -> str:
        if self.inner_fields:
            inner_interface = []
            for field in self.inner_fields:
                inner_interface.extend(field.interface_field(function_name))
            annotation = '{\n' + '\n'.join(inner_interface) + '}'
            if self.is_object_list:
                annotation = f'Array<{annotation}>'
        else:
            type_value = self._field_type.lower()
            type_value = type_value_lookup.get(type_value, type_value)
            if isinstance(type_value, dict):
                # short circuit
                return type_value[f'{function_name}.{self._field_name}']

            annotation = type_value

            param_multi_limit = has_possible_multi_param.search(self._description)
            if param_multi_limit and param_multi_limit.group(1) != '1':
                is_type_naturally_counted = (
                        annotation == 'number'
                        or annotation.endswith('[]')
                        or self.field_name == 'first'
                )
                if not is_type_naturally_counted:
                    annotation = f'{annotation} | {annotation}[]'

        if null_word.search(self._description.lower()) is not None:
            annotation = f'{annotation} | null'

        return annotation

    @property
    def field_parameter_documentation(self) -> List[str]:
        return format_documentation(self._description.splitlines())

    def interface_field(self, function_name: str) -> List[str]:
        optional_string = '' if self._is_required else '?'
        parameter_string = f'{self.field_name}{optional_string}: {self.annotation(function_name)};'
        return self.field_parameter_documentation + [parameter_string]


class EndpointFieldTable:
    def __init__(self, node: HtmlElement, is_parameter_required_by_header: bool, function_name: str):
        self._node = node

        self._fields: List[EndpointField] = []
        self._header_row: List[str] = []

        self._parse_node(is_parameter_required_by_header, function_name)

    def _add_field_deep(self, field: EndpointField, level: int):
        if level > 0:
            parent_field = self._fields[-1]
            if level > 1:
                for _ in range(level - 1):
                    parent_field = parent_field.inner_fields[-1]
            field.parent_field = parent_field
            fields_list = parent_field.inner_fields
        else:
            fields_list = self._fields

        if all(field.field_name != f.field_name for f in fields_list):
            fields_list.append(field)

    def _parse_node(self, is_parameter_required_by_header: bool, function_name: str):
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

        previous_indent_level = 0
        current_inner_level = 0
        forced_inner_level = 0
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

            increment_override_name = f'{function_name}.{field_name}'
            if increment_override_name in set_inner_field_level_before:
                current_inner_level, previous_indent_level = set_inner_field_level_before[increment_override_name]
            else:
                starting_spaces_match = starting_spaces.search(field_name.replace('`', ''))
                if starting_spaces_match is not None:
                    current_indent_level = len(starting_spaces_match.group())
                    if current_indent_level > previous_indent_level:
                        current_inner_level += 1
                    elif current_indent_level < previous_indent_level:
                        current_inner_level -= 1
                    previous_indent_level = current_indent_level
                else:
                    previous_indent_level = 0
                    current_inner_level = 0

            inner_level = current_inner_level + field_name.count('.') + forced_inner_level
            self._add_field_deep(field, inner_level)

            if increment_override_name in set_inner_field_level_after:
                forced_inner_level = set_inner_field_level_after[increment_override_name]

    @property
    def documentation(self) -> List[str]:
        lines = [self._header_row]
        for field in self._fields:
            lines.extend(field.documentation)
        return format_table(lines)

    @property
    def has_standard_response_signature(self) -> bool:
        field_name_set = set(f.field_name for f in self._fields)
        return 'data' not in field_name_set or not field_name_set.difference({'data', 'pagination'})

    def interface_data(self, function_name: str, is_in_response_table=False) -> List[str]:
        parameters = []
        if function_name == 'getUserActiveExtensions' and is_in_response_table:
            # Handle special case for the worst table
            outer_fields = [field for field in self._fields if field._field_type == 'map']
            inner_fields = [field for field in self._fields if field._field_type != 'map']
            for outer in outer_fields:
                parameters.extend(outer.field_parameter_documentation)
                parameters.append(f'{outer.field_name}: Record<string, ' '{')
                for inner in inner_fields:
                    if inner.field_name in ('x', 'y') and outer.field_name != 'component':
                        continue
                    parameters.extend(inner.interface_field(function_name))
                parameters.append('}>')
        else:
            for field in self._fields:
                if is_in_response_table:
                    if field.field_name == 'data':
                        for f in field.inner_fields:
                            parameters.extend(f.interface_field(function_name))
                    elif field.field_name == 'pagination':
                        continue
                    elif not self.has_standard_response_signature:
                        # This field is adjacent to "data" and "pagination" and will be set later
                        continue
                    else:
                        parameters.extend(field.interface_field(function_name))
                else:
                    parameters.extend(field.interface_field(function_name))

        return parameters


class EndpointFunction:
    def __init__(self, node: HtmlElement):
        self._node = node

        self._url_params_tables: List[EndpointFieldTable] = []
        self._request_body_tables: List[EndpointFieldTable] = []
        self._response_body_tables: List[EndpointFieldTable] = []

        self._documentation_lines: List[str] = []

        self._url_method = ''
        self._url_path = ''

        self._is_under_url_header = False
        self._is_parameter_for_body = False
        self._is_under_parameter_header = False
        self._is_parameter_required_by_header = False
        self._is_under_response_header = False
        self._shares_response_typing = False

        self._parse_node()

    def _parse_div(self, node: HtmlElement):
        div_content = node_text(node).split('\n')
        self._documentation_lines.extend([line for line in map(str.strip, div_content) if line])
        self._documentation_lines.append('')

    def _parse_header(self, node: HtmlElement):
        header_text = node_text(node)
        self._is_under_url_header = header_text in url_triggers
        self._is_under_parameter_header = any(p in header_text for p in parameter_triggers)
        self._is_under_response_header = any(p in header_text for p in response_triggers)
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
                    url_method = url_strings.get('url_method') or url_method_fallbacks[self.function_name]
                    assert url_method is not None
                    self._url_method = url_method
                    self._url_path = url_strings.get('url_path') or ''
            if self._is_under_response_header:
                self._shares_response_typing = "Response fields are the same as" in text_lines[0]
            self._documentation_lines.extend(text_lines)
            self._documentation_lines.append('')
        self._is_under_url_header = False

    def _parse_table(self, node: HtmlElement):
        table_trs = node.xpath('*/tr')
        header_row = table_trs[0]
        header_text = [node_text(th) for th in header_row]
        is_in_parameter_table = self._is_under_parameter_header and header_text[0] in table_header_parameter_columns
        is_in_response_table = self._is_under_response_header and header_text[0] in table_header_parameter_columns

        if is_in_parameter_table:
            table = EndpointFieldTable(node, self._is_parameter_required_by_header, self.function_name)
            if self._is_parameter_for_body:
                self._request_body_tables.append(table)
            else:
                self._url_params_tables.append(table)
            documentation = table.documentation
        elif is_in_response_table:
            table = EndpointFieldTable(node, True, self.function_name)
            self._response_body_tables.append(table)
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
        name_parts: List[str] = self._node.xpath('h2[1]/@id')[0].split('-')
        return name_parts[0] + ''.join(part[0].upper() + part[1:] for part in name_parts[1:])

    @property
    def _interface_name(self) -> str:
        return self.function_name[0].upper() + self.function_name[1:]

    @property
    def params_interface_name(self) -> str:
        return f'{self._interface_name}Params'

    @property
    def body_interface_name(self) -> str:
        return f'{self._interface_name}Body'

    @property
    def response_interface_name(self):
        if self._shares_response_typing:
            shared_function_id: str = self._node.xpath(
                'p[contains(text(), "Response fields are the same as")]/a/@href'
            )[0]
            id_parts = shared_function_id.lstrip('#').split('-')
            interface_name = ''.join(part[0].upper() + part[1:] for part in id_parts)
        else:
            interface_name = self._interface_name
        return f'{interface_name}Response'

    @property
    def response_data_interface_name(self):
        return self.response_interface_name + 'Data'

    @property
    def function_parameters(self) -> str:
        function_params = []
        if self._url_params_tables:
            function_params.append(f'params: t.{self.params_interface_name}')
        if self._request_body_tables:
            function_params.append(f'data: t.{self.body_interface_name}')
        return ', '.join(function_params)

    @property
    def function_arguments(self) -> str:
        function_args = [f'method: {self._url_method.strip()!r}', f'url: {self._url_path!r}']
        if self._url_params_tables:
            function_args.append('params')
        if self._request_body_tables:
            function_args.append('data')

        return '{ ' + ', '.join(function_args) + ' }'

    @property
    def function_docstring(self) -> List[str]:
        lines = self._documentation_lines + ['']
        if self._url_params_tables:
            lines.append('@param params The URL params object')
        if self._request_body_tables:
            lines.append('@param body The request body object')
        lines.append('@returns An observable that emits with the response object when the request completes')
        return format_documentation(lines)

    @property
    def function_body(self) -> List[str]:
        has_response_interface = bool(self._response_body_tables) or self._shares_response_typing
        response_type = f't.{self.response_interface_name}' if has_response_interface else 'void'
        def_line = f'{self.function_name}({self.function_parameters}): Observable<AxiosResponse<{response_type}>> ' '{'
        return_line = f'return this._makeRequest<{response_type}>({self.function_arguments});'
        return [
            def_line,
            return_line,
            '}',
        ]

    @property
    def function_test(self) -> List[str]:
        has_response_interface = bool(self._response_body_tables) or self._shares_response_typing
        response_type = f't.{self.response_interface_name}' if has_response_interface else 'void'
        response_value = '{}' if has_response_interface else 'void 0'
        test_lines = [
            f'describe("{self.function_name}", () => ' '{',
            f'it("calls axios request", () => ' '{',
            f'requestMock.mockReturnValueOnce(getResponseObservable<{response_type}>({response_value}));',
        ]

        test_call_args_parts = []
        if self._url_params_tables:
            test_lines.append(f'const params: t.{self.params_interface_name} = ' '{};')
            test_call_args_parts.append('params')
        if self._request_body_tables:
            test_lines.append(f'const data: t.{self.body_interface_name} = ' '{};')
            test_call_args_parts.append('data')
        test_call_args = ', '.join(test_call_args_parts)

        return test_lines + [
            f'const result = direct.{self.function_name}({test_call_args});',
            'expect(requestMock).toHaveBeenCalledTimes(1);',
            f'expect(requestMock).toHaveBeenCalledWith({self.function_arguments});',
            '});',
            '});',
            '',
        ]

    @property
    def response_type_definition(self) -> List[str]:
        lines = []
        code_examples = self._node.xpath(response_example_xpath)
        codes_text = [node_text(node, False) for node in code_examples]
        data_responses = [c for c in codes_text if any(line.lstrip().startswith('"data":') for line in c.splitlines())]
        flattened = [' '.join(line.strip() for line in c.splitlines()) for c in data_responses]
        is_listed_data_response = any(
            m is not None and m.group(1) is not None
            for m in map(data_array_check.search, flattened)
        )
        is_paginated_response = any(
            any(line.lstrip().startswith('"pagination":') for line in c.splitlines())
            for c in codes_text
        )
        if is_listed_data_response:
            data_response_type = f'DataListResponse<{self.response_data_interface_name}>'
        else:
            data_response_type = f'DataObjectResponse<{self.response_data_interface_name}>'

        if is_paginated_response:
            is_pagination_flat_string = any(m is not None for m in map(pagination_string_check.search, flattened))
            if is_pagination_flat_string:
                pagination_response_type = f'PaginatedFlatResponse'
            else:
                pagination_response_type = f'PaginatedCursorResponse'
        else:
            pagination_response_type = None

        table = self._response_body_tables[0]
        inheritance = data_response_type
        if table.has_standard_response_signature:
            if pagination_response_type is not None:
                inheritance = f'{inheritance} & {pagination_response_type}'
            lines.append(f'export type {self.response_interface_name} = {inheritance};')
        else:
            if pagination_response_type is not None:
                inheritance = f'{inheritance}, {pagination_response_type}'
            lines.append(f'export interface {self.response_interface_name} extends {inheritance} ' '{')
            for field in table._fields:
                if field.field_name not in ('data', 'pagination'):
                    lines.extend(field.interface_field(self.function_name))
            lines.append('}')

        return lines

    @property
    def interface_code(self) -> List[str]:
        interfaces = []
        if self._url_params_tables:
            interfaces.append(f'export interface {self.params_interface_name} ' '{')
            for table in self._url_params_tables:
                interfaces.extend(table.interface_data(self.function_name))
            interfaces.append('}')
        if self._request_body_tables:
            interfaces.append(f'export interface {self.body_interface_name} ' '{')
            for table in self._request_body_tables:
                interfaces.extend(table.interface_data(self.function_name))
            interfaces.append('}')
        if self._response_body_tables:
            if len(self._response_body_tables) > 1:
                raise Exception('further inspection needed')
            interfaces.append(f'export interface {self.response_data_interface_name} ' '{')
            table = self._response_body_tables[0]
            interfaces.extend(table.interface_data(self.function_name, True))
            interfaces.append('}')
            interfaces.extend(self.response_type_definition)
        return interfaces

    @property
    def function_code(self) -> List[str]:
        return self.function_docstring + self.function_body


def parse_document(document: HtmlElement) -> Tuple[List[str], List[str]]:
    sections = document.xpath(sections_xpath)
    interface_lines = []
    functions_lines = []

    for section in sections:
        functions_lines.append('')
        function = EndpointFunction(section)
        interface_lines.extend(function.interface_code)
        functions_lines.extend(function.function_code)

    functions_lines.append('}')
    return interface_lines, functions_lines


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
    typings_lines, api_lines = parse_document(markup)

    typings_template = (this_dir / 'types.ts.template').read_text()
    typings_text = typings_template + '\n'.join(typings_lines) + '\n'
    for misspelled, corrected in spelling_fixes.items():
        typings_text = typings_text.replace(misspelled, corrected)
    typings_file = this_dir / 'types.ts'
    typings_file.write_text(typings_text)

    api_template = (this_dir / 'direct.ts.template').read_text()
    api_text = api_template + '\n'.join(api_lines) + '\n'
    for misspelled, corrected in spelling_fixes.items():
        api_text = api_text.replace(misspelled, corrected)
    api_file = this_dir / 'direct.ts'
    api_file.write_text(api_text)
