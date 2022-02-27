# -*- coding: utf-8 -*-
import time
from typing import AsyncIterator, Callable, ClassVar, Dict, Iterator, List, MutableMapping, Optional

from green_eggs.api import TwitchApiCommon
from green_eggs.channel import Channel
from green_eggs.commands.triggers import CommandTrigger
from green_eggs.data_types import PrivMsg
from green_eggs.exceptions import GlobalCooldownNotElapsed, UserCooldownNotElapsed
from green_eggs.types import RegisterAbleFunc
from green_eggs.utils import validate_function_signature


class CommandRunner:
    command_keywords: ClassVar[List[str]] = ['api', 'channel', 'message']

    def __init__(self, command_func: RegisterAbleFunc, *, global_cooldown: Optional[int], user_cooldown: Optional[int]):
        self._command_func: RegisterAbleFunc = command_func
        self._func_keywords: List[str] = [
            p.name for p in validate_function_signature(command_func, self.command_keywords)
        ]
        self._last_run: Optional[float] = None
        self._last_run_for_user: Dict[str, float] = dict()
        self._global_cooldown = global_cooldown
        self._user_cooldown = user_cooldown

    def _check_cooldown_elapsed(self, user_id: str):
        if self._global_cooldown is None and self._user_cooldown is None:
            return

        now = time.monotonic()
        if self._user_cooldown is not None:
            if user_id in self._last_run_for_user:
                has_user_cooldown_elapsed = (self._last_run_for_user[user_id] + self._user_cooldown) <= now
                if not has_user_cooldown_elapsed:
                    remaining = (self._last_run_for_user[user_id] + self._user_cooldown) - now
                    raise UserCooldownNotElapsed(remaining)
            self._last_run_for_user[user_id] = now
        if self._global_cooldown is not None:
            if self._last_run is not None:
                has_global_cooldown_elapsed = (self._last_run + self._global_cooldown) <= now
                if not has_global_cooldown_elapsed:
                    remaining = (self._last_run + self._global_cooldown) - now
                    raise GlobalCooldownNotElapsed(remaining)
            self._last_run = now

    def _filter_func_keywords(self, **kwargs):
        return {k: v for k, v in kwargs.items() if k in self._func_keywords}

    async def run(self, *, api: TwitchApiCommon, channel: Channel, message: PrivMsg) -> Optional[str]:
        """
        Runs this command with the given values.

        Carries the return value of the command as an optional string to send to chat.

        If the cooldowns have not yet elapsed, raises either `GlobalCooldownNotElapsed` or `UserCooldownNotElapsed`.

        :param TwitchApiCommon api: The Twitch API client
        :param Channel channel: The channel the message is from
        :param PrivMsg message: PRIVMSG from Twitch
        :return: Possible message to send to chat
        :rtype: str or None
        """
        self._check_cooldown_elapsed(message.tags.user_id)
        kwargs = self._filter_func_keywords(api=api, channel=channel, message=message)
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

    def add(
        self,
        trigger: CommandTrigger,
        command_func: RegisterAbleFunc,
        *,
        global_cooldown: Optional[int],
        user_cooldown: Optional[int],
    ):
        """
        Add a command function and its trigger to the registry.

        :param CommandTrigger trigger: The trigger that checks messages
        :param command_func: The function that the command runs
        :param global_cooldown: The global cooldown of the command
        :param user_cooldown: The user-specific cooldown of the command
        :type command_func: Callable[..., Union[Optional[str], Awaitable[Optional[str]]]]
        """
        self[trigger] = CommandRunner(command_func, global_cooldown=global_cooldown, user_cooldown=user_cooldown)

    async def all(self, message: PrivMsg, channel: Channel) -> List[CommandRunner]:
        """
        Returns all command functions that were triggered by the message.

        :param PrivMsg message: PRIVMSG from Twitch
        :param Channel channel: The channel the message is from
        :return: The list of command runners that matched the message
        :rtype: List[CommandRunner]
        """
        return [runner async for runner in self._lookup_gen(message, channel)]

    def decorator(
        self,
        trigger: CommandTrigger,
        *,
        global_cooldown: Optional[int],
        user_cooldown: Optional[int],
        target_keywords: Optional[List[str]] = None,
        command_factory: Optional[Callable[[RegisterAbleFunc, List[str]], RegisterAbleFunc]] = None,
    ):
        expected_keywords = CommandRunner.command_keywords if target_keywords is None else target_keywords

        def wrapper(callback: RegisterAbleFunc) -> RegisterAbleFunc:
            callback_accepts = validate_function_signature(callback, expected_keywords)
            callback_keywords = [p.name for p in callback_accepts]
            command = callback if command_factory is None else command_factory(callback, callback_keywords)
            self.add(trigger, command, global_cooldown=global_cooldown, user_cooldown=user_cooldown)
            return callback

        return wrapper

    async def find(self, message: PrivMsg, channel: Channel) -> Optional[CommandRunner]:
        """
        Returns the first command function that was triggered by the message.

        :param PrivMsg message: PRIVMSG from Twitch
        :param Channel channel: The channel the message is from
        :return: The maybe first command runner that matched the message
        :rtype: CommandRunner or None
        """
        async for runner in self._lookup_gen(message, channel):
            return runner
        return None
