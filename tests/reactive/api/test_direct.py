# -*- coding: utf-8 -*-
import pytest
from pytest_mock import MockerFixture

from green_eggs.reactive.api import TwitchApiDirect
from tests.reactive.fixtures import *  # noqa


async def test_basic(api_direct: TwitchApiDirect):
    result = await api_direct._request('method', 'path')
    api_direct._session.request.assert_called_once_with('method', 'base/path', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


async def test_params(api_direct: TwitchApiDirect):
    result = await api_direct._request('method', 'path', params=dict(a=1, b=['hello', 'world']))
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'method', 'base/path?a=1&b=hello&b=world', json=None
    )
    assert result == dict(foo='bar')


async def test_empty_params(api_direct: TwitchApiDirect):
    result = await api_direct._request('method', 'path', params=dict())
    api_direct._session.request.assert_called_once_with('method', 'base/path', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


async def test_body(api_direct: TwitchApiDirect):
    result = await api_direct._request('method', 'path', data=dict(a=1, b=['hello', 'world']))
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'method', 'base/path', json=dict(a=1, b=['hello', 'world'])
    )
    assert result == dict(foo='bar')


async def test_error(api_direct: TwitchApiDirect, mocker: MockerFixture):
    exc = Exception('Bad status')
    mocker.patch('tests.reactive.MockResponse.raise_for_status', side_effect=exc)
    with pytest.raises(Exception, match='Bad status') as exc_info:
        await api_direct._request('method', 'path')
    assert exc_info.value is exc
    api_direct._session.request.assert_called_once_with('method', 'base/path', json=None)  # type: ignore[attr-defined]


async def test_start_commercial(api_direct: TwitchApiDirect):
    result = await api_direct.start_commercial(broadcaster_id='1', length=2)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/channels/commercial', json={'broadcaster_id': '1', 'length': 2}
    )
    assert result == dict(foo='bar')


async def test_get_extension_analytics(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_analytics(
        after='1', ended_at='2', extension_id='3', first=4, started_at='5', type_='6'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/analytics/extensions?after=1&ended_at=2&extension_id=3&first=4&started_at=5&type=6', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_analytics_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_analytics()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/analytics/extensions', json=None
    )
    assert result == dict(foo='bar')


async def test_get_game_analytics(api_direct: TwitchApiDirect):
    result = await api_direct.get_game_analytics(
        after='1', ended_at='2', first=3, game_id='4', started_at='5', type_='6'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/analytics/games?after=1&ended_at=2&first=3&game_id=4&started_at=5&type=6', json=None
    )
    assert result == dict(foo='bar')


async def test_get_game_analytics_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_game_analytics()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/analytics/games', json=None
    )
    assert result == dict(foo='bar')


async def test_get_bits_leaderboard(api_direct: TwitchApiDirect):
    result = await api_direct.get_bits_leaderboard(count=1, period='2', started_at='3', user_id='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/leaderboard?count=1&period=2&started_at=3&user_id=4', json=None
    )
    assert result == dict(foo='bar')


async def test_get_bits_leaderboard_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_bits_leaderboard()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/leaderboard', json=None
    )
    assert result == dict(foo='bar')


