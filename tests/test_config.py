# -*- coding: utf-8 -*-
import re

from green_eggs.config import Config, LinkAllowUserConditions, LinkPurgeActions


def test_validate_enum_member_valid_when_key_not_in_kwargs():
    Config.validate_enum_member(dict(test='abc'), 'not_test', LinkPurgeActions, '')


def test_validate_enum_member_valid_when_value_is_an_enum_instance():
    Config.validate_enum_member(dict(test=LinkPurgeActions.DELETE), 'test', LinkPurgeActions, '')


def test_validate_enum_member_valid_when_value_is_an_enum_value():
    Config.validate_enum_member(dict(test='delete'), 'test', LinkPurgeActions, '')


def test_validate_enum_member_invalid_when_value_is_an_enum_name():
    try:
        Config.validate_enum_member(dict(test='DELETE'), 'test', LinkPurgeActions, 'the illuminati')
    except ValueError as e:
        assert e.args[0] == 'Invalid value for test: \'DELETE\'. Must be a member of the illuminati'
    else:
        assert False, 'Not raised'


def test_validate_enum_member_invalid_when_a_different_enum():
    try:
        Config.validate_enum_member(
            dict(test=LinkPurgeActions.DELETE), 'test', LinkAllowUserConditions, 'the illuminati'
        )
    except ValueError as e:
        assert e.args[0] == (
            'Invalid value for test: <LinkPurgeActions.DELETE: \'delete\'>. Must be a member of the illuminati'
        )
    else:
        assert False, 'Not raised'


def test_validate_enum_member_valid_creatable():
    kwargs = dict(test=-1)
    Config.validate_enum_member(kwargs, 'test', LinkAllowUserConditions, '')
    assert type(kwargs['test']) is LinkAllowUserConditions


def test_validate_instance_valid_when_key_not_in_kwargs():
    Config.validate_instance(dict(test='abc'), 'not_test', int)


def test_validate_instance_invalid_when_wrong_type():
    try:
        Config.validate_instance(dict(test=1), 'test', str)
    except ValueError as e:
        assert e.args[0] == 'Invalid value for test: 1. Must be an instance of str'
    else:
        assert False, 'Not raised'


def test_validate_instance_invalid_with_tuple_of_types():
    try:
        Config.validate_instance(dict(test=2), 'test', (bool, type(None)))
    except ValueError as e:
        assert e.args[0] == 'Invalid value for test: 2. Must be an instance of bool or NoneType'
    else:
        assert False, 'Not raised'


def test_validate_instance_valid_for_subclasses():
    Config.validate_instance(dict(test=True), 'test', int)


def test_validate_config_valid_when_empty():
    Config.validate_config(dict())


def test_validate_config_link_purge_action_valid():
    Config.validate_config(dict(link_purge_action=LinkPurgeActions.DELETE))


def test_validate_config_link_purge_action_invalid():
    try:
        Config.validate_config(dict(link_purge_action='abc'))
    except ValueError as e:
        assert e.args[0] == 'Invalid value for link_purge_action: \'abc\'. Must be a member of LinkPurgeActions'
    else:
        assert False, 'Not raised'


def test_validate_config_link_allow_user_condition_valid():
    Config.validate_config(dict(link_allow_user_condition=-1))


def test_validate_config_link_allow_user_condition_invalid():
    try:
        Config.validate_config(dict(link_allow_user_condition='abc'))
    except ValueError as e:
        assert e.args[0] == (
            'Invalid value for link_allow_user_condition: \'abc\'. Must be a member of LinkAllowUserConditions'
        )
    else:
        assert False, 'Not raised'


def test_validate_config_link_purge_timeout_duration_valid():
    Config.validate_config(dict(link_purge_timeout_duration=2))


def test_validate_config_link_purge_timeout_duration_invalid():
    try:
        Config.validate_config(dict(link_purge_timeout_duration='abc'))
    except ValueError as e:
        assert e.args[0] == 'Invalid value for link_purge_timeout_duration: \'abc\'. Must be an instance of int'
    else:
        assert False, 'Not raised'


def test_validate_config_link_allow_target_conditions_valid_empty():
    Config.validate_config(dict(link_allow_target_conditions=[]))


