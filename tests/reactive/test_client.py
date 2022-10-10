# -*- coding: utf-8 -*-
import asyncio
import datetime
import re

import pytest
from pytest_mock import MockerFixture
from reactivex import operators as ops
from reactivex.internal import DisposedException

from green_eggs import data_types as dt
from green_eggs.reactive.client import TwitchWebsocketClient, ensure_str, format_oauth, pattern_match_mapper
from tests.reactive import get_mock_socket_from_client, mock_socket, test_logger
from tests.reactive.fixtures import *  # noqa
from tests.utils.data_types import join_part


def test_ensure_str():
    assert isinstance(ensure_str(''), str)
    assert isinstance(ensure_str(b''), str)


def test_format_oauth():
    assert format_oauth('abcd') == 'oauth:abcd'
    assert format_oauth('oauth:1234') == 'oauth:1234'


def test_pattern_match_mapper():
    mapper = pattern_match_mapper(re.compile(r'.*'))
    result = mapper(dt.StampedData(data='hello world', stamp=datetime.datetime.utcnow()))
    assert isinstance(result, re.Match)
    assert result.group() == 'hello world'


def test_pattern_match_mapper_no_match():
    mapper = pattern_match_mapper(re.compile(r'never'))
    result = mapper(dt.StampedData(data='can\'t catch me', stamp=datetime.datetime.utcnow()))
    assert result is None


async def test_client_context_disposed_subject_handled(mocker: MockerFixture):
    mocker.patch('websockets.connect', side_effect=mock_socket)
    with TwitchWebsocketClient(
        channel='channel_user', username='test_username', token='test_token', logger=test_logger
    ) as chat:
        subject = chat._internal_subject
        subject.dispose()
        with pytest.raises(DisposedException):
            subject.on_completed()
    assert chat._internal_subject is not subject


async def test_client_observable_works(chat: TwitchWebsocketClient):
    observable = await chat.incoming_data
    # suppress mypy [arg-type] on this line because Observable.__await__ has mismatched typing
    result: dt.HandleAble = await asyncio.wait_for(observable.pipe(ops.first()), timeout=0.1)
    assert result == join_part(
        is_join=True,
        raw=':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel_user',
        where='channel_user',
        who='test_username',
    )


async def test_client_observable_websocket_error_handling(chat: TwitchWebsocketClient):
    exc = Exception('Test error')
    future: asyncio.Future[Exception] = asyncio.Future()
    observable = await chat.incoming_data
    observable.subscribe(on_error=lambda e: future.set_result(e))
    mock = await get_mock_socket_from_client(chat)
    mock.recv_buffer.put_nowait(exc)
    result: Exception = await asyncio.wait_for(future, timeout=0.1)
    assert result is exc


async def test_client_observable_unmatched_data(chat: TwitchWebsocketClient, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.warning')
    incoming: 'asyncio.Queue[dt.HandleAble]' = asyncio.Queue()
    observable = await chat.incoming_data
    observable.subscribe(on_next=incoming.put_nowait)
    mock = await get_mock_socket_from_client(chat)
    result = await asyncio.wait_for(incoming.get(), timeout=0.1)
    assert result == join_part(
        is_join=True,
        raw=':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel_user',
        where='channel_user',
        who='test_username',
    )
    mock.recv_buffer.put_nowait('not matched')
    # The observable should continue
    mock.recv_buffer.put_nowait(':other_user!other_user@other_user.tmi.twitch.tv PART #channel_user')
    result = await asyncio.wait_for(incoming.get(), timeout=0.1)
    assert result == join_part(
        is_join=False,
        raw=':other_user!other_user@other_user.tmi.twitch.tv PART #channel_user',
        where='channel_user',
        who='other_user',
    )
    assert incoming.empty()
    chat._logger.warning.assert_called_once_with(  # type: ignore[attr-defined]
        'Incoming message could not be matched: \'not matched\''
    )


async def test_client_observable_handle_error(chat: TwitchWebsocketClient, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.exception')
    incoming: 'asyncio.Queue[dt.HandleAble]' = asyncio.Queue()
    observable = await chat.incoming_data
    observable.subscribe(on_next=incoming.put_nowait)
    mock = await get_mock_socket_from_client(chat)
    result = await asyncio.wait_for(incoming.get(), timeout=0.1)
    assert result == join_part(
        is_join=True,
        raw=':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel_user',
        where='channel_user',
        who='test_username',
    )
    bad_tags = '@key=value; :user!user@user.tmi.twitch.tv PRIVMSG #channel_user :hello'
    mock.recv_buffer.put_nowait(bad_tags)
    # The observable should continue
    mock.recv_buffer.put_nowait(':other_user!other_user@other_user.tmi.twitch.tv PART #channel_user')
    result = await asyncio.wait_for(incoming.get(), timeout=0.1)
    assert result == join_part(
        is_join=False,
        raw=':other_user!other_user@other_user.tmi.twitch.tv PART #channel_user',
        where='channel_user',
        who='other_user',
    )
    assert incoming.empty()
    chat._logger.exception.assert_called_once()  # type: ignore[attr-defined]
    call_args, call_kwargs = chat._logger.exception.call_args  # type: ignore[attr-defined]
    assert call_args == (f'Error parsing data into handleable: {bad_tags!r}',)
    # cannot use assert_called_once_with because exceptions do not have equality checks outside of object id
    assert set(call_kwargs.keys()) == {'exc_info'}
    error = call_kwargs['exc_info']
    assert isinstance(error, KeyError)
    assert error.args == ('tmi_sent_ts',)


async def test_client_ping_pong(chat: TwitchWebsocketClient):
    observable = await chat.incoming_data
    mock = await get_mock_socket_from_client(chat)
    mock.recv_buffer.put_nowait('PING hello')
    # suppress mypy [arg-type] on this line because Observable.__await__ has mismatched typing
    result: dt.HandleAble = await asyncio.wait_for(observable.pipe(ops.first()), timeout=0.1)
    assert result == join_part(
        is_join=True,
        raw=':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel_user',
        where='channel_user',
        who='test_username',
    )
    assert mock.send_buffer.get_nowait() == 'PONG hello'


async def test_client_reconnect_maintains_observable_connection(chat: TwitchWebsocketClient):
    incoming: 'asyncio.Queue[dt.HandleAble]' = asyncio.Queue()
    observable = await chat.incoming_data
    observable.subscribe(on_next=incoming.put_nowait)
    result = await asyncio.wait_for(incoming.get(), timeout=0.1)
    assert result == join_part(
        is_join=True,
        raw=':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel_user',
        where='channel_user',
        who='test_username',
    )
    assert incoming.empty()
    mock = await get_mock_socket_from_client(chat)
    mock.recv_buffer.put_nowait(':tmi.twitch.tv RECONNECT')
    result = await asyncio.wait_for(incoming.get(), timeout=0.1)
    assert result == join_part(
        is_join=True,
        raw=':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel_user',
        where='channel_user',
        who='test_username',
    )
