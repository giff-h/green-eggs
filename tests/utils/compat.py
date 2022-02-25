# -*- coding: utf-8 -*-
import asyncio
import sys


def coroutine_result_value(value):
    """
    Compatibility function to return the given value in a form that can serve as a valid coroutine mock return value for
    all Python versions from 3.7 to 3.10.
    """
    if sys.version_info[:2] == (3, 7):
        future = asyncio.Future()
        future.set_result(value)
        return future
    else:
        return value
