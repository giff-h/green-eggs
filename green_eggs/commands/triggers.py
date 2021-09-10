# -*- coding: utf-8 -*-
import abc
from collections.abc import Hashable
import itertools
from typing import Iterable, Iterator, List

from green_eggs.data_types import PrivMsg


class CommandTrigger(Hashable, abc.ABC):
    def __and__(self, other: 'CommandTrigger') -> 'AndTrigger':
        return AndTrigger(self, other)

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and hash(self) == hash(other)

    def __or__(self, other: 'CommandTrigger') -> 'OrTrigger':
        return OrTrigger(self, other)

    @abc.abstractmethod
    def check(self, message: PrivMsg) -> bool:
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

    def check(self, message: PrivMsg) -> bool:
        return bool(len(self._triggers)) and all(trigger.check(message) for trigger in self._triggers)


class OrTrigger(LogicTrigger):
    """
    Command trigger that passes the check if there are any internal triggers and at least one internal trigger passes
    the check.

    Construct using the `|` operator on other triggers like `a | b`.
    """

    def check(self, message: PrivMsg) -> bool:
        return bool(len(self._triggers)) and any(trigger.check(message) for trigger in self._triggers)


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

    def check(self, message: PrivMsg) -> bool:
        word = message.words[0] if self._case_sensitive else message.words[0].lower()
        value = self._value if self._case_sensitive else self._value.lower()
        return word == value


class SenderIsModTrigger(CommandTrigger):
    """
    Command trigger that passes the check if the sender is a moderator or the broadcaster.
    """

    def __hash__(self) -> int:
        return hash((type(self),))

    def check(self, message: PrivMsg) -> bool:
        return message.tags.mod or 'broadcaster' in message.tags.badges
