# -*- coding: utf-8 -*-
import inspect
import sys
import time
from typing import List

import pytest

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
from green_eggs.commands.triggers import InvertedTrigger
from green_eggs.exceptions import CooldownNotElapsed, GlobalCooldownNotElapsed, UserCooldownNotElapsed
from green_eggs.types import RegisterAbleFunc
from tests import response_context
from tests.fixtures import *  # noqa
from tests.utils.data_types import priv_msg

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


async def test_inverted_trigger_created_from_tilde():
    trigger = ~FirstWordTrigger('a')
    assert isinstance(trigger, InvertedTrigger)
    assert trigger.inner == FirstWordTrigger('a')


async def test_inverted_trigger_negates_outcome(channel: Channel):
    trigger = FirstWordTrigger('first')
    inverted = ~trigger
    message_first = priv_msg(handle_able_kwargs=dict(message='first word', where='channel_user'))
    assert await trigger.check(message_first, channel)
    assert not await inverted.check(message_first, channel)
    message_second = priv_msg(handle_able_kwargs=dict(message='second word', where='channel_user'))
    assert not await trigger.check(message_second, channel)
    assert await inverted.check(message_second, channel)


async def test_inverted_twice_returns_original():
    trigger = SenderIsModTrigger()
    inverted = ~trigger
    twice = ~inverted
    assert twice is trigger


async def test_inverted_hash_depends_on_inner():
    trigger_one = FirstWordTrigger('hello')
    trigger_two = SenderIsModTrigger()
    assert hash(~trigger_one) != hash(~trigger_two)


# REGISTRY


async def test_runner_sync_function(api_common: TwitchApiCommon, channel: Channel):
    def sync_func():
        return 'hello'

    runner = CommandRunner(sync_func, global_cooldown=None, user_cooldown=None)
    result = await runner.run(api=api_common, channel=channel, message=priv_msg())
    assert result == 'hello'


async def test_runner_async_function(api_common: TwitchApiCommon, channel: Channel):
    async def async_func():
        return 'world'

    runner = CommandRunner(async_func, global_cooldown=None, user_cooldown=None)
    result = await runner.run(api=api_common, channel=channel, message=priv_msg())
    assert result == 'world'


async def test_runner_validates_signature():
    def invalid_function(never):
        return str(never)

    name = 'test_runner_validates_signature.<locals>.invalid_function'
    with pytest.raises(TypeError, match=f'Unexpected required keyword parameter in <{name}>: \'never\''):
        CommandRunner(invalid_function, global_cooldown=None, user_cooldown=None)


async def test_runner_last_runs_not_set_without_cooldown(api_common: TwitchApiCommon, channel: Channel):
    runner = CommandRunner(lambda: None, global_cooldown=None, user_cooldown=None)
    await runner.run(api=api_common, channel=channel, message=priv_msg(tags_kwargs=dict(user_id='123')))
    assert runner._last_run is None
    assert runner._last_run_for_user == dict()


async def test_runner_global_cooldown_allows_when_elapsed(api_common: TwitchApiCommon, channel: Channel):
    runner = CommandRunner(lambda: None, global_cooldown=1, user_cooldown=None)
    runner._last_run = time.monotonic() - 2
    await runner.run(api=api_common, channel=channel, message=priv_msg(tags_kwargs=dict(user_id='123')))
    assert time.monotonic() - runner._last_run < 0.1
    assert runner._last_run_for_user == dict()


async def test_runner_global_cooldown_raises_exception_when_not_elapsed(api_common: TwitchApiCommon, channel: Channel):
    runner = CommandRunner(lambda: None, global_cooldown=4, user_cooldown=None)
    global_last_run = time.monotonic() - 3
    user_last_run = time.monotonic() - 4
    runner._last_run = global_last_run
    runner._last_run_for_user['456'] = user_last_run
    with pytest.raises(CooldownNotElapsed) as exc_info:
        await runner.run(api=api_common, channel=channel, message=priv_msg(tags_kwargs=dict(user_id='456')))
    assert exc_info.type is GlobalCooldownNotElapsed
    assert 0.9 < exc_info.value.remaining < 1.1
    assert runner._last_run == global_last_run
    assert runner._last_run_for_user['456'] == user_last_run


