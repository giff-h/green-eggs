# -*- coding: utf-8 -*-
import inspect
import sys
from typing import List

import pytest

from green_eggs.commands import (
    AndTrigger,
    CommandRegistry,
    CommandRunner,
    FirstWordTrigger,
    OrTrigger,
    SenderIsModTrigger,
)
from green_eggs.types import RegisterAbleFunc
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


def test_first_word_trigger():
    trigger = FirstWordTrigger('one')
    message = priv_msg(handle_able_kwargs=dict(message='one two'))
    assert trigger.check(message)


def test_first_word_case_sensitive():
    trigger = FirstWordTrigger('One', case_sensitive=True)
    message = priv_msg(handle_able_kwargs=dict(message='one two'))
    assert not trigger.check(message)


def test_first_word_case_insensitive():
    trigger = FirstWordTrigger('One', case_sensitive=False)
    message = priv_msg(handle_able_kwargs=dict(message='one two'))
    assert trigger.check(message)


def test_mod_trigger():
    trigger = SenderIsModTrigger()
    message = priv_msg(tags_kwargs=dict(mod=True))
    assert trigger.check(message)


def test_mod_trigger_broadcaster():
    trigger = SenderIsModTrigger()
    message = priv_msg(tags_kwargs=dict(badges=dict(broadcaster=1)))
    assert trigger.check(message)


def test_mod_trigger_normal():
    trigger = SenderIsModTrigger()
    message = priv_msg()
    assert not trigger.check(message)


def test_and_trigger_empty():
    trigger = AndTrigger()
    assert not trigger.check(priv_msg())


def test_and_trigger_single():
    internal = FirstWordTrigger('')
    external = AndTrigger(internal)
    assert external.triggers == [internal]


def test_and_trigger_single_with_empty():
    internal = FirstWordTrigger('')
    empty = AndTrigger()
    external = internal & empty
    assert external.triggers == [internal]


def test_and_trigger_unique():
    internal = FirstWordTrigger('')
    external = internal & internal
    assert external.triggers == [internal]


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
    assert external.triggers == sorted((not_and, one, two, three_or_four), key=hash)


def test_or_trigger_empty():
    trigger = OrTrigger()
    assert not trigger.check(priv_msg())


def test_or_trigger_single():
    internal = FirstWordTrigger('')
    external = OrTrigger(internal)
    assert external.triggers == [internal]


def test_or_trigger_single_with_empty():
    internal = FirstWordTrigger('')
    empty = OrTrigger()
    external = internal | empty
    assert external.triggers == [internal]


def test_or_trigger_unique():
    internal = FirstWordTrigger('')
    external = internal | internal
    assert external.triggers == [internal]


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
    assert external.triggers == sorted((not_or, one, two, three_and_four), key=hash)


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
    assert registry[AndTrigger()].command_func is _command_two
    del registry[AndTrigger()]
    try:
        c = registry[AndTrigger()]
    except KeyError:
        pass  # success
    else:
        assert False, c


def test_registry_all():
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
    commands = registry.all(priv_msg(handle_able_kwargs=dict(message='one'), tags_kwargs=dict(mod=True)))
    assert [r.command_func for r in commands] == [_command_one, _command_three]


def test_registry_all_empty():
    registry = CommandRegistry()
    commands = registry.all(priv_msg())
    assert commands == []


def test_registry_decorator():
    async def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('one'))
    result = wrapper(_command)
    assert result is _command
    assert registry[FirstWordTrigger('one')].command_func is result


def test_registry_decorator_with_sync():
    def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('three'))
    result = wrapper(_command)
    assert result is _command
    registered = registry[FirstWordTrigger('three')]
    assert registered.command_func is result
    assert not inspect.iscoroutinefunction(registered.command_func)


def test_registry_decorator_with_async():
    async def _command():
        return ''

    registry = CommandRegistry()
    wrapper = registry.decorator(FirstWordTrigger('three'))
    result = wrapper(_command)
    assert result is _command
    registered = registry[FirstWordTrigger('three')]
    assert registered.command_func is result
    assert inspect.iscoroutinefunction(registered.command_func)


def test_registry_rejects_func():
    def _command(extra):
        return str(extra)

    registry = CommandRegistry()
    wrapper = registry.decorator(AndTrigger())
    try:
        result = wrapper(_command)
    except TypeError as e:
        assert 'Unexpected required keyword parameter' in e.args[0]
    else:
        assert False, result


if sys.version_info[:2] >= (3, 8):

    def test_registry_rejects_pos_only_args():
        # This is necessary to bypass the syntax error
        func = '''def _command(a, /):
    return str(a)'''
        globals_ = dict(str=str)
        locals_ = dict()
        exec(func, globals_, locals_)
        _command = locals_['_command']

        registry = CommandRegistry()
        wrapper = registry.decorator(AndTrigger())
        try:
            result = wrapper(_command)
        except TypeError as e:
            assert 'Command callbacks may not have any non-default positional-only parameters' in e.args[0]
        else:
            assert False, result


@pytest.mark.asyncio
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
    assert runner.accepts('message')
    assert not runner.accepts('api')
    run_result = await registry[AndTrigger()].run(message='1')
    assert run_result == '12'


@pytest.mark.asyncio
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
    assert runner.accepts('api')
    assert not runner.accepts('message')
    run_result = await registry[AndTrigger()].run(api='1')
    assert run_result == '12'


def test_registry_find():
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
    command = registry.find(priv_msg(handle_able_kwargs=dict(message='one'), tags_kwargs=dict(mod=True)))
    assert command.command_func is _one


def test_registry_find_empty():
    registry = CommandRegistry()
    commands = registry.find(priv_msg())
    assert commands is None
