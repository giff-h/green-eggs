# -*- coding: utf-8 -*-
import inspect
from typing import Any, Awaitable, Callable, List

from aiologger import Logger


async def catch_all(_logger: Logger, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
    """
    Wrap a coroutine function in a full try/except block so the exception can be logged.

    Useful if it needs to be tasked.

    :param _logger: The logger to log the exception
    :param func: The coroutine function
    :param args: The positional arguments of the coroutine function
    :param kwargs: The keyword arguments of the coroutine function
    :return: The return value of the awaited coroutine, or None if it errored
    """
    # noinspection PyBroadException
    try:
        return await func(*args, **kwargs)
    except Exception:
        _logger.exception(f'Error happened in {func.__name__}')


def validate_function_signature(func: Callable[..., Any], expected_keywords: List[str]) -> List[inspect.Parameter]:
    """
    Validate that the given function does not have any unexpected required parameters.

    Any required positional-only parameters will raise `TypeError`. Any required keyword-able arguments that are not in
    `expected_keywords` will raise `TypeError`.

    Returns the subset of parameters that the function accepts.

    :param func: The function to validate
    :param List[str] expected_keywords: The list of keyword-able arguments that are allowed
    :return: The list of Parameter objects from the function that are in the given expected keywords
    :rtype: List[inspect.Parameter]
    """
    sig = inspect.signature(func)
    parameters = list(sig.parameters.values())
    pos_only_no_default = [p.name for p in parameters if p.kind == p.POSITIONAL_ONLY and p.default is p.empty]

    if len(pos_only_no_default):
        arg_names = ', '.join(map(repr, pos_only_no_default))
        raise TypeError(f'Command callbacks may not have any non-default positional-only parameters ({arg_names})')

    keyword_kinds = (
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    )
    unexpected = [
        p.name
        for p in parameters
        if p.kind in keyword_kinds and p.default is p.empty and p.name not in expected_keywords
    ]
    if len(unexpected):
        arg_names = ', '.join(map(repr, unexpected))
        plural = '' if len(unexpected) == 1 else 's'
        raise TypeError(f'Unexpected required keyword parameter{plural} in <{func.__name__}>: {arg_names}')

    return [p for p in parameters if p.kind in keyword_kinds and p.name in expected_keywords]
