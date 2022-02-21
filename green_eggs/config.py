# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
import enum
import re
from typing import Any, Dict, List, Pattern, Type, Union
import urllib.parse


class LinkPurgeActions(enum.Enum):
    DELETE = 'delete'
    TIMEOUT_FLAT = 'timeout-flat'


class LinkAllowUserConditions(enum.IntFlag):
    NOTHING = 0
    USER_VIP = 0b1
    USER_SUBSCRIBED = 0b10


@dataclass
class Config:
    # Links
    purge_links: bool = False
    link_purge_action: LinkPurgeActions = LinkPurgeActions.DELETE
    link_purge_timeout_duration: int = 1
    link_purge_message_after_action: str = 'Please no posting links without permission'
    link_allow_user_condition: LinkAllowUserConditions = LinkAllowUserConditions.USER_VIP
    link_allow_target_conditions: List[Dict[str, Union[str, Pattern[str]]]] = field(default_factory=list)
    link_permit_command_invoke: str = '!permit'
    link_permit_duration: int = 60

    @staticmethod
    def validate_enum_member(kwargs: Dict[str, Any], key: str, enum_class: Type[enum.Enum], container_name: str):
        if key in kwargs:
            value = kwargs[key]
            try:
                value = enum_class(value)
            except ValueError:
                message = f'Invalid value for {key}: {value!r}. Must be a member of {container_name}'
                raise ValueError(message)
            else:
                kwargs[key] = value

    @staticmethod
    def validate_instance(kwargs: Dict[str, Any], key: str, klass: Type):
        if key in kwargs:
            value = kwargs[key]
            if not isinstance(value, klass):
                message = f'Invalid value for {key}: {value!r}. Must be an instance of {klass.__qualname__}'
                raise ValueError(message)

    @classmethod
    def validate_config(cls, kwargs: Dict[str, Any]):
        cls.validate_enum_member(kwargs, 'link_purge_action', LinkPurgeActions, 'LinkPurgeActions')
        cls.validate_enum_member(
            kwargs, 'link_allow_user_condition', LinkAllowUserConditions, 'LinkAllowUserConditions'
        )

        cls.validate_instance(kwargs, 'link_purge_timeout_duration', int)
        cls.validate_instance(kwargs, 'link_purge_message_after_action', str)
        cls.validate_instance(kwargs, 'link_allow_target_conditions', list)
        cls.validate_instance(kwargs, 'link_permit_command_invoke', str)
        cls.validate_instance(kwargs, 'link_permit_duration', int)

        if 'link_allow_target_conditions' in kwargs:
            for condition in kwargs['link_allow_target_conditions']:
                if not all(isinstance(value, (str, re.Pattern)) for value in condition.values()):
                    message = (
                        f'Invalid value for link_allow_target_conditions: {condition!r}. '
                        'All values must either be string or regex pattern'
                    )
                    raise ValueError(message)

    @classmethod
    def from_python(cls, **kwargs) -> 'Config':
        cls.validate_config(kwargs)

        config = cls(**kwargs)
        return config

    def does_link_pass_conditions(self, link: str) -> bool:
        """
        Checks if the given link is allowed by the config `link_allow_target_conditions`.

        If there are no conditions, no links are allowed.
        If the link does not start with a scheme, `'https://'` will be assumed.

        :param str link: The link to check
        :return: True if the link passes at least one condition
        :rtype: bool
        """
        if not self.link_allow_target_conditions:
            return False

        def check_parsed_part(_condition: Dict[str, Union[str, Pattern[str]]], _name: str, _part: str) -> bool:
            if _name in _condition:
                _value = _condition[_name]
                return (isinstance(_value, str) and _value == _part) or (
                    isinstance(_value, re.Pattern) and _value.fullmatch(_part) is not None
                )
            return True

        parsed = urllib.parse.urlparse(link)
        if not parsed.scheme:
            parsed = urllib.parse.urlparse(f'https://{link}')

        return any(
            all(
                check_parsed_part(condition, name, part)
                for name, part in [('domain', parsed.netloc), ('path', parsed.path)]
            )
            for condition in self.link_allow_target_conditions
        )
