# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, fields
import datetime
from functools import partial, reduce
import keyword
import re
from typing import Any, Callable, ClassVar, Dict, Generator, List, Optional, Pattern, Tuple, Type

from green_eggs import constants as const

_Badges = Dict[str, str]
_bool_of_int_of = partial(reduce, lambda x, y: y(x), (int, bool))
_camel_kebab_to_snake_pattern: Pattern[str] = re.compile(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|-+')
_unescape_lookup: Dict[str, str] = {
    '\\': '\\',
    ':': ';',
    's': ' ',
    'r': '\r',
    'n': '\n',
}


def keyword_safe_camel_or_kebab_to_snake(inp: str) -> str:
    out = _camel_kebab_to_snake_pattern.sub('_', inp).lower()
    return f'{out}_' if keyword.iskeyword(out) else out


def _irc_v3_unescape_iter(raw: str) -> Generator[str, None, None]:
    str_iter = iter(raw)
    for c in str_iter:
        if c == '\\':
            try:
                c = next(str_iter)
            except StopIteration:
                yield c
                break
            else:
                yield _unescape_lookup.get(c, f'\\{c}')
        else:
            yield c


def irc_v3_unescape(raw: str) -> str:
    return ''.join(_irc_v3_unescape_iter(raw))


def parse_badge(badge_data: str) -> Tuple[str, str]:
    badge_type, badge_value = badge_data.split('/')
    return badge_type.replace('-', '_'), badge_value


def parse_badges(badges_data: str) -> _Badges:
    return dict(map(parse_badge, filter(None, badges_data.split(','))))


# Tags: Abstract


@dataclass
class BaseTags(abc.ABC):
    deprecated_fields: ClassVar[List[str]] = [
        'subscriber',
        'turbo',
        'user_type',
    ]

    deprecated: Dict[str, str]
    unhandled: Dict[str, str]
    raw: str

    @classmethod
    def from_raw_data(cls, data: str):
        tag: str
        value: str
        to_prepare: Dict[str, str] = dict()
        for tag_pair in data.split(';'):
            tag, value = tag_pair.split('=', 1)
            to_prepare[keyword_safe_camel_or_kebab_to_snake(tag)] = value

        return cls(raw=data, **cls.prepare_data(**to_prepare))

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        deprecated = {field: kwargs.pop(field) for field in cls.deprecated_fields if field in kwargs}
        unhandled = {field: kwargs.pop(field) for field in set(kwargs.keys()) - set(f.name for f in fields(cls))}

        return dict(deprecated=deprecated, unhandled=unhandled, **kwargs)

    def model_data(self) -> Dict[str, Any]:
        data = {f.name: getattr(self, f.name) for f in fields(self) if f.name != 'msg_params'}
        if isinstance(self, UserNoticeTags):
            data['msg_params'] = msg_params = dict()
            for f in fields(self.msg_params):
                val = getattr(self.msg_params, f.name)
                if val is not None:
                    msg_params[f.name] = val

        return data


@dataclass
class TimestampedBaseTags(BaseTags, abc.ABC):
    tmi_sent_ts: datetime.datetime

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        kwargs['tmi_sent_ts'] = datetime.datetime.utcfromtimestamp(int(kwargs['tmi_sent_ts']) / 1000)

        return super().prepare_data(**kwargs)


@dataclass
class UserBaseTags(BaseTags, abc.ABC):
    badges: _Badges
    color: str
    display_name: str

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            badges=parse_badges(kwargs.pop('badges')),
            display_name=irc_v3_unescape(kwargs.pop('display_name')),
            **super().prepare_data(**kwargs),
        )


@dataclass
class UserChatBaseTags(UserBaseTags, abc.ABC):
    badge_info: _Badges

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            badge_info=parse_badges(kwargs.pop('badge_info')),
            **super().prepare_data(**kwargs),
        )


@dataclass
class UserEmoteSetsBaseTags(UserChatBaseTags, abc.ABC):
    emote_sets: List[int]

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            emote_sets=list(map(int, kwargs.pop('emote_sets').split(','))),
            **super().prepare_data(**kwargs),
        )


