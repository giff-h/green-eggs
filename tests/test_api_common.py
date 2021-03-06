# -*- coding: utf-8 -*-
from aiohttp import ClientResponseError
import pytest
from pytest_mock import MockerFixture

from green_eggs.api import TwitchApiCommon, TwitchApiDirect
from green_eggs.api.common import validate_client_id
from tests import response_context
from tests.fixtures import *  # noqa
from tests.utils.compat import coroutine_result_value


async def test_validate_client_id(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.get', return_value=response_context(return_json=dict(client_id='client')))
    client_id = await validate_client_id('token')
    assert client_id == 'client'


def test_direct(api_common: TwitchApiCommon):
    assert isinstance(api_common.direct, TwitchApiDirect)


async def test_get_shoutout_info_both_none(api_common: TwitchApiCommon):
    with pytest.raises(ValueError, match='Most provide either username or user_id'):
        await api_common.get_shoutout_info()


async def test_get_shoutout_info_only_username(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_users',
        return_value=coroutine_result_value(dict(data=[dict(id='123')])),
    )
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_channel_information',
        return_value=coroutine_result_value(
            dict(
                data=[
                    dict(
                        broadcaster_id='123',
                        broadcaster_login='other_streamer',
                        broadcaster_name='Other_streamer',
                        game_name='The Best Game Ever',
                        game_id='456',
                        broadcaster_language='en',
                        title='The Best Stream Ever',
                    )
                ]
            )
        ),
    )

    shoutout_info = await api_common.get_shoutout_info(username='other_streamer')
    assert shoutout_info is not None
    api_common.direct.get_users.assert_called_once_with(login='other_streamer')  # type: ignore[attr-defined]
    api_common.direct.get_channel_information.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='123'
    )
    assert shoutout_info.user_id == '123'
    assert shoutout_info.username == 'other_streamer'
    assert shoutout_info.display_name == 'Other_streamer'
    assert shoutout_info.game_name == 'The Best Game Ever'
    assert shoutout_info.game_id == '456'
    assert shoutout_info.broadcaster_language == 'en'
    assert shoutout_info.stream_title == 'The Best Stream Ever'
    assert shoutout_info.user_link == 'https://twitch.tv/other_streamer'


async def test_get_shoutout_info_only_user_id(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_channel_information',
        return_value=coroutine_result_value(
            dict(
                data=[
                    dict(
                        broadcaster_id='234',
                        broadcaster_login='other_streamer2',
                        broadcaster_name='Other_streamer2',
                        game_name='The Next Best Game Ever',
                        game_id='567',
                        broadcaster_language='en',
                        title='The Next Best Stream Ever',
                    )
                ]
            )
        ),
    )

    shoutout_info = await api_common.get_shoutout_info(user_id='234')
    assert shoutout_info is not None
    api_common.direct.get_channel_information.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='234'
    )
    assert shoutout_info.user_id == '234'
    assert shoutout_info.username == 'other_streamer2'
    assert shoutout_info.display_name == 'Other_streamer2'
    assert shoutout_info.game_name == 'The Next Best Game Ever'
    assert shoutout_info.game_id == '567'
    assert shoutout_info.broadcaster_language == 'en'
    assert shoutout_info.stream_title == 'The Next Best Stream Ever'
    assert shoutout_info.user_link == 'https://twitch.tv/other_streamer2'


async def test_get_shoutout_info_username_and_user_id(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch('green_eggs.api.direct.TwitchApiDirect.get_users')
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_channel_information',
        return_value=coroutine_result_value(
            dict(
                data=[
                    dict(
                        broadcaster_id='345',
                        broadcaster_login='other_streamer3',
                        broadcaster_name='Other_streamer3',
                        game_name='An Okay Game',
                        game_id='678',
                        broadcaster_language='en',
                        title='An Okay Stream',
                    )
                ]
            )
        ),
    )

    assert await api_common.get_shoutout_info(username='other_streamer3', user_id='345') is not None
    api_common.direct.get_users.assert_not_called()  # type: ignore[attr-defined]
    api_common.direct.get_channel_information.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='345'
    )


async def test_get_shoutout_info_none_if_no_user(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch('green_eggs.api.direct.TwitchApiDirect.get_users', return_value=coroutine_result_value(dict(data=[])))

    assert await api_common.get_shoutout_info(username='other_streamer') is None


async def test_get_shoutout_info_none_if_no_stream(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_channel_information',
        return_value=coroutine_result_value(dict(data=[])),
    )

    assert await api_common.get_shoutout_info(user_id='123') is None


async def test_is_user_subscribed_to_channel(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.check_user_subscription',
        return_value=coroutine_result_value(dict(data=[dict(tier='1')])),
    )

    assert await api_common.is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    api_common.direct.check_user_subscription.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='123', user_id='456'
    )


async def test_is_user_subscribed_to_channel_no_tier(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.check_user_subscription',
        return_value=coroutine_result_value(dict(data=[dict()])),
    )

    assert not await api_common.is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    api_common.direct.check_user_subscription.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='123', user_id='456'
    )


async def test_is_user_subscribed_to_channel_404(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.check_user_subscription',
        side_effect=ClientResponseError(None, (), status=404),  # type: ignore[arg-type]
    )

    assert not await api_common.is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    api_common.direct.check_user_subscription.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='123', user_id='456'
    )


async def test_is_user_subscribed_to_channel_raise_not_404(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.check_user_subscription',
        side_effect=ClientResponseError(None, (), status=400),  # type: ignore[arg-type]
    )

    with pytest.raises(ClientResponseError) as exc_info:
        await api_common.is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    assert exc_info.value.status == 400

    api_common.direct.check_user_subscription.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='123', user_id='456'
    )
