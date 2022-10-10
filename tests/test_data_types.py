# -*- coding: utf-8 -*-
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from green_eggs import data_types as dt
from tests.utils.data_types import code_353, join_part, priv_msg

raw_data = json.loads((Path(__file__).resolve().parent / 'utils' / 'raw_data.json').read_text())

# Top-level types from IRC


def default_json_dump(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')


def data_type_from_data(raw: str) -> dt.HandleAble:
    result: Optional[dt.HandleAble] = None
    for handle_type, pattern in dt.patterns.items():
        found = pattern.match(raw)
        if found is not None:
            result = handle_type.from_match_dict(**found.groupdict(), raw=raw, default_timestamp=None)
            break
    assert result is not None
    return result


def base_asserts(data, handle_type):
    assert len(data)
    assert all(isinstance(handle_able, handle_type) for handle_able in data)
    assert all(
        handle_able == handle_able.from_match_dict(**handle_able.as_original_match_dict()) for handle_able in data
    )
    assert all(json.dumps(handle_able.model_data(), default=default_json_dump) for handle_able in data)


def test_clearchat():
    data = list(map(data_type_from_data, raw_data['clear chat']))
    base_asserts(data, dt.ClearChat)


def test_clearmsg():
    data = list(map(data_type_from_data, raw_data['clear message']))
    base_asserts(data, dt.ClearMsg)


def test_code353():
    data = list(map(data_type_from_data, raw_data['code 353']))
    base_asserts(data, dt.Code353)


def test_code366():
    data = list(map(data_type_from_data, raw_data['code 366']))
    base_asserts(data, dt.Code366)


def test_hosttarget():
    data = list(map(data_type_from_data, raw_data['host target']))
    base_asserts(data, dt.HostTarget)


def test_joinpart():
    data = list(map(data_type_from_data, raw_data['join part']))
    base_asserts(data, dt.JoinPart)


def test_notice():
    data = list(map(data_type_from_data, raw_data['notice']))
    base_asserts(data, dt.Notice)


def test_privmsg():
    data = list(map(data_type_from_data, raw_data['message']))
    base_asserts(data, dt.PrivMsg)


def test_roomstate():
    data = list(map(data_type_from_data, raw_data['room state']))
    base_asserts(data, dt.RoomState)


def test_usernotice():
    data = list(map(data_type_from_data, raw_data['user notice']))
    base_asserts(data, dt.UserNotice)


def test_userstate():
    data = list(map(data_type_from_data, raw_data['user state']))
    base_asserts(data, dt.UserState)


def test_whisper():
    data = list(map(data_type_from_data, raw_data['whisper']))
    base_asserts(data, dt.Whisper)


# Functions and properties


def test_badges_badge_order_empty():
    badges = dt.Badges.from_raw_data('')
    assert badges.badge_order == []


def test_badges_badge_order_gets_set_properties():
    badges = dt.Badges.from_raw_data('moderator/1,subscriber/12,bits/50000')
    assert badges.badge_order == ['moderator', 'subscriber', 'bits']
    for attr in badges.badge_order:
        assert getattr(badges, attr) is not None


def test_joinpart_is_join():
    joinpart = join_part(is_join=True)
    assert joinpart.action == 'JOIN'
    assert joinpart.is_join

    joinpart = join_part(is_join=False)
    assert joinpart.action == 'PART'
    assert not joinpart.is_join


def test_privmsg_action_ban():
    privmsg = priv_msg(handle_able_kwargs=dict(who='bad_user'))
    assert privmsg.action_ban() == '/ban bad_user'
    assert privmsg.action_ban('Because') == '/ban bad_user Because'


def test_privmsg_action_delete():
    privmsg = priv_msg(tags_kwargs=dict(id='1234'))
    assert privmsg.action_delete() == '/delete 1234'


def test_privmsg_action_timeout():
    privmsg = priv_msg(handle_able_kwargs=dict(who='bad_user'))
    assert privmsg.action_timeout() == '/timeout bad_user 60'
    assert privmsg.action_timeout(1) == '/timeout bad_user 1'
    assert privmsg.action_timeout(reason='Because') == '/timeout bad_user 60 Because'
    assert privmsg.action_timeout(5, 'Whatever') == '/timeout bad_user 5 Whatever'


def test_privmsg_is_from_user():
    privmsg = priv_msg(handle_able_kwargs=dict(who='it_me'), tags_kwargs=dict(display_name='卄モㄥㄥ口山口尺ㄥ刀'))
    assert privmsg.is_from_user('it_me')
    assert privmsg.is_from_user('IT_ME')
    assert privmsg.is_from_user('卄モㄥㄥ口山口尺ㄥ刀')
    assert not privmsg.is_from_user('@it_me')


def test_privmsg_is_sender_broadcaster():
    assert priv_msg(tags_kwargs=dict(badges_kwargs=dict(broadcaster='1'))).is_sender_broadcaster
    assert not priv_msg(tags_kwargs=dict(badges_kwargs=dict(moderator='1'))).is_sender_broadcaster


def test_privmsg_is_sender_moderator():
    assert priv_msg(tags_kwargs=dict(mod=True)).is_sender_moderator
    assert not priv_msg(tags_kwargs=dict(mod=False)).is_sender_moderator
    assert priv_msg(tags_kwargs=dict(badges_kwargs=dict(moderator='1'))).is_sender_moderator
    assert priv_msg(tags_kwargs=dict(badges_kwargs=dict(broadcaster='1'))).is_sender_moderator
    assert not priv_msg(tags_kwargs=dict(badges_kwargs=dict(subscriber='1'))).is_sender_moderator


def test_privmsg_is_sender_subscribed():
    assert priv_msg(tags_kwargs=dict(badges_kwargs=dict(subscriber='1'))).is_sender_subscribed
    assert priv_msg(tags_kwargs=dict(badge_info_kwargs=dict(subscriber='1'))).is_sender_subscribed
    assert not priv_msg(tags_kwargs=dict(badges_kwargs=dict(moderator='1'))).is_sender_subscribed


def test_privmsg_is_sender_vip():
    assert priv_msg(tags_kwargs=dict(badges_kwargs=dict(vip='1'))).is_sender_vip
    assert not priv_msg(tags_kwargs=dict(badges_kwargs=dict(moderator='1'))).is_sender_vip


def test_privmsg_words():
    assert priv_msg(handle_able_kwargs=dict(message='')).words == []
    assert priv_msg(handle_able_kwargs=dict(message='One Two Three')).words == ['One', 'Two', 'Three']
    assert priv_msg(handle_able_kwargs=dict(message='One  Two')).words == ['One', 'Two']
    assert priv_msg(handle_able_kwargs=dict(message=' One-Two Three/\tFour')).words == ['One-Two', 'Three/', 'Four']


# Basic helpers


def test_normalized_user_from_code353():
    assert dt.NormalizedUser.from_code353(code_353('user1', 'user2', 'user3')) == [
        dt.NormalizedUser(username='user1'),
        dt.NormalizedUser(username='user2'),
        dt.NormalizedUser(username='user3'),
    ]


def test_normalized_user_from_privmsg():
    assert dt.NormalizedUser.from_privmsg(
        priv_msg(handle_able_kwargs=dict(who='user1'), tags_kwargs=dict(display_name='User1', user_id='123'))
    ) == dt.NormalizedUser(user_id='123', username='user1', display_name='User1')


# Complete collection of all users to compare.
# Compare all possible product pairs (including a=b and b=a) on the following conditions:
# Do not compare if the same field has a secondary value in both users.
# Do not compare if any field has a secondary value in one user and an empty value in the other.
# The key is coded as such:
# Position x_y_z: x is user_id, y is username, z is display_name
# Value: 'e' is empty, 'a' is primary, 'b' is secondary
users_to_compare: Dict[str, dt.NormalizedUser] = dict(
    e_e_e=dt.NormalizedUser(user_id='', username='', display_name=''),
    e_e_a=dt.NormalizedUser(user_id='', username='', display_name='User1'),
    e_e_b=dt.NormalizedUser(user_id='', username='', display_name='User2'),
    e_a_e=dt.NormalizedUser(user_id='', username='user1', display_name=''),
    e_a_a=dt.NormalizedUser(user_id='', username='user1', display_name='User1'),
    e_a_b=dt.NormalizedUser(user_id='', username='user1', display_name='User2'),
    e_b_e=dt.NormalizedUser(user_id='', username='user2', display_name=''),
    e_b_a=dt.NormalizedUser(user_id='', username='user2', display_name='User1'),
    e_b_b=dt.NormalizedUser(user_id='', username='user2', display_name='User2'),
    a_e_e=dt.NormalizedUser(user_id='123', username='', display_name=''),
    a_e_a=dt.NormalizedUser(user_id='123', username='', display_name='User1'),
    a_e_b=dt.NormalizedUser(user_id='123', username='', display_name='User2'),
    a_a_e=dt.NormalizedUser(user_id='123', username='user1', display_name=''),
    a_a_a=dt.NormalizedUser(user_id='123', username='user1', display_name='User1'),
    a_a_b=dt.NormalizedUser(user_id='123', username='user1', display_name='User2'),
    a_b_e=dt.NormalizedUser(user_id='123', username='user2', display_name=''),
    a_b_a=dt.NormalizedUser(user_id='123', username='user2', display_name='User1'),
    a_b_b=dt.NormalizedUser(user_id='123', username='user2', display_name='User2'),
    b_e_e=dt.NormalizedUser(user_id='456', username='', display_name=''),
    b_e_a=dt.NormalizedUser(user_id='456', username='', display_name='User1'),
    b_e_b=dt.NormalizedUser(user_id='456', username='', display_name='User2'),
    b_a_e=dt.NormalizedUser(user_id='456', username='user1', display_name=''),
    b_a_a=dt.NormalizedUser(user_id='456', username='user1', display_name='User1'),
    b_a_b=dt.NormalizedUser(user_id='456', username='user1', display_name='User2'),
    b_b_e=dt.NormalizedUser(user_id='456', username='user2', display_name=''),
    b_b_a=dt.NormalizedUser(user_id='456', username='user2', display_name='User1'),
    b_b_b=dt.NormalizedUser(user_id='456', username='user2', display_name='User2'),
)
# Comparisons with group overlaps are prioritized in order of user_id, username, display_name.
equal_users: List[Tuple[str, str]] = [
    ('e_e_e', 'e_e_e'),
    ('e_e_a', 'e_e_a'),
    ('e_a_e', 'e_a_e'),
    ('e_a_a', 'e_a_a'),
    ('a_e_e', 'a_e_e'),
    ('a_e_a', 'a_e_a'),
    ('a_a_e', 'a_a_e'),
    ('a_a_a', 'a_a_a'),
]
same_user_id: List[Tuple[str, str]] = [
    ('a_e_e', 'a_e_a'),
    ('a_e_a', 'a_e_e'),
    ('a_e_a', 'a_e_b'),
    ('a_e_b', 'a_e_a'),
    ('a_e_e', 'a_a_e'),
    ('a_e_e', 'a_a_a'),
    ('a_e_a', 'a_a_e'),
    ('a_e_a', 'a_a_a'),
    ('a_e_a', 'a_a_b'),
    ('a_e_b', 'a_a_a'),
    ('a_a_e', 'a_e_e'),
    ('a_a_e', 'a_e_a'),
    ('a_a_a', 'a_e_e'),
    ('a_a_a', 'a_e_a'),
    ('a_a_a', 'a_e_b'),
    ('a_a_b', 'a_e_a'),
    ('a_a_e', 'a_a_a'),
    ('a_a_a', 'a_a_e'),
    ('a_a_a', 'a_a_b'),
    ('a_a_b', 'a_a_a'),
    ('a_a_e', 'a_b_e'),
    ('a_a_e', 'a_b_a'),
    ('a_a_a', 'a_b_e'),
    ('a_a_a', 'a_b_a'),
    ('a_a_a', 'a_b_b'),
    ('a_a_b', 'a_b_a'),
    ('a_b_e', 'a_a_e'),
    ('a_b_e', 'a_a_a'),
    ('a_b_a', 'a_a_e'),
    ('a_b_a', 'a_a_a'),
    ('a_b_a', 'a_a_b'),
    ('a_b_b', 'a_a_a'),
]
different_user_id: List[Tuple[str, str]] = [
    ('a_e_e', 'b_e_e'),
    ('a_e_e', 'b_e_a'),
    ('a_e_a', 'b_e_e'),
    ('a_e_a', 'b_e_a'),
    ('a_e_a', 'b_e_b'),
    ('a_e_b', 'b_e_a'),
    ('a_e_e', 'b_a_e'),
    ('a_e_e', 'b_a_a'),
    ('a_e_a', 'b_a_e'),
    ('a_e_a', 'b_a_a'),
    ('a_e_a', 'b_a_b'),
    ('a_e_b', 'b_a_a'),
    ('a_a_e', 'b_e_e'),
    ('a_a_e', 'b_e_a'),
    ('a_a_a', 'b_e_e'),
    ('a_a_a', 'b_e_a'),
    ('a_a_a', 'b_e_b'),
    ('a_a_b', 'b_e_a'),
    ('a_a_e', 'b_a_e'),
    ('a_a_e', 'b_a_a'),
    ('a_a_a', 'b_a_e'),
    ('a_a_a', 'b_a_a'),
    ('a_a_a', 'b_a_b'),
    ('a_a_b', 'b_a_a'),
    ('a_a_e', 'b_b_e'),
    ('a_a_e', 'b_b_a'),
    ('a_a_a', 'b_b_e'),
    ('a_a_a', 'b_b_a'),
    ('a_a_a', 'b_b_b'),
    ('a_a_b', 'b_b_a'),
    ('a_b_e', 'b_a_e'),
    ('a_b_e', 'b_a_a'),
    ('a_b_a', 'b_a_e'),
    ('a_b_a', 'b_a_a'),
    ('a_b_a', 'b_a_b'),
    ('a_b_b', 'b_a_a'),
    ('b_e_e', 'a_e_e'),
    ('b_e_e', 'a_e_a'),
    ('b_e_a', 'a_e_e'),
    ('b_e_a', 'a_e_a'),
    ('b_e_a', 'a_e_b'),
    ('b_e_b', 'a_e_a'),
    ('b_e_e', 'a_a_e'),
    ('b_e_e', 'a_a_a'),
    ('b_e_a', 'a_a_e'),
    ('b_e_a', 'a_a_a'),
    ('b_e_a', 'a_a_b'),
    ('b_e_b', 'a_a_a'),
    ('b_a_e', 'a_e_e'),
    ('b_a_e', 'a_e_a'),
    ('b_a_a', 'a_e_e'),
    ('b_a_a', 'a_e_a'),
    ('b_a_a', 'a_e_b'),
    ('b_a_b', 'a_e_a'),
    ('b_a_e', 'a_a_e'),
    ('b_a_e', 'a_a_a'),
    ('b_a_a', 'a_a_e'),
    ('b_a_a', 'a_a_a'),
    ('b_a_a', 'a_a_b'),
    ('b_a_b', 'a_a_a'),
    ('b_a_e', 'a_b_e'),
    ('b_a_e', 'a_b_a'),
    ('b_a_a', 'a_b_e'),
    ('b_a_a', 'a_b_a'),
    ('b_a_a', 'a_b_b'),
    ('b_a_b', 'a_b_a'),
    ('b_b_e', 'a_a_e'),
    ('b_b_e', 'a_a_a'),
    ('b_b_a', 'a_a_e'),
    ('b_b_a', 'a_a_a'),
    ('b_b_a', 'a_a_b'),
    ('b_b_b', 'a_a_a'),
]
same_username: List[Tuple[str, str]] = [
    ('e_a_e', 'e_a_a'),
    ('e_a_a', 'e_a_e'),
    ('e_a_a', 'e_a_b'),
    ('e_a_b', 'e_a_a'),
    ('e_a_e', 'a_a_e'),
    ('e_a_e', 'a_a_a'),
    ('e_a_a', 'a_a_e'),
    ('e_a_a', 'a_a_a'),
    ('e_a_a', 'a_a_b'),
    ('e_a_b', 'a_a_a'),
    ('a_a_e', 'e_a_e'),
    ('a_a_e', 'e_a_a'),
    ('a_a_a', 'e_a_e'),
    ('a_a_a', 'e_a_a'),
    ('a_a_a', 'e_a_b'),
    ('a_a_b', 'e_a_a'),
]
different_username: List[Tuple[str, str]] = [
    ('e_a_e', 'e_b_e'),
    ('e_a_e', 'e_b_a'),
    ('e_a_a', 'e_b_e'),
    ('e_a_a', 'e_b_a'),
    ('e_a_a', 'e_b_b'),
    ('e_a_b', 'e_b_a'),
    ('e_b_e', 'e_a_e'),
    ('e_b_e', 'e_a_a'),
    ('e_b_a', 'e_a_e'),
    ('e_b_a', 'e_a_a'),
    ('e_b_a', 'e_a_b'),
    ('e_b_b', 'e_a_a'),
    ('e_a_e', 'a_b_e'),
    ('e_a_e', 'a_b_a'),
    ('e_a_a', 'a_b_e'),
    ('e_a_a', 'a_b_a'),
    ('e_a_a', 'a_b_b'),
    ('e_a_b', 'a_b_a'),
    ('e_b_e', 'a_a_e'),
    ('e_b_e', 'a_a_a'),
    ('e_b_a', 'a_a_e'),
    ('e_b_a', 'a_a_a'),
    ('e_b_a', 'a_a_b'),
    ('e_b_b', 'a_a_a'),
    ('a_a_e', 'e_b_e'),
    ('a_a_e', 'e_b_a'),
    ('a_a_a', 'e_b_e'),
    ('a_a_a', 'e_b_a'),
    ('a_a_a', 'e_b_b'),
    ('a_a_b', 'e_b_a'),
    ('a_b_e', 'e_a_e'),
    ('a_b_e', 'e_a_a'),
    ('a_b_a', 'e_a_e'),
    ('a_b_a', 'e_a_a'),
    ('a_b_a', 'e_a_b'),
    ('a_b_b', 'e_a_a'),
]
same_display_name: List[Tuple[str, str]] = [
    ('e_e_a', 'e_a_a'),
    ('e_a_a', 'e_e_a'),
    ('e_e_a', 'a_e_a'),
    ('e_e_a', 'a_a_a'),
    ('e_a_a', 'a_e_a'),
    ('a_e_a', 'e_e_a'),
    ('a_e_a', 'e_a_a'),
    ('a_a_a', 'e_e_a'),
]
different_display_name: List[Tuple[str, str]] = [
    ('e_e_a', 'e_e_b'),
    ('e_e_b', 'e_e_a'),
    ('e_e_a', 'e_a_b'),
    ('e_e_b', 'e_a_a'),
    ('e_a_a', 'e_e_b'),
    ('e_a_b', 'e_e_a'),
    ('e_e_a', 'a_e_b'),
    ('e_e_b', 'a_e_a'),
    ('e_e_a', 'a_a_b'),
    ('e_e_b', 'a_a_a'),
    ('e_a_a', 'a_e_b'),
    ('e_a_b', 'a_e_a'),
    ('a_e_a', 'e_e_b'),
    ('a_e_b', 'e_e_a'),
    ('a_e_a', 'e_a_b'),
    ('a_e_b', 'e_a_a'),
    ('a_a_a', 'e_e_b'),
    ('a_a_b', 'e_e_a'),
]
all_fields_at_least_one_empty: List[Tuple[str, str]] = [
    ('e_e_e', 'e_e_a'),
    ('e_e_a', 'e_e_e'),
    ('e_e_e', 'e_a_e'),
    ('e_e_e', 'e_a_a'),
    ('e_e_a', 'e_a_e'),
    ('e_a_e', 'e_e_e'),
    ('e_a_e', 'e_e_a'),
    ('e_a_a', 'e_e_e'),
    ('e_e_e', 'a_e_e'),
    ('e_e_e', 'a_e_a'),
    ('e_e_a', 'a_e_e'),
    ('e_e_e', 'a_a_e'),
    ('e_e_e', 'a_a_a'),
    ('e_e_a', 'a_a_e'),
    ('e_a_e', 'a_e_e'),
    ('e_a_e', 'a_e_a'),
    ('e_a_a', 'a_e_e'),
    ('a_e_e', 'e_e_e'),
    ('a_e_e', 'e_e_a'),
    ('a_e_a', 'e_e_e'),
    ('a_e_e', 'e_a_e'),
    ('a_e_e', 'e_a_a'),
    ('a_e_a', 'e_a_e'),
    ('a_a_e', 'e_e_e'),
    ('a_a_e', 'e_e_a'),
    ('a_a_a', 'e_e_e'),
]


def test_normalized_user_is_same_user_equal_true():
    # Compare identical users
    for key1, key2 in equal_users:
        assert users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_is_same_user_same_user_id_true():
    # Compare all users with user_id='123'
    for key1, key2 in same_user_id:
        assert users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_is_same_user_different_user_id_false():
    # Compare all users with a different user_id but both populated
    for key1, key2 in different_user_id:
        assert not users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_is_same_user_same_username_true():
    # Compare all users with username='user1' that weren't compared above
    # All user_id fields are empty in at least one user
    for key1, key2 in same_username:
        assert key1[0] == 'e' or key2[0] == 'e'
        assert users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_is_same_user_different_username_false():
    # Compare all users with a different username but both populated that weren't compared above
    # All user_id fields are empty in at least one user
    for key1, key2 in different_username:
        assert key1[0] == 'e' or key2[0] == 'e'
        assert not users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_is_same_user_same_display_name_true():
    # Compare all users with display_name='User1' that weren't compared above
    # All user_id and username fields are empty in at least one user
    for key1, key2 in same_display_name:
        assert (key1[0] == 'e' or key2[0] == 'e') and (key1[2] == 'e' or key2[2] == 'e')
        assert users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_is_same_user_different_display_name_false():
    # Compare all users with a different display_name but both populated that weren't compared above
    # All user_id and username fields are empty in at least one user
    for key1, key2 in different_display_name:
        assert (key1[0] == 'e' or key2[0] == 'e') and (key1[2] == 'e' or key2[2] == 'e')
        assert not users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_is_same_user_one_field_value_empty_other_value_filled_false():
    # Compare all remaining user pairings
    # As it turns out, for all users:
    # One or more fields will have an empty value in one user and a filled value in the other user
    # All other fields will be empty
    for key1, key2 in all_fields_at_least_one_empty:
        assert (
            (key1[0] == 'e' or key2[0] == 'e')
            and (key1[2] == 'e' or key2[2] == 'e')
            and (key1[4] == 'e' or key2[4] == 'e')
        )
        assert not users_to_compare[key1].is_same_user(users_to_compare[key2])


def test_normalized_user_match_to_other_none_if_different_user():
    # For all the false comparisons above, match_to_other should return None
    for key1, key2 in different_user_id + different_username + different_display_name + all_fields_at_least_one_empty:
        assert users_to_compare[key1].match_to_other(users_to_compare[key2]) is None


def test_normalized_user_match_to_other_more_recent_or_filled_value_if_same_user():
    # For all the true comparisons above, match_to_other should return a user with the most up-to-date info
    def get_expected_key(self_key, other_key):
        indexes = (0, 2, 4)
        # Assume other to start
        replacement = {i: other_key[i] for i in indexes}
        for i in indexes:
            if other_key[i] == 'e':
                # Default to self if empty
                replacement[i] = self_key[i]
        return '_'.join(replacement[i] for i in indexes)

    for key1, key2 in equal_users + same_user_id + same_username + same_display_name:
        expected_key = get_expected_key(key1, key2)
        assert users_to_compare[key1].match_to_other(users_to_compare[key2]) == users_to_compare[expected_key]
