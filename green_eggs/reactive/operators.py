# -*- coding: utf-8 -*-
from typing import Any, Callable, Optional, cast

import reactivex as rx
from reactivex import operators as ops

__all__ = ('filter_is_instance', 'filter_is_not_none')


def filter_is_instance(klass):
    def _is_instance(value) -> bool:
        return isinstance(value, klass)

    return cast(Callable[[rx.Observable[Any]], rx.Observable[klass]], ops.filter(_is_instance))


def filter_is_not_none(internal):
    def _is_not_none(value) -> bool:
        return value is not None

    return cast(Callable[[rx.Observable[Optional[internal]]], rx.Observable[internal]], ops.filter(_is_not_none))
