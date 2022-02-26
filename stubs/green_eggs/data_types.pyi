import abc
import datetime
from typing import Any, Callable, ClassVar, Dict, List, Optional, Pattern, Tuple, Type

class BaseTags(abc.ABC):
    deprecated_fields: ClassVar[List[str]]
    pair_list_splitter: ClassVar[str]
    key_value_splitter: ClassVar[str]
    deprecated: Dict[str, str]
    unhandled: Dict[str, str]
    raw: str
    @classmethod
    def from_raw_data(cls, data: str): ...
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def model_data(self) -> Dict[str, Any]: ...
    def __init__(self, deprecated, unhandled, raw) -> None: ...

class BaseBadges(BaseTags, abc.ABC):
    deprecated_fields: ClassVar[List[str]]
    pair_list_splitter: ClassVar[str]
    key_value_splitter: ClassVar[str]
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]]
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    @property
    def badge_order(self) -> List[str]: ...
    def __init__(self, deprecated, unhandled, raw) -> None: ...

class TimestampedBaseTags(BaseTags, abc.ABC):
    tmi_sent_ts: datetime.datetime
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(self, deprecated, unhandled, raw, tmi_sent_ts) -> None: ...

class Badges(BaseBadges):
    admin: Optional[str]
    ambassador: Optional[str]
    anomaly_2_1: Optional[str]
    anomaly_warzone_earth_1: Optional[str]
    anonymous_cheerer: Optional[str]
    artist_badge: Optional[str]
    axiom_verge_1: Optional[str]
    battlechefbrigade_1: Optional[str]
    battlechefbrigade_2: Optional[str]
    battlechefbrigade_3: Optional[str]
    battlerite_1: Optional[str]
    bits: Optional[str]
    bits_charity: Optional[str]
    bits_leader: Optional[str]
    brawlhalla_1: Optional[str]
    broadcaster: Optional[str]
    broken_age_1: Optional[str]
    bubsy_the_woolies_1: Optional[str]
    clip_champ: Optional[str]
    cuphead_1: Optional[str]
    darkest_dungeon_1: Optional[str]
    deceit_1: Optional[str]
    devil_may_cry_hd_1: Optional[str]
    devil_may_cry_hd_2: Optional[str]
    devil_may_cry_hd_3: Optional[str]
    devil_may_cry_hd_4: Optional[str]
    devilian_1: Optional[str]
    duelyst_1: Optional[str]
    duelyst_2: Optional[str]
    duelyst_3: Optional[str]
    duelyst_4: Optional[str]
    duelyst_5: Optional[str]
    duelyst_6: Optional[str]
    duelyst_7: Optional[str]
    enter_the_gungeon_1: Optional[str]
    eso_1: Optional[str]
    extension: Optional[str]
    firewatch_1: Optional[str]
    founder: Optional[str]
    frozen_cortext_1: Optional[str]
    frozen_synapse_1: Optional[str]
    getting_over_it_1: Optional[str]
    getting_over_it_2: Optional[str]
    glhf_pledge: Optional[str]
    glitchcon2020: Optional[str]
    global_mod: Optional[str]
    h1z1_1: Optional[str]
    heavy_bullets_1: Optional[str]
    hello_neighbor_1: Optional[str]
    hype_train: Optional[str]
    innerspace_1: Optional[str]
    innerspace_2: Optional[str]
    jackbox_party_pack_1: Optional[str]
    kingdom_new_lands_1: Optional[str]
    moderator: Optional[str]
    moments: Optional[str]
    num_1979_revolution_1: Optional[str]
    num_60_seconds_1: Optional[str]
    num_60_seconds_2: Optional[str]
    num_60_seconds_3: Optional[str]
    okhlos_1: Optional[str]
    overwatch_league_insider_1: Optional[str]
    overwatch_league_insider_2018b: Optional[str]
    overwatch_league_insider_2019a: Optional[str]
    overwatch_league_insider_2019b: Optional[str]
    partner: Optional[str]
    power_rangers: Optional[str]
    predictions: Optional[str]
    premium: Optional[str]
    psychonauts_1: Optional[str]
    raiden_v_directors_cut_1: Optional[str]
    rift_1: Optional[str]
    samusoffer_beta: Optional[str]
    staff: Optional[str]
    starbound_1: Optional[str]
    strafe_1: Optional[str]
    sub_gift_leader: Optional[str]
    sub_gifter: Optional[str]
    subscriber: Optional[str]
    superhot_1: Optional[str]
    the_surge_1: Optional[str]
    the_surge_2: Optional[str]
    the_surge_3: Optional[str]
    this_war_of_mine_1: Optional[str]
    titan_souls_1: Optional[str]
    treasure_adventure_world_1: Optional[str]
    turbo: Optional[str]
    twitchbot: Optional[str]
    twitchcon2017: Optional[str]
    twitchcon2018: Optional[str]
    twitchcon_amsterdam2020: Optional[str]
    twitchcon_eu2019: Optional[str]
    twitchcon_na2019: Optional[str]
    twitchcon_na2020: Optional[str]
    tyranny_1: Optional[str]
    user_anniversary: Optional[str]
    vga_champ_2017: Optional[str]
    vip: Optional[str]
    warcraft: Optional[str]
    def __init__(
        self,
        deprecated,
        unhandled,
        raw,
        admin,
        ambassador,
        anomaly_2_1,
        anomaly_warzone_earth_1,
        anonymous_cheerer,
        artist_badge,
        axiom_verge_1,
        battlechefbrigade_1,
        battlechefbrigade_2,
        battlechefbrigade_3,
        battlerite_1,
        bits,
        bits_charity,
        bits_leader,
        brawlhalla_1,
        broadcaster,
        broken_age_1,
        bubsy_the_woolies_1,
        clip_champ,
        cuphead_1,
        darkest_dungeon_1,
        deceit_1,
        devil_may_cry_hd_1,
        devil_may_cry_hd_2,
        devil_may_cry_hd_3,
        devil_may_cry_hd_4,
        devilian_1,
        duelyst_1,
        duelyst_2,
        duelyst_3,
        duelyst_4,
        duelyst_5,
        duelyst_6,
        duelyst_7,
        enter_the_gungeon_1,
        eso_1,
        extension,
        firewatch_1,
        founder,
        frozen_cortext_1,
        frozen_synapse_1,
        getting_over_it_1,
        getting_over_it_2,
        glhf_pledge,
        glitchcon2020,
        global_mod,
        h1z1_1,
        heavy_bullets_1,
        hello_neighbor_1,
        hype_train,
        innerspace_1,
        innerspace_2,
        jackbox_party_pack_1,
        kingdom_new_lands_1,
        moderator,
        moments,
        num_1979_revolution_1,
        num_60_seconds_1,
        num_60_seconds_2,
        num_60_seconds_3,
        okhlos_1,
        overwatch_league_insider_1,
        overwatch_league_insider_2018b,
        overwatch_league_insider_2019a,
        overwatch_league_insider_2019b,
        partner,
        power_rangers,
        predictions,
        premium,
        psychonauts_1,
        raiden_v_directors_cut_1,
        rift_1,
        samusoffer_beta,
        staff,
        starbound_1,
        strafe_1,
        sub_gift_leader,
        sub_gifter,
        subscriber,
        superhot_1,
        the_surge_1,
        the_surge_2,
        the_surge_3,
        this_war_of_mine_1,
        titan_souls_1,
        treasure_adventure_world_1,
        turbo,
        twitchbot,
        twitchcon2017,
        twitchcon2018,
        twitchcon_amsterdam2020,
        twitchcon_eu2019,
        twitchcon_na2019,
        twitchcon_na2020,
        tyranny_1,
        user_anniversary,
        vga_champ_2017,
        vip,
        warcraft,
    ) -> None: ...

