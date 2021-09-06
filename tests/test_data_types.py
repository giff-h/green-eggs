# -*- coding: utf-8 -*-
import datetime
import json
from pathlib import Path
from typing import Optional

from green_eggs.data_types import (
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

raw_data = json.loads((Path(__file__).resolve().parent / 'utils' / 'raw_data.json').read_text())


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


def test_clear_chat():
    data = list(map(data_type_from_data, raw_data['clear chat']))
    assert all(isinstance(dt, ClearChat) for dt in data)
    base_asserts(data)


def test_code_353():
    data = list(map(data_type_from_data, raw_data['code 353']))
    assert all(isinstance(dt, Code353) for dt in data)
    base_asserts(data)


def test_code_366():
    data = list(map(data_type_from_data, raw_data['code 366']))
    assert all(isinstance(dt, Code366) for dt in data)
    base_asserts(data)


def test_host_target():
    data = list(map(data_type_from_data, raw_data['host target']))
    assert all(isinstance(dt, HostTarget) for dt in data)
    base_asserts(data)


def test_join_part():
    data = list(map(data_type_from_data, raw_data['join part']))
    assert all(isinstance(dt, JoinPart) for dt in data)
    base_asserts(data)


def test_notice():
    data = list(map(data_type_from_data, raw_data['notice']))
    assert all(isinstance(dt, Notice) for dt in data)
    base_asserts(data)


def test_message():
    data = list(map(data_type_from_data, raw_data['message']))
    assert all(isinstance(dt, PrivMsg) for dt in data)
    base_asserts(data)


def test_room_state():
    data = list(map(data_type_from_data, raw_data['room state']))
    assert all(isinstance(dt, RoomState) for dt in data)
    base_asserts(data)


def test_user_notice():
    data = list(map(data_type_from_data, raw_data['user notice']))
    assert all(isinstance(dt, UserNotice) for dt in data)
    base_asserts(data)


def test_user_state():
    data = list(map(data_type_from_data, raw_data['user state']))
    assert all(isinstance(dt, UserState) for dt in data)
    base_asserts(data)
