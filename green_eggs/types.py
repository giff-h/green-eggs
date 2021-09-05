# -*- coding: utf-8 -*-
from typing import Awaitable, Callable, Optional, Union

# Type of the user defined function
RegisterAbleFunc = Callable[..., Union[Optional[str], Awaitable[Optional[str]]]]