class UserBaseTags(BaseTags, abc.ABC):
    badges: Badges
    color: str
    display_name: str
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def model_data(self) -> Dict[str, Any]: ...
    def __init__(self, deprecated, unhandled, raw, badges, color, display_name) -> None: ...

class BadgeInfo(BaseBadges):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]]
    founder: Optional[str]
    subscriber: Optional[str]
    predictions: Optional[str]
    def __init__(self, deprecated, unhandled, raw, founder, subscriber, predictions) -> None: ...

class UserChatBaseTags(UserBaseTags, abc.ABC):
    badge_info: BadgeInfo
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def model_data(self) -> Dict[str, Any]: ...
    def __init__(self, deprecated, unhandled, raw, badges, color, display_name, badge_info) -> None: ...

class UserEmoteSetsBaseTags(UserChatBaseTags, abc.ABC):
    emote_sets: str
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(self, deprecated, unhandled, raw, badges, color, display_name, badge_info, emote_sets) -> None: ...

class UserIsModBaseTags(UserChatBaseTags, abc.ABC):
    mod: bool
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(self, deprecated, unhandled, raw, badges, color, display_name, badge_info, mod) -> None: ...

class UserMessageBaseTags(UserBaseTags, abc.ABC):
    emotes: str
    user_id: str
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(self, deprecated, unhandled, raw, badges, color, display_name, emotes, user_id) -> None: ...

