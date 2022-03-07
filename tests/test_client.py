# -*- coding: utf-8 -*-
import asyncio

import pytest
from pytest_mock import MockerFixture
from websockets.exceptions import ConnectionClosedError
from websockets.frames import Close

from green_eggs.client import TwitchChatClient, ensure_str
from green_eggs.exceptions import ChannelPresenceRaceCondition
from tests import logger, mock_socket
from tests.fixtures import *  # noqa


def none_future():
    future = asyncio.Future()
    future.set_result(None)
    return future


def test_ensure_str():
    assert isinstance(ensure_str(''), str)
    assert isinstance(ensure_str(b''), str)


async def test_failed_connection_fails_all(mocker: MockerFixture):
    exc = Exception('FAIL')
    mocker.patch('websockets.connect', side_effect=exc)
    client = TwitchChatClient(username='test_username', token='test_token', logger=logger)
    with pytest.raises(Exception) as exc_info:
        async with client:
            pass
    assert client.ws_exc is exc
    assert exc_info.value is exc


async def test_broken_expectations(mocker: MockerFixture):
    mocker.patch('websockets.connect', return_value=mock_socket(ignore=['auth']))
    client = TwitchChatClient(username='test_username', token='test_token', logger=logger)
    client._expect_timeout = 0.1
    with pytest.raises(asyncio.TimeoutError):
        async with client:
            pass
    assert client.ws_exc is None


async def test_initialize_requires_connection(mocker: MockerFixture):
    mocker.patch('websockets.connect', return_value=none_future())
    async with TwitchChatClient(username='test_username', token='test_token', logger=logger) as client:
        assert client._websocket is None
        assert client._buffer_task is None
        assert not await client.is_connected()


async def test_initial_assumptions(client: TwitchChatClient):
    assert client._buffer_task is not None
    assert client._websocket is not None


async def test_buffer_task_captures_closed_connection(client: TwitchChatClient, mocker: MockerFixture):
    mocker.patch('green_eggs.client.TwitchChatClient.connect', return_value=none_future())
    mocker.patch('green_eggs.client.TwitchChatClient.initialize', return_value=none_future())
    await client._websocket._recv_buffer.put(  # type: ignore[union-attr]
        ConnectionClosedError(Close(code=2000, reason=''), None)
    )
    await client._websocket._recv_buffer.put('something')  # type: ignore[union-attr]
    async for data in client.incoming():
        assert data[0] == 'something'
        break  # FIXME add a wait timeout fail condition
    client.connect.assert_called_once_with()  # type: ignore[attr-defined]
    client.initialize.assert_called_once_with()  # type: ignore[attr-defined]


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


async def test_connection_needs_websocket(client: TwitchChatClient):
    client._websocket = None
    assert not await client.is_connected()


async def test_ping_pong(client: TwitchChatClient):
    await client._websocket._recv_buffer.put('PING hello')  # type: ignore[union-attr]
    await client._websocket._recv_buffer.put('something')  # type: ignore[union-attr]
    async for data in client.incoming():
        assert data[0] == 'something'
        break  # FIXME add a wait timeout fail condition
    pong = client._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert pong == 'PONG hello'


async def test_join(client: TwitchChatClient):
    result = await client.join('Channel')
    assert result is True
    async for data in client.incoming():
        assert data[0] == ':test_username!test_username@test_username.tmi.twitch.tv JOIN #channel'
        break  # FIXME add a wait timeout fail condition


async def test_join_when_joining(client: TwitchChatClient):
    client._expectations['join'] = dict(channel=asyncio.Future())
    result = await client.join('Channel')
    assert result is False


async def test_join_when_leaving_wait(client: TwitchChatClient):
    client._expect_timeout = 0.1
    client._expectations['part'] = dict(leavingchannel=asyncio.Future())
    result = await client.join('LeavingChannel', 'wait')
    assert result is False


async def test_join_when_leaving_raise(client: TwitchChatClient):
    client._expectations['part'] = dict(raising=asyncio.Future())
    with pytest.raises(ChannelPresenceRaceCondition, match='Tried to join while leaving'):
        await client.join('raising', 'raise')


async def test_join_when_leaving_abort(client: TwitchChatClient):
    client._expectations['part'] = dict(aborting=asyncio.Future())
    result = await client.join('aborting', 'abort')
    assert result is False


async def test_leave(client: TwitchChatClient):
    result = await client.leave('Channel')
    assert result is True
    async for data in client.incoming():
        assert data[0] == ':test_username!test_username@test_username.tmi.twitch.tv PART #channel'
        break  # FIXME add a wait timeout fail condition


async def test_leave_when_leaving(client: TwitchChatClient):
    client._expectations['part'] = dict(channel=asyncio.Future())
    result = await client.leave('Channel')
    assert result is False


async def test_leave_when_joining_wait(client: TwitchChatClient):
    client._expect_timeout = 0.1
    client._expectations['join'] = dict(leavingchannel=asyncio.Future())
    result = await client.leave('LeavingChannel', 'wait')
    assert result is False


async def test_leave_when_joining_raise(client: TwitchChatClient):
    client._expectations['join'] = dict(raising=asyncio.Future())
    with pytest.raises(ChannelPresenceRaceCondition, match='Tried to leave while joining'):
        await client.leave('raising', 'raise')


async def test_leave_when_joining_abort(client: TwitchChatClient):
    client._expectations['join'] = dict(aborting=asyncio.Future())
    result = await client.leave('aborting', 'abort')
    assert result is False


async def test_send_websocket_is_null(client: TwitchChatClient):
    websocket = client._websocket  # hold it to put it back for teardown
    client._websocket = None
    await client.send('Nothing')
    assert websocket._send_buffer.empty()  # type: ignore[union-attr]
    client._websocket = websocket


async def test_send_logs_message(client: TwitchChatClient, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.debug')
    await client.send('Something')
    client._logger.debug.assert_called_once_with('Sending data: \'Something\'')  # type: ignore[attr-defined]


async def test_send_logs_redacted(client: TwitchChatClient, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.debug')
    await client.send('SECRETS', 'redacted')
    client._logger.debug.assert_called_once_with('Sending data: \'redacted\'')  # type: ignore[attr-defined]


async def test_send_sends_data(client: TwitchChatClient):
    await client.send('Message')
    data = client._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert data == 'Message'