async def test_runner_user_cooldown_allows_when_elapsed(api_common: TwitchApiCommon, channel: Channel):
    runner = CommandRunner(lambda: None, global_cooldown=None, user_cooldown=1)
    runner._last_run_for_user['123'] = time.monotonic() - 2
    await runner.run(api=api_common, channel=channel, message=priv_msg(tags_kwargs=dict(user_id='123')))
    assert time.monotonic() - runner._last_run_for_user['123'] < 0.1
    assert runner._last_run is None


async def test_runner_user_cooldown_raises_exception_when_not_elapsed(api_common: TwitchApiCommon, channel: Channel):
    runner = CommandRunner(lambda: None, global_cooldown=None, user_cooldown=2)
    user_last_run = time.monotonic() - 1
    global_last_run = time.monotonic() - 2
    runner._last_run = global_last_run
    runner._last_run_for_user['123'] = user_last_run
    with pytest.raises(CooldownNotElapsed) as exc_info:
        await runner.run(api=api_common, channel=channel, message=priv_msg(tags_kwargs=dict(user_id='123')))
    assert exc_info.type is UserCooldownNotElapsed
    assert 0.9 < exc_info.value.remaining < 1.1
    assert runner._last_run_for_user['123'] == user_last_run
    assert runner._last_run == global_last_run


async def test_runner_populates_both_times_with_both_cooldowns(api_common: TwitchApiCommon, channel: Channel):
    runner = CommandRunner(lambda: None, global_cooldown=1, user_cooldown=1)
    runner._last_run_for_user['123'] = time.monotonic() - 2
    await runner.run(api=api_common, channel=channel, message=priv_msg(tags_kwargs=dict(user_id='123')))
    post_run = time.monotonic()
    assert post_run - runner._last_run_for_user['123'] < 0.1
    assert runner._last_run is not None
    assert post_run - runner._last_run < 0.1


async def test_runner_user_cooldown_beats_global_cooldown(api_common: TwitchApiCommon, channel: Channel):
    runner = CommandRunner(lambda: None, global_cooldown=2, user_cooldown=4)
    last_run = time.monotonic() - 1
    runner._last_run = last_run
    runner._last_run_for_user['123'] = last_run
    with pytest.raises(CooldownNotElapsed) as exc_info:
        await runner.run(api=api_common, channel=channel, message=priv_msg(tags_kwargs=dict(user_id='123')))
    assert exc_info.type is UserCooldownNotElapsed
    assert 2.9 < exc_info.value.remaining < 3.1
    assert runner._last_run_for_user['123'] == last_run
    assert runner._last_run == last_run


def test_registry():
    async def _command_one():
        return ''

    async def _command_two():
        return ''

    registry = CommandRegistry()
    registry[AndTrigger()] = CommandRunner(_command_one, global_cooldown=None, user_cooldown=None)
    registry[AndTrigger()] = CommandRunner(_command_two, global_cooldown=None, user_cooldown=None)
    assert len(registry) == 1
    assert list(registry) == [AndTrigger()]
    assert registry[AndTrigger()]._command_func is _command_two
    del registry[AndTrigger()]
    with pytest.raises(KeyError):
        _ = registry[AndTrigger()]


async def test_registry_all(channel: Channel):
    async def _command_one():
        return ''

    async def _command_two():
        return ''

    async def _command_three():
        return ''

    registry = CommandRegistry()
    registry[FirstWordTrigger('one')] = CommandRunner(_command_one, global_cooldown=None, user_cooldown=None)
    registry[FirstWordTrigger('two')] = CommandRunner(_command_two, global_cooldown=None, user_cooldown=None)
    registry[SenderIsModTrigger()] = CommandRunner(_command_three, global_cooldown=None, user_cooldown=None)
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
    wrapper = registry.decorator(FirstWordTrigger('one'), global_cooldown=None, user_cooldown=None)
    result = wrapper(_command)
    assert result is _command
    assert registry[FirstWordTrigger('one')]._command_func is result


