# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, field, fields
import datetime
from functools import partial, reduce
import keyword
import re
from typing import Any, Callable, ClassVar, Dict, Generator, List, Optional, Pattern, Tuple, Type

from green_eggs import constants as const

_Badges = Dict[str, str]
_bool_of_int_of: 'partial[bool]' = partial(reduce, lambda x, y: y(x), (int, bool))
_camel_kebab_to_snake_pattern: Pattern[str] = re.compile(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|-+')
_unescape_lookup: Dict[str, str] = {
    '\\': '\\',
    ':': ';',
    's': ' ',
    'r': '\r',
    'n': '\n',
}


def _keyword_safe_camel_or_kebab_to_snake(inp: str) -> str:
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


def _irc_v3_unescape(raw: str) -> str:
    return ''.join(_irc_v3_unescape_iter(raw))


def _parse_badge(badge_data: str) -> Tuple[str, str]:
    badge_type, badge_value = badge_data.split('/')
    return badge_type.replace('-', '_'), badge_value


def _parse_badges(badges_data: str) -> _Badges:
    return dict(map(_parse_badge, filter(None, badges_data.split(','))))


# Tags: Abstract


@dataclass(frozen=True)
class BaseTags(abc.ABC):
    deprecated_fields: ClassVar[List[str]] = [
        'subscriber',
        'turbo',
        'user_type',
    ]

    deprecated: Dict[str, str]
    unhandled: Dict[str, str]
    raw: str = field(compare=False)

    @classmethod
    def from_raw_data(cls, data: str):
        tag: str
        value: str
        to_prepare: Dict[str, str] = dict()
        for tag_pair in data.split(';'):
            tag, value = tag_pair.split('=', 1)
            to_prepare[_keyword_safe_camel_or_kebab_to_snake(tag)] = value

        return cls(raw=data, **cls.prepare_data(**to_prepare))

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        deprecated = {f_name: kwargs.pop(f_name) for f_name in cls.deprecated_fields if f_name in kwargs}
        unhandled = {f_name: kwargs.pop(f_name) for f_name in set(kwargs.keys()) - set(f.name for f in fields(cls))}

        return dict(deprecated=deprecated, unhandled=unhandled, **kwargs)

    def model_data(self) -> Dict[str, Any]:
        data = {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if not isinstance(getattr(self, f.name), UserNoticeMessageParams)
        }
        if isinstance(self, UserNoticeTags):
            data['msg_params'] = msg_params = dict()
            for f in fields(self.msg_params):
                val = getattr(self.msg_params, f.name)
                if val is not None:
                    msg_params[f.name] = val

        return data


@dataclass(frozen=True)
class TimestampedBaseTags(BaseTags, abc.ABC):
    tmi_sent_ts: datetime.datetime

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        kwargs['tmi_sent_ts'] = datetime.datetime.utcfromtimestamp(int(kwargs['tmi_sent_ts']) / 1000)

        return super().prepare_data(**kwargs)


@dataclass(frozen=True)
class UserBaseTags(BaseTags, abc.ABC):
    badges: _Badges
    color: str
    display_name: str

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            badges=_parse_badges(kwargs.pop('badges')),
            display_name=_irc_v3_unescape(kwargs.pop('display_name')),
            **super().prepare_data(**kwargs),
        )


@dataclass(frozen=True)
class UserChatBaseTags(UserBaseTags, abc.ABC):
    badge_info: _Badges

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            badge_info=_parse_badges(kwargs.pop('badge_info')),
            **super().prepare_data(**kwargs),
        )


@dataclass(frozen=True)
class UserEmoteSetsBaseTags(UserChatBaseTags, abc.ABC):
    emote_sets: List[int]

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            emote_sets=list(map(int, kwargs.pop('emote_sets').split(','))),
            **super().prepare_data(**kwargs),
        )


@dataclass(frozen=True)
class UserIsModBaseTags(UserChatBaseTags, abc.ABC):
    mod: bool

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(mod=bool(int(kwargs.pop('mod'))), **super().prepare_data(**kwargs))


@dataclass(frozen=True)
class UserMessageBaseTags(UserBaseTags, abc.ABC):
    emotes: str
    user_id: str

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(**super().prepare_data(**kwargs))


@dataclass(frozen=True)
class UserChatMessageBaseTags(TimestampedBaseTags, UserIsModBaseTags, UserMessageBaseTags, abc.ABC):
    id: str
    room_id: str