def test_validate_config_link_allow_target_conditions_valid_str():
    Config.validate_config(dict(link_allow_target_conditions=[dict(test='abc')]))


def test_validate_config_link_allow_target_conditions_valid_pattern():
    Config.validate_config(dict(link_allow_target_conditions=[dict(test=re.compile('abc'))]))


def test_validate_config_link_allow_target_conditions_invalid_not_list():
    try:
        Config.validate_config(dict(link_allow_target_conditions='abc'))
    except ValueError as e:
        assert e.args[0] == 'Invalid value for link_allow_target_conditions: \'abc\'. Must be an instance of list'
    else:
        assert False, 'Not raised'


def test_validate_config_link_allow_target_conditions_invalid_int():
    try:
        Config.validate_config(dict(link_allow_target_conditions=[dict(test=1)]))
    except ValueError as e:
        assert e.args[0] == (
            'Invalid value for link_allow_target_conditions: {\'test\': 1}. '
            'All values must either be string or regex pattern'
        )
    else:
        assert False, 'Not raised'


def test_from_python_defaults():
    config = Config.from_python()
    assert config.should_purge_links is False
    assert config.link_purge_action == LinkPurgeActions.DELETE
    assert config.link_purge_timeout_duration == 1
    assert config.link_allow_user_condition == LinkAllowUserConditions.USER_VIP
    assert config.link_allow_target_conditions == []


def test_does_link_pass_conditions_false_with_no_conditions():
    config = Config.from_python(link_allow_target_conditions=[])
    assert not config.does_link_pass_conditions('link')


def test_does_link_pass_conditions_true_if_passes_condition_str():
    condition = dict(path='/abcd')
    config = Config.from_python(link_allow_target_conditions=[condition])
    assert config.does_link_pass_conditions('clips.twitch.tv/abcd')
    assert config.does_link_pass_conditions('https://clips.twitch.tv/abcd')


def test_does_link_pass_conditions_true_if_passes_condition_pattern():
    condition = dict(domain=re.compile(r'(clips\.)?twitch\.tv'))
    config = Config.from_python(link_allow_target_conditions=[condition])
    assert config.does_link_pass_conditions('clips.twitch.tv/abcd')
    assert config.does_link_pass_conditions('https://twitch.tv/abcd')


def test_does_link_pass_conditions_false_if_does_not_pass_condition_str():
    condition = dict(domain='twitch.tv')
    config = Config.from_python(link_allow_target_conditions=[condition])
    assert not config.does_link_pass_conditions('clips.twitch.tv/def')
    assert not config.does_link_pass_conditions('https://clips.twitch.tv/def')


def test_does_link_pass_conditions_false_if_does_not_pass_condition_pattern():
    condition = dict(path=re.compile(r'/\w{4}'))
    config = Config.from_python(link_allow_target_conditions=[condition])
    assert not config.does_link_pass_conditions('clips.twitch.tv/abcde')
    assert not config.does_link_pass_conditions('https://clips.twitch.tv/abcde')


def test_does_link_pass_conditions_false_if_does_not_pass_full_condition():
    condition = dict(domain='www.twitch.tv', path=re.compile(r'/abcd'))
    config = Config.from_python(link_allow_target_conditions=[condition])
    assert not config.does_link_pass_conditions('www.twitch.tv/def')
    assert not config.does_link_pass_conditions('https://www.twitch.tv/def')


def test_does_link_pass_conditions_true_if_passes_all_conditions():
    condition_one = dict(domain='clips.twitch.tv')
    condition_two = dict(path='/abcd')
    config = Config.from_python(link_allow_target_conditions=[condition_one, condition_two])
    assert config.does_link_pass_conditions('clips.twitch.tv/abcd')
    assert config.does_link_pass_conditions('https://clips.twitch.tv/abcd')


def test_does_link_pass_conditions_true_if_only_passes_some_conditions():
    condition_one = dict(domain='twitch.tv')
    condition_two = dict(path='/abcd')
    config = Config.from_python(link_allow_target_conditions=[condition_one, condition_two])
    assert config.does_link_pass_conditions('clips.twitch.tv/abcd')
    assert config.does_link_pass_conditions('https://twitch.tv/123')
