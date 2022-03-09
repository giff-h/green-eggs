# -*- coding: utf-8 -*-
import datetime
import json
from pathlib import Path
from typing import Optional

from green_eggs import data_types as dt
from tests.utils.data_types import join_part, priv_msg

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
            result = handle_type.from_match_dict(
                **found.groupdict(), raw=raw, default_timestamp=datetime.datetime.utcnow()
            )
            break
    assert result is not None
    return result


def base_asserts(handleable_list, handle_type):
    assert len(handleable_list)
    for handleable in handleable_list:
        assert isinstance(handleable, handle_type)
        assert handleable == handleable.from_match_dict(**handleable.as_original_match_dict())
        model_data = handleable.model_data()
        for value in model_data.values():
            assert isinstance(value, (bool, int, str, list, dict, datetime.datetime))
        assert handleable == handleable.from_model_data(**model_data)


def test_clearchat():
    handleable_list = list(map(data_type_from_data, raw_data['clear chat']))
    base_asserts(handleable_list, dt.ClearChat)


def test_clearmsg():
    handleable_list = list(map(data_type_from_data, raw_data['clear message']))
    base_asserts(handleable_list, dt.ClearMsg)


def test_code353():
    handleable_list = list(map(data_type_from_data, raw_data['code 353']))
    base_asserts(handleable_list, dt.Code353)


def test_code366():
    handleable_list = list(map(data_type_from_data, raw_data['code 366']))
    base_asserts(handleable_list, dt.Code366)


def test_hosttarget():
    handleable_list = list(map(data_type_from_data, raw_data['host target']))
    base_asserts(handleable_list, dt.HostTarget)


def test_joinpart():
    handleable_list = list(map(data_type_from_data, raw_data['join part']))
    base_asserts(handleable_list, dt.JoinPart)


def test_notice():
    handleable_list = list(map(data_type_from_data, raw_data['notice']))
    base_asserts(handleable_list, dt.Notice)


def test_privmsg():
    handleable_list = list(map(data_type_from_data, raw_data['message']))
    base_asserts(handleable_list, dt.PrivMsg)


def test_roomstate():
    handleable_list = list(map(data_type_from_data, raw_data['room state']))
    base_asserts(handleable_list, dt.RoomState)


def test_usernotice():
    handleable_list = list(map(data_type_from_data, raw_data['user notice']))
    base_asserts(handleable_list, dt.UserNotice)


def test_userstate():
    handleable_list = list(map(data_type_from_data, raw_data['user state']))
    base_asserts(handleable_list, dt.UserState)


def test_whisper():
    handleable_list = list(map(data_type_from_data, raw_data['whisper']))
    base_asserts(handleable_list, dt.Whisper)


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
    privmsg = priv_msg(handleable_kwargs=dict(who='bad_user'))
    assert privmsg.action_ban() == '/ban bad_user'
    assert privmsg.action_ban('Because') == '/ban bad_user Because'


def test_privmsg_action_delete():
    privmsg = priv_msg(tags_kwargs=dict(id='1234'))
    assert privmsg.action_delete() == '/delete 1234'


def test_privmsg_action_timeout():
    privmsg = priv_msg(handleable_kwargs=dict(who='bad_user'))
    assert privmsg.action_timeout() == '/timeout bad_user 60'
    assert privmsg.action_timeout(1) == '/timeout bad_user 1'
    assert privmsg.action_timeout(reason='Because') == '/timeout bad_user 60 Because'
    assert privmsg.action_timeout(5, 'Whatever') == '/timeout bad_user 5 Whatever'


def test_privmsg_is_from_user():
    privmsg = priv_msg(handleable_kwargs=dict(who='it_me'), tags_kwargs=dict(display_name='卄モㄥㄥ口山口尺ㄥ刀'))
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
    assert priv_msg(handleable_kwargs=dict(message='')).words == []
    assert priv_msg(handleable_kwargs=dict(message='One Two Three')).words == ['One', 'Two', 'Three']
    assert priv_msg(handleable_kwargs=dict(message='One  Two')).words == ['One', 'Two']
    assert priv_msg(handleable_kwargs=dict(message=' One-Two Three/\tFour')).words == ['One-Two', 'Three/', 'Four']
