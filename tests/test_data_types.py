# -*- coding: utf-8 -*-
import datetime
import json
from pathlib import Path
from typing import Optional

from green_eggs.data_types import (
    Badges,
    ClearChat,
    Code353,
    Code366,
    HandleAble,
    HostTarget,
    JoinPart,
    Notice,
    PrivMsg,
    RoomState,
    UserNotice,
    UserState,
    patterns,
)
from tests.utils.data_types import join_part, priv_msg

raw_data = json.loads((Path(__file__).resolve().parent / 'utils' / 'raw_data.json').read_text())

# Top-level types from IRC


def default_json_dump(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')


def data_type_from_data(raw: str) -> HandleAble:
    result: Optional[HandleAble] = None
    for dt, pattern in patterns.items():
        found = pattern.match(raw)
        if found is not None:
            result = dt.from_match_dict(**found.groupdict(), raw=raw, default_timestamp=None)
            break
    assert result is not None
    return result


def base_asserts(data):
    assert len(data)
    assert all(dt == dt.from_match_dict(**dt.as_original_match_dict()) for dt in data)
    assert all(json.dumps(dt.model_data(), default=default_json_dump) for dt in data)


def test_clearchat():
    data = list(map(data_type_from_data, raw_data['clear chat']))
    assert all(isinstance(dt, ClearChat) for dt in data)
    base_asserts(data)


def test_code353():
    data = list(map(data_type_from_data, raw_data['code 353']))
    assert all(isinstance(dt, Code353) for dt in data)
    base_asserts(data)


def test_code366():
    data = list(map(data_type_from_data, raw_data['code 366']))
    assert all(isinstance(dt, Code366) for dt in data)
    base_asserts(data)


def test_hosttarget():
    data = list(map(data_type_from_data, raw_data['host target']))
    assert all(isinstance(dt, HostTarget) for dt in data)
    base_asserts(data)


def test_joinpart():
    data = list(map(data_type_from_data, raw_data['join part']))
    assert all(isinstance(dt, JoinPart) for dt in data)
    base_asserts(data)


def test_notice():
    data = list(map(data_type_from_data, raw_data['notice']))
    assert all(isinstance(dt, Notice) for dt in data)
    base_asserts(data)


def test_privmsg():
    data = list(map(data_type_from_data, raw_data['message']))
    assert all(isinstance(dt, PrivMsg) for dt in data)
    base_asserts(data)


def test_roomstate():
    data = list(map(data_type_from_data, raw_data['room state']))
    assert all(isinstance(dt, RoomState) for dt in data)
    base_asserts(data)


def test_usernotice():
    data = list(map(data_type_from_data, raw_data['user notice']))
    assert all(isinstance(dt, UserNotice) for dt in data)
    base_asserts(data)


def test_userstate():
    data = list(map(data_type_from_data, raw_data['user state']))
    assert all(isinstance(dt, UserState) for dt in data)
    base_asserts(data)


# Functions and properties


def test_badges_badge_order_empty():
    badges = Badges.from_raw_data('')
    assert badges.badge_order == []


def test_badges_badge_order_gets_set_properties():
    badges = Badges.from_raw_data('moderator/1,subscriber/12,bits/50000')
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