class UserChatMessageBaseTags(TimestampedBaseTags, UserIsModBaseTags, UserMessageBaseTags, abc.ABC):
    id: str
    room_id: str
    def __init__(
        self,
        deprecated,
        unhandled,
        raw,
        badges,
        color,
        display_name,
        emotes,
        user_id,
        badge_info,
        mod,
        tmi_sent_ts,
        id,
        room_id,
    ) -> None: ...

class UserSentNoticeBaseTags(BaseTags, abc.ABC):
    login: str
    def __init__(self, deprecated, unhandled, raw, login) -> None: ...

class ClearChatTags(BaseTags):
    ban_duration: Optional[int]
    room_id: Optional[str]
    target_msg_id: Optional[str]
    target_user_id: Optional[str]
    tmi_sent_ts: Optional[datetime.datetime]
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(
        self, deprecated, unhandled, raw, ban_duration, room_id, target_msg_id, target_user_id, tmi_sent_ts
    ) -> None: ...

class ClearMsgTags(TimestampedBaseTags, UserSentNoticeBaseTags):
    deprecated_fields: ClassVar[List[str]]
    target_msg_id: str
    def __init__(self, deprecated, unhandled, raw, login, tmi_sent_ts, target_msg_id) -> None: ...

class GlobalUserStateTags(UserEmoteSetsBaseTags):
    def __init__(self, deprecated, unhandled, raw, badges, color, display_name, badge_info, emote_sets) -> None: ...

class NoticeTags(BaseTags):
    msg_id: str
    def __init__(self, deprecated, unhandled, raw, msg_id) -> None: ...

class PrivMsgTags(UserChatMessageBaseTags):
    bits_re: ClassVar[Pattern[str]]
    bits: Optional[str]
    client_nonce: Optional[str]
    crowd_chant_parent_msg_id: Optional[str]
    custom_reward_id: Optional[str]
    emote_only: Optional[bool]
    first_msg: Optional[bool]
    flags: Optional[str]
    msg_id: Optional[str]
    reply_parent_display_name: Optional[str]
    reply_parent_msg_body: Optional[str]
    reply_parent_msg_id: Optional[str]
    reply_parent_user_id: Optional[str]
    reply_parent_user_login: Optional[str]
    sent_ts: Optional[int]
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(
        self,
        deprecated,
        unhandled,
        raw,
        badges,
        color,
        display_name,
        emotes,
        user_id,
        badge_info,
        mod,
        tmi_sent_ts,
        id,
        room_id,
        bits,
        client_nonce,
        crowd_chant_parent_msg_id,
        custom_reward_id,
        emote_only,
        first_msg,
        flags,
        msg_id,
        reply_parent_display_name,
        reply_parent_msg_body,
        reply_parent_msg_id,
        reply_parent_user_id,
        reply_parent_user_login,
        sent_ts,
    ) -> None: ...

