# -*- coding: utf-8 -*-
import asyncio

from pytest_mock import MockerFixture

from green_eggs.api import TwitchApiCommon
from green_eggs.channel import Channel
from green_eggs.config import LinkAllowUserConditions, LinkPurgeActions
from tests import response_context
from tests.fixtures import *  # noqa
from tests.utils.compat import coroutine_result_value
from tests.utils.data_types import code_353, join_part, priv_msg, room_state


async def test_add_permit_for_user_false_if_already_permit(channel: Channel):
    async def permit_task():
        pass

    channel._permit_cache['user'] = asyncio.create_task(permit_task())
    result = channel.add_permit_for_user('User')
    assert not result


async def test_add_permit_for_user_true_if_permit_added(channel: Channel):
    channel._config.link_permit_duration = 0
    result = channel.add_permit_for_user('user')
    assert result
    assert 'user' in channel._permit_cache
    await asyncio.sleep(0.01)
    assert 'user' not in channel._permit_cache


async def test_add_permit_for_user_fine_if_permit_cleared(channel: Channel):
    channel._config.link_permit_duration = 0
    result = channel.add_permit_for_user('user')
    assert result
    assert 'user' in channel._permit_cache
    del channel._permit_cache['user']
    await asyncio.sleep(0.01)
    assert 'user' not in channel._permit_cache


async def test_check_for_links_does_nothing_by_default(api_common: TwitchApiCommon, channel: Channel):
    assert not await channel.check_for_links(
        priv_msg(handle_able_kwargs=dict(message='Go to youtube.com'), tags_kwargs=dict(id='message-with-link'))
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


async def test_check_for_links_deletes_message(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    mocker.patch('aiologger.Logger.debug')
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    assert await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com', who='sender'),
            tags_kwargs=dict(display_name='Sender', id='message-with-link'),
        )
    )
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :/delete message-with-link'
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :@Sender - Please no posting links without permission'
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )
    channel._logger.debug.assert_any_call(  # type: ignore[attr-defined]
        'Purging link(s) from sender: [\'youtube.com\']'
    )


async def test_check_for_links_times_out_sender(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.TIMEOUT_FLAT
    assert await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com', who='sender'),
            tags_kwargs=dict(display_name='Sender', id='message-with-link'),
        )
    )
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :/timeout sender 1 Link detected'
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :@Sender - Please no posting links without permission'
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )


async def test_check_for_links_sends_no_message_after_if_blank(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_purge_message_after_action = ''
    assert await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(display_name='Sender', id='message-with-link'),
        )
    )
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :/delete message-with-link'
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )


async def test_check_for_links_allows_permitted(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.debug')

    async def permit_task():
        pass

    channel._permit_cache['sender'] = asyncio.create_task(permit_task())
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_allow_user_condition = LinkAllowUserConditions.NOTHING
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com', who='sender'),
            tags_kwargs=dict(display_name='Sender', id='message-with-link'),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]
    channel._logger.debug.assert_called_once_with(  # type: ignore[attr-defined]
        'Link(s) allowed because permit: [\'youtube.com\']'
    )


async def test_check_for_links_allows_permitted_after_message_without_link(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch('aiologger.Logger.debug')

    async def permit_task():
        pass

    channel._permit_cache['sender'] = asyncio.create_task(permit_task())
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_allow_user_condition = LinkAllowUserConditions.NOTHING
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='No link here', who='sender'),
            tags_kwargs=dict(display_name='Sender', id='message-without-link'),
        )
    )
    assert 'sender' in channel._permit_cache
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com', who='sender'),
            tags_kwargs=dict(display_name='Sender', id='message-with-link'),
        )
    )
    assert 'sender' not in channel._permit_cache
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]
    channel._logger.debug.assert_called_once_with(  # type: ignore[attr-defined]
        'Link(s) allowed because permit: [\'youtube.com\']'
    )


async def test_check_for_links_allows_vip_by_default(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    mocker.patch('aiologger.Logger.debug')
    channel._config.purge_links = True
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(badges_kwargs=dict(vip='1'), id='message-with-link'),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )
    channel._logger.debug.assert_called_once_with(  # type: ignore[attr-defined]
        'Link(s) allowed because VIP: [\'youtube.com\']'
    )


async def test_check_for_links_allows_subscriber_if_told_to(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    mocker.patch('aiologger.Logger.debug')
    channel._config.purge_links = True
    channel._config.link_allow_user_condition = LinkAllowUserConditions.USER_SUBSCRIBED
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(
                badge_info_kwargs=dict(subscriber='7'), badges_kwargs=dict(subscriber='2006'), id='message-with-link'
            ),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )
    channel._logger.debug.assert_called_once_with(  # type: ignore[attr-defined]
        'Link(s) allowed because subscribed: [\'youtube.com\']'
    )


