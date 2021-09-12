# -*- coding: utf-8 -*-
import pytest
from pytest_mock import MockerFixture

from green_eggs.api import TwitchApi
from tests.fixtures import *  # noqa


@pytest.mark.asyncio
async def test_basic(api: TwitchApi):
    result = await api._request('method', 'path')
    api._session.request.assert_called_once_with('method', 'base/path', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_params(api: TwitchApi):
    result = await api._request('method', 'path', params=dict(a=1, b=['hello', 'world']))
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'method', 'base/path?a=1&b=hello&b=world', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_empty_params(api: TwitchApi):
    result = await api._request('method', 'path', params=dict())
    api._session.request.assert_called_once_with('method', 'base/path', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_body(api: TwitchApi):
    result = await api._request('method', 'path', data=dict(a=1, b=['hello', 'world']))
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'method', 'base/path', json=dict(a=1, b=['hello', 'world'])
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_raise(api: TwitchApi, mocker: MockerFixture):
    mocker.patch('tests.MockResponse.raise_for_status', side_effect=Exception('Bad status'))
    try:
        await api._request('method', 'path')
    except Exception as e:
        assert e.args == ('Bad status',)
    else:
        assert False, 'Did not raise'
    api._session.request.assert_called_once_with('method', 'base/path', json=None)  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_no_raise(api: TwitchApi, mocker: MockerFixture):
    mocker.patch('tests.MockResponse.raise_for_status', side_effect=Exception('Bad status'))
    try:
        result = await api._request('method', 'path', raise_for_status=False)
    except Exception as e:
        assert False, e
    else:
        api._session.request.assert_called_once_with('method', 'base/path', json=None)  # type: ignore[attr-defined]
        assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_start_commercial(api: TwitchApi):
    result = await api.start_commercial(broadcaster_id='1', length=2)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/channels/commercial', json={'broadcaster_id': '1', 'length': 2}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_analytics(api: TwitchApi):
    result = await api.get_extension_analytics(
        after='1', ended_at='2', extension_id='3', first=4, started_at='5', type_='6'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/analytics/extensions?after=1&ended_at=2&extension_id=3&first=4&started_at=5&type=6', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_analytics_exclude_empty(api: TwitchApi):
    result = await api.get_extension_analytics()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/analytics/extensions', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_game_analytics(api: TwitchApi):
    result = await api.get_game_analytics(after='1', ended_at='2', first=3, game_id='4', started_at='5', type_='6')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/analytics/games?after=1&ended_at=2&first=3&game_id=4&started_at=5&type=6', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_game_analytics_exclude_empty(api: TwitchApi):
    result = await api.get_game_analytics()
    api._session.request.assert_called_once_with('GET', 'base/analytics/games', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_bits_leaderboard(api: TwitchApi):
    result = await api.get_bits_leaderboard(count=1, period='2', started_at='3', user_id='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/leaderboard?count=1&period=2&started_at=3&user_id=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_bits_leaderboard_exclude_empty(api: TwitchApi):
    result = await api.get_bits_leaderboard()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/leaderboard', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_cheermotes(api: TwitchApi):
    result = await api.get_cheermotes(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/cheermotes?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_cheermotes_exclude_empty(api: TwitchApi):
    result = await api.get_cheermotes()
    api._session.request.assert_called_once_with('GET', 'base/bits/cheermotes', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_transactions(api: TwitchApi):
    result = await api.get_extension_transactions(extension_id='1', id_=['2', 'also'], after='3', first=4)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/transactions?extension_id=1&id=2&id=also&after=3&first=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_transactions_exclude_empty(api: TwitchApi):
    result = await api.get_extension_transactions(extension_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/transactions?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_information(api: TwitchApi):
    result = await api.get_channel_information(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channels?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_modify_channel_information(api: TwitchApi):
    result = await api.modify_channel_information(
        broadcaster_id='1', game_id='2', broadcaster_language='3', title='4', delay=5
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/channels?broadcaster_id=1',
        json={'broadcaster_language': '3', 'delay': 5, 'game_id': '2', 'title': '4'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_modify_channel_information_exclude_empty(api: TwitchApi):
    result = await api.modify_channel_information(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/channels?broadcaster_id=1', json=dict()
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_editors(api: TwitchApi):
    result = await api.get_channel_editors(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channels/editors?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_custom_rewards(api: TwitchApi):
    result = await api.create_custom_rewards(
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
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
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


@pytest.mark.asyncio
async def test_create_custom_rewards_exclude_empty(api: TwitchApi):
    result = await api.create_custom_rewards(broadcaster_id='1', title='2', cost=3)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/channel_points/custom_rewards?broadcaster_id=1', json={'cost': 3, 'title': '2'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_delete_custom_reward(api: TwitchApi):
    result = await api.delete_custom_reward(broadcaster_id='1', id_='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/channel_points/custom_rewards?broadcaster_id=1&id=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_custom_reward(api: TwitchApi):
    result = await api.get_custom_reward(broadcaster_id='1', id_=['2', 'also'], only_manageable_rewards=True)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/channel_points/custom_rewards?broadcaster_id=1&id=2&id=also&only_manageable_rewards=True',
        json=None,
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_custom_reward_exclude_empty(api: TwitchApi):
    result = await api.get_custom_reward(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channel_points/custom_rewards?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_custom_reward_redemption(api: TwitchApi):
    result = await api.get_custom_reward_redemption(
        broadcaster_id='1', reward_id='2', id_=['3', 'also'], status='4', sort='5', after='6', first=7
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/channel_points/custom_rewards/redemptions'
        '?broadcaster_id=1&reward_id=2&id=3&id=also&status=4&sort=5&after=6&first=7',
        json=None,
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_custom_reward_redemption_exclude_empty(api: TwitchApi):
    result = await api.get_custom_reward_redemption(broadcaster_id='1', reward_id='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/channel_points/custom_rewards/redemptions?broadcaster_id=1&reward_id=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_custom_reward(api: TwitchApi):
    result = await api.update_custom_reward(
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
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
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


@pytest.mark.asyncio
async def test_update_custom_reward_exclude_empty(api: TwitchApi):
    result = await api.update_custom_reward(broadcaster_id='1', id_='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/channel_points/custom_rewards?broadcaster_id=1&id=2', json=dict()
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_redemption_status(api: TwitchApi):
    result = await api.update_redemption_status(id_=['1', 'also'], broadcaster_id='2', reward_id='3', status='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/channel_points/custom_rewards/redemptions?id=1&id=also&broadcaster_id=2&reward_id=3',
        json={'status': '4'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_emotes(api: TwitchApi):
    result = await api.get_channel_emotes(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/emotes?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_global_emotes(api: TwitchApi):
    result = await api.get_global_emotes()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/emotes/global', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_emote_sets(api: TwitchApi):
    result = await api.get_emote_sets(emote_set_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/emotes/set?emote_set_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_chat_badges(api: TwitchApi):
    result = await api.get_channel_chat_badges(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/badges?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_global_chat_badges(api: TwitchApi):
    result = await api.get_global_chat_badges()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/chat/badges/global', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_clip(api: TwitchApi):
    result = await api.create_clip(broadcaster_id='1', has_delay=True)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/clips?broadcaster_id=1&has_delay=True', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_clip_exclude_empty(api: TwitchApi):
    result = await api.create_clip(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/clips?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_clips(api: TwitchApi):
    result = await api.get_clips(
        broadcaster_id='1', game_id='2', id_=['3', 'also'], after='4', before='5', ended_at='6', first=7, started_at='8'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/clips?broadcaster_id=1&game_id=2&id=3&id=also&after=4&before=5&ended_at=6&first=7&started_at=8',
        json=None,
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_clips_exclude_empty(api: TwitchApi):
    result = await api.get_clips(broadcaster_id='1', game_id='2', id_=['3', 'also'])
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/clips?broadcaster_id=1&game_id=2&id=3&id=also', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_code_status(api: TwitchApi):
    result = await api.get_code_status()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/entitlements/codes', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_drops_entitlements(api: TwitchApi):
    result = await api.get_drops_entitlements(
        id_='1', user_id='2', game_id='3', fulfillment_status='4', after='5', first=6
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/entitlements/drops?id=1&user_id=2&game_id=3&fulfillment_status=4&after=5&first=6', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_drops_entitlements_exclude_empty(api: TwitchApi):
    result = await api.get_drops_entitlements()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/entitlements/drops', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_drops_entitlements(api: TwitchApi):
    result = await api.update_drops_entitlements(entitlement_ids=['1', 'also'], fulfillment_status='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/entitlements/drops?entitlement_ids=1&entitlement_ids=also&fulfillment_status=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_drops_entitlements_exclude_empty(api: TwitchApi):
    result = await api.update_drops_entitlements()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/entitlements/drops', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_redeem_code(api: TwitchApi):
    result = await api.redeem_code(code='1', user_id=2)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/entitlements/codes?code=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_redeem_code_exclude_empty(api: TwitchApi):
    result = await api.redeem_code()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/entitlements/codes', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_configuration_segment(api: TwitchApi):
    result = await api.get_extension_configuration_segment(broadcaster_id='1', extension_id='2', segment='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/configurations?broadcaster_id=1&extension_id=2&segment=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_set_extension_configuration_segment(api: TwitchApi):
    result = await api.set_extension_configuration_segment(
        extension_id='1', segment='2', broadcaster_id='3', content='4', version='5'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT',
        'base/extensions/configurations',
        json={'extension_id': '1', 'segment': '2', 'broadcaster_id': '3', 'content': '4', 'version': '5'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_set_extension_configuration_segment_exclude_empty(api: TwitchApi):
    result = await api.set_extension_configuration_segment(extension_id='1', segment='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/extensions/configurations', json={'extension_id': '1', 'segment': '2'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_set_extension_required_configuration(api: TwitchApi):
    result = await api.set_extension_required_configuration(
        broadcaster_id='1', extension_id='2', extension_version='3', configuration_version='4'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT',
        'base/extensions/required_configuration?broadcaster_id=1',
        json={'configuration_version': '4', 'extension_id': '2', 'extension_version': '3'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_send_extension_pubsub_message(api: TwitchApi):
    result = await api.send_extension_pubsub_message(
        target=['1', 'also'], broadcaster_id='2', is_global_broadcast=True, message='4'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/extensions/pubsub',
        json={'broadcaster_id': '2', 'is_global_broadcast': True, 'message': '4', 'target': ['1', 'also']},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_live_channels(api: TwitchApi):
    result = await api.get_live_channels(extension_id='1', first=2, after='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/live?extension_id=1&first=2&after=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_live_channels_exclude_empty(api: TwitchApi):
    result = await api.get_live_channels(extension_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/live?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_secrets(api: TwitchApi):
    result = await api.get_extension_secrets()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/jwt/secrets', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_extension_secret(api: TwitchApi):
    result = await api.create_extension_secret(delay=1)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/extensions/jwt/secrets?delay=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_extension_secret_exclude_empty(api: TwitchApi):
    result = await api.create_extension_secret()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/extensions/jwt/secrets', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_send_extension_chat_message(api: TwitchApi):
    result = await api.send_extension_chat_message(
        broadcaster_id='1', text='2', extension_id='3', extension_version='4'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/extensions/chat?broadcaster_id=1',
        json={'extension_id': '3', 'extension_version': '4', 'text': '2'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extensions(api: TwitchApi):
    result = await api.get_extensions(extension_id='1', extension_version='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions?extension_id=1&extension_version=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extensions_exclude_empty(api: TwitchApi):
    result = await api.get_extensions(extension_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_released_extensions(api: TwitchApi):
    result = await api.get_released_extensions(extension_id='1', extension_version='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/released?extension_id=1&extension_version=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_released_extensions_exclude_empty(api: TwitchApi):
    result = await api.get_released_extensions(extension_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/extensions/released?extension_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_bits_products(api: TwitchApi):
    result = await api.get_extension_bits_products(should_include_all=True)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/bits/extensions?should_include_all=True', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_extension_bits_products_exclude_empty(api: TwitchApi):
    result = await api.get_extension_bits_products()
    api._session.request.assert_called_once_with('GET', 'base/bits/extensions', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_extension_bits_product(api: TwitchApi):
    result = await api.update_extension_bits_product(
        sku='1', cost=dict(key=2), display_name='3', in_development=True, expiration='5', is_broadcast=False
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT',
        'base/bits/extensions',
        json={
            'sku': '1',
            'cost': {'key': 2},
            'display_name': '3',
            'in_development': True,
            'expiration': '5',
            'is_broadcast': False,
        },
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_extension_bits_product_exclude_empty(api: TwitchApi):
    result = await api.update_extension_bits_product(sku='1', cost=dict(key=2), display_name='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/bits/extensions', json={'cost': {'key': 2}, 'display_name': '3', 'sku': '1'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_eventsub_subscription(api: TwitchApi):
    result = await api.create_eventsub_subscription(
        type_='1', version='2', condition=dict(key=3), transport=dict(key=4)
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/eventsub/subscriptions',
        json={'condition': {'key': 3}, 'transport': {'key': 4}, 'type': '1', 'version': '2'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_delete_eventsub_subscription(api: TwitchApi):
    result = await api.delete_eventsub_subscription(id_='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/eventsub/subscriptions?id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_eventsub_subscriptions(api: TwitchApi):
    result = await api.get_eventsub_subscriptions(status='1', type_='2', after='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/eventsub/subscriptions?status=1&type=2&after=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_eventsub_subscriptions_exclude_empty(api: TwitchApi):
    result = await api.get_eventsub_subscriptions()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/eventsub/subscriptions', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_top_games(api: TwitchApi):
    result = await api.get_top_games(after='1', before='2', first=3)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/games/top?after=1&before=2&first=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_top_games_exclude_empty(api: TwitchApi):
    result = await api.get_top_games()
    api._session.request.assert_called_once_with('GET', 'base/games/top', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_games(api: TwitchApi):
    result = await api.get_games(id_='1', name='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/games?id=1&name=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_creator_goals(api: TwitchApi):
    result = await api.get_creator_goals(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/goals?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_hype_train_events(api: TwitchApi):
    result = await api.get_hype_train_events(broadcaster_id='1', first=2, id_='3', cursor='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/hypetrain/events?broadcaster_id=1&first=2&id=3&cursor=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_hype_train_events_exclude_empty(api: TwitchApi):
    result = await api.get_hype_train_events(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/hypetrain/events?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_check_automod_status(api: TwitchApi):
    result = await api.check_automod_status(broadcaster_id='1', msg_id='2', msg_text='3', user_id='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/moderation/enforcements/status?broadcaster_id=1',
        json={'msg_id': '2', 'msg_text': '3', 'user_id': '4'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_manage_held_automod_messages(api: TwitchApi):
    result = await api.manage_held_automod_messages(user_id='1', msg_id='2', action='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/moderation/automod/message', json={'action': '3', 'msg_id': '2', 'user_id': '1'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_banned_events(api: TwitchApi):
    result = await api.get_banned_events(broadcaster_id='1', user_id=['2', 'also'], after='3', first='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/banned/events?broadcaster_id=1&user_id=2&user_id=also&after=3&first=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_banned_events_exclude_empty(api: TwitchApi):
    result = await api.get_banned_events(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/banned/events?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_banned_users(api: TwitchApi):
    result = await api.get_banned_users(broadcaster_id='1', user_id=['2', 'also'], first='3', after='4', before='5')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/banned?broadcaster_id=1&user_id=2&user_id=also&first=3&after=4&before=5', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_banned_users_exclude_empty(api: TwitchApi):
    result = await api.get_banned_users(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/banned?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_moderators(api: TwitchApi):
    result = await api.get_moderators(broadcaster_id='1', user_id=['2', 'also'], first='3', after='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/moderators?broadcaster_id=1&user_id=2&user_id=also&first=3&after=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_moderators_exclude_empty(api: TwitchApi):
    result = await api.get_moderators(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/moderators?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_moderator_events(api: TwitchApi):
    result = await api.get_moderator_events(broadcaster_id='1', user_id=['2', 'also'], after='3', first='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/moderators/events?broadcaster_id=1&user_id=2&user_id=also&after=3&first=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_moderator_events_exclude_empty(api: TwitchApi):
    result = await api.get_moderator_events(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/moderation/moderators/events?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_polls(api: TwitchApi):
    result = await api.get_polls(broadcaster_id='1', id_=['2', 'also'], after='3', first='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/polls?broadcaster_id=1&id=2&id=also&after=3&first=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_polls_exclude_empty(api: TwitchApi):
    result = await api.get_polls(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/polls?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_poll(api: TwitchApi):
    result = await api.create_poll(
        broadcaster_id='1',
        title='2',
        choices=[dict(foo=3), dict(bar='also')],
        duration=4,
        bits_voting_enabled=True,
        bits_per_vote=6,
        channel_points_voting_enabled=False,
        channel_points_per_vote=8,
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/polls',
        json={
            'broadcaster_id': '1',
            'title': '2',
            'choices': [{'foo': 3}, {'bar': 'also'}],
            'duration': 4,
            'bits_voting_enabled': True,
            'bits_per_vote': 6,
            'channel_points_voting_enabled': False,
            'channel_points_per_vote': 8,
        },
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_poll_exclude_empty(api: TwitchApi):
    result = await api.create_poll(broadcaster_id='1', title='2', choices=[dict(foo=3), dict(bar='also')], duration=4)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/polls',
        json={'broadcaster_id': '1', 'choices': [{'foo': 3}, {'bar': 'also'}], 'duration': 4, 'title': '2'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_end_poll(api: TwitchApi):
    result = await api.end_poll(broadcaster_id='1', id_='2', status='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/polls', json={'broadcaster_id': '1', 'id': '2', 'status': '3'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_predictions(api: TwitchApi):
    result = await api.get_predictions(broadcaster_id='1', id_=['2', 'also'], after='3', first='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/predictions?broadcaster_id=1&id=2&id=also&after=3&first=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_predictions_exclude_empty(api: TwitchApi):
    result = await api.get_predictions(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/predictions?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_prediction(api: TwitchApi):
    result = await api.create_prediction(
        broadcaster_id='1', title='2', outcomes=[dict(foo=3), dict(bar='also')], prediction_window=4
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/predictions',
        json={'broadcaster_id': '1', 'outcomes': [{'foo': 3}, {'bar': 'also'}], 'prediction_window': 4, 'title': '2'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_end_prediction(api: TwitchApi):
    result = await api.end_prediction(broadcaster_id='1', id_='2', status='3', winning_outcome_id='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/predictions', json={'broadcaster_id': '1', 'id': '2', 'status': '3', 'winning_outcome_id': '4'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_end_prediction_exclude_empty(api: TwitchApi):
    result = await api.end_prediction(broadcaster_id='1', id_='2', status='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/predictions', json={'broadcaster_id': '1', 'id': '2', 'status': '3'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_stream_schedule(api: TwitchApi):
    result = await api.get_channel_stream_schedule(
        broadcaster_id='1', id_=['2', 'also'], start_time='3', utc_offset='4', first=5, after='6'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/schedule?broadcaster_id=1&id=2&id=also&start_time=3&utc_offset=4&first=5&after=6', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_stream_schedule_exclude_empty(api: TwitchApi):
    result = await api.get_channel_stream_schedule(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/schedule?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_icalendar(api: TwitchApi):
    result = await api.get_channel_icalendar(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/schedule/icalendar?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_channel_stream_schedule(api: TwitchApi):
    result = await api.update_channel_stream_schedule(
        broadcaster_id='1', is_vacation_enabled=True, vacation_start_time='3', vacation_end_time='4', timezone='5'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH',
        'base/schedule/settings'
        '?broadcaster_id=1&is_vacation_enabled=True&vacation_start_time=3&vacation_end_time=4&timezone=5',
        json=None,
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_channel_stream_schedule_exclude_empty(api: TwitchApi):
    result = await api.update_channel_stream_schedule(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/schedule/settings?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_channel_stream_schedule_segment(api: TwitchApi):
    result = await api.create_channel_stream_schedule_segment(
        broadcaster_id='1', start_time='2', timezone='3', is_recurring=True, duration='5', category_id='6', title='7'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
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


@pytest.mark.asyncio
async def test_create_channel_stream_schedule_segment_exclude_empty(api: TwitchApi):
    result = await api.create_channel_stream_schedule_segment(
        broadcaster_id='1', start_time='2', timezone='3', is_recurring=True
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST',
        'base/schedule/segment?broadcaster_id=1',
        json={'is_recurring': True, 'start_time': '2', 'timezone': '3'},
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_channel_stream_schedule_segment(api: TwitchApi):
    result = await api.update_channel_stream_schedule_segment(
        broadcaster_id='1',
        id_='2',
        start_time='3',
        duration='4',
        category_id='5',
        title='6',
        is_canceled=True,
        timezone='8',
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
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


@pytest.mark.asyncio
async def test_update_channel_stream_schedule_segment_exclude_empty(api: TwitchApi):
    result = await api.update_channel_stream_schedule_segment(broadcaster_id='1', id_='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PATCH', 'base/schedule/segment?broadcaster_id=1&id=2', json=dict()
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_delete_channel_stream_schedule_segment(api: TwitchApi):
    result = await api.delete_channel_stream_schedule_segment(broadcaster_id='1', id_='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/schedule/segment?broadcaster_id=1&id=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_search_categories(api: TwitchApi):
    result = await api.search_categories(query='1', first=2, after='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/categories?query=1&first=2&after=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_search_categories_exclude_empty(api: TwitchApi):
    result = await api.search_categories(query='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/categories?query=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_search_channels(api: TwitchApi):
    result = await api.search_channels(query='1', first=2, after='3', live_only=True)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/channels?query=1&first=2&after=3&live_only=True', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_search_channels_exclude_empty(api: TwitchApi):
    result = await api.search_channels(query='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/search/channels?query=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_stream_key(api: TwitchApi):
    result = await api.get_stream_key(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/key?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_streams(api: TwitchApi):
    result = await api.get_streams(
        after='1', before='2', first=3, game_id='4', language='5', user_id='6', user_login='7'
    )
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams?after=1&before=2&first=3&game_id=4&language=5&user_id=6&user_login=7', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_streams_exclude_empty(api: TwitchApi):
    result = await api.get_streams()
    api._session.request.assert_called_once_with('GET', 'base/streams', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_followed_streams(api: TwitchApi):
    result = await api.get_followed_streams(user_id='1', after='2', first=3)
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/followed?user_id=1&after=2&first=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_followed_streams_exclude_empty(api: TwitchApi):
    result = await api.get_followed_streams(user_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/followed?user_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_stream_marker(api: TwitchApi):
    result = await api.create_stream_marker(user_id='1', description='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/streams/markers', json={'description': '2', 'user_id': '1'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_create_stream_marker_exclude_empty(api: TwitchApi):
    result = await api.create_stream_marker(user_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'POST', 'base/streams/markers', json={'user_id': '1'}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_stream_markers(api: TwitchApi):
    result = await api.get_stream_markers(user_id='1', video_id='2', after='3', before='4', first='5')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/markers?user_id=1&video_id=2&after=3&before=4&first=5', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_stream_markers_exclude_empty(api: TwitchApi):
    result = await api.get_stream_markers(user_id='1', video_id='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/markers?user_id=1&video_id=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_broadcaster_subscriptions(api: TwitchApi):
    result = await api.get_broadcaster_subscriptions(broadcaster_id='1', user_id='2', after='3', first='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions?broadcaster_id=1&user_id=2&after=3&first=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_broadcaster_subscriptions_exclude_empty(api: TwitchApi):
    result = await api.get_broadcaster_subscriptions(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_check_user_subscription(api: TwitchApi):
    result = await api.check_user_subscription(broadcaster_id='1', user_id='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=1&user_id=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_all_stream_tags(api: TwitchApi):
    result = await api.get_all_stream_tags(after='1', first=2, tag_id='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/tags/streams?after=1&first=2&tag_id=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_all_stream_tags_exclude_empty(api: TwitchApi):
    result = await api.get_all_stream_tags()
    api._session.request.assert_called_once_with('GET', 'base/tags/streams', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_stream_tags(api: TwitchApi):
    result = await api.get_stream_tags(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/streams/tags?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_replace_stream_tags(api: TwitchApi):
    result = await api.replace_stream_tags(broadcaster_id='1', tag_ids=['2', 'also'])
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/streams/tags?broadcaster_id=1', json={'tag_ids': ['2', 'also']}
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_replace_stream_tags_exclude_empty(api: TwitchApi):
    result = await api.replace_stream_tags(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/streams/tags?broadcaster_id=1', json=dict()
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_channel_teams(api: TwitchApi):
    result = await api.get_channel_teams(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/teams/channel?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_teams(api: TwitchApi):
    result = await api.get_teams(name='1', id_='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/teams?name=1&id=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_teams_exclude_empty(api: TwitchApi):
    result = await api.get_teams()
    api._session.request.assert_called_once_with('GET', 'base/teams', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_users(api: TwitchApi):
    result = await api.get_users(id_=['1', 'also'], login=['2', 'also'])
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users?id=1&id=also&login=2&login=also', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_users_exclude_empty(api: TwitchApi):
    result = await api.get_users()
    api._session.request.assert_called_once_with('GET', 'base/users', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_user(api: TwitchApi):
    result = await api.update_user(description='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users?description=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_user_exclude_empty(api: TwitchApi):
    result = await api.update_user()
    api._session.request.assert_called_once_with('PUT', 'base/users', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_users_follows(api: TwitchApi):
    result = await api.get_users_follows(after='1', first=2, from_id='3', to_id='4')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/follows?after=1&first=2&from_id=3&to_id=4', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_users_follows_exclude_empty(api: TwitchApi):
    result = await api.get_users_follows()
    api._session.request.assert_called_once_with('GET', 'base/users/follows', json=None)  # type: ignore[attr-defined]
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_user_block_list(api: TwitchApi):
    result = await api.get_user_block_list(broadcaster_id='1', first=2, after='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/blocks?broadcaster_id=1&first=2&after=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_user_block_list_exclude_empty(api: TwitchApi):
    result = await api.get_user_block_list(broadcaster_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/blocks?broadcaster_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_block_user(api: TwitchApi):
    result = await api.block_user(target_user_id='1', source_context='2', reason='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users/blocks?target_user_id=1&source_context=2&reason=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_block_user_exclude_empty(api: TwitchApi):
    result = await api.block_user(target_user_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users/blocks?target_user_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_unblock_user(api: TwitchApi):
    result = await api.unblock_user(target_user_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/users/blocks?target_user_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_user_extensions(api: TwitchApi):
    result = await api.get_user_extensions()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/extensions/list', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_user_active_extensions(api: TwitchApi):
    result = await api.get_user_active_extensions(user_id='1')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/extensions?user_id=1', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_user_active_extensions_exclude_empty(api: TwitchApi):
    result = await api.get_user_active_extensions()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/users/extensions', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_update_user_extensions(api: TwitchApi):
    result = await api.update_user_extensions()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'PUT', 'base/users/extensions', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_videos(api: TwitchApi):
    result = await api.get_videos(
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
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET',
        'base/videos?id=1&id=also&user_id=2&game_id=3&after=4&before=5&first=6&language=7&period=8&sort=9&type=10',
        json=None,
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_videos_exclude_empty(api: TwitchApi):
    result = await api.get_videos(id_=['1', 'also'], user_id='2', game_id='3')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/videos?id=1&id=also&user_id=2&game_id=3', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_delete_videos(api: TwitchApi):
    result = await api.delete_videos(id_=['1', 'also'])
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'DELETE', 'base/videos?id=1&id=also', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_webhook_subscriptions(api: TwitchApi):
    result = await api.get_webhook_subscriptions(after='1', first='2')
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/webhooks/subscriptions?after=1&first=2', json=None
    )
    assert result == dict(foo='bar')


@pytest.mark.asyncio
async def test_get_webhook_subscriptions_exclude_empty(api: TwitchApi):
    result = await api.get_webhook_subscriptions()
    api._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/webhooks/subscriptions', json=None
    )
    assert result == dict(foo='bar')
