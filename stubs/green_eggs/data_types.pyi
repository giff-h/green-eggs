import abc
import datetime
from typing import Any, Callable, ClassVar, Dict, List, Optional, Pattern, Tuple, Type

class BaseTags(abc.ABC):
    deprecated_fields: ClassVar[List[str]]
    deprecated: Dict[str, str]
    unhandled: Dict[str, str]
    raw: str
    @classmethod
    def from_raw_data(cls, data: str): ...
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...
    def model_data(self) -> Dict[str, Any]: ...

class TimestampedBaseTags(BaseTags, abc.ABC):
    tmi_sent_ts: datetime.datetime
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class UserBaseTags(BaseTags, abc.ABC):
    badges: _Badges
    color: str
    display_name: str
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class UserChatBaseTags(UserBaseTags, abc.ABC):
    badge_info: _Badges
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class UserEmoteSetsBaseTags(UserChatBaseTags, abc.ABC):
    emote_sets: List[int]
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class UserIsModBaseTags(UserChatBaseTags, abc.ABC):
    mod: bool
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class UserMessageBaseTags(UserBaseTags, abc.ABC):
    emotes: str
    user_id: str
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class UserChatMessageBaseTags(TimestampedBaseTags, UserIsModBaseTags, UserMessageBaseTags, abc.ABC):
    id: str
    room_id: str

class UserSentNoticeBaseTags(BaseTags, abc.ABC):
    login: str

class ClearChatTags(BaseTags):
    ban_duration: Optional[int]
    room_id: Optional[int]
    target_msg_id: Optional[str]
    target_user_id: Optional[int]
    tmi_sent_ts: Optional[datetime.datetime]
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class ClearMsgTags(TimestampedBaseTags, UserSentNoticeBaseTags):
    deprecated_fields: ClassVar[List[str]]
    target_msg_id: str

class GlobalUserStateTags(UserEmoteSetsBaseTags): ...

class NoticeTags(BaseTags):
    msg_id: str

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
    gifter_id: Optional[int]
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
    prior_gifter_id: Optional[int]
    prior_gifter_user_name: Optional[str]
    profile_image_url: Optional[str]
    promo_gift_total: Optional[int]
    promo_name: Optional[str]
    recipient_display_name: Optional[str]
    recipient_id: Optional[int]
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

class UserNoticeTags(UserChatMessageBaseTags, UserSentNoticeBaseTags):
    flags: str
    msg_id: str
    system_msg: str
    msg_params: UserNoticeMessageParams
    @classmethod
    def prepare_data(cls, **kwargs) -> Dict[str, Any]: ...

class UserStateTags(UserEmoteSetsBaseTags, UserIsModBaseTags): ...

class WhisperTags(UserMessageBaseTags):
    message_id: int
    thread_id: str

class HandleAble(abc.ABC):
    default_timestamp: datetime.datetime
    unhandled: Dict[str, str]
    raw: str
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    def as_original_match_dict(self) -> Dict[str, Any]: ...
    def model_data(self) -> Dict[str, Any]: ...

class FromUser(HandleAble, abc.ABC):
    who: str

class HasMessage(HandleAble, abc.ABC):
    message: str
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...

class HasTags(HandleAble, abc.ABC):
    tags: BaseTags
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...

class InChannel(HandleAble, abc.ABC):
    where: str

class UserInChannel(FromUser, InChannel, abc.ABC): ...

class Code353(UserInChannel):
    users: List[str]
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...
    def as_original_match_dict(self) -> Dict[str, Any]: ...

class Code366(UserInChannel): ...

class ClearChat(HasTags, UserInChannel):
    tags: ClearChatTags

class ClearMsg(HasMessage, HasTags, InChannel):
    tags: ClearMsgTags

class HostTarget(InChannel):
    number_of_viewers: Optional[int]
    target: Optional[str]
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...

class JoinPart(UserInChannel):
    action: str
    @property
    def is_join(self) -> bool: ...

class Notice(HasMessage, HasTags, InChannel):
    tags: NoticeTags

class PrivMsg(HasMessage, HasTags, UserInChannel):
    tags: PrivMsgTags
    def is_from_user(self, user: str) -> bool: ...
    @property
    def is_subscribed(self) -> bool: ...
    @property
    def words(self) -> List[str]: ...

class RoomState(HasTags, InChannel):
    tags: RoomStateTags

class UserNotice(HasTags, InChannel):
    tags: UserNoticeTags
    message: Optional[str]
    @classmethod
    def from_match_dict(cls, **kwargs) -> HandleAble: ...

class UserState(HasTags, InChannel):
    tags: UserStateTags

class Whisper(HasMessage, HasTags, UserInChannel):
    tags: WhisperTags

patterns: Dict[Type[HandleAble], Pattern[str]]
