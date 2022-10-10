# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, fields
import datetime
import keyword
import re
from typing import Any, Callable, ClassVar, Dict, Generator, List, Optional, Pattern, Tuple, Type

from green_eggs import constants as const

_camel_kebab_to_snake_pattern: Pattern[str] = re.compile(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|-+')
_unescape_lookup: Dict[str, str] = {
    '\\': '\\',
    ':': ';',
    's': ' ',
    'r': '\r',
    'n': '\n',
}


def _clean_for_attribute(inp: str) -> str:
    """
    Cleans a potentially unsafe string for attribute assignment.

    Input can be camel case, kebab case, or hybrid, and will be converted to lower snake case.
    Anything beginning with a number 0-9 will be prefixed with 'num_'

    :param str inp: The potentially unsafe string to clean
    :return: A string that is safe for attribute assignment
    :rtype: str
    """
    snake_case = _camel_kebab_to_snake_pattern.sub('_', inp).lower()
    keyword_safe = f'{snake_case}_' if keyword.iskeyword(snake_case) else snake_case
    numeric_safe = f'num_{keyword_safe}' if keyword_safe[0].isdecimal() else keyword_safe

    return numeric_safe


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


def _bool_of_int_of(inp: str) -> bool:
    return bool(int(inp))


# Tags: Abstract


@dataclass(frozen=True)
class BaseTags:
    deprecated_fields: ClassVar[List[str]] = [
        'subscriber',
        'turbo',
        'user_type',
    ]
    pair_list_splitter: ClassVar[str] = ';'
    key_value_splitter: ClassVar[str] = '='

    deprecated: Dict[str, str]
    unhandled: Dict[str, str]
    raw: str = field(compare=False)

    @classmethod
    def from_raw_data(cls, data: str):
        tag: str
        value: str
        to_prepare: Dict[str, str] = dict()
        for tag_pair in data.split(cls.pair_list_splitter):
            if tag_pair:
                tag, value = tag_pair.split(cls.key_value_splitter, 1)
                to_prepare[_clean_for_attribute(tag)] = value

        return cls(raw=data, **cls.prepare_data(**to_prepare))

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        deprecated = {f_name: kwargs.pop(f_name) for f_name in cls.deprecated_fields if f_name in kwargs}
        unhandled = {f_name: kwargs.pop(f_name) for f_name in set(kwargs.keys()) - set(f.name for f in fields(cls))}

        return dict(deprecated=deprecated, unhandled=unhandled, **kwargs)

    def model_data(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass(frozen=True)
class BaseBadges(BaseTags):
    deprecated_fields: ClassVar[List[str]] = []
    pair_list_splitter: ClassVar[str] = ','
    key_value_splitter: ClassVar[str] = '/'
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]] = []

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            **{
                attr: converter(kwargs.pop(attr))
                for converter, attrs in cls.converter_mapping
                for attr in attrs
                if attr in kwargs
            },
            **super().prepare_data(**kwargs),
        )

    @property
    def badge_order(self) -> List[str]:
        return [
            _clean_for_attribute(tag_pair.split(self.key_value_splitter, 1)[0])
            for tag_pair in self.raw.split(self.pair_list_splitter)
            if tag_pair
        ]


@dataclass(frozen=True)
class TimestampedBaseTags(BaseTags):
    tmi_sent_ts: datetime.datetime

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        kwargs['tmi_sent_ts'] = datetime.datetime.utcfromtimestamp(int(kwargs['tmi_sent_ts']) / 1000)

        return super().prepare_data(**kwargs)