def test_registry_decorator_with_sync():
    def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('three'), global_cooldown=None, user_cooldown=None)
    result = wrapper(_command)
    assert result is _command
    registered = registry[FirstWordTrigger('three')]
    assert registered._command_func is result
    assert not inspect.iscoroutinefunction(registered._command_func)


def test_registry_decorator_with_async():
    async def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('three'), global_cooldown=None, user_cooldown=None)
    result = wrapper(_command)
    assert result is _command
    registered = registry[FirstWordTrigger('three')]
    assert registered._command_func is result
    assert inspect.iscoroutinefunction(registered._command_func)


def test_registry_rejects_func():
    def _command(extra):
        return str(extra)

    registry = CommandRegistry()
    wrapper = registry.decorator(AndTrigger(), global_cooldown=None, user_cooldown=None)
    name = 'test_registry_rejects_func.<locals>._command'
    with pytest.raises(TypeError, match=f'Unexpected required keyword parameter in <{name}>: \'extra\''):
        wrapper(_command)


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
        wrapper = registry.decorator(AndTrigger(), global_cooldown=None, user_cooldown=None)
        with pytest.raises(
            TypeError, match='Positional-only parameters without defaults are not allowed in <_command>'
        ):
            wrapper(_command)


async def test_registry_decorator_with_factory(api_common: TwitchApiCommon, channel: Channel):
    def factory(callback: RegisterAbleFunc, callback_accepts: List[str]) -> RegisterAbleFunc:
        assert callback_accepts == ['one']

        def inner(message):
            return callback(one=message.tags.user_id)

        return inner

    def _command(one, two='2'):
        return str(one) + two

    registry = CommandRegistry()
    wrapper = registry.decorator(
        AndTrigger(),
        global_cooldown=None,
        user_cooldown=None,
        target_keywords=['one', 'three'],
        command_factory=factory,
    )
    result = wrapper(_command)
    assert result is _command
    runner = registry[AndTrigger()]
    assert 'message' in runner._func_keywords
    assert 'api' not in runner._func_keywords
    message_ = priv_msg(tags_kwargs=dict(user_id='1'))
    run_result = await registry[AndTrigger()].run(api=api_common, channel=channel, message=message_)
    assert run_result == '12'


async def test_registry_decorator_async_with_factory(api_common: TwitchApiCommon, channel: Channel):
    def factory(callback: RegisterAbleFunc, callback_accepts: List[str]) -> RegisterAbleFunc:
        assert callback_accepts == ['one']

        def inner(message):
            return callback(one=message.message)

        return inner

    async def _command(one, two='2'):
        return str(one) + two

    registry = CommandRegistry()
    wrapper = registry.decorator(
        AndTrigger(), global_cooldown=None, user_cooldown=None, target_keywords=['one', 'five'], command_factory=factory
    )
    result = wrapper(_command)
    assert result is _command
    runner = registry[AndTrigger()]
    assert 'api' not in runner._func_keywords
    assert 'message' in runner._func_keywords
    message_ = priv_msg(handle_able_kwargs=dict(message='1'))
    run_result = await registry[AndTrigger()].run(api=api_common, channel=channel, message=message_)
    assert run_result == '12'


async def test_registry_find(channel: Channel):
    def _one():
        return ''

    def _two():
        return ''

    def _three():
        return ''

    registry = CommandRegistry()
    registry[FirstWordTrigger('three')] = CommandRunner(_one, global_cooldown=None, user_cooldown=None)
    registry[FirstWordTrigger('four')] = CommandRunner(_two, global_cooldown=None, user_cooldown=None)
    registry[SenderIsModTrigger()] = CommandRunner(_three, global_cooldown=None, user_cooldown=None)
    command = await registry.find(
        priv_msg(handle_able_kwargs=dict(message='three'), tags_kwargs=dict(mod=True)), channel
    )
    assert command is not None
    assert command._command_func is _one


async def test_registry_find_empty(channel: Channel):
    registry = CommandRegistry()
    commands = await registry.find(priv_msg(), channel)
    assert commands is None