@dataclass(frozen=True)
class UserSentNoticeBaseTags(BaseTags, abc.ABC):
    login: str  # the user who sent the notice


# Tags: Final


@dataclass(frozen=True)
class ClearChatTags(BaseTags):
    ban_duration: Optional[int] = None
    room_id: Optional[str] = None
    target_msg_id: Optional[str] = None
    target_user_id: Optional[str] = None
    tmi_sent_ts: Optional[datetime.datetime] = None

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        if 'ban_duration' in kwargs:
            kwargs['ban_duration'] = int(kwargs['ban_duration'])

        if 'tmi_sent_ts' in kwargs and kwargs['tmi_sent_ts'] is not None:
            kwargs['tmi_sent_ts'] = datetime.datetime.utcfromtimestamp(int(kwargs['tmi_sent_ts']) / 1000)

        return super().prepare_data(**kwargs)


@dataclass(frozen=True)
class ClearMsgTags(TimestampedBaseTags, UserSentNoticeBaseTags):
    deprecated_fields: ClassVar[List[str]] = BaseTags.deprecated_fields + [
        'room_id',
    ]

    target_msg_id: str


@dataclass(frozen=True)
class GlobalUserStateTags(UserEmoteSetsBaseTags):
    pass


@dataclass(frozen=True)
class NoticeTags(BaseTags):
    msg_id: str


@dataclass(frozen=True)
class PrivMsgTags(UserChatMessageBaseTags):
    # not sure what this is or is meant to represent, but twitch said so
    bits_re: ClassVar[Pattern[str]] = re.compile(r'(^|\s)(?P<emote_name>\D+)\d+(\s|$)', flags=re.IGNORECASE)

    bits: Optional[str] = None
    client_nonce: Optional[str] = None
    crowd_chant_parent_msg_id: Optional[str] = None
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

        for f_name in ('emote_only', 'first_msg'):
            if f_name in kwargs and kwargs[f_name] is not None:
                kwargs[f_name] = _bool_of_int_of(kwargs[f_name])

        for f_name in ('reply_parent_display_name', 'reply_parent_msg_body'):
            if f_name in kwargs and kwargs[f_name] is not None:
                kwargs[f_name] = _irc_v3_unescape(kwargs[f_name])

        return dict(
            **super().prepare_data(**kwargs),
        )


@dataclass(frozen=True)
class RoomStateTags(BaseTags):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]] = [
        (int, ['followers_only', 'slow']),
        (_bool_of_int_of, ['emote_only', 'r9k', 'rituals', 'subs_only']),
    ]

    emote_only: Optional[bool]
    followers_only: Optional[int]
    r9k: Optional[bool]
    rituals: Optional[bool]
    room_id: str
    slow: Optional[int]
    subs_only: Optional[bool]

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            **{
                attr: converter(kwargs.pop(attr)) if attr in kwargs else None
                for converter, attrs in cls.converter_mapping
                for attr in attrs
            },
            **super().prepare_data(**kwargs),
        )


