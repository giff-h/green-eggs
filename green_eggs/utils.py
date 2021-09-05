# -*- coding: utf-8 -*-
import inspect
from typing import Any, Callable, List


def validate_function_signature(func: Callable[..., Any], expected_keywords: List[str]) -> List[inspect.Parameter]:
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
