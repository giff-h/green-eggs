# -*- coding: utf-8 -*-
import pytest
from pytest_mock import MockerFixture

from green_eggs.config import Config
from green_eggs.reactive.api import TwitchApiCommon
from green_eggs.reactive.api.direct import TwitchApiDirect
from green_eggs.reactive.channel import Channel
from green_eggs.reactive.client import TwitchWebsocketClient
from tests.reactive import mock_socket, response_context, test_logger

__all__ = ('api_common', 'api_direct', 'channel', 'chat')


@pytest.fixture
async def api_common(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.request', return_value=response_context())

    async with TwitchApiCommon(client_id='test client', token='test token', logger=test_logger) as api_client:
        api_client.direct.base_url = 'base/'
        yield api_client


@pytest.fixture
async def api_direct(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.request', return_value=response_context())

    async with TwitchApiDirect(client_id='test client', token='test token', logger=test_logger) as api_client:
        api_client.base_url = 'base/'
        yield api_client


@pytest.fixture
async def chat(mocker: MockerFixture):
    mocker.patch('websockets.connect', side_effect=mock_socket)
    async with TwitchWebsocketClient(username='test_username', token='test_token', logger=test_logger) as chat:
        yield chat


@pytest.fixture
async def channel(api_common: TwitchApiCommon, chat: TwitchWebsocketClient):
    async with Channel(
        channel_name='channel_user', api=api_common, chat=chat, config=Config(), logger=test_logger
    ) as channel:
        yield channel