class RoomStateTags(BaseTags):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]]
    emote_only: Optional[bool]
    followers_only: Optional[int]
    r9k: Optional[bool]
    rituals: Optional[bool]
    room_id: str
    slow: Optional[int]
    subs_only: Optional[bool]
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(
        self, deprecated, unhandled, raw, emote_only, followers_only, r9k, rituals, room_id, slow, subs_only
    ) -> None: ...

class UserNoticeMessageParams(BaseTags):
    converter_mapping: ClassVar[List[Tuple[Callable[[str], Any], List[str]]]]
    deprecated_fields: ClassVar[List[str]]
    prefix: ClassVar[str]
    anon_gift: Optional[bool]
    cumulative_months: Optional[int]
    display_name: Optional[str]
    domain: Optional[str]
    fun_string: Optional[str]
    gift_month_being_redeemed: Optional[int]
    gift_months: Optional[int]
    gift_theme: Optional[str]
    gifter_id: Optional[str]
    gifter_login: Optional[str]
    gifter_name: Optional[str]
    login: Optional[str]
    mass_gift_count: Optional[int]
    months: Optional[int]
    multimonth_duration: Optional[int]
    multimonth_tenure: Optional[int]
    origin_id: Optional[str]
    prior_gifter_anonymous: Optional[bool]
    prior_gifter_display_name: Optional[str]
    prior_gifter_id: Optional[str]
    prior_gifter_user_name: Optional[str]
    profile_image_url: Optional[str]
    promo_gift_total: Optional[int]
    promo_name: Optional[str]
    recipient_display_name: Optional[str]
    recipient_id: Optional[str]
    recipient_user_name: Optional[str]
    ritual_name: Optional[str]
    selected_count: Optional[int]
    sender_count: Optional[int]
    sender_login: Optional[str]
    sender_name: Optional[str]
    should_share_streak: Optional[bool]
    streak_months: Optional[int]
    sub_benefit_end_month: Optional[int]
    sub_plan: Optional[str]
    sub_plan_name: Optional[str]
    threshold: Optional[int]
    total_reward_count: Optional[int]
    trigger_amount: Optional[int]
    trigger_type: Optional[str]
    viewer_count: Optional[int]
    was_gifted: Optional[bool]
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def __init__(
        self,
        deprecated,
        unhandled,
        raw,
        anon_gift,
        cumulative_months,
        display_name,
        domain,
        fun_string,
        gift_month_being_redeemed,
        gift_months,
        gift_theme,
        gifter_id,
        gifter_login,
        gifter_name,
        login,
        mass_gift_count,
        months,
        multimonth_duration,
        multimonth_tenure,
        origin_id,
        prior_gifter_anonymous,
        prior_gifter_display_name,
        prior_gifter_id,
        prior_gifter_user_name,
        profile_image_url,
        promo_gift_total,
        promo_name,
        recipient_display_name,
        recipient_id,
        recipient_user_name,
        ritual_name,
        selected_count,
        sender_count,
        sender_login,
        sender_name,
        should_share_streak,
        streak_months,
        sub_benefit_end_month,
        sub_plan,
        sub_plan_name,
        threshold,
        total_reward_count,
        trigger_amount,
        trigger_type,
        viewer_count,
        was_gifted,
    ) -> None: ...

class UserNoticeTags(UserChatMessageBaseTags, UserSentNoticeBaseTags):
    flags: str
    msg_id: str
    system_msg: str
    msg_params: UserNoticeMessageParams
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def model_data(self) -> Dict[str, Any]: ...
    def __init__(
        self,
        deprecated,
        unhandled,
        raw,
        login,
        badges,
        color,
        display_name,
        emotes,
        user_id,
        badge_info,
        mod,
        tmi_sent_ts,
        id,
        room_id,
        flags,
        msg_id,
        system_msg,
        msg_params,
    ) -> None: ...

class UserStateTags(UserEmoteSetsBaseTags, UserIsModBaseTags):
    def __init__(
        self, deprecated, unhandled, raw, badges, color, display_name, badge_info, mod, emote_sets
    ) -> None: ...

