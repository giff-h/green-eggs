from typing import Awaitable, Callable, Optional, Union

RegisterAbleFunc = Union[Callable[..., Optional[str]], Callable[..., Awaitable[Optional[str]]]]
