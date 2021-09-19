# -*- coding: utf-8 -*-
import abc
from collections.abc import Hashable
import itertools
from typing import Any, AsyncGenerator, Iterable, Iterator, List

from green_eggs.channel import Channel
from green_eggs.data_types import PrivMsg


async def async_all(async_generator: AsyncGenerator[Any, None]) -> bool:
    async for v in async_generator:
        if not v:
            return False
    return True


async def async_any(async_generator: AsyncGenerator[Any, None]) -> bool:
    async for v in async_generator:
        if v:
            return True
    return False


class CommandTrigger(Hashable, abc.ABC):
    def __and__(self, other: 'CommandTrigger') -> 'AndTrigger':
        return AndTrigger(self, other)

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and hash(self) == hash(other)

    def __or__(self, other: 'CommandTrigger') -> 'OrTrigger':
        return OrTrigger(self, other)

    @abc.abstractmethod
    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        raise NotImplementedError()


class LogicTrigger(CommandTrigger, abc.ABC):
    @classmethod
    def _flatten(cls, triggers: Iterable[CommandTrigger]) -> Iterator[Iterable[CommandTrigger]]:
        for trigger in triggers:
            if isinstance(trigger, cls):
                # a & (b & c) & d ≡ a & b & c & d
                # a | (b | c) | d ≡ a | b | c | d
                yield trigger._triggers
            elif isinstance(trigger, LogicTrigger) and not len(trigger._triggers):
                yield tuple()
            else:
                yield (trigger,)

    def __init__(self, *triggers: CommandTrigger):
        # set because a & a ≡ a and a | a ≡ a
        # sorted because a & b ≡ b & a and a | b ≡ b | a
        self._triggers: List[CommandTrigger] = sorted(
            set(itertools.chain.from_iterable(self._flatten(triggers))), key=hash
        )

    def __hash__(self) -> int:
        return hash((type(self), tuple(self._triggers)))


class AndTrigger(LogicTrigger):
    """
    Command trigger that passes the check if there are any internal triggers and every internal trigger passes the
    check.

    Construct using the `&` operator on other triggers like `a & b`.
    """

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        # noinspection PyTypeChecker
        return bool(len(self._triggers)) and await async_all(  # type: ignore[arg-type]
            await trigger.check(message, channel) for trigger in self._triggers
        )


class OrTrigger(LogicTrigger):
    """
    Command trigger that passes the check if there are any internal triggers and at least one internal trigger passes
    the check.

    Construct using the `|` operator on other triggers like `a | b`.
    """

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        # noinspection PyTypeChecker
        return bool(len(self._triggers)) and await async_any(  # type: ignore[arg-type]
            await trigger.check(message, channel) for trigger in self._triggers
        )


class FirstWordTrigger(CommandTrigger):
    """
    Command trigger that passes the check if the first word of the message matches the given value.

    Can be made case sensitive or not. Case insensitive by default.
    """

    def __init__(self, value: str, case_sensitive=False):
        self._value: str = value
        self._case_sensitive: bool = case_sensitive

    def __hash__(self) -> int:
        return hash((type(self), self._value, self._case_sensitive))

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        word = message.words[0] if self._case_sensitive else message.words[0].lower()
        value = self._value if self._case_sensitive else self._value.lower()
        return word == value


class SenderIsModTrigger(CommandTrigger):
    """
    Command trigger that passes the check if the sender is a moderator or the broadcaster.
    """

    def __hash__(self) -> int:
        return hash((type(self),))

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        return message.tags.mod or 'broadcaster' in message.tags.badges


class SenderIsSubscribedTrigger(CommandTrigger):
    """
    Command trigger that passes the check if the sender is subscribed.
    """

    def __hash__(self) -> int:
        return hash((type(self),))

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        return await channel.is_user_subscribed(message.tags.user_id)