class WhisperTags(UserMessageBaseTags):
    message_id: str
    thread_id: str
    def __init__(
        self, deprecated, unhandled, raw, badges, color, display_name, emotes, user_id, message_id, thread_id
    ) -> None: ...

class HandleAble(abc.ABC):
    default_timestamp: datetime.datetime
    raw: str
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    def as_original_match_dict(self) -> Dict[str, Any]: ...
    def model_data(self) -> Dict[str, Any]: ...
    def __init__(self, default_timestamp, raw) -> None: ...

class FromUser(HandleAble, abc.ABC):
    who: str
    def __init__(self, default_timestamp, raw, who) -> None: ...

class HasMessage(HandleAble, abc.ABC):
    message: str
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    @property
    def words(self) -> List[str]: ...
    def __init__(self, default_timestamp, raw, message) -> None: ...

class HasTags(HandleAble, abc.ABC):
    tags: BaseTags
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    def __init__(self, default_timestamp, raw, tags) -> None: ...

class InChannel(HandleAble, abc.ABC):
    where: str
    def __init__(self, default_timestamp, raw, where) -> None: ...

class UserInChannel(FromUser, InChannel, abc.ABC):
    def __init__(self, default_timestamp, raw, where, who) -> None: ...

class Code353(UserInChannel):
    users: List[str]
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    def as_original_match_dict(self) -> Dict[str, Any]: ...
    def __init__(self, default_timestamp, raw, where, who, users) -> None: ...

class Code366(UserInChannel):
    def __init__(self, default_timestamp, raw, where, who) -> None: ...

class ClearChat(HasTags, UserInChannel):
    tags: ClearChatTags
    def __init__(self, default_timestamp, raw, where, who, tags) -> None: ...

class ClearMsg(HasMessage, HasTags, InChannel):
    tags: ClearMsgTags
    def __init__(self, default_timestamp, raw, where, tags, message) -> None: ...

class HostTarget(InChannel):
    number_of_viewers: Optional[int]
    target: Optional[str]
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    def as_original_match_dict(self) -> Dict[str, Any]: ...
    def __init__(self, default_timestamp, raw, where, number_of_viewers, target) -> None: ...

class JoinPart(UserInChannel):
    action: str
    @property
    def is_join(self) -> bool: ...
    def __init__(self, default_timestamp, raw, where, who, action) -> None: ...

class Notice(HasMessage, HasTags, InChannel):
    tags: NoticeTags
    def __init__(self, default_timestamp, raw, where, tags, message) -> None: ...

class PrivMsg(HasMessage, HasTags, UserInChannel):
    tags: PrivMsgTags
    def action_ban(self, reason: str = ...) -> str: ...
    def action_delete(self) -> str: ...
    def action_timeout(self, seconds: int = ..., reason: str = ...) -> str: ...
    def is_from_user(self, user: str) -> bool: ...
    @property
    def is_sender_broadcaster(self) -> bool: ...
    @property
    def is_sender_moderator(self) -> bool: ...
    @property
    def is_sender_subscribed(self) -> bool: ...
    @property
    def is_sender_vip(self) -> bool: ...
    def __init__(self, default_timestamp, raw, where, who, tags, message) -> None: ...

class RoomState(HasTags, InChannel):
    tags: RoomStateTags
    def __init__(self, default_timestamp, raw, where, tags) -> None: ...

class UserNotice(HasTags, InChannel):
    tags: UserNoticeTags
    message: Optional[str]
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    def __init__(self, default_timestamp, raw, where, tags, message) -> None: ...

class UserState(HasTags, InChannel):
    tags: UserStateTags
    def __init__(self, default_timestamp, raw, where, tags) -> None: ...

class Whisper(HasMessage, HasTags, UserInChannel):
    tags: WhisperTags
    def __init__(self, default_timestamp, raw, where, who, tags, message) -> None: ...

patterns: Dict[Type[HandleAble], Pattern[str]]
