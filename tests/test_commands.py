# -*- coding: utf-8 -*-
import asyncio
import inspect
import sys
from typing import List

from green_eggs.api import TwitchApiCommon
from green_eggs.channel import Channel
from green_eggs.commands import (
    AndTrigger,
    CommandRegistry,
    CommandRunner,
    FirstWordTrigger,
    OrTrigger,
    SenderIsModTrigger,
    SenderIsSubscribedTrigger,
)
from green_eggs.commands.triggers import async_all, async_any
from green_eggs.types import RegisterAbleFunc
from tests import response_context
from tests.fixtures import *  # noqa
from tests.utils.data_types import priv_msg

# ANY AND ALL


async def test_async_all_empty():
    assert await async_all(await nothing for nothing in [])  # type: ignore[arg-type]


async def test_async_all_one_false():
    true_future = asyncio.Future()
    true_future.set_result(True)
    false_future = asyncio.Future()
    false_future.set_result(False)
    assert not await async_all(await future for future in [true_future, false_future])  # type: ignore[arg-type]


async def test_async_all_none_false():
    future_one = asyncio.Future()
    future_one.set_result(True)
    future_two = asyncio.Future()
    future_two.set_result(True)
    assert await async_all(await future for future in [future_one, future_two])  # type: ignore[arg-type]


async def test_async_any_empty():
    assert not await async_any(await nothing for nothing in [])  # type: ignore[arg-type]


async def test_async_any_one_false():
    true_future = asyncio.Future()
    true_future.set_result(True)
    false_future = asyncio.Future()
    false_future.set_result(False)
    assert await async_any(await future for future in [true_future, false_future])  # type: ignore[arg-type]


async def test_async_any_none_false():
    future_one = asyncio.Future()
    future_one.set_result(True)
    future_two = asyncio.Future()
    future_two.set_result(True)
    assert await async_any(await future for future in [future_one, future_two])  # type: ignore[arg-type]


# TRIGGERS


def test_trigger_equality():
    assert AndTrigger() == AndTrigger()
    assert OrTrigger() == OrTrigger()
    assert FirstWordTrigger('one', True) == FirstWordTrigger('one', True)
    assert FirstWordTrigger('one', False) == FirstWordTrigger('one', False)
    assert SenderIsModTrigger() == SenderIsModTrigger()
    assert FirstWordTrigger('one') & SenderIsModTrigger() == SenderIsModTrigger() & FirstWordTrigger('one')
    assert FirstWordTrigger('one') | SenderIsModTrigger() == SenderIsModTrigger() | FirstWordTrigger('one')


def test_trigger_inequality():
    assert AndTrigger() != OrTrigger()
    assert FirstWordTrigger('one') != FirstWordTrigger('two')
    assert FirstWordTrigger('one', True) != FirstWordTrigger('one', False)
    assert FirstWordTrigger('one') != SenderIsModTrigger()
    assert FirstWordTrigger('one') & SenderIsModTrigger() != FirstWordTrigger('two') & SenderIsModTrigger()
    assert FirstWordTrigger('one') | SenderIsModTrigger() != FirstWordTrigger('two') | SenderIsModTrigger()


async def test_first_word_trigger(channel: Channel):
    trigger = FirstWordTrigger('one')
    message = priv_msg(handle_able_kwargs=dict(message='one two'))
    assert await trigger.check(message, channel)


async def test_first_word_trigger_case_sensitive(channel: Channel):
    trigger = FirstWordTrigger('One', case_sensitive=True)
    message = priv_msg(handle_able_kwargs=dict(message='one two'))
    assert not await trigger.check(message, channel)


async def test_first_word_trigger_case_insensitive(channel: Channel):
    trigger = FirstWordTrigger('One', case_sensitive=False)
    message = priv_msg(handle_able_kwargs=dict(message='one two'))
    assert await trigger.check(message, channel)


async def test_mod_trigger(channel: Channel):
    trigger = SenderIsModTrigger()
    message = priv_msg(tags_kwargs=dict(mod=True))
    assert await trigger.check(message, channel)


async def test_mod_trigger_hash():
    assert hash(SenderIsModTrigger()) == hash(SenderIsModTrigger())


async def test_mod_trigger_broadcaster(channel: Channel):
    trigger = SenderIsModTrigger()
    message = priv_msg(tags_kwargs=dict(badges_kwargs=dict(broadcaster=1)))
    assert await trigger.check(message, channel)


