# -*- coding: utf-8 -*-
import asyncio

import pytest
from reactivex import Observable, of

from green_eggs.data_types import HandleAble, NormalizedUser
from green_eggs.reactive.channel import Channel
from tests.reactive import get_mock_socket_from_client
from tests.reactive.fixtures import *  # noqa
from tests.utils.data_types import clear_chat, code_353, join_part, priv_msg, room_state, user_notice, user_state


def test_code_353(channel: Channel):
    channel._users_in_channel._persistent = {NormalizedUser(username='user1'), NormalizedUser(username='already_here')}
    channel._handle_code353(code_353('user1', 'user2', 'another_user', where='channel_user'))
    assert channel._users_in_channel._temporary == set()
    assert channel._users_in_channel._persistent == {
        NormalizedUser(username='user1'),
        NormalizedUser(username='user2'),
        NormalizedUser(username='another_user'),
    }


def test_join(channel: Channel):
    channel._users_in_channel._persistent = {NormalizedUser(username='user1'), NormalizedUser(username='already_here')}
    channel._users_in_channel._temporary = {NormalizedUser(username='other_user')}
    channel._handle_joinpart_list([join_part(True, who='new_user', where='channel_user')])
    assert channel._users_in_channel._persistent == {
        NormalizedUser(username='user1'),
        NormalizedUser(username='already_here'),
        NormalizedUser(username='new_user'),
    }
    assert channel._users_in_channel._temporary == set()


def test_part(channel: Channel):
    channel._users_in_channel._persistent = {NormalizedUser(username='user1'), NormalizedUser(username='already_here')}
    channel._users_in_channel._temporary = {NormalizedUser(username='other_user')}
    channel._handle_joinpart_list([join_part(False, who='already_here', where='channel_user')])
    assert channel._users_in_channel._persistent == {NormalizedUser(username='user1')}
    assert channel._users_in_channel._temporary == set()


def test_privmsg(channel: Channel):
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user', who='message_sender'), tags_kwargs=dict(user_id='123')
    )
    channel._handle_privmsg(message)
    expected_user = NormalizedUser(username='message_sender', user_id='123')
    assert channel._users_in_channel._temporary == {expected_user}
    assert expected_user in channel._users_last_messages
    assert list(channel._users_last_messages[expected_user]) == [message]


def test_room_state(channel: Channel):
    channel._handle_roomstate(
        room_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    )
    assert channel.broadcaster_id == '123'


def test_user_state(channel: Channel):
    # TODO extend testing a bit once this is used
    assert channel._userstate is None
    channel._handle_userstate(user_state())
    assert channel._userstate is not None


def test_setup(channel: Channel):
    pass


def test_test_users_from_query_privmsg(channel: Channel):
    message = priv_msg(
        handle_able_kwargs=dict(who='username'), tags_kwargs=dict(display_name='UserName', user_id='123')
    )
    assert channel._users_from_query(message) == [
        NormalizedUser(user_id='123', username='username', display_name='UserName')
    ]


def test_users_from_query_string(channel: Channel):
    assert channel._users_from_query('123') == [
        NormalizedUser(user_id='123'),
        NormalizedUser(username='123'),
        NormalizedUser(display_name='123'),
    ]
    assert channel._users_from_query('@User12') == [
        NormalizedUser(user_id='User12'),
        NormalizedUser(username='user12'),
        NormalizedUser(display_name='User12'),
    ]


def test_users_from_query_normalized_user(channel: Channel):
    user = NormalizedUser(user_id='1234', username='abcd', display_name='ABCD')
    assert channel._users_from_query(user) == [user]


def test_users_from_query_error(channel: Channel):
    with pytest.raises(ValueError, match='Query value must be a string, NormalizedUser, or PrivMsg'):
        channel._users_from_query(1)  # type: ignore[arg-type]