@dataclass(frozen=True)
class UserNoticeMessageParams(BaseTags):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]] = [
        (
            int,
            [
                'cumulative_months',
                'gift_month_being_redeemed',
                'gift_months',
                'mass_gift_count',
                'months',
                'multimonth_duration',
                'multimonth_tenure',
                'promo_gift_total',
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
            _irc_v3_unescape,
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
    gift_theme: Optional[str] = None
    gifter_id: Optional[str] = None
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
    prior_gifter_user_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    promo_gift_total: Optional[int] = None
    promo_name: Optional[str] = None
    recipient_display_name: Optional[str] = None
    recipient_id: Optional[str] = None
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


@dataclass(frozen=True)
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
        # Note that this is not an exact recreation of the raw tag values
        # but is just meant to show the set that was given
        msg_params_raw = ';'.join(f'{k}={v}' for k, v in msg_params.items())

        return dict(
            msg_params=UserNoticeMessageParams(
                raw=msg_params_raw, **UserNoticeMessageParams.prepare_data(**msg_params)
            ),
            system_msg=_irc_v3_unescape(kwargs.pop('system_msg')),
            **super().prepare_data(**kwargs),
        )


@dataclass(frozen=True)
class UserStateTags(UserEmoteSetsBaseTags, UserIsModBaseTags):
    pass


@dataclass(frozen=True)
class WhisperTags(UserMessageBaseTags):
    message_id: str
    thread_id: str


# Handle-able: Abstract


@dataclass(frozen=True)
class HandleAble(abc.ABC):
    # `default_timestamp` is not from twitch, but is set by the IRC client when the data was received
    default_timestamp: datetime.datetime = field(compare=False)
    raw: str = field(compare=False)

    @classmethod
    def from_match_dict(cls, **kwargs) -> 'HandleAble':
        return cls(**kwargs)

    def as_original_match_dict(self) -> Dict[str, Any]:
        data = {
            f.name: getattr(self, f.name) for f in fields(self) if f.name != 'tags' or not isinstance(self, HasTags)
        }
        if isinstance(self, HasTags):
            data['tags'] = self.tags.raw

        return data

    def model_data(self) -> Dict[str, Any]:
        data = {
            f.name: getattr(self, f.name) for f in fields(self) if f.name != 'tags' or not isinstance(self, HasTags)
        }
        if isinstance(self, HasTags):
            data.update(self.tags.model_data())

        return data


@dataclass(frozen=True)
class FromUser(HandleAble, abc.ABC):
    who: str


@dataclass(frozen=True)
class HasMessage(HandleAble, abc.ABC):
    message: str

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        kwargs['message'] = _irc_v3_unescape(kwargs['message'])

        return super().from_match_dict(**kwargs)


@dataclass(frozen=True)
class HasTags(HandleAble, abc.ABC):
    tags: BaseTags

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        tags_type: Type[BaseTags] = next(f.type for f in fields(cls) if f.name == 'tags')

        return super().from_match_dict(tags=tags_type.from_raw_data(kwargs.pop('tags')), **kwargs)


@dataclass(frozen=True)
class InChannel(HandleAble, abc.ABC):
    where: str


@dataclass(frozen=True)
class UserInChannel(FromUser, InChannel, abc.ABC):
    pass


# Handle-able: Final


@dataclass(frozen=True)
class Code353(UserInChannel):
    users: List[str]

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        return super().from_match_dict(users=kwargs.pop('users').split(' '), **kwargs)

    def as_original_match_dict(self) -> Dict[str, Any]:
        data = super().as_original_match_dict()
        data['users'] = ' '.join(data['users'])
        return data


@dataclass(frozen=True)
class Code366(UserInChannel):
    pass


@dataclass(frozen=True)
class ClearChat(HasTags, UserInChannel):
    tags: ClearChatTags


@dataclass(frozen=True)
class ClearMsg(HasMessage, HasTags, InChannel):
    tags: ClearMsgTags


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class JoinPart(UserInChannel):
    action: str

    @property
    def is_join(self) -> bool:
        """
        Is this a JOIN rather than a PART.

        :return: True if the action is `'JOIN'`
        :rtype: bool
        """
        return self.action == 'JOIN'


@dataclass(frozen=True)
class Notice(HasMessage, HasTags, InChannel):
    tags: NoticeTags


@dataclass(frozen=True)
class PrivMsg(HasMessage, HasTags, UserInChannel):
    tags: PrivMsgTags

    def is_from_user(self, user: str) -> bool:
        """
        Is this message sent by the given user.

        Checks display name and login case insensitive.

        :param user: The display or login name of the user
        :return: True if the user sent the message
        :rtype: bool
        """
        user = user.lower()
        return self.who == user or self.tags.display_name.lower() == user

    @property
    def is_sender_subscribed(self) -> bool:
        """
        Is the sender indicated as subscribed in the channel this message was sent.

        :return: True if the message has a subscriber badge
        :rtype: bool
        """
        return 'subscriber' in self.tags.badges

    @property
    def words(self) -> List[str]:
        """
        The words of the message, split by any amount of empty space.

        :return: List of words
        :rtype: List[str]
        """
        return self.message.split()


@dataclass(frozen=True)
class RoomState(HasTags, InChannel):
    tags: RoomStateTags


@dataclass(frozen=True)
class UserNotice(HasTags, InChannel):
    tags: UserNoticeTags
    message: Optional[str]

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        if 'message' in kwargs and kwargs['message'] is not None:
            kwargs['message'] = _irc_v3_unescape(kwargs['message'])

        return super().from_match_dict(**kwargs)


@dataclass(frozen=True)
class UserState(HasTags, InChannel):
    tags: UserStateTags


@dataclass(frozen=True)
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
