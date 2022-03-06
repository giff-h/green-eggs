# -*- coding: utf-8 -*-
import asyncio
import contextlib

from aiologger import Logger

from green_eggs.constants import EXPECTED_AUTH_CODES

logger = Logger.with_default_handlers(name='testing')


class MockSocket:
    def __init__(self, *, ignore=None):
        self._recv_buffer: 'asyncio.Queue[str]' = asyncio.Queue()
        self._send_buffer: 'asyncio.Queue[str]' = asyncio.Queue()

        self._auth_nick = False
        self._auth_pass = False
        self._cap_req = False

        self._ignore = ignore or []

    @staticmethod
    async def ensure_open():
        pass

    @staticmethod
    async def close():
        pass

    async def recv(self):
        data = await self._recv_buffer.get()
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
            await self._recv_buffer.put(f':test_username!test_username@test_username.tmi.twitch.tv JOIN #{channel}')
        elif data.startswith('PART #'):
            channel = data[6:]
            await self._recv_buffer.put(f':test_username!test_username@test_username.tmi.twitch.tv PART #{channel}')
        else:
            # Do not include initializing data in the testing buffer
            assert data.endswith('\r\n'), data
            await self._send_buffer.put(data.rstrip('\r\n'))

        if self._auth_pass and self._auth_nick:
            self._auth_pass = self._auth_nick = False
            if 'auth' not in self._ignore:
                for code in EXPECTED_AUTH_CODES:
                    await self._recv_buffer.put(f':tmi.twitch.tv {code} twisty maze')

        if self._cap_req:
            self._cap_req = False
            if 'cap_req' not in self._ignore:
                await self._recv_buffer.put(
                    f':tmi.twitch.tv CAP * ACK :twitch.tv/commands twitch.tv/membership twitch.tv/tags'
                )


async def mock_socket(**k):
    return MockSocket(**k)


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
