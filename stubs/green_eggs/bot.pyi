from typing import Any, Dict, Mapping, Optional

from green_eggs.api import TwitchApiCommon as TwitchApiCommon
from green_eggs.channel import Channel as Channel
from green_eggs.client import TwitchChatClient as TwitchChatClient
from green_eggs.commands import CommandRegistry as CommandRegistry
from green_eggs.commands import FirstWordTrigger as FirstWordTrigger
from green_eggs.commands import SenderIsModTrigger as SenderIsModTrigger
from green_eggs.config import Config as Config
from green_eggs.data_types import PrivMsg as PrivMsg
from green_eggs.exceptions import CooldownNotElapsed as CooldownNotElapsed
from green_eggs.types import RegisterAbleFunc as RegisterAbleFunc
from green_eggs.utils import catch_all as catch_all

class ChatBot:
    def __init__(self, channel: str, *, config: Dict[str, Any] = ...) -> None: ...
    def register_basic_commands(
        self,
        commands: Mapping[str, str],
        *,
        case_sensitive: bool = ...,
        global_cooldown: Optional[int] = ...,
        user_cooldown: Optional[int] = ...,
    ): ...
    def register_caster_command(
        self,
        invoke: str,
        *,
        case_sensitive: bool = ...,
        global_cooldown: Optional[int] = ...,
        user_cooldown: Optional[int] = ...,
    ): ...
    def register_command(
        self,
        invoke: str,
        *,
        case_sensitive: bool = ...,
        global_cooldown: Optional[int] = ...,
        user_cooldown: Optional[int] = ...,
    ): ...
    def run_sync(self, username: str, token: str, client_id: str): ...
    async def run_async(self, username: str, token: str, client_id: str): ...