async def test_check_for_links_allows_subscriber_if_told_to_with_api(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.check_user_subscription',
        return_value=coroutine_result_value(dict(data=[dict(tier='1')])),
    )
    channel._config.purge_links = True
    channel._config.link_allow_user_condition = LinkAllowUserConditions.USER_SUBSCRIBED
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(id='message-with-link', user_id='subbed-id'),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )
    api_common.direct.check_user_subscription.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', user_id='subbed-id'
    )


async def test_check_for_links_allows_subbed_vip_if_config_allows_sub_not_vip(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    channel._config.purge_links = True
    channel._config.link_allow_user_condition = LinkAllowUserConditions.USER_SUBSCRIBED
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(
                badge_info_kwargs=dict(subscriber='1'),
                badges_kwargs=dict(subscriber='1', vip='1'),
                id='message-with-link',
            ),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )


async def test_check_for_links_allows_subscriber_if_config_allows_subs_and_vip(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    mocker.patch('aiologger.Logger.debug')
    channel._config.purge_links = True
    channel._config.link_allow_user_condition = (
        LinkAllowUserConditions.USER_VIP | LinkAllowUserConditions.USER_SUBSCRIBED
    )
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com now'),
            tags_kwargs=dict(
                badge_info_kwargs=dict(subscriber='1'), badges_kwargs=dict(subscriber='1'), id='message-with-link'
            ),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )
    channel._logger.debug.assert_called_once_with(  # type: ignore[attr-defined]
        'Link(s) allowed because subscribed: [\'youtube.com\']'
    )


async def test_check_for_links_deletes_vip_if_told_by_default(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_allow_user_condition = LinkAllowUserConditions.NOTHING
    assert await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(badges_kwargs=dict(vip='1'), id='message-with-link'),
        )
    )
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :/delete message-with-link'
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )


async def test_check_for_links_allows_moderator_always(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch('aiologger.Logger.debug')
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_allow_user_condition = LinkAllowUserConditions.NOTHING
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(badges_kwargs=dict(moderator='1'), id='message-with-link', mod=True),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]
    channel._logger.debug.assert_called_once_with(  # type: ignore[attr-defined]
        'Link(s) allowed because moderator: [\'youtube.com\']'
    )


async def test_check_for_links_allows_moderator_checks_api(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators',
        return_value=coroutine_result_value(dict(data=[dict(user_id='mod-id')])),
    )
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_allow_user_condition = LinkAllowUserConditions.NOTHING
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Go to youtube.com'),
            tags_kwargs=dict(id='message-with-link', user_id='mod-id'),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )


async def test_check_for_links_allows_valid_link_format(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch('aiologger.Logger.debug')
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_allow_target_conditions = [dict(domain='clips.twitch.tv')]
    assert not await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(message='Just clipped this https://clips.twitch.tv/ABCD-srao89esir2ua'),
            tags_kwargs=dict(id='message-with-link'),
        )
    )
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]
    channel._logger.debug.assert_called_once_with(  # type: ignore[attr-defined]
        'Link(s) allowed by target format: [\'https://clips.twitch.tv/ABCD-srao89esir2ua\']'
    )


async def test_check_for_links_unhandled_link_purge_action(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    channel._config.purge_links = True
    channel._config.link_purge_action = 'THIS WILL NEVER BE A PURGE ACTION'  # type: ignore[assignment]
    channel._config.link_allow_user_condition = LinkAllowUserConditions.NOTHING
    try:
        await channel.check_for_links(priv_msg(handle_able_kwargs=dict(message='Go to youtube.com')))
    except ValueError as e:
        assert e.args[0] == 'Unhandled link purge action: \'THIS WILL NEVER BE A PURGE ACTION\''
    else:
        assert False, 'No exception'


async def test_check_for_links_allows_valid_link_format_and_purges_invalid(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators', return_value=coroutine_result_value(dict(data=[]))
    )
    mocker.patch('aiologger.Logger.debug')
    channel._config.purge_links = True
    channel._config.link_purge_action = LinkPurgeActions.DELETE
    channel._config.link_allow_target_conditions = [dict(domain='clips.twitch.tv')]
    assert await channel.check_for_links(
        priv_msg(
            handle_able_kwargs=dict(
                message='Just clipped this https://clips.twitch.tv/ABCD-sNCuhds4g403 gonna upload it to youtube.com',
                who='sender',
            ),
            tags_kwargs=dict(id='message-with-links'),
        )
    )
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :/delete message-with-links'
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )
    channel._logger.debug.assert_any_call(  # type: ignore[attr-defined]
        'Link(s) allowed by target format: [\'https://clips.twitch.tv/ABCD-sNCuhds4g403\']'
    )
    channel._logger.debug.assert_any_call(  # type: ignore[attr-defined]
        'Purging link(s) from sender: [\'youtube.com\']'
    )


