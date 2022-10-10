# -*- coding: utf-8 -*-
from pytest_mock import MockerFixture

from green_eggs.reactive.api import validate_client_id
from tests.reactive import response_context


async def test_validate_client_id(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.get', return_value=response_context(return_json=dict(client_id='client')))
    client_id = await validate_client_id('token')
    assert client_id == 'client'
