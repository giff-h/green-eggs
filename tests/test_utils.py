# -*- coding: utf-8 -*-
from inspect import Parameter
import sys

from pytest_mock import MockerFixture

from green_eggs.utils import catch_all, validate_function_signature
from tests import logger


async def test_catch_all_returns_value(mocker: MockerFixture):
    mocker.patch('aiologger.Logger.exception')

    async def _add_five(x):
        return x + 5

    assert await catch_all(logger, _add_five, 3) == 8
    logger.exception.assert_not_called()  # type: ignore[attr-defined]


async def test_catch_all_logs_exception(mocker: MockerFixture):
    mocker.patch('aiologger.Logger.exception')

    async def _throw_exception(message):
        raise ValueError(message)

    assert await catch_all(logger, _throw_exception, message='foo bar') is None
    name = 'test_catch_all_logs_exception.<locals>._throw_exception'
    logger.exception.assert_called_once_with(f'Error happened in <{name}>')  # type: ignore[attr-defined]


if sys.version_info[:2] >= (3, 8):  # These test asserts a condition that only happens on python 3.8 and later

    def test_validate_function_signature_positional_only_no_defaults_not_allowed():
        # This is necessary to bypass the syntax error on 3.7
        func = '''
def _invalid_function(a, b=1, /):
    return str(a) + str(b)'''.strip()
        globals_ = dict(str=str)
        locals_ = dict()
        exec(func, globals_, locals_)
        _invalid_function = locals_['_invalid_function']

        try:
            validate_function_signature(_invalid_function, ['a', 'b'])
        except TypeError as e:
            assert e.args[0] == 'Positional-only parameters without defaults are not allowed in <_invalid_function>'
        else:
            assert False, 'Not raised'

    def test_validate_function_signature_positional_only_with_defaults_allowed():
        # This is necessary to bypass the syntax error on 3.7
        func = '''
def _valid_function(a='0', b=1, /):
    return str(a) + str(b)'''.strip()
        globals_ = dict(str=str)
        locals_ = dict()
        exec(func, globals_, locals_)
        _valid_function = locals_['_valid_function']

        assert validate_function_signature(_valid_function, ['a', 'b']) == []


def test_validate_function_signature_one_unexpected_parameter():
    def _invalid_function(unexpected, with_default=None):
        return str(unexpected) + str(with_default)

    try:
        validate_function_signature(_invalid_function, ['not_present'])
    except TypeError as e:
        name = 'test_validate_function_signature_one_unexpected_parameter.<locals>._invalid_function'
        assert e.args[0] == f'Unexpected required keyword parameter in <{name}>: \'unexpected\''
    else:
        assert False, 'Not raised'


def test_validate_function_signature_multiple_unexpected_parameters():
    def _invalid_function(unexpected_one, unexpected_two, with_default=None):
        return str(unexpected_one) + str(unexpected_two) + str(with_default)

    try:
        validate_function_signature(_invalid_function, ['not_found'])
    except TypeError as e:
        name = 'test_validate_function_signature_multiple_unexpected_parameters.<locals>._invalid_function'
        assert (
            e.args[0] == f'Unexpected required keyword parameters in <{name}>: '
            '\'unexpected_one\', \'unexpected_two\''
        )
    else:
        assert False, 'Not raised'


def test_validate_function_signature_returns_subset_of_expected_keywords():
    def _valid_function(expected_two, *, expected_one, with_default=None):
        return str(expected_one) + str(expected_two) + str(with_default)

    result = validate_function_signature(_valid_function, ['expected_one', 'expected_two', 'expected_three'])
    assert result == [
        Parameter('expected_two', Parameter.POSITIONAL_OR_KEYWORD),
        Parameter('expected_one', Parameter.KEYWORD_ONLY),
    ]