def test_code_353(channel: Channel):
    channel._users_in_channel = {'user1', 'already_here'}
    channel.handle_code_353(code_353('user1', 'user2', 'another_user', where='channel_user'))
    assert channel._users_in_channel == {'user1', 'user2', 'another_user', 'already_here'}


def test_code_353_wrong_channel(channel: Channel):
    try:
        channel.handle_code_353(code_353('user1', 'user2', 'another_user', where='wrong_channel'))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a code353 from wrong_channel'
    else:
        assert False


def test_join(channel: Channel):
    channel._users_in_channel = {'user1', 'already_here'}
    channel._users_in_channel_tmp = {'other_user'}
    channel.handle_join_part(join_part(True, who='new_user', where='channel_user'))
    assert channel._users_in_channel == {'user1', 'already_here', 'new_user'}
    assert channel._users_in_channel_tmp == set()


def test_part(channel: Channel):
    channel._users_in_channel = {'user1', 'already_here'}
    channel._users_in_channel_tmp = {'other_user'}
    channel.handle_join_part(join_part(False, who='already_here', where='channel_user'))
    assert channel._users_in_channel == {'user1'}
    assert channel._users_in_channel_tmp == set()


def test_join_part_wrong_channel(channel: Channel):
    try:
        channel.handle_join_part(join_part(where='wrong_channel'))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a join/part from wrong_channel'
    else:
        assert False


def test_message(channel: Channel):
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user', who='message_sender'), tags_kwargs=dict(user_id='123')
    )
    channel.handle_message(message)
    assert channel._users_in_channel_tmp == {'message_sender'}
    assert '123' in channel._last_five_for_user_id
    assert list(channel._last_five_for_user_id['123']) == [message]


def test_message_max_five(channel: Channel):
    message = priv_msg(
        handle_able_kwargs=dict(where='channel_user', who='message_sender'), tags_kwargs=dict(user_id='123')
    )
    for _ in range(6):
        channel.handle_message(message)
    assert len(channel._last_five_for_user_id['123']) == 5


def test_message_wrong_channel(channel: Channel):
    try:
        channel.handle_message(priv_msg(handle_able_kwargs=dict(where='wrong_channel')))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a message from wrong_channel'
    else:
        assert False


def test_room_state(channel: Channel):
    channel.handle_room_state(
        room_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    )
    assert channel.broadcaster_id == '123'


def test_room_state_wrong_channel(channel: Channel):
    try:
        channel.handle_room_state(room_state(handle_able_kwargs=dict(where='wrong_channel')))
    except ValueError as e:
        assert e.args[0] == 'Channel for channel_user was given a room state from wrong_channel'
        assert channel.broadcaster_id == ''
    else:
        assert False


def test_is_user_in_channel(channel: Channel):
    channel._users_in_channel.update(('user1', 'user2'))
    channel._users_in_channel_tmp.update(('user1', 'other_user'))
    assert channel.is_user_in_channel('user1')
    assert channel.is_user_in_channel('user2')
    assert channel.is_user_in_channel('other_user')
    assert not channel.is_user_in_channel('not_found')


async def test_is_user_moderator_true_with_broadcaster_id(api_common: TwitchApiCommon, channel: Channel):
    channel.handle_room_state(
        room_state(handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(room_id='123'))
    )
    result = await channel.is_user_moderator('123')
    assert result
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


async def test_is_user_moderator_true_if_they_sent_moderator_messages(api_common: TwitchApiCommon, channel: Channel):
    channel.handle_message(
        priv_msg(
            handle_able_kwargs=dict(message='Hi', where='channel_user'),
            tags_kwargs=dict(badges_kwargs=dict(moderator='1'), mod=True, user_id='mod-id'),
        )
    )
    result = await channel.is_user_moderator('mod-id')
    assert result
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


async def test_is_user_moderator_true_if_api_says_so(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators',
        return_value=coroutine_result_value(dict(data=[dict(user_id='mod-id')])),
    )
    result = await channel.is_user_moderator('mod-id')
    assert result
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )


