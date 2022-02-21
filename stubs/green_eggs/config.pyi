import enum
from typing import Any, Dict, List, Pattern, Type, Union

class LinkPurgeActions(enum.Enum):
    DELETE: str
    TIMEOUT_FLAT: str

class LinkAllowUserConditions(enum.IntFlag):
    NOTHING: int
    USER_VIP: int
    USER_SUBSCRIBED: int

class Config:
    purge_links: bool
    link_purge_action: LinkPurgeActions
    link_purge_timeout_duration: int
    link_purge_message_after_action: str
    link_allow_user_condition: LinkAllowUserConditions
    link_allow_target_conditions: List[Dict[str, Union[str, Pattern[str]]]]
    link_permit_command_invoke: str
    link_permit_duration: int
    @staticmethod
    def validate_enum_member(kwargs: Dict[str, Any], key: str, enum_class: Type[enum.Enum], container_name: str): ...
    @staticmethod
    def validate_instance(kwargs: Dict[str, Any], key: str, klass: Type): ...
    @classmethod
    def validate_config(cls, kwargs: Dict[str, Any]): ...
    @classmethod
    def from_python(cls, **kwargs) -> Config: ...
    def does_link_pass_conditions(self, link: str) -> bool: ...
    def __init__(
        self,
        purge_links,
        link_purge_action,
        link_purge_timeout_duration,
        link_purge_message_after_action,
        link_allow_user_condition,
        link_allow_target_conditions,
        link_permit_command_invoke,
        link_permit_duration,
    ) -> None: ...
