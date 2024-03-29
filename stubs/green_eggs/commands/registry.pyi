from typing import Callable, ClassVar, Iterator, List, MutableMapping, Optional

from green_eggs.api import TwitchApiCommon as TwitchApiCommon
from green_eggs.channel import Channel as Channel
from green_eggs.commands.triggers import CommandTrigger as CommandTrigger
from green_eggs.data_types import PrivMsg as PrivMsg
from green_eggs.exceptions import GlobalCooldownNotElapsed as GlobalCooldownNotElapsed
from green_eggs.exceptions import UserCooldownNotElapsed as UserCooldownNotElapsed
from green_eggs.types import RegisterAbleFunc as RegisterAbleFunc
from green_eggs.utils import validate_function_signature as validate_function_signature

class CommandRunner:
    command_keywords: ClassVar[List[str]]
    def __init__(
        self, command_func: RegisterAbleFunc, *, global_cooldown: Optional[int], user_cooldown: Optional[int]
    ) -> None: ...
    async def run(self, *, api: TwitchApiCommon, channel: Channel, message: PrivMsg) -> Optional[str]: ...

class CommandRegistry(MutableMapping[CommandTrigger, CommandRunner]):
    def __init__(self) -> None: ...
    def __setitem__(self, k: CommandTrigger, v: CommandRunner) -> None: ...
    def __delitem__(self, k: CommandTrigger) -> None: ...
    def __getitem__(self, k: CommandTrigger) -> CommandRunner: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[CommandTrigger]: ...
    def add(
        self,
        trigger: CommandTrigger,
        command_func: RegisterAbleFunc,
        *,
        global_cooldown: Optional[int],
        user_cooldown: Optional[int],
    ): ...
    async def all(self, message: PrivMsg, channel: Channel) -> List[CommandRunner]: ...
    def decorator(
        self,
        trigger: CommandTrigger,
        *,
        global_cooldown: Optional[int],
        user_cooldown: Optional[int],
        target_keywords: Optional[List[str]] = ...,
        command_factory: Optional[Callable[[RegisterAbleFunc, List[str]], RegisterAbleFunc]] = ...,
    ): ...
    async def find(self, message: PrivMsg, channel: Channel) -> Optional[CommandRunner]: ...
