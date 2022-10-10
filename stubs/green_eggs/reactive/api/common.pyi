from types import TracebackType
from typing import Any, Dict, Optional, Type

from aiologger import Logger
import reactivex as rx

from green_eggs.reactive.api.direct import TwitchApiDirect

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
    @staticmethod
    def from_channel_info(channel: Dict[str, Any]) -> ShoutoutInfo: ...
    def __init__(
        self, user_id, username, display_name, game_name, game_id, broadcaster_language, stream_title
    ) -> None: ...

MaybeShoutout = Optional[ShoutoutInfo]

class TwitchApiCommon:
    def __init__(self, client_id: str, token: str, logger: Logger) -> None: ...
    @property
    def direct(self) -> TwitchApiDirect: ...
    async def __aenter__(self) -> TwitchApiCommon: ...
    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None: ...
    def get_is_user_subscribed_to_channel(self, broadcaster_id: str, user_id: str) -> rx.Observable[bool]: ...
    def get_shoutout_info(self, *, username: str = ..., user_id: str = ...) -> rx.Observable[MaybeShoutout]: ...
