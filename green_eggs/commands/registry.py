# -*- coding: utf-8 -*-
from typing import AsyncIterator, Callable, ClassVar, Dict, Iterator, List, MutableMapping, Optional

from green_eggs.api import TwitchApi
from green_eggs.channel import Channel
from green_eggs.data_types import PrivMsg
from green_eggs.types import RegisterAbleFunc
from green_eggs.utils import validate_function_signature

from .triggers import CommandTrigger


class CommandRunner:
    command_keywords: ClassVar[List[str]] = ['api', 'channel', 'message']

    def __init__(self, command_func: RegisterAbleFunc):
        self._command_func: RegisterAbleFunc = command_func
        self._func_keywords: List[str] = [
            p.name for p in validate_function_signature(command_func, self.command_keywords)
        ]

    async def run(self, *, api: TwitchApi, channel: Channel, message: PrivMsg) -> Optional[str]:
        kwargs = dict(api=api, channel=channel, message=message)
        kwargs = {k: v for k, v in kwargs.items() if k in self._func_keywords}
        output = self._command_func(**kwargs)
        if output is None or isinstance(output, str):
            return output
        else:
            return await output


class CommandRegistry(MutableMapping[CommandTrigger, CommandRunner]):
    def __init__(self):
        super().__init__()

        self._commands: Dict[CommandTrigger, CommandRunner] = dict()

    def __setitem__(self, k: CommandTrigger, v: CommandRunner) -> None:
        self._commands[k] = v

    def __delitem__(self, k: CommandTrigger) -> None:
        del self._commands[k]

    def __getitem__(self, k: CommandTrigger) -> CommandRunner:
        return self._commands[k]

    def __len__(self) -> int:
        return len(self._commands)

    def __iter__(self) -> Iterator[CommandTrigger]:
        return iter(self._commands)

    async def _lookup_gen(self, message: PrivMsg, channel: Channel) -> AsyncIterator[CommandRunner]:
        for t, f in self.items():
            if await t.check(message, channel):
                yield f

    def add(self, trigger: CommandTrigger, command_func: RegisterAbleFunc):
        """
        Add a command function and its trigger to the registry.

        :param CommandTrigger trigger: The trigger that checks messages
        :param command_func: The function that the command runs
        :type command_func: Callable[..., Union[Optional[str], Awaitable[Optional[str]]]]
        """
        self[trigger] = CommandRunner(command_func)

    async def all(self, message: PrivMsg, channel: Channel) -> List[CommandRunner]:
        """
        Returns all command functions that were triggered by the message.

        :param PrivMsg message: Message from Twitch
        :param Channel channel: The channel the message is from
        :return: The list of command runners that matched the message
        :rtype: List[CommandRunner]
        """
        return [runner async for runner in self._lookup_gen(message, channel)]

    def decorator(
        self,
        trigger: CommandTrigger,
        *,
        target_keywords: Optional[List[str]] = None,
        command_factory: Optional[Callable[[RegisterAbleFunc, List[str]], RegisterAbleFunc]] = None,
    ):
        expected_keywords = CommandRunner.command_keywords if target_keywords is None else target_keywords

        def wrapper(callback: RegisterAbleFunc) -> RegisterAbleFunc:
            callback_accepts = validate_function_signature(callback, expected_keywords)
            callback_keywords = [p.name for p in callback_accepts]
            command = callback if command_factory is None else command_factory(callback, callback_keywords)
            self.add(trigger, command)
            return callback

        return wrapper

    async def find(self, message: PrivMsg, channel: Channel) -> Optional[CommandRunner]:
        """
        Returns the first command function that was triggered by the message.

        :param PrivMsg message: Message from Twitch
        :param Channel channel: The channel the message is from
        :return: The maybe first command runner that matched the message
        :rtype: CommandRunner or None
        """
        async for runner in self._lookup_gen(message, channel):
            return runner
        return None
