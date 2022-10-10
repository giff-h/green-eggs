# -*- coding: utf-8 -*-
from aiohttp import ClientResponseError
import pytest
from pytest_mock import MockerFixture
import reactivex as rx

from green_eggs.reactive.api import TwitchApiCommon, TwitchApiDirect
from tests.reactive import response_context
from tests.reactive.fixtures import *  # noqa


def test_direct(api_common: TwitchApiCommon):
    assert isinstance(api_common.direct, TwitchApiDirect)


async def test_get_is_user_subscribed_to_channel(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'aiohttp.ClientSession.request', return_value=response_context(return_json=dict(data=[dict(tier='1')]))
    )

    result = await api_common.get_is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    assert result is True
    api_common.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=123&user_id=456', json=None
    )


async def test_get_is_user_subscribed_to_channel_no_tier(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession.request', return_value=response_context(return_json=dict(data=[dict()])))

    result = await api_common.get_is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    assert result is False
    api_common.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=123&user_id=456', json=None
    )


async def test_get_is_user_subscribed_to_channel_404(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'tests.reactive.MockResponse.raise_for_status',
        side_effect=ClientResponseError(None, (), status=404),  # type: ignore[arg-type]
    )

    result = await api_common.get_is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    assert result is False
    api_common.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=123&user_id=456', json=None
    )


async def test_get_is_user_subscribed_to_channel_raise_not_404(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'tests.reactive.MockResponse.raise_for_status',
        side_effect=ClientResponseError(None, (), status=400),  # type: ignore[arg-type]
    )

    # the error shouldn't happen until subscribed
    obs = api_common.get_is_user_subscribed_to_channel(broadcaster_id='123', user_id='456')
    with pytest.raises(ClientResponseError) as exc_info:
        await obs
    assert exc_info.value.status == 400

    api_common.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=123&user_id=456', json=None
    )


def test_get_shoutout_info_both_none(api_common: TwitchApiCommon):
    with pytest.raises(ValueError, match='Most provide either username or user_id'):
        api_common.get_shoutout_info()


async def test_get_shoutout_info_only_username(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.reactive.api.direct.TwitchApiDirect.get_users',
        return_value=rx.of(dict(data=[dict(id='123')])),
    )
    mocker.patch(
        'green_eggs.reactive.api.direct.TwitchApiDirect.get_channel_information',
        return_value=rx.of(
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
        'green_eggs.reactive.api.direct.TwitchApiDirect.get_channel_information',
        return_value=rx.of(
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
    mocker.patch('green_eggs.reactive.api.direct.TwitchApiDirect.get_users')
    mocker.patch(
        'green_eggs.reactive.api.direct.TwitchApiDirect.get_channel_information',
        return_value=rx.of(
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

    result = await api_common.get_shoutout_info(username='other_streamer3', user_id='345')
    assert result is not None
    api_common.direct.get_users.assert_not_called()  # type: ignore[attr-defined]
    api_common.direct.get_channel_information.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='345'
    )


async def test_get_shoutout_info_none_if_no_user(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch('green_eggs.reactive.api.direct.TwitchApiDirect.get_users', return_value=rx.of(dict(data=[])))

    assert await api_common.get_shoutout_info(username='other_streamer') is None


async def test_get_shoutout_info_none_if_no_stream(api_common: TwitchApiCommon, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.reactive.api.direct.TwitchApiDirect.get_channel_information',
        return_value=rx.of(dict(data=[])),
    )

    assert await api_common.get_shoutout_info(user_id='123') is None
