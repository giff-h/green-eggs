# -*- coding: utf-8 -*-
from typing import Callable, ClassVar, Dict, Iterator, List, MutableMapping, Optional

from green_eggs.data_types import PrivMsg
from green_eggs.types import RegisterAbleFunc
from green_eggs.utils import validate_function_signature

from .triggers import CommandTrigger


class CommandRunner:
    command_keywords: ClassVar[List[str]] = ['api', 'channel', 'message']

    def __init__(self, command_func: RegisterAbleFunc):
        self.command_func = command_func
        self.func_keywords = [p.name for p in validate_function_signature(command_func, self.command_keywords)]

    def accepts(self, keyword: str) -> bool:
        return keyword in self.func_keywords

    async def run(self, **kwargs) -> Optional[str]:
        output = self.command_func(**kwargs)
        if output is None or isinstance(output, str):
            return output
        else:
            return await output


class CommandRegistry(MutableMapping[CommandTrigger, CommandRunner]):
    def __init__(self):
        super().__init__()

        self.__commands: Dict[CommandTrigger, CommandRunner] = dict()

    def __setitem__(self, k: CommandTrigger, v: CommandRunner) -> None:
        self.__commands[k] = v

    def __delitem__(self, k: CommandTrigger) -> None:
        del self.__commands[k]

    def __getitem__(self, k: CommandTrigger) -> CommandRunner:
        return self.__commands[k]

    def __len__(self) -> int:
        return len(self.__commands)

    def __iter__(self) -> Iterator[CommandTrigger]:
        return iter(self.__commands)

    def __lookup_gen(self, message: PrivMsg) -> Iterator[CommandRunner]:
        for t, f in self.items():
            if t.check(message):
                yield f

    def add(self, trigger: CommandTrigger, command_func: RegisterAbleFunc):
        """
        Add a command function and its trigger to the registry.

        :param CommandTrigger trigger: The trigger that checks messages
        :param command_func: The function that the command runs
        :type command_func: Callable[..., Union[Optional[str], Awaitable[Optional[str]]]]
        """
        self[trigger] = CommandRunner(command_func)

    def all(self, message: PrivMsg) -> List[CommandRunner]:
        """
        Returns all command functions that were triggered by the message.

        :param PrivMsg message: Message from Twitch
        :return: The list of command runners that matched the message
        :rtype: List[CommandRunner]
        """
        return list(self.__lookup_gen(message))

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

    def find(self, message: PrivMsg) -> Optional[CommandRunner]:
        """
        Returns the first command function that was triggered by the message.

        :param PrivMsg message: Message from Twitch
        :return: The maybe first command runner that matched the message
        :rtype: CommandRunner or None
        """
        return next(self.__lookup_gen(message), None)
