# -*- coding: utf-8 -*-
import asyncio

import pytest
from pytest_mock import MockerFixture
import websockets

from green_eggs.client import TwitchChatClient, ensure_str
from green_eggs.exceptions import ChannelPresenceRaceCondition
from tests import client, logger, mock_socket  # noqa


def none_future():
    future = asyncio.Future()
    future.set_result(None)
    return future


def test_ensure_str():
    assert isinstance(ensure_str(''), str)
    assert isinstance(ensure_str(b''), str)


@pytest.mark.asyncio
async def test_failed_connection_fails_all(mocker: MockerFixture):
    exc = Exception('FAIL')
    mocker.patch('websockets.connect', side_effect=exc)
    client = TwitchChatClient(username='test_username', token='test_token', logger=logger)
    try:
        async with client:
            assert False
    except Exception as e:
        assert client.ws_exc is exc
        assert e is exc


@pytest.mark.asyncio
async def test_broken_expectations(mocker: MockerFixture):
    mocker.patch('websockets.connect', return_value=mock_socket(ignore=['auth']))
    client = TwitchChatClient(username='test_username', token='test_token', logger=logger)
    client._expect_timeout = 0.1
    try:
        async with client:
            assert False
    except asyncio.TimeoutError:
        assert client.ws_exc is None


@pytest.mark.asyncio
async def test_initialize_requires_connection(mocker: MockerFixture):
    mocker.patch('websockets.connect', return_value=none_future())
    async with TwitchChatClient(username='test_username', token='test_token', logger=logger) as client:
        assert client._websocket is None
        assert client._buffer_task is None
        assert not await client.is_connected()


@pytest.mark.asyncio
async def test_initial_assumptions(client: TwitchChatClient):
    assert client._buffer_task is not None
    assert client._websocket is not None


@pytest.mark.asyncio
async def test_buffer_task_captures_closed_connection(client: TwitchChatClient, mocker: MockerFixture):
    mocker.patch('green_eggs.client.TwitchChatClient.connect', return_value=none_future())
    mocker.patch('green_eggs.client.TwitchChatClient.initialize', return_value=none_future())
    await client._websocket._recv_buffer.put(websockets.ConnectionClosedError(2000, ''))  # type: ignore[union-attr]
    await client._websocket._recv_buffer.put('something')  # type: ignore[union-attr]
    async for data in client.incoming():
        assert data[0] == 'something'
        break  # FIXME add a wait timeout fail condition
    client.connect.assert_called_once_with()  # type: ignore[attr-defined]
    client.initialize.assert_called_once_with()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_buffer_task_captures_other_exception(client: TwitchChatClient, mocker: MockerFixture):
    mocker.patch('green_eggs.client.TwitchChatClient.connect')
    mocker.patch('green_eggs.client.TwitchChatClient.initialize')
    await client._websocket._recv_buffer.put(Exception())  # type: ignore[union-attr]
    await client._websocket._recv_buffer.put('something')  # type: ignore[union-attr]
    async for data in client.incoming():
        assert data[0] == 'something'
        break  # FIXME add a wait timeout fail condition
    client.connect.assert_not_called()  # type: ignore[attr-defined]
    client.initialize.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_reconnect_message_causes_reconnect(client: TwitchChatClient, mocker: MockerFixture):
    mocker.patch('green_eggs.client.TwitchChatClient.connect', return_value=none_future())
    mocker.patch('green_eggs.client.TwitchChatClient.initialize', return_value=none_future())
    await client._websocket._recv_buffer.put(':tmi.twitch.tv RECONNECT')  # type: ignore[union-attr]
    await client._websocket._recv_buffer.put('something')  # type: ignore[union-attr]
    async for data in client.incoming():
        assert data[0] == 'something'
        break  # FIXME add a wait timeout fail condition
    client.connect.assert_called_once_with()  # type: ignore[attr-defined]
    client.initialize.assert_called_once_with()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_connection_needs_websocket(client: TwitchChatClient):
    client._websocket = None
    assert not await client.is_connected()


@pytest.mark.asyncio
async def test_ping_pong(client: TwitchChatClient):
    await client._websocket._recv_buffer.put('PING hello')  # type: ignore[union-attr]
    await client._websocket._recv_buffer.put('something')  # type: ignore[union-attr]
    async for data in client.incoming():
        assert data[0] == 'something'
        break  # FIXME add a wait timeout fail condition
    pong = client._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert pong == 'PONG hello'


@pytest.mark.asyncio
async def test_join(client: TwitchChatClient):
    result = await client.join('Channel')
    assert result is True
    async for data in client.incoming():
        assert data[0] == ':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel'
        break  # FIXME add a wait timeout fail condition


@pytest.mark.asyncio
async def test_join_when_joining(client: TwitchChatClient):
    client._expectations['join'] = dict(channel=asyncio.Future())
    result = await client.join('Channel')
    assert result is False


@pytest.mark.asyncio
async def test_join_when_leaving_wait(client: TwitchChatClient):
    client._expect_timeout = 0.1
    client._expectations['part'] = dict(leavingchannel=asyncio.Future())
    result = await client.join('LeavingChannel', 'wait')
    assert result is False


@pytest.mark.asyncio
async def test_join_when_leaving_raise(client: TwitchChatClient):
    client._expectations['part'] = dict(raising=asyncio.Future())
    try:
        result = await client.join('raising', 'raise')
    except ChannelPresenceRaceCondition as e:
        assert e.args[0] == 'Tried to join while leaving'
    else:
        assert False, result


@pytest.mark.asyncio
async def test_join_when_leaving_abort(client: TwitchChatClient):
    client._expectations['part'] = dict(aborting=asyncio.Future())
    result = await client.join('aborting', 'abort')
    assert result is False


@pytest.mark.asyncio
async def test_leave(client: TwitchChatClient):
    result = await client.leave('Channel')
    assert result is True
    async for data in client.incoming():
        assert data[0] == ':test_username!test_username@test_username.tmi.twitch.tv PART #channel'
        break  # FIXME add a wait timeout fail condition


@pytest.mark.asyncio
async def test_leave_when_leaving(client: TwitchChatClient):
    client._expectations['part'] = dict(channel=asyncio.Future())
    result = await client.leave('Channel')
    assert result is False


@pytest.mark.asyncio
async def test_leave_when_joining_wait(client: TwitchChatClient):
    client._expect_timeout = 0.1
    client._expectations['join'] = dict(leavingchannel=asyncio.Future())
    result = await client.leave('LeavingChannel', 'wait')
    assert result is False


@pytest.mark.asyncio
async def test_leave_when_joining_raise(client: TwitchChatClient):
    client._expectations['join'] = dict(raising=asyncio.Future())
    try:
        result = await client.leave('raising', 'raise')
    except ChannelPresenceRaceCondition as e:
        assert e.args[0] == 'Tried to leave while joining'
    else:
        assert False, result


@pytest.mark.asyncio
async def test_leave_when_joining_abort(client: TwitchChatClient):
    client._expectations['join'] = dict(aborting=asyncio.Future())
    result = await client.leave('aborting', 'abort')
    assert result is False
