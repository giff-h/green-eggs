# -*- coding: utf-8 -*-
import copy
import datetime
from typing import Any, Dict, Optional

from green_eggs import data_types as dt

_default_base_tags_kwargs = dict(deprecated=dict(), unhandled=dict(), raw='')


def clear_chat(
    *, handle_able_kwargs: Optional[Dict[str, Any]] = None, tags_kwargs: Optional[Dict[str, Any]] = None
) -> dt.ClearChat:
    if tags_kwargs:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **tags_kwargs,
        }
    else:
        tags_kwargs = copy.deepcopy(_default_base_tags_kwargs)
    tags = dt.ClearChatTags(**tags_kwargs)

    default_handle_able_kwargs = dict(default_timestamp=datetime.datetime.utcnow(), raw='', tags=tags, where='', who='')
    if handle_able_kwargs:
        handle_able_kwargs = {
            **default_handle_able_kwargs,
            **handle_able_kwargs,
        }
    else:
        handle_able_kwargs = default_handle_able_kwargs
    return dt.ClearChat(**handle_able_kwargs)


def code_353(*users: str, **kwargs) -> dt.Code353:
    default_kwargs = dict(default_timestamp=datetime.datetime.utcnow(), raw='', where='', who='')
    default_kwargs.update(kwargs)
    return dt.Code353(**default_kwargs, users=list(users))  # type: ignore[arg-type]


def join_part(is_join=True, **kwargs) -> dt.JoinPart:
    default_kwargs = dict(default_timestamp=datetime.datetime.utcnow(), raw='', where='', who='')
    default_kwargs.update(kwargs)
    default_kwargs['action'] = 'JOIN' if is_join else 'PART'
    return dt.JoinPart(**default_kwargs)  # type: ignore[arg-type]


def priv_msg(
    *, handle_able_kwargs: Optional[Dict[str, Any]] = None, tags_kwargs: Optional[Dict[str, Any]] = None
) -> dt.PrivMsg:
    default_tags_kwargs = dict(
        badge_info_kwargs=dict(),
        badges_kwargs=dict(),
        color='',
        display_name='',
        emotes='',
        id='',
        mod=False,
        room_id='',
        tmi_sent_ts=datetime.datetime.utcnow(),
        user_id='1',
    )
    if tags_kwargs:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
            **tags_kwargs,
        }
    else:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
        }
    badges_kwargs = {
        **copy.deepcopy(_default_base_tags_kwargs),
        **tags_kwargs.pop('badges_kwargs'),
    }
    tags_kwargs['badges'] = dt.Badges(**badges_kwargs)  # type: ignore[arg-type]
    badge_info_kwargs = {
        **copy.deepcopy(_default_base_tags_kwargs),
        **tags_kwargs.pop('badge_info_kwargs'),
    }
    tags_kwargs['badge_info'] = dt.BadgeInfo(**badge_info_kwargs)  # type: ignore[arg-type]
    tags = dt.PrivMsgTags(**tags_kwargs)

    default_handle_able_kwargs = dict(
        default_timestamp=datetime.datetime.utcnow(),
        message='',
        raw='',
        tags=tags,
        where='',
        who='',
    )
    if handle_able_kwargs:
        handle_able_kwargs = {
            **default_handle_able_kwargs,
            **handle_able_kwargs,
        }
    else:
        handle_able_kwargs = default_handle_able_kwargs
    return dt.PrivMsg(**handle_able_kwargs)


def room_state(
    *, handle_able_kwargs: Optional[Dict[str, Any]] = None, tags_kwargs: Optional[Dict[str, Any]] = None
) -> dt.RoomState:
    default_tags_kwargs: Dict[str, Any] = dict(
        emote_only=None,
        followers_only=None,
        r9k=None,
        rituals=None,
        room_id='1',
        slow=None,
        subs_only=None,
    )
    if tags_kwargs:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
            **tags_kwargs,
        }
    else:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
        }
    tags = dt.RoomStateTags(**tags_kwargs)

    default_handle_able_kwargs = dict(default_timestamp=datetime.datetime.utcnow(), raw='', tags=tags, where='')
    if handle_able_kwargs:
        handle_able_kwargs = {
            **default_handle_able_kwargs,
            **handle_able_kwargs,
        }
    else:
        handle_able_kwargs = default_handle_able_kwargs
    return dt.RoomState(**handle_able_kwargs)


