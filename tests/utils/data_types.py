# -*- coding: utf-8 -*-
import datetime
from typing import Any, Dict, Optional

from green_eggs.data_types import Code353, JoinPart, PrivMsg, PrivMsgTags, RoomState, RoomStateTags


def code_353(*users: str, **kwargs) -> Code353:
    default_kwargs = dict(default_timestamp=datetime.datetime.utcnow(), raw='', unhandled=dict(), where='', who='')
    default_kwargs.update(kwargs)
    return Code353(**default_kwargs, users=list(users))  # type: ignore[arg-type]


def join_part(is_join=True, **kwargs) -> JoinPart:
    default_kwargs = dict(default_timestamp=datetime.datetime.utcnow(), raw='', unhandled=dict(), where='', who='')
    default_kwargs.update(kwargs)
    default_kwargs['action'] = 'JOIN' if is_join else 'PART'
    return JoinPart(**default_kwargs)  # type: ignore[arg-type]


def priv_msg(
    *, handle_able_kwargs: Optional[Dict[str, Any]] = None, tags_kwargs: Optional[Dict[str, Any]] = None
) -> PrivMsg:
    default_tags_kwargs = dict(
        badge_info=dict(),
        badges=dict(),
        color='',
        deprecated=dict(),
        display_name='',
        emotes='',
        id='',
        mod=False,
        raw='',
        room_id='',
        tmi_sent_ts=datetime.datetime.utcnow(),
        unhandled=dict(),
        user_id='1',
    )
    if tags_kwargs:
        default_tags_kwargs.update(tags_kwargs)
    tags = PrivMsgTags(**default_tags_kwargs)  # type: ignore[arg-type]

    default_handle_able_kwargs = dict(
        default_timestamp=datetime.datetime.utcnow(),
        message='',
        raw='',
        tags=tags,
        unhandled=dict(),
        where='',
        who='',
    )
    if handle_able_kwargs:
        default_handle_able_kwargs.update(handle_able_kwargs)
    return PrivMsg(**default_handle_able_kwargs)  # type: ignore[arg-type]


def room_state(
    *, handle_able_kwargs: Optional[Dict[str, Any]] = None, tags_kwargs: Optional[Dict[str, Any]] = None
) -> RoomState:
    default_tags_kwargs: Dict[str, Any] = dict(
        deprecated=dict(),
        emote_only=None,
        followers_only=None,
        r9k=None,
        raw='',
        rituals=None,
        room_id='1',
        slow=None,
        subs_only=None,
        unhandled=dict(),
    )
    if tags_kwargs:
        default_tags_kwargs.update(tags_kwargs)
    tags = RoomStateTags(**default_tags_kwargs)  # type: ignore[arg-type]

    default_handle_able_kwargs = dict(
        default_timestamp=datetime.datetime.utcnow(), raw='', tags=tags, unhandled=dict(), where=''
    )
    if handle_able_kwargs:
        default_handle_able_kwargs.update(handle_able_kwargs)
    return RoomState(**default_handle_able_kwargs)  # type: ignore[arg-type]