@dataclass(frozen=True)
class Badges(BaseBadges):
    # Populated from TwitchApiDirect.get_global_chat_badges
    # `sorted(_clean_for_attribute(badge['set_id']) for badge in results['data'])`
    admin: Optional[str] = None
    ambassador: Optional[str] = None
    anomaly_2_1: Optional[str] = None
    anomaly_warzone_earth_1: Optional[str] = None
    anonymous_cheerer: Optional[str] = None
    artist_badge: Optional[str] = None
    axiom_verge_1: Optional[str] = None
    battlechefbrigade_1: Optional[str] = None
    battlechefbrigade_2: Optional[str] = None
    battlechefbrigade_3: Optional[str] = None
    battlerite_1: Optional[str] = None
    bits: Optional[str] = None
    bits_charity: Optional[str] = None
    bits_leader: Optional[str] = None
    brawlhalla_1: Optional[str] = None
    broadcaster: Optional[str] = None
    broken_age_1: Optional[str] = None
    bubsy_the_woolies_1: Optional[str] = None
    clip_champ: Optional[str] = None
    cuphead_1: Optional[str] = None
    darkest_dungeon_1: Optional[str] = None
    deceit_1: Optional[str] = None
    devil_may_cry_hd_1: Optional[str] = None
    devil_may_cry_hd_2: Optional[str] = None
    devil_may_cry_hd_3: Optional[str] = None
    devil_may_cry_hd_4: Optional[str] = None
    devilian_1: Optional[str] = None
    duelyst_1: Optional[str] = None
    duelyst_2: Optional[str] = None
    duelyst_3: Optional[str] = None
    duelyst_4: Optional[str] = None
    duelyst_5: Optional[str] = None
    duelyst_6: Optional[str] = None
    duelyst_7: Optional[str] = None
    enter_the_gungeon_1: Optional[str] = None
    eso_1: Optional[str] = None
    extension: Optional[str] = None
    firewatch_1: Optional[str] = None
    founder: Optional[str] = None
    frozen_cortext_1: Optional[str] = None
    frozen_synapse_1: Optional[str] = None
    getting_over_it_1: Optional[str] = None
    getting_over_it_2: Optional[str] = None
    glhf_pledge: Optional[str] = None
    glitchcon2020: Optional[str] = None
    global_mod: Optional[str] = None
    h1z1_1: Optional[str] = None
    heavy_bullets_1: Optional[str] = None
    hello_neighbor_1: Optional[str] = None
    hype_train: Optional[str] = None
    innerspace_1: Optional[str] = None
    innerspace_2: Optional[str] = None
    jackbox_party_pack_1: Optional[str] = None
    kingdom_new_lands_1: Optional[str] = None
    moderator: Optional[str] = None
    moments: Optional[str] = None
    num_1979_revolution_1: Optional[str] = None
    num_60_seconds_1: Optional[str] = None
    num_60_seconds_2: Optional[str] = None
    num_60_seconds_3: Optional[str] = None
    okhlos_1: Optional[str] = None
    overwatch_league_insider_1: Optional[str] = None
    overwatch_league_insider_2018b: Optional[str] = None
    overwatch_league_insider_2019a: Optional[str] = None
    overwatch_league_insider_2019b: Optional[str] = None
    partner: Optional[str] = None
    power_rangers: Optional[str] = None
    predictions: Optional[str] = None
    premium: Optional[str] = None
    psychonauts_1: Optional[str] = None
    raiden_v_directors_cut_1: Optional[str] = None
    rift_1: Optional[str] = None
    samusoffer_beta: Optional[str] = None
    staff: Optional[str] = None
    starbound_1: Optional[str] = None
    strafe_1: Optional[str] = None
    sub_gift_leader: Optional[str] = None
    sub_gifter: Optional[str] = None
    subscriber: Optional[str] = None
    superhot_1: Optional[str] = None
    the_surge_1: Optional[str] = None
    the_surge_2: Optional[str] = None
    the_surge_3: Optional[str] = None
    this_war_of_mine_1: Optional[str] = None
    titan_souls_1: Optional[str] = None
    treasure_adventure_world_1: Optional[str] = None
    turbo: Optional[str] = None
    twitchbot: Optional[str] = None
    twitchcon2017: Optional[str] = None
    twitchcon2018: Optional[str] = None
    twitchcon_amsterdam2020: Optional[str] = None
    twitchcon_eu2019: Optional[str] = None
    twitchcon_na2019: Optional[str] = None
    twitchcon_na2020: Optional[str] = None
    tyranny_1: Optional[str] = None
    user_anniversary: Optional[str] = None
    vga_champ_2017: Optional[str] = None
    vip: Optional[str] = None
    warcraft: Optional[str] = None


@dataclass(frozen=True)
class UserBaseTags(BaseTags):
    badges: Badges
    color: str
    display_name: str

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            badges=Badges.from_raw_data(kwargs.pop('badges')),
            display_name=_irc_v3_unescape(kwargs.pop('display_name')),
            **super().prepare_data(**kwargs),
        )

    def model_data(self) -> Dict[str, Any]:
        data = super().model_data()

        data['badges'] = badges = dict()
        for f in fields(self.badges):
            value = getattr(self.badges, f.name)
            if value is not None:
                badges[f.name] = value

        return data