async def test_mod_trigger_normal(api_common: TwitchApiCommon, channel: Channel):
    api_common.direct._session.request.return_value = response_context(  # type: ignore[attr-defined]
        return_json=dict(data=[])
    )
    trigger = SenderIsModTrigger()
    message = priv_msg()
    assert not await trigger.check(message, channel)
    api_common.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/moderators?broadcaster_id=&first=100', json=None
    )


async def test_sub_trigger(channel: Channel):
    trigger = SenderIsSubscribedTrigger()
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(badges_kwargs=dict(subscriber='1'))
    )
    channel.handle_message(message)
    assert await trigger.check(message, channel)


async def test_sub_trigger_hash():
    assert hash(SenderIsSubscribedTrigger()) == hash(SenderIsSubscribedTrigger())


async def test_and_trigger_empty(channel: Channel):
    trigger = AndTrigger()
    assert not await trigger.check(priv_msg(), channel)


def test_and_trigger_single():
    internal = FirstWordTrigger('')
    external = AndTrigger(internal)
    assert external._triggers == [internal]


def test_and_trigger_single_with_empty():
    internal = FirstWordTrigger('')
    empty = AndTrigger()
    external = internal & empty
    assert external._triggers == [internal]


def test_and_trigger_unique():
    internal = FirstWordTrigger('')
    external = internal & internal
    assert external._triggers == [internal]


def test_and_trigger_nested():
    not_and = SenderIsModTrigger()
    empty = AndTrigger()
    one = FirstWordTrigger('one')
    two = FirstWordTrigger('two')
    one_and_two = one & two
    three = FirstWordTrigger('three')
    four = FirstWordTrigger('four')
    three_or_four = three | four
    empty_or = OrTrigger()
    external = not_and & empty & one_and_two & empty_or & three_or_four
    assert external._triggers == sorted((not_and, one, two, three_or_four), key=hash)


async def test_and_trigger_check(channel: Channel):
    trigger = FirstWordTrigger('a') & SenderIsModTrigger()
    message = priv_msg(handle_able_kwargs=dict(message='a'), tags_kwargs=dict(mod=True))
    assert await trigger.check(message, channel)


async def test_or_trigger_empty(channel: Channel):
    trigger = OrTrigger()
    assert not await trigger.check(priv_msg(), channel)


def test_or_trigger_single():
    internal = FirstWordTrigger('')
    external = OrTrigger(internal)
    assert external._triggers == [internal]


def test_or_trigger_single_with_empty():
    internal = FirstWordTrigger('')
    empty = OrTrigger()
    external = internal | empty
    assert external._triggers == [internal]


def test_or_trigger_unique():
    internal = FirstWordTrigger('')
    external = internal | internal
    assert external._triggers == [internal]


def test_or_trigger_nested():
    not_or = SenderIsModTrigger()
    empty = OrTrigger()
    one = FirstWordTrigger('one')
    two = FirstWordTrigger('two')
    one_or_two = one | two
    three = FirstWordTrigger('three')
    four = FirstWordTrigger('four')
    three_and_four = three & four
    empty_and = AndTrigger()
    external = not_or | empty | one_or_two | empty_and | three_and_four
    assert external._triggers == sorted((not_or, one, two, three_and_four), key=hash)


async def test_or_trigger_check(channel: Channel):
    a_not_mod = priv_msg(
        handle_able_kwargs=dict(message='a', where='channel_user'), tags_kwargs=dict(user_id='not-a-mod')
    )
    b_is_mod = priv_msg(
        handle_able_kwargs=dict(message='b', where='channel_user'),
        tags_kwargs=dict(badges_kwargs=dict(moderator='1'), mod=True, user_id='mod-id'),
    )
    channel.handle_message(a_not_mod)
    channel.handle_message(b_is_mod)
    trigger = FirstWordTrigger('a') | SenderIsModTrigger()
    assert await trigger.check(a_not_mod, channel)
    assert await trigger.check(b_is_mod, channel)


# REGISTRY


def test_registry():
    async def _command_one():
        return ''

    async def _command_two():
        return ''

    registry = CommandRegistry()
    registry[AndTrigger()] = CommandRunner(_command_one)
    registry[AndTrigger()] = CommandRunner(_command_two)
    assert len(registry) == 1
    assert list(registry) == [AndTrigger()]
    assert registry[AndTrigger()]._command_func is _command_two
    del registry[AndTrigger()]
    try:
        c = registry[AndTrigger()]
    except KeyError:
        pass  # success
    else:
        assert False, c