@dataclass
class UserIsModBaseTags(UserChatBaseTags, abc.ABC):
    mod: bool

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(mod=bool(int(kwargs.pop('mod'))), **super().prepare_data(**kwargs))


@dataclass
class UserMessageBaseTags(UserBaseTags, abc.ABC):
    emotes: str
    user_id: int

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(user_id=int(kwargs.pop('user_id')), **super().prepare_data(**kwargs))


@dataclass
class UserChatMessageBaseTags(TimestampedBaseTags, UserIsModBaseTags, UserMessageBaseTags, abc.ABC):
    id: str
    room_id: str


@dataclass
class UserSentNoticeBaseTags(BaseTags, abc.ABC):
    login: str  # the user who sent the notice


# Tags: Final


@dataclass
class ClearChatTags(BaseTags):
    ban_duration: Optional[int] = None
    room_id: Optional[int] = None
    target_msg_id: Optional[str] = None
    target_user_id: Optional[int] = None
    tmi_sent_ts: Optional[datetime.datetime] = None

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        for field in ('ban_duration', 'room_id', 'target_user_id'):
            if field in kwargs:
                kwargs[field] = int(kwargs[field])

        if 'tmi_sent_ts' in kwargs and kwargs['tmi_sent_ts'] is not None:
            kwargs['tmi_sent_ts'] = datetime.datetime.utcfromtimestamp(int(kwargs['tmi_sent_ts']) / 1000)

        return super().prepare_data(**kwargs)


@dataclass
class ClearMsgTags(TimestampedBaseTags, UserSentNoticeBaseTags):
    deprecated_fields: ClassVar[List[str]] = BaseTags.deprecated_fields + [
        'room_id',
    ]

    target_msg_id: str


@dataclass
class GlobalUserStateTags(UserEmoteSetsBaseTags):
    pass


@dataclass
class NoticeTags(BaseTags):
    msg_id: str


@dataclass
class PrivMsgTags(UserChatMessageBaseTags):
    # not sure what this is or is meant to represent, but twitch said so
    bits_re: ClassVar[Pattern[str]] = re.compile(r'(^|\s)(?P<emote_name>\D+)\d+(\s|$)', flags=re.IGNORECASE)

    bits: Optional[str] = None
    client_nonce: Optional[str] = None
    custom_reward_id: Optional[str] = None
    emote_only: Optional[bool] = None
    first_msg: Optional[bool] = None
    flags: Optional[str] = None
    msg_id: Optional[str] = None
    reply_parent_display_name: Optional[str] = None
    reply_parent_msg_body: Optional[str] = None
    reply_parent_msg_id: Optional[str] = None
    reply_parent_user_id: Optional[str] = None
    reply_parent_user_login: Optional[str] = None
    sent_ts: Optional[int] = None

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        if 'sent_ts' in kwargs:
            kwargs['sent_ts'] = int(kwargs['sent_ts'])

        for field in ('emote_only', 'first_msg'):
            if field in kwargs and kwargs[field] is not None:
                kwargs[field] = _bool_of_int_of(kwargs[field])

        for field in ('reply_parent_display_name', 'reply_parent_msg_body'):
            if field in kwargs and kwargs[field] is not None:
                kwargs[field] = irc_v3_unescape(kwargs[field])

        return dict(
            **super().prepare_data(**kwargs),
        )


@dataclass
class RoomStateTags(BaseTags):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]] = [
        (int, ['followers_only', 'slow']),
        (_bool_of_int_of, ['emote_only', 'r9k', 'rituals', 'subs_only']),
    ]

    emote_only: Optional[bool]
    followers_only: Optional[int]
    r9k: Optional[bool]
    rituals: Optional[bool]
    room_id: int
    slow: Optional[int]
    subs_only: Optional[bool]

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            room_id=int(kwargs.pop('room_id')),
            **{
                attr: converter(kwargs.pop(attr)) if attr in kwargs else None
                for converter, attrs in cls.converter_mapping
                for attr in attrs
            },
            **super().prepare_data(**kwargs),
        )


