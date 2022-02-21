# -*- coding: utf-8 -*-
import pytest
from pytest_mock import MockerFixture

from green_eggs.api import TwitchApiCommon, TwitchApiDirect
from green_eggs.channel import Channel
from green_eggs.client import TwitchChatClient
from green_eggs.config import Config
from tests import logger, mock_socket, response_context

__all__ = ('api_common', 'api_direct', 'channel', 'client')


@pytest.fixture
async def api_common(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.request', return_value=response_context())

    async with TwitchApiCommon(client_id='test client', token='test token', logger=logger) as api_client:
        api_client.direct._base_url = 'base/'
        yield api_client


@pytest.fixture
async def api_direct(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.request', return_value=response_context())

    async with TwitchApiDirect(client_id='test client', token='test token', logger=logger) as api_client:
        api_client._base_url = 'base/'
        yield api_client


@pytest.fixture
def channel(api_common: TwitchApiCommon, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api_common, chat=client, logger=logger, config=Config())
    return channel


@pytest.fixture
async def client(mocker: MockerFixture):
    mocker.patch('websockets.connect', return_value=mock_socket())

    async with TwitchChatClient(username='test_username', token='test_token', logger=logger) as chat:
        # noinspection PyProtectedMember
        assert chat._websocket._recv_buffer.empty()  # type: ignore[union-attr]
        yield chat
