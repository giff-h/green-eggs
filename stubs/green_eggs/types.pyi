from typing import Awaitable, Callable, Optional, Union

RegisterAbleFunc = Callable[..., Union[Optional[str], Awaitable[Optional[str]]]]