@dataclass
class UserNoticeMessageParams(BaseTags):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]] = [
        (
            int,
            [
                'cumulative_months',
                'gift_month_being_redeemed',
                'gift_months',
                'gifter_id',
                'mass_gift_count',
                'months',
                'multimonth_duration',
                'multimonth_tenure',
                'prior_gifter_id',
                'promo_gift_total',
                'recipient_id',
                'selected_count',
                'sender_count',
                'streak_months',
                'sub_benefit_end_month',
                'threshold',
                'total_reward_count',
                'trigger_amount',
                'viewer_count',
            ],
        ),
        (
            irc_v3_unescape,
            [
                'display_name',
                'gifter_name',
                'origin_id',
                'prior_gifter_display_name',
                'promo_name',
                'recipient_display_name',
                'sender_name',
                'sub_plan_name',
            ],
        ),
        (_bool_of_int_of, ['should_share_streak']),
        (lambda x: x == 'true', ['anon_gift', 'was_gifted']),
    ]
    deprecated_fields: ClassVar[List[str]] = []
    prefix: ClassVar[str] = 'msg_param_'

    anon_gift: Optional[bool] = None
    cumulative_months: Optional[int] = None
    display_name: Optional[str] = None
    domain: Optional[str] = None
    fun_string: Optional[str] = None
    gift_month_being_redeemed: Optional[int] = None
    gift_months: Optional[int] = None
    gifter_id: Optional[int] = None
    gifter_login: Optional[str] = None
    gifter_name: Optional[str] = None
    login: Optional[str] = None
    mass_gift_count: Optional[int] = None
    months: Optional[int] = None
    multimonth_duration: Optional[int] = None
    multimonth_tenure: Optional[int] = None
    origin_id: Optional[str] = None
    prior_gifter_anonymous: Optional[bool] = None
    prior_gifter_display_name: Optional[str] = None
    prior_gifter_id: Optional[int] = None
    prior_gifter_user_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    promo_gift_total: Optional[int] = None
    promo_name: Optional[str] = None
    recipient_display_name: Optional[str] = None
    recipient_id: Optional[int] = None
    recipient_user_name: Optional[str] = None
    ritual_name: Optional[str] = None
    selected_count: Optional[int] = None
    sender_count: Optional[int] = None
    sender_login: Optional[str] = None
    sender_name: Optional[str] = None
    should_share_streak: Optional[bool] = None
    streak_months: Optional[int] = None
    sub_benefit_end_month: Optional[int] = None
    sub_plan: Optional[str] = None
    sub_plan_name: Optional[str] = None
    threshold: Optional[int] = None
    total_reward_count: Optional[int] = None
    trigger_amount: Optional[int] = None
    trigger_type: Optional[str] = None
    viewer_count: Optional[int] = None
    was_gifted: Optional[bool] = None

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        if 'prior_gifter_anonymous' in kwargs:
            kwargs['prior_gifter_anonymous'] = kwargs['prior_gifter_anonymous'] == 'true'

        return dict(
            **{
                attr: converter(kwargs.pop(attr))
                for converter, attrs in cls.converter_mapping
                for attr in attrs
                if attr in kwargs
            },
            **super().prepare_data(**kwargs),
        )


@dataclass
class UserNoticeTags(UserChatMessageBaseTags, UserSentNoticeBaseTags):
    flags: str
    msg_id: str  # the type of the notice
    system_msg: str

    msg_params: UserNoticeMessageParams

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        prefix_chop = len(UserNoticeMessageParams.prefix)
        msg_params = {
            attr[prefix_chop:]: kwargs.pop(attr)
            for attr in tuple(kwargs.keys())
            if attr.startswith(UserNoticeMessageParams.prefix)
        }
        # Note that this is not an exact recreation of the raw tag values but is just meant to show the set that was given
        msg_params_raw = ';'.join(f'{k}={v}' for k, v in msg_params.items())

        return dict(
            msg_params=UserNoticeMessageParams(
                raw=msg_params_raw, **UserNoticeMessageParams.prepare_data(**msg_params)
            ),
            system_msg=irc_v3_unescape(kwargs.pop('system_msg')),
            **super().prepare_data(**kwargs),
        )


