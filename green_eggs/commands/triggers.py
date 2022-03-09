# -*- coding: utf-8 -*-
from __future__ import annotations

import abc
from collections.abc import Hashable
from typing import Iterable, Iterator, List

import asyncstdlib as a

from green_eggs.channel import Channel
from green_eggs.data_types import PrivMsg


class CommandTrigger(Hashable, abc.ABC):
    def __and__(self, other: CommandTrigger) -> AndTrigger:
        return AndTrigger(self, other)

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and hash(self) == hash(other)

    def __invert__(self) -> CommandTrigger:
        return InvertedTrigger(self)

    def __or__(self, other: CommandTrigger) -> OrTrigger:
        return OrTrigger(self, other)

    @abc.abstractmethod
    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        raise NotImplementedError()


class InvertedTrigger(CommandTrigger):
    def __init__(self, inner: CommandTrigger):
        self.inner = inner

    def __hash__(self) -> int:
        return hash((type(self), self.inner))

    def __invert__(self) -> CommandTrigger:
        return self.inner

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        return not await self.inner.check(message, channel)


class LogicTrigger(CommandTrigger, abc.ABC):
    @classmethod
    def _flatten(cls, triggers: Iterable[CommandTrigger]) -> Iterator[CommandTrigger]:
        for trigger in triggers:
            if isinstance(trigger, cls):
                # a & (b & c) & d ≡ a & b & c & d
                # a | (b | c) | d ≡ a | b | c | d
                yield from trigger._triggers
            elif isinstance(trigger, LogicTrigger) and not len(trigger._triggers):
                pass
            else:
                yield trigger

    def __init__(self, *triggers: CommandTrigger):
        # set because a & a ≡ a and a | a ≡ a
        # sorted because a & b ≡ b & a and a | b ≡ b | a
        self._triggers: List[CommandTrigger] = sorted(set(self._flatten(triggers)), key=hash)

    def __hash__(self) -> int:
        return hash((type(self), *self._triggers))


class AndTrigger(LogicTrigger):
    """
    Command trigger that passes the check if there are any internal triggers and every internal trigger passes the
    check.

    Construct using the `&` operator on other triggers like `a & b`.
    """

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        return bool(len(self._triggers)) and await a.all(
            await trigger.check(message, channel) for trigger in self._triggers
        )


class OrTrigger(LogicTrigger):
    """
    Command trigger that passes the check if there are any internal triggers and at least one internal trigger passes
    the check.

    Construct using the `|` operator on other triggers like `a | b`.
    """

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        return bool(len(self._triggers)) and await a.any(
            await trigger.check(message, channel) for trigger in self._triggers
        )


class FirstWordTrigger(CommandTrigger):
    """
    Command trigger that passes the check if the first word of the message matches the given value.

    Can be made case-sensitive or not. Case-insensitive by default.
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
        return hash(type(self))

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        return message.is_sender_moderator or await channel.is_user_moderator(message.tags.user_id)


class SenderIsSubscribedTrigger(CommandTrigger):
    """
    Command trigger that passes the check if the sender is subscribed.
    """

    def __hash__(self) -> int:
        return hash(type(self))

    async def check(self, message: PrivMsg, channel: Channel) -> bool:
        return message.is_sender_subscribed or await channel.is_user_subscribed(message.tags.user_id)
