# -*- coding: utf-8 -*-
import pytest

from green_eggs.api import TwitchApi
from green_eggs.channel import Channel
from green_eggs.client import TwitchChatClient
from tests import api, client, logger, response_context  # noqa
from tests.utils.data_types import code_353, join_part, priv_msg, room_state


def test_code_353(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel._users_in_channel = {'user1', 'already_here'}
    channel.handle_code_353(code_353('user1', 'user2', 'another_user', where='channel_user'))
    assert channel._users_in_channel == {'user1', 'user2', 'another_user', 'already_here'}


def test_code_353_wrong_channel(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    try:
        channel.handle_code_353(code_353('user1', 'user2', 'another_user', where='wrong_channel'))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a code353 from wrong_channel'
    else:
        assert False


def test_join(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel._users_in_channel = {'user1', 'already_here'}
    channel._users_in_channel_tmp = {'other_user'}
    channel.handle_join_part(join_part(True, who='new_user', where='channel_user'))
    assert channel._users_in_channel == {'user1', 'already_here', 'new_user'}
    assert channel._users_in_channel_tmp == set()


def test_part(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel._users_in_channel = {'user1', 'already_here'}
    channel._users_in_channel_tmp = {'other_user'}
    channel.handle_join_part(join_part(False, who='already_here', where='channel_user'))
    assert channel._users_in_channel == {'user1'}
    assert channel._users_in_channel_tmp == set()


def test_join_part_wrong_channel(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    try:
        channel.handle_join_part(join_part(where='wrong_channel'))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a join/part from wrong_channel'
    else:
        assert False


def test_message(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user', who='message_sender'), tags_kwargs=dict(user_id='123')
    )
    channel.handle_message(message)
    assert channel._users_in_channel_tmp == {'message_sender'}
    assert '123' in channel._last_five_for_user_id
    assert list(channel._last_five_for_user_id['123']) == [message]


def test_message_max_five(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user', who='message_sender'), tags_kwargs=dict(user_id='123')
    )
    for _ in range(6):
        channel.handle_message(message)
    assert len(channel._last_five_for_user_id['123']) == 5


def test_message_wrong_channel(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    try:
        channel.handle_message(priv_msg(handle_able_kwargs=dict(where='wrong_channel')))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a message from wrong_channel'
    else:
        assert False


def test_room_state(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel.handle_room_state(
        room_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    )
    assert channel._broadcaster_id == '123'


def test_room_state_wrong_channel(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    try:
        channel.handle_room_state(room_state(handle_able_kwargs=dict(where='wrong_channel')))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a room state from wrong_channel'
    else:
        assert False


def test_is_user_in_channel(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel._users_in_channel.update(('user1', 'user2'))
    channel._users_in_channel_tmp.update(('user1', 'other_user'))
    assert channel.is_user_in_channel('user1')
    assert channel.is_user_in_channel('user2')
    assert channel.is_user_in_channel('other_user')
    assert not channel.is_user_in_channel('not_found')


@pytest.mark.asyncio
async def test_is_user_subscribed_with_messages(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    message_subscribed = priv_msg(
        handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(user_id='123', badges=dict(subscriber='1'))
    )
    message_not_subscribed = priv_msg(
        handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(user_id='123', badges=dict())
    )
    channel.handle_message(message_subscribed)
    channel.handle_message(message_not_subscribed)
    assert await channel.is_user_subscribed('123')
    assert '123' not in channel._api_results_cache
    api._session.request.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_is_user_subscribed_with_api(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    api._session.request.return_value = response_context(  # type: ignore[attr-defined]
        return_json=dict(data=[dict(tier='1000')])
    )
    assert '123' not in channel._api_results_cache
    assert await channel.is_user_subscribed('123')
    assert '123' in channel._api_results_cache
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=&user_id=123', json=None
    )


@pytest.mark.asyncio
async def test_is_user_subscribed_false_with_api(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    api._session.request.return_value = response_context(return_json=dict(data=[dict()]))  # type: ignore[attr-defined]
    assert '123' not in channel._api_results_cache
    assert not await channel.is_user_subscribed('123')
    assert '123' in channel._api_results_cache
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=&user_id=123', json=None
    )


@pytest.mark.asyncio
async def test_is_user_subscribed_with_cache(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel._api_results_cache['123'] = dict(is_subscribed=True)
    assert await channel.is_user_subscribed('123')
    api._session.request.assert_not_called()  # type: ignore[attr-defined]


def test_user_latest_message_none(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel.handle_message(priv_msg(handle_able_kwargs=dict(where='channel_user', who='other_user')))
    assert channel.user_latest_message('login') is None


def test_user_latest_message_login(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(where='channel_user', who='user_login', message='message one'))
    )
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(where='channel_user', who='user_login', message='message two'))
    )
    result = channel.user_latest_message('User_Login')
    assert result is not None
    assert result.message == 'message two'


def test_user_latest_message_display(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    channel.handle_message(
        priv_msg(
            handle_able_kwargs=dict(where='channel_user', message='message one'),
            tags_kwargs=dict(display_name='User_Login'),
        )
    )
    channel.handle_message(
        priv_msg(
            handle_able_kwargs=dict(where='channel_user', message='message two'),
            tags_kwargs=dict(display_name='User_Login'),
        )
    )
    result = channel.user_latest_message('User_login')
    assert result is not None
    assert result.message == 'message two'


@pytest.mark.asyncio
async def test_send(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    await channel.send('message content')
    sent = client._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :message content'


@pytest.mark.asyncio
async def test_send_too_long(api: TwitchApi, client: TwitchChatClient):
    channel = Channel(login='channel_user', api=api, chat=client, logger=logger)
    try:
        await channel.send('A' * 501)
    except ValueError as e:
        assert e.args[0] == 'Messages cannot exceed 500 characters'
    else:
        assert False
