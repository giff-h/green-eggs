# -*- coding: utf-8 -*-
import pytest

from green_eggs import data_types as dt
from green_eggs.reactive.channel import UserLastMessagesCache, UsersInChannel
from tests.utils.data_types import code_353, join_part, priv_msg


def test_users_in_channel_update_from_code353_sets_from_object():
    cache = UsersInChannel()
    cache.update_from_code353(code_353('new_user1', 'new_user2'))
    assert cache._persistent == {dt.NormalizedUser(username='new_user1'), dt.NormalizedUser(username='new_user2')}
    assert cache._temporary == set()


def test_users_in_channel_update_from_code353_removes_users_not_in_object():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1}
    cache._temporary = {user2}
    cache.update_from_code353(code_353('new_user'))
    assert cache._persistent == {dt.NormalizedUser(username='new_user')}
    assert cache._temporary == set()


def test_users_in_channel_update_from_code353_uses_data_from_existing_users_if_found():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    user3 = dt.NormalizedUser(user_id='3', username='user3', display_name='User3')
    user4 = dt.NormalizedUser(user_id='4', username='user4', display_name='User4')
    cache._persistent = {user1, user2}
    cache._temporary = {user3, user4}
    cache.update_from_code353(code_353('user1', 'user3'))
    assert cache._persistent == {user1, user3}
    assert cache._temporary == set()


def test_users_in_channel_update_from_joinpart_list_moves_from_temporary():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1}
    cache._temporary = {user2}
    cache.update_from_joinpart_list([join_part(is_join=True, who='user2')])
    assert cache._persistent == {user1, user2}
    assert cache._temporary == set()


def test_users_in_channel_update_from_joinpart_list_adds_and_removes_from_persistent():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='123', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='234', username='user2', display_name='User2')
    user3 = dt.NormalizedUser(user_id='345', username='user3', display_name='User3')
    user4 = dt.NormalizedUser(user_id='456', username='user4', display_name='User4')
    cache._persistent = {user1, user2, user3, user4}
    cache.update_from_joinpart_list([join_part(is_join=True, who='user5'), join_part(is_join=False, who='user2')])
    assert cache._persistent == {user1, user3, user4, dt.NormalizedUser(username='user5')}
    assert cache._temporary == set()


def test_users_in_channel_update_from_joinpart_list_wipes_temporary_if_none_of_them_joined():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1}
    cache._temporary = {user2}
    cache.update_from_joinpart_list([join_part(is_join=True, who='user3')])
    assert cache._persistent == {user1, dt.NormalizedUser(username='user3')}
    assert cache._temporary == set()


def test_users_in_channel_update_from_joinpart_list_does_not_choke_if_joined_user_was_persistent_somehow():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1, user2}
    cache.update_from_joinpart_list([join_part(is_join=True, who='user2')])
    assert cache._persistent == {user1, user2}
    assert cache._temporary == set()


def test_users_in_channel_update_from_privmsg_adds_new_user_to_temporary():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1, user2}
    cache.update_from_privmsg(
        priv_msg(handle_able_kwargs=dict(who='user3'), tags_kwargs=dict(display_name='User3', user_id='3'))
    )
    assert cache._persistent == {user1, user2}
    assert cache._temporary == {dt.NormalizedUser(user_id='3', username='user3', display_name='User3')}


def test_users_in_channel_update_from_privmsg_updates_existing_user_in_persistent():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1, user2}
    cache.update_from_privmsg(
        priv_msg(handle_able_kwargs=dict(who='user1'), tags_kwargs=dict(display_name='USER1', user_id='1'))
    )
    assert cache._persistent == {dt.NormalizedUser(user_id='1', username='user1', display_name='USER1'), user2}
    assert cache._temporary == set()


def test_users_in_channel_update_from_privmsg_updates_existing_user_in_temporary():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1}
    cache._temporary = {user2}
    cache.update_from_privmsg(
        priv_msg(handle_able_kwargs=dict(who='user2'), tags_kwargs=dict(display_name='USER2', user_id='2'))
    )
    assert cache._persistent == {user1}
    assert cache._temporary == {dt.NormalizedUser(user_id='2', username='user2', display_name='USER2')}


def test_users_in_channel_update_from_privmsg_updates_existing_user_in_persistent_first():
    cache = UsersInChannel()
    user1 = dt.NormalizedUser(user_id='1', username='user1', display_name='User1')
    user2 = dt.NormalizedUser(user_id='2', username='user2', display_name='User2')
    cache._persistent = {user1, user2}
    cache._temporary = {user1}
    cache.update_from_privmsg(
        priv_msg(handle_able_kwargs=dict(who='user1'), tags_kwargs=dict(display_name='USER1', user_id='1'))
    )
    assert cache._persistent == {dt.NormalizedUser(user_id='1', username='user1', display_name='USER1'), user2}
    assert cache._temporary == {user1}


def test_user_last_messages_cache_max_privmsg_count():
    cache = UserLastMessagesCache(3)
    privmsg = priv_msg(
        handle_able_kwargs=dict(message='hello', who='user'), tags_kwargs=dict(display_name='User', user_id='1')
    )
    for _ in range(5):
        cache.update_from_privmsg(privmsg)
    assert len(cache) == 1
    user = list(cache.keys())[0]
    assert len(cache[user]) == 3


def test_user_last_messages_cache_does_not_require_exact_user():
    cache = UserLastMessagesCache(3)
    privmsg = priv_msg(
        handle_able_kwargs=dict(message='hello', who='user'), tags_kwargs=dict(display_name='User', user_id='1')
    )
    cache.update_from_privmsg(privmsg)
    user = dt.NormalizedUser(username='user')
    assert cache[user] == [privmsg]


def test_user_last_messages_cache_raises_key_error_if_no_user_found():
    cache = UserLastMessagesCache(3)
    privmsg = priv_msg(
        handle_able_kwargs=dict(message='hello', who='user'), tags_kwargs=dict(display_name='User', user_id='1')
    )
    cache.update_from_privmsg(privmsg)
    user = dt.NormalizedUser(username='wrong_user')
    assert cache.get(user) is None
    with pytest.raises(KeyError):
        assert cache[user]


def test_user_last_messages_cache_update_from_privmsg_updates_user_key():
    cache = UserLastMessagesCache(3)
    privmsg_one = priv_msg(
        handle_able_kwargs=dict(message='hello', who='user'), tags_kwargs=dict(display_name='User', user_id='1')
    )
    cache.update_from_privmsg(privmsg_one)
    original_user = list(cache.keys())[0]
    privmsg_two = priv_msg(
        handle_able_kwargs=dict(message='hello', who='new_name'), tags_kwargs=dict(display_name='NEW_NAME', user_id='1')
    )
    cache.update_from_privmsg(privmsg_two)
    assert len(cache) == 1
    new_user = list(cache.keys())[0]
    assert original_user != new_user
    assert cache[new_user] == cache[original_user]  # The lookup should still work
    assert cache[new_user] == [privmsg_two, privmsg_one]
