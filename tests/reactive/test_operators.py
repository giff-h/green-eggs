# -*- coding: utf-8 -*-
from typing import Any

from reactivex import of

from green_eggs.reactive.operators import filter_is_instance, filter_is_not_none


def test_filter_is_instance():
    should_be_int = []
    of(1, 'hello', [True], False).pipe(filter_is_instance(int)).subscribe(lambda x: should_be_int.append(x))
    assert should_be_int == [1, False]


def test_filter_is_not_none():
    should_be_not_none = []
    of(None, False, 'hello', [1, 2]).pipe(filter_is_not_none(Any)).subscribe(lambda x: should_be_not_none.append(x))
    assert should_be_not_none == [False, 'hello', [1, 2]]