@dataclass(frozen=True)
class BadgeInfo(BaseBadges):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]] = [
        (_irc_v3_unescape, ['predictions']),
    ]

    founder: Optional[str] = None
    subscriber: Optional[str] = None
    predictions: Optional[str] = None


@dataclass(frozen=True)
class UserChatBaseTags(UserBaseTags):
    badge_info: BadgeInfo

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            badge_info=BadgeInfo.from_raw_data(kwargs.pop('badge_info')),
            **super().prepare_data(**kwargs),
        )

    def model_data(self) -> Dict[str, Any]:
        data = super().model_data()

        data['badge_info'] = badge_info = dict()
        for f in fields(self.badge_info):
            value = getattr(self.badge_info, f.name)
            if value is not None:
                badge_info[f.name] = value

        return data


@dataclass(frozen=True)
class UserEmoteSetsBaseTags(UserChatBaseTags):
    emote_sets: str

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(
            # emote_sets=list(map(int, kwargs.pop('emote_sets').split(','))),  # FIXME needs work
            **super().prepare_data(**kwargs),
        )


@dataclass(frozen=True)
class UserIsModBaseTags(UserChatBaseTags):
    mod: bool

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(mod=bool(int(kwargs.pop('mod'))), **super().prepare_data(**kwargs))


@dataclass(frozen=True)
class UserMessageBaseTags(UserBaseTags):
    emotes: str
    user_id: str

    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]:
        return dict(**super().prepare_data(**kwargs))


@dataclass(frozen=True)
class UserChatMessageBaseTags(TimestampedBaseTags, UserIsModBaseTags, UserMessageBaseTags):
    id: str
    room_id: str


@dataclass(frozen=True)
class UserSentNoticeBaseTags(BaseTags):
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
    prior_gifter_id: Optional[str] = None
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

    def model_data(self) -> Dict[str, Any]:
        data = super().model_data()

        data['msg_params'] = msg_params = dict()
        for f in fields(self.msg_params):
            value = getattr(self.msg_params, f.name)
            if value is not None:
                msg_params[f.name] = value

        return data


@dataclass(frozen=True)
class UserStateTags(UserEmoteSetsBaseTags, UserIsModBaseTags):
    pass


@dataclass(frozen=True)
class WhisperTags(UserMessageBaseTags):
    message_id: str
    thread_id: str


# Handle-able: Abstract


@dataclass(frozen=True)
class HandleAble:
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
class FromUser(HandleAble):
    who: str


@dataclass(frozen=True)
class HasMessage(HandleAble):
    message: str

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        kwargs['message'] = _irc_v3_unescape(kwargs['message'])

        return super().from_match_dict(**kwargs)

    @property
    def words(self) -> List[str]:
        """
        Returns the words of the message, split by any amount of empty space.

        :return: List of words
        :rtype: List[str]
        """
        return self.message.split()


@dataclass(frozen=True)
class HasTags(HandleAble):
    tags: BaseTags

    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble:
        tags_type: Type[BaseTags] = next(f.type for f in fields(cls) if f.name == 'tags')

        return super().from_match_dict(tags=tags_type.from_raw_data(kwargs.pop('tags')), **kwargs)


@dataclass(frozen=True)
class InChannel(HandleAble):
    where: str


