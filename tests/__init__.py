# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager

import pytest
from pytest_mock import MockerFixture

from green_eggs.api import TwitchApi


class MockResponse:
    @staticmethod
    async def json():
        return dict(foo='bar')

    @staticmethod
    def raise_for_status():
        pass


@asynccontextmanager
async def response_context():
    yield MockResponse()


@pytest.fixture
async def api(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.request', return_value=response_context())

    async with TwitchApi(client_id='test client', token='test token') as api_client:
        api_client._base_url = 'base/'
        yield api_client
