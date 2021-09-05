# -*- coding: utf-8 -*-
import datetime
from typing import Any, Dict, Optional

from green_eggs.data_types import PrivMsg, PrivMsgTags


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
        user_id=1,
    )
    if tags_kwargs:
        default_tags_kwargs.update(tags_kwargs)
    tags = PrivMsgTags(**default_tags_kwargs)  # type: ignore[arg-type]

    default_handle_able_kwargs = dict(
        default_timestamp=datetime.datetime.utcnow(), message='', raw='', tags=tags, where='', who=''
    )
    if handle_able_kwargs:
        default_handle_able_kwargs.update(handle_able_kwargs)
    return PrivMsg(**default_handle_able_kwargs)  # type: ignore[arg-type]
