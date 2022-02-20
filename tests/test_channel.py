# -*- coding: utf-8 -*-
from green_eggs.channel import Channel
from tests import response_context
from tests.fixtures import *  # noqa
from tests.utils.data_types import code_353, join_part, priv_msg, room_state


def test_code_353(channel: Channel):
    channel._users_in_channel = {'user1', 'already_here'}
    channel.handle_code_353(code_353('user1', 'user2', 'another_user', where='channel_user'))
    assert channel._users_in_channel == {'user1', 'user2', 'another_user', 'already_here'}


def test_code_353_wrong_channel(channel: Channel):
    try:
        channel.handle_code_353(code_353('user1', 'user2', 'another_user', where='wrong_channel'))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a code353 from wrong_channel'
    else:
        assert False


def test_join(channel: Channel):
    channel._users_in_channel = {'user1', 'already_here'}
    channel._users_in_channel_tmp = {'other_user'}
    channel.handle_join_part(join_part(True, who='new_user', where='channel_user'))
    assert channel._users_in_channel == {'user1', 'already_here', 'new_user'}
    assert channel._users_in_channel_tmp == set()


def test_part(channel: Channel):
    channel._users_in_channel = {'user1', 'already_here'}
    channel._users_in_channel_tmp = {'other_user'}
    channel.handle_join_part(join_part(False, who='already_here', where='channel_user'))
    assert channel._users_in_channel == {'user1'}
    assert channel._users_in_channel_tmp == set()


def test_join_part_wrong_channel(channel: Channel):
    try:
        channel.handle_join_part(join_part(where='wrong_channel'))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a join/part from wrong_channel'
    else:
        assert False


def test_message(channel: Channel):
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user', who='message_sender'), tags_kwargs=dict(user_id='123')
    )
    channel.handle_message(message)
    assert channel._users_in_channel_tmp == {'message_sender'}
    assert '123' in channel._last_five_for_user_id
    assert list(channel._last_five_for_user_id['123']) == [message]


def test_message_max_five(channel: Channel):
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user', who='message_sender'), tags_kwargs=dict(user_id='123')
    )
    for _ in range(6):
        channel.handle_message(message)
    assert len(channel._last_five_for_user_id['123']) == 5


def test_message_wrong_channel(channel: Channel):
    try:
        channel.handle_message(priv_msg(handle_able_kwargs=dict(where='wrong_channel')))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a message from wrong_channel'
    else:
        assert False


def test_room_state(channel: Channel):
    channel.handle_room_state(
        room_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    )
    assert channel.broadcaster_id == '123'


def test_room_state_wrong_channel(channel: Channel):
    try:
        channel.handle_room_state(room_state(handle_able_kwargs=dict(where='wrong_channel')))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a room state from wrong_channel'
        assert channel.broadcaster_id == ''
    else:
        assert False


def test_is_user_in_channel(channel: Channel):
    channel._users_in_channel.update(('user1', 'user2'))
    channel._users_in_channel_tmp.update(('user1', 'other_user'))
    assert channel.is_user_in_channel('user1')
    assert channel.is_user_in_channel('user2')
    assert channel.is_user_in_channel('other_user')
    assert not channel.is_user_in_channel('not_found')


async def test_is_user_subscribed_with_messages(channel: Channel):
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
    channel._api.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


async def test_is_user_subscribed_with_api(channel: Channel):
    channel._api.direct._session.request.return_value = response_context(  # type: ignore[attr-defined]
        return_json=dict(data=[dict(tier='1000')])
    )
    assert '123' not in channel._api_results_cache
    assert await channel.is_user_subscribed('123')
    assert '123' in channel._api_results_cache
    channel._api.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=&user_id=123', json=None
    )


async def test_is_user_subscribed_false_with_api(channel: Channel):
    channel._api.direct._session.request.return_value = response_context(  # type: ignore[attr-defined]
        return_json=dict(data=[dict()])
    )
    assert '123' not in channel._api_results_cache
    assert not await channel.is_user_subscribed('123')
    assert '123' in channel._api_results_cache
    channel._api.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=&user_id=123', json=None
    )


async def test_is_user_subscribed_with_cache(channel: Channel):
    channel._api_results_cache['123'] = dict(is_subscribed=True)
    assert await channel.is_user_subscribed('123')
    channel._api.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


def test_user_latest_message_none(channel: Channel):
    channel.handle_message(priv_msg(handle_able_kwargs=dict(where='channel_user', who='other_user')))
    assert channel.user_latest_message('login') is None


def test_user_latest_message_login(channel: Channel):
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(where='channel_user', who='user_login', message='message one'))
    )
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(where='channel_user', who='user_login', message='message two'))
    )
    result = channel.user_latest_message('User_Login')
    assert result is not None
    assert result.message == 'message two'


def test_user_latest_message_display(channel: Channel):
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


async def test_send(channel: Channel):
    await channel.send('message content')
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :message content'


async def test_send_too_long(channel: Channel):
    try:
        await channel.send('A' * 501)
    except ValueError as e:
        assert e.args[0] == 'Messages cannot exceed 500 characters'
    else:
        assert False
