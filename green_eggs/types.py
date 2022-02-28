# -*- coding: utf-8 -*-
from typing import Awaitable, Callable, Optional, Union

# Type of the user defined function
RegisterAbleFunc = Union[Callable[..., Optional[str]], Callable[..., Awaitable[Optional[str]]]]