async def test_get_cheermotes(api_direct: TwitchApiDirect):
    result = await api_direct.get_cheermotes(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/cheermotes?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_cheermotes_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_cheermotes()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/cheermotes', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_transactions(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_transactions(extension_id='1', id_=['2', 'also'], after='3', first=4)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/transactions?after=3&extension_id=1&first=4&id=2&id=also', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_transactions_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_transactions(extension_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/transactions?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_channel_information(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_information(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channels?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_modify_channel_information(api_direct: TwitchApiDirect):
    result = await api_direct.modify_channel_information(
        broadcaster_id='1', game_id='2', broadcaster_language='3', title='4', delay=5
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/channels?broadcaster_id=1',
        json={'broadcaster_language': '3', 'delay': 5, 'game_id': '2', 'title': '4'},
    )
    assert result == dict(foo='bar')


async def test_modify_channel_information_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.modify_channel_information(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/channels?broadcaster_id=1', json=dict()
    )
    assert result == dict(foo='bar')


async def test_get_channel_editors(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_editors(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channels/editors?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_create_custom_rewards(api_direct: TwitchApiDirect):
    result = await api_direct.create_custom_rewards(
        broadcaster_id='1',
        title='2',
        cost=3,
        prompt='4',
        is_enabled=True,
        background_color='6',
        is_user_input_required=False,
        is_max_per_stream_enabled=True,
        max_per_stream=9,
        is_max_per_user_per_stream_enabled=False,
        max_per_user_per_stream=11,
        is_global_cooldown_enabled=True,
        global_cooldown_seconds=13,
        should_redemptions_skip_request_queue=False,
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/channel_points/custom_rewards?broadcaster_id=1',
        json={
            'title': '2',
            'cost': 3,
            'prompt': '4',
            'is_enabled': True,
            'background_color': '6',
            'is_user_input_required': False,
            'is_max_per_stream_enabled': True,
            'max_per_stream': 9,
            'is_max_per_user_per_stream_enabled': False,
            'max_per_user_per_stream': 11,
            'is_global_cooldown_enabled': True,
            'global_cooldown_seconds': 13,
            'should_redemptions_skip_request_queue': False,
        },
    )
    assert result == dict(foo='bar')


async def test_create_custom_rewards_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.create_custom_rewards(broadcaster_id='1', title='2', cost=3)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/channel_points/custom_rewards?broadcaster_id=1', json={'cost': 3, 'title': '2'}
    )
    assert result == dict(foo='bar')


async def test_delete_custom_reward(api_direct: TwitchApiDirect):
    result = await api_direct.delete_custom_reward(broadcaster_id='1', id_='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/channel_points/custom_rewards?broadcaster_id=1&id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_custom_reward(api_direct: TwitchApiDirect):
    result = await api_direct.get_custom_reward(broadcaster_id='1', id_=['2', 'also'], only_manageable_rewards=True)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/channel_points/custom_rewards?broadcaster_id=1&id=2&id=also&only_manageable_rewards=true',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_get_custom_reward_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_custom_reward(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channel_points/custom_rewards?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_custom_reward_redemption(api_direct: TwitchApiDirect):
    result = await api_direct.get_custom_reward_redemption(
        broadcaster_id='1', reward_id='2', id_=['3', 'also'], status='4', sort='5', after='6', first=7
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/channel_points/custom_rewards/redemptions'
        '?after=6&broadcaster_id=1&first=7&id=3&id=also&reward_id=2&sort=5&status=4',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_get_custom_reward_redemption_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_custom_reward_redemption(broadcaster_id='1', reward_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channel_points/custom_rewards/redemptions?broadcaster_id=1&reward_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_update_custom_reward(api_direct: TwitchApiDirect):
    result = await api_direct.update_custom_reward(
        broadcaster_id='1',
        id_='2',
        title='3',
        prompt='4',
        cost=5,
        background_color='6',
        is_enabled=True,
        is_user_input_required=False,
        is_max_per_stream_enabled=True,
        max_per_stream=10,
        is_max_per_user_per_stream_enabled=False,
        max_per_user_per_stream=12,
        is_global_cooldown_enabled=True,
        global_cooldown_seconds=14,
        is_paused=False,
        should_redemptions_skip_request_queue=True,
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/channel_points/custom_rewards?broadcaster_id=1&id=2',
        json={
            'title': '3',
            'prompt': '4',
            'cost': 5,
            'background_color': '6',
            'is_enabled': True,
            'is_user_input_required': False,
            'is_max_per_stream_enabled': True,
            'max_per_stream': 10,
            'is_max_per_user_per_stream_enabled': False,
            'max_per_user_per_stream': 12,
            'is_global_cooldown_enabled': True,
            'global_cooldown_seconds': 14,
            'is_paused': False,
            'should_redemptions_skip_request_queue': True,
        },
    )
    assert result == dict(foo='bar')


async def test_update_custom_reward_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_custom_reward(broadcaster_id='1', id_='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/channel_points/custom_rewards?broadcaster_id=1&id=2', json=dict()
    )
    assert result == dict(foo='bar')


async def test_update_redemption_status(api_direct: TwitchApiDirect):
    result = await api_direct.update_redemption_status(id_=['1', 'also'], broadcaster_id='2', reward_id='3', status='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/channel_points/custom_rewards/redemptions?broadcaster_id=2&id=1&id=also&reward_id=3',
        json={'status': '4'},
    )
    assert result == dict(foo='bar')


async def test_get_charity_campaign(api_direct: TwitchApiDirect):
    result = await api_direct.get_charity_campaign(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/charity/campaigns?broadcaster_id=1',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_get_chatters(api_direct: TwitchApiDirect):
    result = await api_direct.get_chatters(after='1', broadcaster_id='2', first=3, moderator_id='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/chat/chatters?after=1&broadcaster_id=2&first=3&moderator_id=4',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_get_chatters_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_chatters(broadcaster_id='1', moderator_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/chat/chatters?broadcaster_id=1&moderator_id=2',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_get_channel_emotes(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_emotes(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/emotes?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_global_emotes(api_direct: TwitchApiDirect):
    result = await api_direct.get_global_emotes()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/emotes/global', json=None
    )
    assert result == dict(foo='bar')


async def test_get_emote_sets(api_direct: TwitchApiDirect):
    result = await api_direct.get_emote_sets(emote_set_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/emotes/set?emote_set_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_channel_chat_badges(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_chat_badges(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/badges?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_global_chat_badges(api_direct: TwitchApiDirect):
    result = await api_direct.get_global_chat_badges()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/badges/global', json=None
    )
    assert result == dict(foo='bar')


async def test_get_chat_settings(api_direct: TwitchApiDirect):
    result = await api_direct.get_chat_settings(broadcaster_id='1', moderator_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/settings?broadcaster_id=1&moderator_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_chat_settings_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_chat_settings(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/settings?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_update_chat_settings(api_direct: TwitchApiDirect):
    result = await api_direct.update_chat_settings(
        broadcaster_id='1',
        moderator_id='2',
        emote_mode=True,
        follower_mode=False,
        follower_mode_duration=3,
        non_moderator_chat_delay=True,
        non_moderator_chat_delay_duration=4,
        slow_mode=False,
        slow_mode_wait_time=5,
        subscriber_mode=True,
        unique_chat_mode=False,
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/chat/settings?broadcaster_id=1&moderator_id=2',
        json=dict(
            emote_mode=True,
            follower_mode=False,
            follower_mode_duration=3,
            non_moderator_chat_delay=True,
            non_moderator_chat_delay_duration=4,
            slow_mode=False,
            slow_mode_wait_time=5,
            subscriber_mode=True,
            unique_chat_mode=False,
        ),
    )
    assert result == dict(foo='bar')


async def test_update_chat_settings_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_chat_settings(broadcaster_id='1', moderator_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/chat/settings?broadcaster_id=1&moderator_id=2', json=dict()
    )
    assert result == dict(foo='bar')


async def test_send_chat_announcement(api_direct: TwitchApiDirect):
    result = await api_direct.send_chat_announcement(broadcaster_id='1', moderator_id='2', color='3', message='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/chat/announcements?broadcaster_id=1&moderator_id=2', json=dict(color='3', message='4')
    )
    assert result == dict(foo='bar')


async def test_send_chat_announcement_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.send_chat_announcement(broadcaster_id='1', moderator_id='2', message='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/chat/announcements?broadcaster_id=1&moderator_id=2', json=dict(message='3')
    )
    assert result == dict(foo='bar')


async def test_get_user_chat_color(api_direct: TwitchApiDirect):
    result = await api_direct.get_user_chat_color(user_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/color?user_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_update_user_chat_color(api_direct: TwitchApiDirect):
    result = await api_direct.update_user_chat_color(color='1', user_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/chat/color?color=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_create_clip(api_direct: TwitchApiDirect):
    result = await api_direct.create_clip(broadcaster_id='1', has_delay=True)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/clips?broadcaster_id=1&has_delay=true', json=None
    )
    assert result == dict(foo='bar')


async def test_create_clip_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.create_clip(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/clips?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_clips(api_direct: TwitchApiDirect):
    result = await api_direct.get_clips(
        broadcaster_id='1', game_id='2', id_=['3', 'also'], after='4', before='5', ended_at='6', first=7, started_at='8'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/clips?after=4&before=5&broadcaster_id=1&ended_at=6&first=7&game_id=2&id=3&id=also&started_at=8',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_get_clips_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_clips(broadcaster_id='1', game_id='2', id_=['3', 'also'])
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/clips?broadcaster_id=1&game_id=2&id=3&id=also', json=None
    )
    assert result == dict(foo='bar')


async def test_get_code_status(api_direct: TwitchApiDirect):
    result = await api_direct.get_code_status()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/entitlements/codes', json=None
    )
    assert result == dict(foo='bar')


async def test_get_drops_entitlements(api_direct: TwitchApiDirect):
    result = await api_direct.get_drops_entitlements(
        id_='1', user_id='2', game_id='3', fulfillment_status='4', after='5', first=6
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/entitlements/drops?after=5&first=6&fulfillment_status=4&game_id=3&id=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_drops_entitlements_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_drops_entitlements()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/entitlements/drops', json=None
    )
    assert result == dict(foo='bar')


async def test_update_drops_entitlements(api_direct: TwitchApiDirect):
    result = await api_direct.update_drops_entitlements(entitlement_ids=['1', 'also'], fulfillment_status='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/entitlements/drops', json=dict(entitlement_ids=['1', 'also'], fulfillment_status='2')
    )
    assert result == dict(foo='bar')


async def test_update_drops_entitlements_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_drops_entitlements()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/entitlements/drops', json=dict()
    )
    assert result == dict(foo='bar')


async def test_redeem_code(api_direct: TwitchApiDirect):
    result = await api_direct.redeem_code(code='1', user_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/entitlements/codes?code=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_redeem_code_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.redeem_code()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/entitlements/codes', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_configuration_segment(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_configuration_segment(broadcaster_id='1', extension_id='2', segment='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/configurations?broadcaster_id=1&extension_id=2&segment=3', json=None
    )
    assert result == dict(foo='bar')


async def test_set_extension_configuration_segment(api_direct: TwitchApiDirect):
    result = await api_direct.set_extension_configuration_segment(
        extension_id='1', segment='2', broadcaster_id='3', content='4', version='5'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT',
        'base/extensions/configurations',
        json={'extension_id': '1', 'segment': '2', 'broadcaster_id': '3', 'content': '4', 'version': '5'},
    )
    assert result == dict(foo='bar')


async def test_set_extension_configuration_segment_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.set_extension_configuration_segment(extension_id='1', segment='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/extensions/configurations', json={'extension_id': '1', 'segment': '2'}
    )
    assert result == dict(foo='bar')


async def test_set_extension_required_configuration(api_direct: TwitchApiDirect):
    result = await api_direct.set_extension_required_configuration(
        broadcaster_id='1', extension_id='2', extension_version='3', required_configuration='4'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT',
        'base/extensions/required_configuration?broadcaster_id=1',
        json={'extension_id': '2', 'extension_version': '3', 'required_configuration': '4'},
    )
    assert result == dict(foo='bar')


async def test_send_extension_pubsub_message(api_direct: TwitchApiDirect):
    result = await api_direct.send_extension_pubsub_message(
        target=['1', 'also'], broadcaster_id='2', is_global_broadcast=True, message='4'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/extensions/pubsub',
        json={'broadcaster_id': '2', 'is_global_broadcast': True, 'message': '4', 'target': ['1', 'also']},
    )
    assert result == dict(foo='bar')


async def test_get_extension_live_channels(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_live_channels(extension_id='1', first=2, after='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/live?after=3&extension_id=1&first=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_live_channels_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_live_channels(extension_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/live?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_secrets(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_secrets()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/jwt/secrets', json=None
    )
    assert result == dict(foo='bar')


async def test_create_extension_secret(api_direct: TwitchApiDirect):
    result = await api_direct.create_extension_secret(delay=1, extension_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/extensions/jwt/secrets?delay=1&extension_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_create_extension_secret_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.create_extension_secret(extension_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/extensions/jwt/secrets?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_send_extension_chat_message(api_direct: TwitchApiDirect):
    result = await api_direct.send_extension_chat_message(
        broadcaster_id='1', text='2', extension_id='3', extension_version='4'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/extensions/chat?broadcaster_id=1',
        json={'extension_id': '3', 'extension_version': '4', 'text': '2'},
    )
    assert result == dict(foo='bar')


async def test_get_extensions(api_direct: TwitchApiDirect):
    result = await api_direct.get_extensions(extension_id='1', extension_version='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions?extension_id=1&extension_version=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extensions_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_extensions(extension_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_released_extensions(api_direct: TwitchApiDirect):
    result = await api_direct.get_released_extensions(extension_id='1', extension_version='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/released?extension_id=1&extension_version=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_released_extensions_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_released_extensions(extension_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/released?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_bits_products(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_bits_products(should_include_all=True)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/extensions?should_include_all=true', json=None
    )
    assert result == dict(foo='bar')


async def test_get_extension_bits_products_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_extension_bits_products()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/extensions', json=None
    )
    assert result == dict(foo='bar')


async def test_update_extension_bits_product(api_direct: TwitchApiDirect):
    result = await api_direct.update_extension_bits_product(
        cost_amount=1, cost_type='2', display_name='3', expiration='4', in_development=True, is_broadcast=False, sku='5'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT',
        'base/bits/extensions',
        json={
            'cost': {'amount': 1, 'type': '2'},
            'display_name': '3',
            'expiration': '4',
            'in_development': True,
            'is_broadcast': False,
            'sku': '5',
        },
    )
    assert result == dict(foo='bar')


async def test_update_extension_bits_product_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_extension_bits_product(cost_amount=1, cost_type='2', display_name='3', sku='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/bits/extensions', json={'cost': {'amount': 1, 'type': '2'}, 'display_name': '3', 'sku': '4'}
    )
    assert result == dict(foo='bar')


async def test_create_eventsub_subscription(api_direct: TwitchApiDirect):
    result = await api_direct.create_eventsub_subscription(
        type_='1', version='2', condition=dict(key=3), transport=dict(key=4)
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/eventsub/subscriptions',
        json={'condition': {'key': 3}, 'transport': {'key': 4}, 'type': '1', 'version': '2'},
    )
    assert result == dict(foo='bar')


async def test_delete_eventsub_subscription(api_direct: TwitchApiDirect):
    result = await api_direct.delete_eventsub_subscription(id_='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/eventsub/subscriptions?id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_eventsub_subscriptions(api_direct: TwitchApiDirect):
    result = await api_direct.get_eventsub_subscriptions(status='1', type_='2', after='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/eventsub/subscriptions?after=3&status=1&type=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_eventsub_subscriptions_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_eventsub_subscriptions()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/eventsub/subscriptions', json=None
    )
    assert result == dict(foo='bar')


async def test_get_top_games(api_direct: TwitchApiDirect):
    result = await api_direct.get_top_games(after='1', before='2', first=3)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/games/top?after=1&before=2&first=3', json=None
    )
    assert result == dict(foo='bar')


async def test_get_top_games_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_top_games()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/games/top', json=None
    )
    assert result == dict(foo='bar')


async def test_get_games(api_direct: TwitchApiDirect):
    result = await api_direct.get_games(id_='1', name='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/games?id=1&name=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_creator_goals(api_direct: TwitchApiDirect):
    result = await api_direct.get_creator_goals(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/goals?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_hype_train_events(api_direct: TwitchApiDirect):
    result = await api_direct.get_hype_train_events(broadcaster_id='1', first=2, cursor='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/hypetrain/events?broadcaster_id=1&cursor=3&first=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_hype_train_events_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_hype_train_events(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/hypetrain/events?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_check_automod_status(api_direct: TwitchApiDirect):
    result = await api_direct.check_automod_status(broadcaster_id='1', msg_id='2', msg_text='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/moderation/enforcements/status?broadcaster_id=1',
        json={'msg_id': '2', 'msg_text': '3'},
    )
    assert result == dict(foo='bar')


async def test_manage_held_automod_messages(api_direct: TwitchApiDirect):
    result = await api_direct.manage_held_automod_messages(user_id='1', msg_id='2', action='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/moderation/automod/message', json={'action': '3', 'msg_id': '2', 'user_id': '1'}
    )
    assert result == dict(foo='bar')


async def test_get_automod_settings(api_direct: TwitchApiDirect):
    result = await api_direct.get_automod_settings(broadcaster_id='1', moderator_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/automod/settings?broadcaster_id=1&moderator_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_update_automod_settings(api_direct: TwitchApiDirect):
    result = await api_direct.update_automod_settings(
        broadcaster_id='1',
        moderator_id='2',
        aggression=3,
        bullying=4,
        disability=5,
        misogyny=6,
        overall_level=7,
        race_ethnicity_or_religion=8,
        sex_based_terms=9,
        sexuality_sex_or_gender=10,
        swearing=11,
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT',
        'base/moderation/automod/settings?broadcaster_id=1&moderator_id=2',
        json=dict(
            aggression=3,
            bullying=4,
            disability=5,
            misogyny=6,
            overall_level=7,
            race_ethnicity_or_religion=8,
            sex_based_terms=9,
            sexuality_sex_or_gender=10,
            swearing=11,
        ),
    )
    assert result == dict(foo='bar')


async def test_update_automod_settings_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_automod_settings(broadcaster_id='1', moderator_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/moderation/automod/settings?broadcaster_id=1&moderator_id=2', json=dict()
    )
    assert result == dict(foo='bar')


async def test_get_banned_users(api_direct: TwitchApiDirect):
    result = await api_direct.get_banned_users(
        broadcaster_id='1', user_id=['2', 'also'], first='3', after='4', before='5'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/banned?after=4&before=5&broadcaster_id=1&first=3&user_id=2&user_id=also', json=None
    )
    assert result == dict(foo='bar')


async def test_get_banned_users_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_banned_users(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/banned?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_ban_user(api_direct: TwitchApiDirect):
    result = await api_direct.ban_user(broadcaster_id='1', moderator_id='2', duration=4, reason='5', user_id='6')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/moderation/bans?broadcaster_id=1&moderator_id=2',
        json=dict(data=dict(duration=4, reason='5', user_id='6')),
    )
    assert result == dict(foo='bar')


async def test_ban_user_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.ban_user(broadcaster_id='1', moderator_id='2', reason='4', user_id='5')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/moderation/bans?broadcaster_id=1&moderator_id=2',
        json=dict(data=dict(reason='4', user_id='5')),
    )
    assert result == dict(foo='bar')


async def test_unban_user(api_direct: TwitchApiDirect):
    result = await api_direct.unban_user(broadcaster_id='1', moderator_id='2', user_id='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/moderation/bans?broadcaster_id=1&moderator_id=2&user_id=3', json=None
    )
    assert result == dict(foo='bar')


async def test_get_blocked_terms(api_direct: TwitchApiDirect):
    result = await api_direct.get_blocked_terms(broadcaster_id='1', moderator_id='2', after='3', first=4)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/blocked_terms?after=3&broadcaster_id=1&first=4&moderator_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_blocked_terms_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_blocked_terms(broadcaster_id='1', moderator_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/blocked_terms?broadcaster_id=1&moderator_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_add_blocked_term(api_direct: TwitchApiDirect):
    result = await api_direct.add_blocked_term(broadcaster_id='1', moderator_id='2', text='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/moderation/blocked_terms?broadcaster_id=1&moderator_id=2', json=dict(text='3')
    )
    assert result == dict(foo='bar')


async def test_remove_blocked_term(api_direct: TwitchApiDirect):
    result = await api_direct.remove_blocked_term(broadcaster_id='1', id_='2', moderator_id='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/moderation/blocked_terms?broadcaster_id=1&id=2&moderator_id=3', json=None
    )
    assert result == dict(foo='bar')


async def test_delete_chat_messages(api_direct: TwitchApiDirect):
    result = await api_direct.delete_chat_messages(broadcaster_id='1', message_id='2', moderator_id='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/moderation/chat?broadcaster_id=1&message_id=2&moderator_id=3', json=None
    )
    assert result == dict(foo='bar')


async def test_delete_chat_messages_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.delete_chat_messages(broadcaster_id='1', moderator_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/moderation/chat?broadcaster_id=1&moderator_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_moderators(api_direct: TwitchApiDirect):
    result = await api_direct.get_moderators(broadcaster_id='1', user_id=['2', 'also'], first='3', after='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/moderators?after=4&broadcaster_id=1&first=3&user_id=2&user_id=also', json=None
    )
    assert result == dict(foo='bar')


async def test_get_moderators_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_moderators(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/moderators?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_add_channel_moderator(api_direct: TwitchApiDirect):
    result = await api_direct.add_channel_moderator(broadcaster_id='1', user_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/moderation/moderators?broadcaster_id=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_remove_channel_moderator(api_direct: TwitchApiDirect):
    result = await api_direct.remove_channel_moderator(broadcaster_id='1', user_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/moderation/moderators?broadcaster_id=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_vips(api_direct: TwitchApiDirect):
    result = await api_direct.get_vips(after='1', broadcaster_id='2', first=3, user_id='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channels/vips?after=1&broadcaster_id=2&first=3&user_id=4', json=None
    )
    assert result == dict(foo='bar')


async def test_get_vips_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_vips(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channels/vips?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_add_channel_vip(api_direct: TwitchApiDirect):
    result = await api_direct.add_channel_vip(broadcaster_id='1', user_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/channels/vips?broadcaster_id=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_remove_channel_vip(api_direct: TwitchApiDirect):
    result = await api_direct.remove_channel_vip(broadcaster_id='1', user_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/channels/vips?broadcaster_id=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_polls(api_direct: TwitchApiDirect):
    result = await api_direct.get_polls(broadcaster_id='1', id_=['2', 'also'], after='3', first='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/polls?after=3&broadcaster_id=1&first=4&id=2&id=also', json=None
    )
    assert result == dict(foo='bar')


async def test_get_polls_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_polls(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/polls?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_create_poll(api_direct: TwitchApiDirect):
    result = await api_direct.create_poll(
        broadcaster_id='1',
        title='2',
        choice_title=['3', 'also'],
        duration=4,
        channel_points_voting_enabled=False,
        channel_points_per_vote=5,
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/polls',
        json={
            'broadcaster_id': '1',
            'title': '2',
            'choices': [{'title': '3'}, {'title': 'also'}],
            'duration': 4,
            'channel_points_voting_enabled': False,
            'channel_points_per_vote': 5,
        },
    )
    assert result == dict(foo='bar')


async def test_create_poll_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.create_poll(broadcaster_id='1', title='2', choice_title=['3', 'also'], duration=4)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/polls',
        json={'broadcaster_id': '1', 'choices': [{'title': '3'}, {'title': 'also'}], 'duration': 4, 'title': '2'},
    )
    assert result == dict(foo='bar')


async def test_end_poll(api_direct: TwitchApiDirect):
    result = await api_direct.end_poll(broadcaster_id='1', id_='2', status='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/polls', json={'broadcaster_id': '1', 'id': '2', 'status': '3'}
    )
    assert result == dict(foo='bar')


async def test_get_predictions(api_direct: TwitchApiDirect):
    result = await api_direct.get_predictions(broadcaster_id='1', id_=['2', 'also'], after='3', first='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/predictions?after=3&broadcaster_id=1&first=4&id=2&id=also', json=None
    )
    assert result == dict(foo='bar')


async def test_get_predictions_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_predictions(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/predictions?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_create_prediction(api_direct: TwitchApiDirect):
    result = await api_direct.create_prediction(
        broadcaster_id='1', title='2', outcome_title=['3', 'also'], prediction_window=4
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/predictions',
        json={
            'broadcaster_id': '1',
            'outcomes': [{'title': '3'}, {'title': 'also'}],
            'prediction_window': 4,
            'title': '2',
        },
    )
    assert result == dict(foo='bar')


async def test_end_prediction(api_direct: TwitchApiDirect):
    result = await api_direct.end_prediction(broadcaster_id='1', id_='2', status='3', winning_outcome_id='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/predictions', json={'broadcaster_id': '1', 'id': '2', 'status': '3', 'winning_outcome_id': '4'}
    )
    assert result == dict(foo='bar')


async def test_end_prediction_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.end_prediction(broadcaster_id='1', id_='2', status='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/predictions', json={'broadcaster_id': '1', 'id': '2', 'status': '3'}
    )
    assert result == dict(foo='bar')


async def test_start_a_raid(api_direct: TwitchApiDirect):
    result = await api_direct.start_a_raid(from_broadcaster_id='1', to_broadcaster_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/raids?from_broadcaster_id=1&to_broadcaster_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_cancel_a_raid(api_direct: TwitchApiDirect):
    result = await api_direct.cancel_a_raid(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/raids?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_channel_stream_schedule(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_stream_schedule(
        broadcaster_id='1', id_=['2', 'also'], start_time='3', utc_offset='4', first=5, after='6'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/schedule?after=6&broadcaster_id=1&first=5&id=2&id=also&start_time=3&utc_offset=4', json=None
    )
    assert result == dict(foo='bar')


async def test_get_channel_stream_schedule_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_stream_schedule(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/schedule?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_channel_icalendar(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_icalendar(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/schedule/icalendar?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_update_channel_stream_schedule(api_direct: TwitchApiDirect):
    result = await api_direct.update_channel_stream_schedule(
        broadcaster_id='1', is_vacation_enabled=True, vacation_start_time='3', vacation_end_time='4', timezone='5'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/schedule/settings'
        '?broadcaster_id=1&is_vacation_enabled=true&timezone=5&vacation_end_time=4&vacation_start_time=3',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_update_channel_stream_schedule_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_channel_stream_schedule(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/schedule/settings?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_create_channel_stream_schedule_segment(api_direct: TwitchApiDirect):
    result = await api_direct.create_channel_stream_schedule_segment(
        broadcaster_id='1', start_time='2', timezone='3', is_recurring=True, duration='5', category_id='6', title='7'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/schedule/segment?broadcaster_id=1',
        json={
            'start_time': '2',
            'timezone': '3',
            'is_recurring': True,
            'duration': '5',
            'category_id': '6',
            'title': '7',
        },
    )
    assert result == dict(foo='bar')


async def test_create_channel_stream_schedule_segment_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.create_channel_stream_schedule_segment(
        broadcaster_id='1', start_time='2', timezone='3', is_recurring=True
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/schedule/segment?broadcaster_id=1',
        json={'is_recurring': True, 'start_time': '2', 'timezone': '3'},
    )
    assert result == dict(foo='bar')


async def test_update_channel_stream_schedule_segment(api_direct: TwitchApiDirect):
    result = await api_direct.update_channel_stream_schedule_segment(
        broadcaster_id='1',
        id_='2',
        start_time='3',
        duration='4',
        category_id='5',
        title='6',
        is_canceled=True,
        timezone='8',
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/schedule/segment?broadcaster_id=1&id=2',
        json={
            'start_time': '3',
            'duration': '4',
            'category_id': '5',
            'title': '6',
            'is_canceled': True,
            'timezone': '8',
        },
    )
    assert result == dict(foo='bar')


async def test_update_channel_stream_schedule_segment_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_channel_stream_schedule_segment(broadcaster_id='1', id_='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/schedule/segment?broadcaster_id=1&id=2', json=dict()
    )
    assert result == dict(foo='bar')


async def test_delete_channel_stream_schedule_segment(api_direct: TwitchApiDirect):
    result = await api_direct.delete_channel_stream_schedule_segment(broadcaster_id='1', id_='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/schedule/segment?broadcaster_id=1&id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_search_categories(api_direct: TwitchApiDirect):
    result = await api_direct.search_categories(query='1', first=2, after='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/categories?after=3&first=2&query=1', json=None
    )
    assert result == dict(foo='bar')


async def test_search_categories_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.search_categories(query='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/categories?query=1', json=None
    )
    assert result == dict(foo='bar')


async def test_search_channels(api_direct: TwitchApiDirect):
    result = await api_direct.search_channels(query='1', first=2, after='3', live_only=True)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/channels?after=3&first=2&live_only=true&query=1', json=None
    )
    assert result == dict(foo='bar')


async def test_search_channels_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.search_channels(query='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/channels?query=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_soundtrack_current_track(api_direct: TwitchApiDirect):
    result = await api_direct.get_soundtrack_current_track(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/soundtrack/current_track?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_soundtrack_playlist(api_direct: TwitchApiDirect):
    result = await api_direct.get_soundtrack_playlist(id_='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/soundtrack/playlist?id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_soundtrack_playlists(api_direct: TwitchApiDirect):
    result = await api_direct.get_soundtrack_playlists()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/soundtrack/playlists', json=None
    )
    assert result == dict(foo='bar')


async def test_get_stream_key(api_direct: TwitchApiDirect):
    result = await api_direct.get_stream_key(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/key?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_streams(api_direct: TwitchApiDirect):
    result = await api_direct.get_streams(
        after='1', before='2', first=3, game_id='4', language='5', user_id='6', user_login='7'
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams?after=1&before=2&first=3&game_id=4&language=5&user_id=6&user_login=7', json=None
    )
    assert result == dict(foo='bar')


async def test_get_streams_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_streams()
    api_direct._session.request.assert_called_once_with('GET', 'base/streams', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


async def test_get_followed_streams(api_direct: TwitchApiDirect):
    result = await api_direct.get_followed_streams(user_id='1', after='2', first=3)
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/followed?after=2&first=3&user_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_followed_streams_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_followed_streams(user_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/followed?user_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_create_stream_marker(api_direct: TwitchApiDirect):
    result = await api_direct.create_stream_marker(user_id='1', description='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/streams/markers', json={'description': '2', 'user_id': '1'}
    )
    assert result == dict(foo='bar')


async def test_create_stream_marker_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.create_stream_marker(user_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/streams/markers', json={'user_id': '1'}
    )
    assert result == dict(foo='bar')


async def test_get_stream_markers(api_direct: TwitchApiDirect):
    result = await api_direct.get_stream_markers(user_id='1', video_id='2', after='3', before='4', first='5')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/markers?after=3&before=4&first=5&user_id=1&video_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_stream_markers_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_stream_markers(user_id='1', video_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/markers?user_id=1&video_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_broadcaster_subscriptions(api_direct: TwitchApiDirect):
    result = await api_direct.get_broadcaster_subscriptions(broadcaster_id='1', user_id='2', after='3', first='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions?after=3&broadcaster_id=1&first=4&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_broadcaster_subscriptions_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_broadcaster_subscriptions(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_check_user_subscription(api_direct: TwitchApiDirect):
    result = await api_direct.check_user_subscription(broadcaster_id='1', user_id='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_all_stream_tags(api_direct: TwitchApiDirect):
    result = await api_direct.get_all_stream_tags(after='1', first=2, tag_id='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/tags/streams?after=1&first=2&tag_id=3', json=None
    )
    assert result == dict(foo='bar')


async def test_get_all_stream_tags_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_all_stream_tags()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/tags/streams', json=None
    )
    assert result == dict(foo='bar')


async def test_get_stream_tags(api_direct: TwitchApiDirect):
    result = await api_direct.get_stream_tags(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/tags?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_replace_stream_tags(api_direct: TwitchApiDirect):
    result = await api_direct.replace_stream_tags(broadcaster_id='1', tag_ids=['2', 'also'])
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/streams/tags?broadcaster_id=1', json={'tag_ids': ['2', 'also']}
    )
    assert result == dict(foo='bar')


async def test_replace_stream_tags_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.replace_stream_tags(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/streams/tags?broadcaster_id=1', json=dict()
    )
    assert result == dict(foo='bar')


async def test_get_channel_teams(api_direct: TwitchApiDirect):
    result = await api_direct.get_channel_teams(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/teams/channel?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_teams(api_direct: TwitchApiDirect):
    result = await api_direct.get_teams(name='1', id_='2')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/teams?id=2&name=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_teams_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_teams()
    api_direct._session.request.assert_called_once_with('GET', 'base/teams', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


async def test_get_users(api_direct: TwitchApiDirect):
    result = await api_direct.get_users(id_=['1', 'also'], login=['2', 'also'])
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users?id=1&id=also&login=2&login=also', json=None
    )
    assert result == dict(foo='bar')


async def test_get_users_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_users()
    api_direct._session.request.assert_called_once_with('GET', 'base/users', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


async def test_update_user(api_direct: TwitchApiDirect):
    result = await api_direct.update_user(description='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users?description=1', json=None
    )
    assert result == dict(foo='bar')


async def test_update_user_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.update_user()
    api_direct._session.request.assert_called_once_with('PUT', 'base/users', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


async def test_get_users_follows(api_direct: TwitchApiDirect):
    result = await api_direct.get_users_follows(after='1', first=2, from_id='3', to_id='4')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/follows?after=1&first=2&from_id=3&to_id=4', json=None
    )
    assert result == dict(foo='bar')


async def test_get_users_follows_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_users_follows()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/follows', json=None
    )
    assert result == dict(foo='bar')


async def test_get_user_block_list(api_direct: TwitchApiDirect):
    result = await api_direct.get_user_block_list(broadcaster_id='1', first=2, after='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/blocks?after=3&broadcaster_id=1&first=2', json=None
    )
    assert result == dict(foo='bar')


async def test_get_user_block_list_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_user_block_list(broadcaster_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/blocks?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_block_user(api_direct: TwitchApiDirect):
    result = await api_direct.block_user(target_user_id='1', source_context='2', reason='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users/blocks?reason=3&source_context=2&target_user_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_block_user_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.block_user(target_user_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users/blocks?target_user_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_unblock_user(api_direct: TwitchApiDirect):
    result = await api_direct.unblock_user(target_user_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/users/blocks?target_user_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_user_extensions(api_direct: TwitchApiDirect):
    result = await api_direct.get_user_extensions()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/extensions/list', json=None
    )
    assert result == dict(foo='bar')


async def test_get_user_active_extensions(api_direct: TwitchApiDirect):
    result = await api_direct.get_user_active_extensions(user_id='1')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/extensions?user_id=1', json=None
    )
    assert result == dict(foo='bar')


async def test_get_user_active_extensions_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_user_active_extensions()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/extensions', json=None
    )
    assert result == dict(foo='bar')


async def test_update_user_extensions(api_direct: TwitchApiDirect):
    result = await api_direct.update_user_extensions()
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users/extensions', json=None
    )
    assert result == dict(foo='bar')


async def test_get_videos(api_direct: TwitchApiDirect):
    result = await api_direct.get_videos(
        id_=['1', 'also'],
        user_id='2',
        game_id='3',
        after='4',
        before='5',
        first='6',
        language='7',
        period='8',
        sort='9',
        type_='10',
    )
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/videos?after=4&before=5&first=6&game_id=3&id=1&id=also&language=7&period=8&sort=9&type=10&user_id=2',
        json=None,
    )
    assert result == dict(foo='bar')


async def test_get_videos_exclude_empty(api_direct: TwitchApiDirect):
    result = await api_direct.get_videos(id_=['1', 'also'], user_id='2', game_id='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/videos?game_id=3&id=1&id=also&user_id=2', json=None
    )
    assert result == dict(foo='bar')


async def test_delete_videos(api_direct: TwitchApiDirect):
    result = await api_direct.delete_videos(id_=['1', 'also'])
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/videos?id=1&id=also', json=None
    )
    assert result == dict(foo='bar')


async def test_send_whisper(api_direct: TwitchApiDirect):
    result = await api_direct.send_whisper(from_user_id='1', to_user_id='2', message='3')
    api_direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/whispers?from_user_id=1&to_user_id=2', json=dict(message='3')
    )
    assert result == dict(foo='bar')