@dataclass(frozen=True)
class UserInChannel(FromUser, InChannel):
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

    def as_original_match_dict(self) -> Dict[str, Any]:
        data = super().as_original_match_dict()
        is_target_none = data['target'] is None
        if is_target_none:
            data['target'] = '-'
            del data['number_of_viewers']
        else:
            if data['number_of_viewers'] is None:
                data['number_of_viewers'] = '-'
        return data


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

    def action_ban(self, reason: str = '') -> str:
        """
        Returns a message to send to a channel to ban the sender of this message.

        :param str reason: The optional reason for banning this user
        :rtype: str
        """
        reason = reason.strip()
        return f'/ban {self.who} {reason}' if reason else f'/ban {self.who}'

    def action_delete(self) -> str:
        """
        Returns a message to send to a channel to delete this message.

        :rtype: str
        """
        return f'/delete {self.tags.id}'

    def action_timeout(self, seconds: int = 60, reason: str = '') -> str:
        """
        Returns a message to send to a channel to time out the sender of this message.

        Timeout duration defaults to one minute.

        :param int seconds: The duration of the timeout
        :param str reason: The optional reason for timing out this user
        :rtype: str
        """
        reason = reason.strip()
        return f'/timeout {self.who} {seconds} {reason}' if reason else f'/timeout {self.who} {seconds}'

    def is_from_user(self, user: str) -> bool:
        """
        Returns whether this message was sent by the given user.

        Checks display name and login case-insensitive.

        :param user: The display or login name of the user
        :return: True if the user sent the message
        :rtype: bool
        """
        user = user.lower()
        return self.who == user or self.tags.display_name.lower() == user

    @property
    def is_sender_broadcaster(self) -> bool:
        """
        Returns whether the sender is the broadcaster in the channel this message was sent.

        :return: True if the message has a broadcaster badge
        :rtype: bool
        """
        return self.tags.badges.broadcaster is not None

    @property
    def is_sender_moderator(self) -> bool:
        """
        Returns whether the sender is a moderator in the channel this message was sent.

        The broadcaster counts as a mod.

        :return: True if the message has a moderator badge or is the broadcaster
        :rtype: bool
        """
        return self.tags.mod or self.tags.badges.moderator is not None or self.is_sender_broadcaster

    @property
    def is_sender_subscribed(self) -> bool:
        """
        Returns whether the sender is indicated as subscribed in the channel this message was sent.

        :return: True if the message has a subscriber badge
        :rtype: bool
        """
        return self.tags.badges.subscriber is not None or self.tags.badge_info.subscriber is not None

    @property
    def is_sender_vip(self) -> bool:
        """
        Returns whether the sender is a VIP in the channel this message was sent.

        :return: True if the message has a VIP badge
        :rtype: bool
        """
        return self.tags.badges.vip is not None


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


# Basic helpers


@dataclass(frozen=True)
class StampedData:
    data: str
    stamp: datetime.datetime


@dataclass(frozen=True)
class NormalizedUser:
    user_id: str = ''
    username: str = ''
    display_name: str = ''

    @classmethod
    def from_code353(cls, code353: Code353) -> List['NormalizedUser']:
        return [cls(username=user) for user in code353.users]

    @classmethod
    def from_joinpart(cls, joinpart: JoinPart) -> 'NormalizedUser':
        return cls(username=joinpart.who)

    @classmethod
    def from_privmsg(cls, privmsg: PrivMsg) -> 'NormalizedUser':
        return cls(user_id=privmsg.tags.user_id, username=privmsg.who, display_name=privmsg.tags.display_name)

    def is_same_user(self, other: 'NormalizedUser') -> bool:
        if self.user_id:
            if self.user_id == other.user_id:
                return True
            if other.user_id:
                return False

        if self.username:
            if self.username == other.username:
                return True
            if other.username:
                return False

        if self.display_name:
            return self.display_name == other.display_name

        # To get here, all fields have an empty value in either self or other, if both users
        # are fully empty just assume they're the same so there's no duplication of empty objects
        return self == other

    def match_to_other(self, other: 'NormalizedUser') -> Optional['NormalizedUser']:
        """
        Compares this object to the given object.

        If they are deemed to be the same user, returns an object with the most up-to-date information.

        If they are deemed to not be the same user, returns None.
        """
        if not self.is_same_user(other):
            return None

        # For all fields:
        # If either value is empty, the other one will suffice. If both are empty, the result will also be empty.
        # If both values differ, the other user is presumed to be a newer value.
        # If both values are the same, the priority doesn't matter.
        return NormalizedUser(
            user_id=other.user_id or self.user_id,
            username=other.username or self.username,
            display_name=other.display_name or self.display_name,
        )


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

pattern_mapping: Dict[Pattern[str], Type[HandleAble]] = {
    const.PRIVMSG_PATTERN: PrivMsg,
    const.JOIN_PART_PATTERN: JoinPart,
    const.CLEARCHAT_PATTERN: ClearChat,
    const.USERNOTICE_PATTERN: UserNotice,
    const.ROOMSTATE_PATTERN: RoomState,
    const.USERSTATE_PATTERN: UserState,
    const.CLEARMSG_PATTERN: ClearMsg,
    const.NOTICE_PATTERN: Notice,
    const.HOSTTARGET_PATTERN: HostTarget,
    const.CODE_353_PATTERN: Code353,
    const.CODE_366_PATTERN: Code366,
    const.WHISPER_PATTERN: Whisper,
}
