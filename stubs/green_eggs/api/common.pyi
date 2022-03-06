from types import TracebackType
from typing import Any, Dict, Optional, Type

from aiologger import Logger

from .direct import TwitchApiDirect

async def validate_client_id(api_token: str) -> str: ...

class ShoutoutInfo:
    user_id: str
    username: str
    display_name: str
    game_name: str
    game_id: str
    broadcaster_language: str
    stream_title: str
    @property
    def user_link(self) -> str: ...
    def update_from_stream_result(self, stream: Dict[str, Any]): ...
    def __init__(
        self, user_id, username, display_name, game_name, game_id, broadcaster_language, stream_title
    ) -> None: ...

class TwitchApiCommon:
    def __init__(self, client_id: str, token: str, logger: Logger) -> None: ...
    @property
    def direct(self) -> TwitchApiDirect: ...
    async def __aenter__(self) -> TwitchApiCommon: ...
    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ): ...
    async def get_shoutout_info(self, *, username: str = ..., user_id: str = ...) -> Optional[ShoutoutInfo]: ...
    async def is_user_subscribed_to_channel(self, broadcaster_id: str, user_id: str) -> bool: ...