async def test_registry_all(channel: Channel):
    async def _command_one():
        return ''

    async def _command_two():
        return ''

    async def _command_three():
        return ''

    registry = CommandRegistry()
    registry[FirstWordTrigger('one')] = CommandRunner(_command_one)
    registry[FirstWordTrigger('two')] = CommandRunner(_command_two)
    registry[SenderIsModTrigger()] = CommandRunner(_command_three)
    commands = await registry.all(priv_msg(handle_able_kwargs=dict(message='one'), tags_kwargs=dict(mod=True)), channel)
    assert [r._command_func for r in commands] == [_command_one, _command_three]


async def test_registry_all_empty(channel: Channel):
    registry = CommandRegistry()
    commands = await registry.all(priv_msg(), channel)
    assert commands == []


def test_registry_decorator():
    async def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('one'))
    result = wrapper(_command)
    assert result is _command
    assert registry[FirstWordTrigger('one')]._command_func is result


def test_registry_decorator_with_sync():
    def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('three'))
    result = wrapper(_command)
    assert result is _command
    registered = registry[FirstWordTrigger('three')]
    assert registered._command_func is result
    assert not inspect.iscoroutinefunction(registered._command_func)


def test_registry_decorator_with_async():
    async def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('three'))
    result = wrapper(_command)
    assert result is _command
    registered = registry[FirstWordTrigger('three')]
    assert registered._command_func is result
    assert inspect.iscoroutinefunction(registered._command_func)


def test_registry_rejects_func():
    def _command(extra):
        return str(extra)

    registry = CommandRegistry()
    wrapper = registry.decorator(AndTrigger())
    try:
        result = wrapper(_command)
    except TypeError as e:
        name = 'test_registry_rejects_func.<locals>._command'
        assert e.args[0] == f'Unexpected required keyword parameter in <{name}>: \'extra\''
    else:
        assert False, result


# This test asserts a condition that only happens on python 3.8 and later
if sys.version_info[:2] >= (3, 8):

    def test_registry_rejects_pos_only_args():
        # This is necessary to bypass the syntax error
        func = '''
def _command(a, /):
    return str(a)'''.strip()
        globals_ = dict(str=str)
        locals_ = dict()
        exec(func, globals_, locals_)
        _command = locals_['_command']

        registry = CommandRegistry()
        wrapper = registry.decorator(AndTrigger())
        try:
            result = wrapper(_command)
        except TypeError as e:
            assert e.args[0] == 'Positional-only parameters without defaults are not allowed in <_command>'
        else:
            assert False, result


async def test_registry_decorator_with_factory():
    def factory(callback: RegisterAbleFunc, callback_accepts: List[str]) -> RegisterAbleFunc:
        assert callback_accepts == ['one']

        def inner(message):
            return callback(one=message)

        return inner

    def _command(one, two='2'):
        return str(one) + two

    registry = CommandRegistry()
    wrapper = registry.decorator(AndTrigger(), target_keywords=['one', 'three'], command_factory=factory)
    result = wrapper(_command)
    assert result is _command
    runner = registry[AndTrigger()]
    assert 'message' in runner._func_keywords
    assert 'api' not in runner._func_keywords
    run_result = await registry[AndTrigger()].run(api=None, channel=None, message='1')  # type: ignore
    assert run_result == '12'


async def test_registry_decorator_async_with_factory():
    def factory(callback: RegisterAbleFunc, callback_accepts: List[str]) -> RegisterAbleFunc:
        assert callback_accepts == ['one']

        def inner(api):
            return callback(one=api)

        return inner

    async def _command(one, two='2'):
        return str(one) + two

    registry = CommandRegistry()
    wrapper = registry.decorator(AndTrigger(), target_keywords=['one', 'five'], command_factory=factory)
    result = wrapper(_command)
    assert result is _command
    runner = registry[AndTrigger()]
    assert 'api' in runner._func_keywords
    assert 'message' not in runner._func_keywords
    run_result = await registry[AndTrigger()].run(api='1', channel=None, message=None)  # type: ignore
    assert run_result == '12'


async def test_registry_find(channel: Channel):
    def _one():
        return ''

    def _two():
        return ''

    def _three():
        return ''

    registry = CommandRegistry()
    registry[FirstWordTrigger('one')] = CommandRunner(_one)
    registry[FirstWordTrigger('two')] = CommandRunner(_two)
    registry[SenderIsModTrigger()] = CommandRunner(_three)
    command = await registry.find(priv_msg(handle_able_kwargs=dict(message='one'), tags_kwargs=dict(mod=True)), channel)
    assert command is not None
    assert command._command_func is _one


async def test_registry_find_empty(channel: Channel):
    registry = CommandRegistry()
    commands = await registry.find(priv_msg(), channel)
    assert commands is None
