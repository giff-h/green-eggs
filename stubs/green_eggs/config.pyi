import enum
from typing import Any, Dict, List, Optional, Pattern, Tuple, Type, Union

class LinkPurgeActions(enum.Enum):
    DELETE: str
    TIMEOUT_FLAT: str

class LinkAllowUserConditions(enum.IntFlag):
    NOTHING: int
    USER_VIP: int
    USER_SUBSCRIBED: int

class Config:
    should_purge_links: bool
    link_purge_action: LinkPurgeActions
    link_purge_timeout_duration: int
    link_purge_message_after_action: str
    link_allow_user_condition: LinkAllowUserConditions
    link_allow_target_conditions: List[Dict[str, Union[str, Pattern[str]]]]
    link_permit_command_invoke: str
    link_permit_duration: int
    default_command_user_cooldown: Optional[int]
    default_command_global_cooldown: Optional[int]
    should_notify_if_cooldown_has_not_elapsed: bool
    @staticmethod
    def validate_enum_member(kwargs: Dict[str, Any], key: str, enum_class: Type[enum.Enum], container_name: str): ...
    @staticmethod
    def validate_instance(kwargs: Dict[str, Any], key: str, klass: Union[Type, Tuple[Type, ...]]): ...
    @classmethod
    def validate_config(cls, kwargs: Dict[str, Any]): ...
    @classmethod
    def from_python(cls, **kwargs) -> Config: ...
    def does_link_pass_conditions(self, link: str) -> bool: ...
    def __init__(
        self,
        should_purge_links,
        link_purge_action,
        link_purge_timeout_duration,
        link_purge_message_after_action,
        link_allow_user_condition,
        link_allow_target_conditions,
        link_permit_command_invoke,
        link_permit_duration,
        default_command_user_cooldown,
        default_command_global_cooldown,
        should_notify_if_cooldown_has_not_elapsed,
    ) -> None: ...