async def test_is_user_moderator_false_if_they_sent_non_moderator_messages(
    api_common: TwitchApiCommon, channel: Channel
):
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(message='Hi', where='channel_user'), tags_kwargs=dict(user_id='not-mod-id'))
    )
    result = await channel.is_user_moderator('not-mod-id')
    assert not result
    api_common.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


async def test_is_user_moderator_false_if_the_api_says_so(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_moderators',
        return_value=coroutine_result_value(dict(data=[dict(user_id='mod-id')])),
    )
    result = await channel.is_user_moderator('not-mod-id')
    assert not result
    api_common.direct.get_moderators.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='', first='100'
    )


async def test_is_user_subscribed_with_messages(channel: Channel):
    message_subscribed = priv_msg(
        handle_able_kwargs=dict(where='channel_user'),
        tags_kwargs=dict(user_id='123', badges_kwargs=dict(subscriber='1')),
    )
    message_not_subscribed = priv_msg(
        handle_able_kwargs=dict(where='channel_user'), tags_kwargs=dict(user_id='123', badges_kwargs=dict())
    )
    channel.handle_message(message_subscribed)
    channel.handle_message(message_not_subscribed)
    assert await channel.is_user_subscribed('123')
    assert '123' not in channel._api_results_cache
    channel._api.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


async def test_is_user_subscribed_with_api(channel: Channel):
    channel._api.direct._session.request.return_value = response_context(  # type: ignore[attr-defined]
        return_json=dict(data=[dict(tier='1000')])
    )
    assert '123' not in channel._api_results_cache
    assert await channel.is_user_subscribed('123')
    assert '123' in channel._api_results_cache
    channel._api.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=&user_id=123', json=None
    )


async def test_is_user_subscribed_false_with_api(channel: Channel):
    channel._api.direct._session.request.return_value = response_context(  # type: ignore[attr-defined]
        return_json=dict(data=[dict()])
    )
    assert '123' not in channel._api_results_cache
    assert not await channel.is_user_subscribed('123')
    assert '123' in channel._api_results_cache
    channel._api.direct._session.request.assert_called_once_with(  # type: ignore[attr-defined]
        'GET', 'base/subscriptions/user?broadcaster_id=&user_id=123', json=None
    )


async def test_is_user_subscribed_with_cache(channel: Channel):
    channel._api_results_cache['123'] = dict(is_subscribed=True)
    assert await channel.is_user_subscribed('123')
    channel._api.direct._session.request.assert_not_called()  # type: ignore[attr-defined]


def test_is_user_vip_true_if_they_sent_vip_messages(channel: Channel):
    channel.handle_message(
        priv_msg(
            handle_able_kwargs=dict(message='Hi', where='channel_user'),
            tags_kwargs=dict(badges_kwargs=dict(vip='1'), user_id='vip-id'),
        )
    )
    result = channel.is_user_vip('vip-id')
    assert result


def test_is_user_vip_false_if_they_sent_no_messages(channel: Channel):
    result = channel.is_user_vip('not-vip-id')
    assert not result


def test_is_user_vip_false_if_they_sent_non_vip_messages(channel: Channel):
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(message='Hi', where='channel_user'), tags_kwargs=dict(user_id='not-vip-id'))
    )
    result = channel.is_user_vip('not-vip-id')
    assert not result


def test_user_latest_message_none(channel: Channel):
    channel.handle_message(priv_msg(handle_able_kwargs=dict(where='channel_user', who='other_user')))
    assert channel.user_latest_message('login') is None


def test_user_latest_message_login(channel: Channel):
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(where='channel_user', who='user_login', message='message one'))
    )
    channel.handle_message(
        priv_msg(handle_able_kwargs=dict(where='channel_user', who='user_login', message='message two'))
    )
    result = channel.user_latest_message('User_Login')
    assert result is not None
    assert result.message == 'message two'


def test_user_latest_message_display(channel: Channel):
    channel.handle_message(
        priv_msg(
            handle_able_kwargs=dict(where='channel_user', message='message one'),
            tags_kwargs=dict(display_name='User_Login'),
        )
    )
    channel.handle_message(
        priv_msg(
            handle_able_kwargs=dict(where='channel_user', message='message two'),
            tags_kwargs=dict(display_name='User_Login'),
        )
    )
    result = channel.user_latest_message('User_login')
    assert result is not None
    assert result.message == 'message two'


async def test_send(channel: Channel):
    await channel.send('message content')
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :message content'


async def test_send_too_long(channel: Channel):
    try:
        await channel.send('A' * 501)
    except ValueError as e:
        assert e.args[0] == 'Messages cannot exceed 500 characters'
    else:
        assert False
