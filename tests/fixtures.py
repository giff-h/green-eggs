# -*- coding: utf-8 -*-
import pytest
from pytest_mock import MockerFixture

from green_eggs.api import TwitchApi
from green_eggs.channel import Channel
from green_eggs.client import TwitchChatClient
from tests import logger, mock_socket, response_context

__all__ = ('api', 'channel', 'client')


@pytest.fixture
async def api(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.request', return_value=response_context())

    async with TwitchApi(client_id='test client', token='test token', logger=logger) as api_client:
        api_client._base_url = 'base/'
        yield api_client


@pytest.fixture
async def client(mocker: MockerFixture):
    mocker.patch('websockets.connect', return_value=mock_socket())

    async with TwitchChatClient(username='test_username', token='test_token', logger=logger) as chat:
        # noinspection PyProtectedMember
        assert chat._websocket._recv_buffer.empty()  # type: ignore[union-attr]
        yield chat


@pytest.fixture
def channel(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    return channel