@dataclass
class UserStateTags(UserEmoteSetsBaseTags, UserIsModBaseTags):
    pass


@dataclass
class WhisperTags(UserMessageBaseTags):
    message_id: int
    thread_id: str


# Handle-able: Abstract


@dataclass
class HandleAble(abc.ABC):
    default_timestamp: datetime.datetime
    raw: str

    @classmethod
    def from_match_dict(cls, **kwargs) -> 'HandleAble':
        return cls(**kwargs)

    def model_data(self) -> Dict[str, Any]:
        data = {f.name: getattr(self, f.name) for f in fields(self) if f.name != 'tags'}
        if isinstance(self, HasTags):
            data.update(self.tags.model_data())

        return data


@dataclass
class FromUser(HandleAble, abc.ABC):
    who: str


@dataclass
class HasMessage(HandleAble, abc.ABC):
    message: str

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        kwargs['message'] = irc_v3_unescape(kwargs['message'])

        return super().from_match_dict(**kwargs)


@dataclass
class HasTags(HandleAble, abc.ABC):
    tags: BaseTags

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        tags_type: Type[BaseTags] = next(f.type for f in fields(cls) if f.name == 'tags')

        return super().from_match_dict(tags=tags_type.from_raw_data(kwargs.pop('tags')), **kwargs)


@dataclass
class InChannel(HandleAble, abc.ABC):
    where: str


@dataclass
class UserInChannel(FromUser, InChannel, abc.ABC):
    pass


# Handle-able: Final


@dataclass
class Code353(UserInChannel):
    users: List[str]

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        return super().from_match_dict(users=kwargs.pop('users').split(' '), **kwargs)


@dataclass
class Code366(UserInChannel):
    pass


@dataclass
class ClearChat(HasTags, UserInChannel):
    tags: ClearChatTags


@dataclass
class ClearMsg(HasMessage, HasTags, InChannel):
    tags: ClearMsgTags


@dataclass
class HostTarget(InChannel):
    number_of_viewers: Optional[int]
    target: Optional[str]

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        number_of_viewers = kwargs.pop('number_of_viewers', None)
        if number_of_viewers is not None:
            number_of_viewers = None if number_of_viewers == '-' else int(number_of_viewers)
        if kwargs['target'] == '-':
            kwargs['target'] = None

        return super().from_match_dict(number_of_viewers=number_of_viewers, **kwargs)


@dataclass
class JoinPart(UserInChannel):
    action: str


@dataclass
class Notice(HasMessage, HasTags, InChannel):
    tags: NoticeTags


@dataclass
class PrivMsg(HasMessage, HasTags, UserInChannel):
    tags: PrivMsgTags


@dataclass
class RoomState(HasTags, InChannel):
    tags: RoomStateTags


@dataclass
class UserNotice(HasTags, InChannel):
    tags: UserNoticeTags
    message: Optional[str]

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        if 'message' in kwargs and kwargs['message'] is not None:
            kwargs['message'] = irc_v3_unescape(kwargs['message'])

        return super().from_match_dict(**kwargs)


@dataclass
class UserState(HasTags, InChannel):
    tags: UserStateTags


@dataclass
class Whisper(HasMessage, HasTags, UserInChannel):
    tags: WhisperTags


patterns: Dict[Type[HandleAble], Pattern[str]] = {
    PrivMsg: const.PRIVMSG_PATTERN,
    JoinPart: const.JOIN_PART_PATTERN,
    ClearChat: const.CLEARCHAT_PATTERN,
    UserNotice: const.USERNOTICE_PATTERN,
    RoomState: const.ROOMSTATE_PATTERN,
    UserState: const.USERSTATE_PATTERN,
    ClearMsg: const.CLEARMSG_PATTERN,
    Notice: const.NOTICE_PATTERN,
    HostTarget: const.HOSTTARGET_PATTERN,
    Code353: const.CODE_353_PATTERN,
    Code366: const.CODE_366_PATTERN,
    Whisper: const.WHISPER_PATTERN,
}