def user_notice(
    *, handle_able_kwargs: Optional[Dict[str, Any]] = None, tags_kwargs: Optional[Dict[str, Any]] = None
) -> dt.UserNotice:
    default_tags_kwargs = dict(
        badge_info_kwargs=dict(),
        badges_kwargs=dict(),
        color='',
        display_name='',
        emotes='',
        flags='',
        id='',
        login='',
        mod=False,
        msg_id='',
        msg_params_kwargs=dict(),
        room_id='',
        system_msg='',
        tmi_sent_ts=datetime.datetime.utcnow(),
        user_id='',
    )
    if tags_kwargs:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
            **tags_kwargs,
        }
    else:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
        }
    badges_kwargs = {
        **copy.deepcopy(_default_base_tags_kwargs),
        **tags_kwargs.pop('badges_kwargs'),
    }
    tags_kwargs['badges'] = dt.Badges(**badges_kwargs)  # type: ignore[arg-type]
    badge_info_kwargs = {
        **copy.deepcopy(_default_base_tags_kwargs),
        **tags_kwargs.pop('badge_info_kwargs'),
    }
    tags_kwargs['badge_info'] = dt.BadgeInfo(**badge_info_kwargs)  # type: ignore[arg-type]
    msg_params_kwargs = {
        **copy.deepcopy(_default_base_tags_kwargs),
        **tags_kwargs.pop('msg_params_kwargs'),
    }
    tags_kwargs['msg_params'] = dt.UserNoticeMessageParams(**msg_params_kwargs)  # type: ignore[arg-type]
    tags = dt.UserNoticeTags(**tags_kwargs)

    default_handle_able_kwargs = dict(
        default_timestamp=datetime.datetime.utcnow(), message=None, raw='', tags=tags, where=''
    )
    if handle_able_kwargs:
        handle_able_kwargs = {
            **default_handle_able_kwargs,
            **handle_able_kwargs,
        }
    else:
        handle_able_kwargs = default_handle_able_kwargs
    return dt.UserNotice(**handle_able_kwargs)


def user_state(
    *, handle_able_kwargs: Optional[Dict[str, Any]] = None, tags_kwargs: Optional[Dict[str, Any]] = None
) -> dt.UserState:
    default_tags_kwargs = dict(
        badge_info_kwargs=dict(),
        badges_kwargs=dict(),
        color='',
        display_name='',
        emote_sets='',
        mod=False,
    )
    if tags_kwargs:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
            **tags_kwargs,
        }
    else:
        tags_kwargs = {
            **copy.deepcopy(_default_base_tags_kwargs),
            **default_tags_kwargs,
        }
    badges_kwargs = {
        **copy.deepcopy(_default_base_tags_kwargs),
        **tags_kwargs.pop('badges_kwargs'),
    }
    tags_kwargs['badges'] = dt.Badges(**badges_kwargs)  # type: ignore[arg-type]
    badge_info_kwargs = {
        **copy.deepcopy(_default_base_tags_kwargs),
        **tags_kwargs.pop('badge_info_kwargs'),
    }
    tags_kwargs['badge_info'] = dt.BadgeInfo(**badge_info_kwargs)  # type: ignore[arg-type]
    tags = dt.UserStateTags(**tags_kwargs)

    default_handle_able_kwargs = dict(default_timestamp=datetime.datetime.utcnow(), raw='', tags=tags, where='')
    if handle_able_kwargs:
        handle_able_kwargs = {
            **default_handle_able_kwargs,
            **handle_able_kwargs,
        }
    else:
        handle_able_kwargs = default_handle_able_kwargs
    return dt.UserState(**handle_able_kwargs)