def test_actionable_messages_operator(channel: Channel):
    # TODO test link blocking
    expected_privmsg_one = priv_msg(
        handle_able_kwargs=dict(message='message one', where='channel_user'), tags_kwargs=dict(id='123')
    )
    expected_privmsg_two = priv_msg(
        handle_able_kwargs=dict(message='message two', where='channel_user'), tags_kwargs=dict(id='456')
    )
    only_messages = []
    observable: Observable[HandleAble] = of(
        expected_privmsg_one,
        join_part(True, who='new_user', where='channel_user'),
        priv_msg(handle_able_kwargs=dict(where='other_user'), tags_kwargs=dict(id='456')),
        user_notice(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123')),
        expected_privmsg_two,
        user_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(color='red')),
    )
    observable.pipe(channel.actionable_messages_operator).subscribe(lambda x: only_messages.append(x))
    assert only_messages == [expected_privmsg_one, expected_privmsg_two]


async def test_add_permit_for_user_false_if_already_permit(channel: Channel):
    async def permit_task():
        pass

    channel._permit_cache['user'] = asyncio.create_task(permit_task())
    result = channel.add_permit_for_user('User')
    assert not result


async def test_add_permit_for_user_true_if_permit_added(channel: Channel):
    channel._config.link_permit_duration = 0
    result = channel.add_permit_for_user('user')
    assert result
    assert 'user' in channel._permit_cache
    await asyncio.sleep(0.01)
    assert 'user' not in channel._permit_cache


async def test_add_permit_for_user_fine_if_permit_cleared(channel: Channel):
    channel._config.link_permit_duration = 0
    result = channel.add_permit_for_user('user')
    assert result
    assert 'user' in channel._permit_cache
    del channel._permit_cache['user']
    await asyncio.sleep(0.01)
    assert 'user' not in channel._permit_cache


def test_broadcaster_id_empty_without_roomstate(channel: Channel):
    assert channel._roomstate is None
    assert channel.broadcaster_id == ''


def test_broadcaster_id_uses_roomstate(channel: Channel):
    channel._roomstate = room_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    assert channel.broadcaster_id == '123'


def test_filter_for_channel(channel: Channel):
    expected_privmsg = priv_msg(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(id='123'))
    expected_join = join_part(True, who='new_user', where='channel_user')
    expected_part = join_part(False, who='gone_user', where='channel_user')
    expected_clearchat = clear_chat(handle_able_kwargs=dict(who='cleared_user', where='channel_user'))
    expected_usernotice = user_notice(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    expected_roomstate = room_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    expected_userstate = user_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(color='red'))

    only_for_channel = []
    observable: Observable[HandleAble] = of(
        expected_privmsg,
        priv_msg(handle_able_kwargs=dict(where='other_user'), tags_kwargs=dict(id='456')),
        expected_join,
        join_part(True, who='whoever', where='other_user'),
        expected_part,
        join_part(False, who='whoever', where='other_user'),
        expected_clearchat,
        clear_chat(handle_able_kwargs=dict(who='whoever', where='other_user')),
        expected_usernotice,
        user_notice(handle_able_kwargs=dict(where='other_user'), tags_kwargs=dict(room_id='456')),
        expected_roomstate,
        room_state(handle_able_kwargs=dict(where='other_user'), tags_kwargs=dict(room_id='456')),
        expected_userstate,
        user_state(handle_able_kwargs=dict(where='other_user'), tags_kwargs=dict(color='blue')),
    )
    observable.pipe(channel.filter_for_channel).subscribe(lambda x: only_for_channel.append(x))
    assert only_for_channel == [
        expected_privmsg,
        expected_join,
        expected_part,
        expected_clearchat,
        expected_usernotice,
        expected_roomstate,
        expected_userstate,
    ]


def test_is_user_moderator(channel: Channel):
    pass


def test_is_user_subscribed(channel: Channel):
    pass


def test_is_user_vip(channel: Channel):
    pass


async def test_send_message(channel: Channel):
    mock = await get_mock_socket_from_client(channel._chat)
    await channel.send_message('hello chat')
    assert mock.send_buffer.get_nowait() == 'PRIVMSG #channel_user :hello chat'


async def test_send_message_too_long(channel: Channel):
    with pytest.raises(ValueError, match='Messages cannot exceed 500 characters'):
        await channel.send_message('A' * 501)
