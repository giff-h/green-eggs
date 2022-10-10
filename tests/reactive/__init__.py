# -*- coding: utf-8 -*-
import asyncio
import contextlib
from typing import AsyncContextManager, AsyncIterator, Union

from aiologger import Logger

from green_eggs.constants import EXPECTED_AUTH_CODES

Text = Union[str, bytes]
test_logger = Logger(name='testing')  # no handlers


class MockSocket(AsyncIterator[Text], AsyncContextManager):
    def __init__(self):
        self.recv_buffer: 'asyncio.Queue[Union[Text, BaseException]]' = asyncio.Queue()
        self.send_buffer: 'asyncio.Queue[Text]' = asyncio.Queue()

        self._auth_nick = False
        self._auth_pass = False
        self._cap_req = False

    async def __anext__(self) -> Text:
        try:
            data = await self.recv_buffer.get()
        except RuntimeError as e:
            if e.args[0] == 'Event loop is closed':
                raise StopAsyncIteration
            else:
                raise

        if isinstance(data, BaseException):
            raise data

        return data

    async def send(self, data: str):
        if data.startswith('PASS '):
            assert data == 'PASS oauth:test_token\r\n', data
            self._auth_pass = True
        elif data.startswith('NICK '):
            assert data == 'NICK test_username\r\n', data
            self._auth_nick = True
        elif data.startswith('CAP REQ :'):
            assert data == 'CAP REQ :twitch.tv/commands twitch.tv/membership twitch.tv/tags\r\n', data
            self._cap_req = True
        elif data.startswith('JOIN #'):
            channel = data[6:]
            await self.recv_buffer.put(f':test_username!test_username@test_username.tmi.twitch.tv JOIN #{channel}')
        elif data.startswith('PART #'):
            channel = data[6:]
            await self.recv_buffer.put(f':test_username!test_username@test_username.tmi.twitch.tv PART #{channel}')
        else:
            # Do not include initializing data in the testing buffer
            assert data.endswith('\r\n'), data
            await self.send_buffer.put(data.rstrip('\r\n'))

        if self._auth_pass and self._auth_nick:
            self._auth_pass = self._auth_nick = False
            for code in EXPECTED_AUTH_CODES:
                await self.recv_buffer.put(f':tmi.twitch.tv {code} twisty maze')

        if self._cap_req:
            self._cap_req = False
            await self.recv_buffer.put(
                f':tmi.twitch.tv CAP * ACK :twitch.tv/commands twitch.tv/membership twitch.tv/tags'
            )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def mock_socket(*_args, **_kwargs):
    return MockSocket()


async def get_mock_socket_from_client(client) -> MockSocket:
    # noinspection PyProtectedMember
    send_func = await client._websocket_send_func
    return send_func.__self__


class MockResponse:
    def __init__(self, return_json=None):
        self._return_json = return_json or dict(foo='bar')

    async def json(self):
        return self._return_json

    @staticmethod
    def raise_for_status():
        pass


@contextlib.asynccontextmanager
async def response_context(return_json=None):
    yield MockResponse(return_json=return_json)
