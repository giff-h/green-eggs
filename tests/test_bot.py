# -*- coding: utf-8 -*-
import asyncio
import datetime
import json
from pathlib import Path
import time

from pytest_mock import MockerFixture

from green_eggs import data_types as dt
from green_eggs.api import TwitchApiCommon

# noinspection PyProtectedMember
from green_eggs.bot import ChatBot, _main_handler
from green_eggs.channel import Channel
from green_eggs.commands import CommandRegistry, FirstWordTrigger, SenderIsModTrigger
from green_eggs.config import Config
from tests import logger
from tests.fixtures import *  # noqa
from tests.utils.compat import coroutine_result_value
from tests.utils.data_types import priv_msg

raw_data = json.loads((Path(__file__).resolve().parent / 'utils' / 'raw_data.json').read_text())

# MAIN LOOP


async def test_main_loop_not_handled(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw='',
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert result is None


async def test_main_loop_message(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    registry.add(FirstWordTrigger('any'), lambda: 'result message', global_cooldown=None, user_cooldown=None)
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['message'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.PrivMsg), type(result)
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :result message'


async def test_main_loop_join_part(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['join part'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.JoinPart), type(result)


async def test_main_loop_clear_chat(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['clear chat'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.ClearChat), type(result)


async def test_main_loop_user_notice(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['user notice'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.UserNotice), type(result)


async def test_main_loop_room_state(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['room state'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.RoomState), type(result)


async def test_main_loop_user_state(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['user state'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.UserState), type(result)


async def test_main_loop_clear_msg(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['clear message'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.ClearMsg), type(result)


async def test_main_loop_notice(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['notice'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Notice), type(result)


async def test_main_loop_host_target(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['host target'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.HostTarget), type(result)


async def test_main_loop_353(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['code 353'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Code353), type(result)


async def test_main_loop_366(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['code 366'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Code366), type(result)


async def test_main_loop_whisper(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['whisper'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Whisper), type(result)


async def test_main_loop_unhandled_tags(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.warning')
    registry = CommandRegistry()
    raw = '@msg-id=host_on;not-a-tag=foo :tmi.twitch.tv NOTICE #channel_user :Now hosting another_user.'
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw,
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Notice)
    logger.warning.assert_called_once_with(  # type: ignore[attr-defined]
        'Unhandled tags on Notice: {\'not_a_tag\': \'foo\'}'
    )


async def test_main_loop_unhandled_msg_params(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.warning')
    registry = CommandRegistry()
    raw = (
        '@badge-info=;badges=;color=#0000FF;display-name=User2;emotes=;flags=;id=d029028b-6061-414c-8a80-ddc296fe92fd;'
        'login=user2;mod=0;msg-id=raid;msg-param-unhandled-value=hello;room-id=123;subscriber=0;'
        'system-msg=3\\sraiders\\sfrom\\sRaiding_Channel\\shave\\sjoined!;tmi-sent-ts=1630899958631;user-id=2;'
        'user-type= :tmi.twitch.tv USERNOTICE #channel_user'
    )
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw,
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.UserNotice)
    logger.warning.assert_called_once_with(  # type: ignore[attr-defined]
        'Unhandled msg params on UserNotice: {\'unhandled_value\': \'hello\'}'
    )


async def test_main_loop_unhandled_badges(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.warning')
    registry = CommandRegistry()
    raw = (
        '@badge-info=subscriber/8;badges=subscriber/6,sub-gifter/5,unhandled-badge/0;color=#FF0000;display-name=UsEr7;'
        'emotes=;flags=;id=85ea8f04-e52e-4849-ab68-011bc135553a;mod=0;room-id=123;subscriber=1;'
        'tmi-sent-ts=1630898786409;turbo=0;user-id=7;user-type= :user7!user7@user7.tmi.twitch.tv PRIVMSG #channel_user '
        ':oops, #testingiscool'
    )
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw,
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.PrivMsg)
    logger.warning.assert_called_once_with(  # type: ignore[attr-defined]
        'Unhandled badges on PrivMsg: {\'unhandled_badge\': \'0\'}'
    )


async def test_main_loop_unhandled_badge_info(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch('aiologger.Logger.warning')
    registry = CommandRegistry()
    raw = (
        '@badge-info=subscriber/8,unhandled-badge/0;badges=subscriber/6,sub-gifter/5;color=#FF0000;display-name=UsEr7;'
        'emotes=;flags=;id=85ea8f04-e52e-4849-ab68-011bc135553a;mod=0;room-id=123;subscriber=1;'
        'tmi-sent-ts=1630898786409;turbo=0;user-id=7;user-type= :user7!user7@user7.tmi.twitch.tv PRIVMSG #channel_user '
        ':oops, #testingiscool'
    )
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw,
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.PrivMsg)
    logger.warning.assert_called_once_with(  # type: ignore[attr-defined]
        'Unhandled badge info on PrivMsg: {\'unhandled_badge\': \'0\'}'
    )


async def test_main_loop_notifies_of_global_cooldown(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    trigger = FirstWordTrigger('any')
    registry.add(trigger, lambda: 'never sent', global_cooldown=1, user_cooldown=None)
    registry[trigger]._last_run = time.monotonic()
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['message'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.PrivMsg)
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :@User1 - That command is on cooldown for 1 more second'
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]


async def test_main_loop_notifies_of_user_cooldown(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    trigger = FirstWordTrigger('Cog')
    registry.add(trigger, lambda: 'never sent', global_cooldown=None, user_cooldown=2)
    registry[trigger]._last_run_for_user['3'] = time.monotonic() - 0.1
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(),
        logger=logger,
        raw=raw_data['message'][3],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.PrivMsg)
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :@USER3 - That command is on cooldown for 1.9 more seconds'
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]


async def test_main_loop_does_not_notify_when_told_not_to(api_common: TwitchApiCommon, channel: Channel):
    registry = CommandRegistry()
    trigger = FirstWordTrigger('Cog')
    registry.add(trigger, lambda: 'never sent', global_cooldown=2, user_cooldown=None)
    registry[trigger]._last_run = time.monotonic() - 0.1
    result = await _main_handler(
        api=api_common,
        channel=channel,
        commands=registry,
        config=Config(should_notify_if_cooldown_has_not_elapsed=False),
        logger=logger,
        raw=raw_data['message'][3],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.PrivMsg)
    assert channel._chat._websocket._send_buffer.empty()  # type: ignore[union-attr]


# BOT CLASS


def test_register_permit_not_by_default():
    bot = ChatBot(channel='channel_user')
    assert not bot._commands


def test_register_permit_default_invoke():
    bot = ChatBot(channel='channel_user', config=dict(should_purge_links=True))
    assert len(bot._commands) == 1
    trigger = next(iter(bot._commands.keys()))
    assert trigger == FirstWordTrigger('!permit') & SenderIsModTrigger()


def test_register_permit_uses_config():
    bot = ChatBot(channel='channel_user', config=dict(should_purge_links=True, link_permit_command_invoke='!antibop'))
    assert len(bot._commands) == 1
    trigger = next(iter(bot._commands.keys()))
    assert trigger == FirstWordTrigger('!antibop') & SenderIsModTrigger()


async def test_permit_adds_permit_for_user(api_common: TwitchApiCommon, channel: Channel):
    bot = ChatBot(channel='channel_user', config=dict(should_purge_links=True, link_permit_duration=0))
    assert len(bot._commands) == 1
    command = bot._commands[FirstWordTrigger('!permit') & SenderIsModTrigger()]
    message = priv_msg(
        handleable_kwargs=dict(message='!permit @GoodUser', who='sender'),
        tags_kwargs=dict(badges_kwargs=dict(moderator='1'), display_name='Sender', mod=True),
    )
    result = await command.run(api=api_common, channel=channel, message=message)
    assert result == 'GoodUser - You have 0 seconds to post one message with links that will not get bopped'
    assert 'gooduser' in channel._permit_cache


async def test_permit_does_nothing_with_existing_permit(api_common: TwitchApiCommon, channel: Channel):
    async def permit_task():
        pass

    bot = ChatBot(channel='channel_user', config=dict(should_purge_links=True, link_permit_duration=0))
    assert len(bot._commands) == 1
    command = bot._commands[FirstWordTrigger('!permit') & SenderIsModTrigger()]
    channel._permit_cache['gooduser'] = asyncio.create_task(permit_task())
    message = priv_msg(
        handleable_kwargs=dict(message='!permit @GoodUser', who='sender'),
        tags_kwargs=dict(badges_kwargs=dict(moderator='1'), display_name='Sender', mod=True),
    )
    result = await command.run(api=api_common, channel=channel, message=message)
    assert result == '@Sender - That user already has a standing permit'
    assert 'gooduser' in channel._permit_cache


async def test_permit_with_no_user_does_nothing(api_common: TwitchApiCommon, channel: Channel):
    bot = ChatBot(channel='channel_user', config=dict(should_purge_links=True, link_permit_duration=0))
    assert len(bot._commands) == 1
    command = bot._commands[FirstWordTrigger('!permit') & SenderIsModTrigger()]
    message = priv_msg(
        handleable_kwargs=dict(message='!permit ', who='sender'),
        tags_kwargs=dict(badges_kwargs=dict(moderator='1'), display_name='Sender', mod=True),
    )
    result = await command.run(api=api_common, channel=channel, message=message)
    assert result == '@Sender - Who do I permit exactly?'
    assert not channel._permit_cache


async def test_register_basic(api_common: TwitchApiCommon, channel: Channel):
    bot = ChatBot(channel='channel_user')
    bot.register_basic_commands({'!command': 'Response message'})
    trigger = FirstWordTrigger('!command')
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!command'))
    )
    assert result == 'Response message'


async def test_register_basic_many(api_common: TwitchApiCommon, channel: Channel):
    bot = ChatBot(channel='channel_user')
    bot.register_basic_commands({'!one': 'Response One', '!two': 'Second Response'})
    trigger = FirstWordTrigger('!one')
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!one')))
    assert result == 'Response One'
    trigger = FirstWordTrigger('!two')
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!two')))
    assert result == 'Second Response'


async def test_register_caster_with_no_name(api_common: TwitchApiCommon, channel: Channel):
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!caster')
    def _caster():
        return 'Never'

    trigger = FirstWordTrigger('!caster') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!caster'))
    )
    assert result == 'No name was given'


async def test_register_caster_with_prior_message(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    channel.handle_message(
        priv_msg(
            handleable_kwargs=dict(where='channel_user', who='streamer'), tags_kwargs=dict(display_name='Streamer')
        )
    )

    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_channel_information',
        return_value=coroutine_result_value(
            dict(
                data=[
                    dict(
                        broadcaster_id='1234',
                        broadcaster_login='streamer',
                        broadcaster_name='Streamer',
                        game_name='The Best Game Ever',
                        game_id='5678',
                        broadcaster_language='en',
                        title='My Stream',
                    )
                ]
            )
        ),
    )
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!so')
    def _caster(display_name, user_link, game_name):
        return f'User {display_name} was playing {game_name} at {user_link}'

    trigger = FirstWordTrigger('!so') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!so streamer'))
    )
    assert result == 'User Streamer was playing The Best Game Ever at https://twitch.tv/streamer'
    api_common.direct.get_channel_information.assert_called_once_with(broadcaster_id='1')  # type: ignore[attr-defined]


async def test_register_caster_without_prior_message(
    api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture
):
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_users',
        return_value=coroutine_result_value(dict(data=[dict(id='135')])),
    )
    mocker.patch(
        'green_eggs.api.direct.TwitchApiDirect.get_channel_information',
        return_value=coroutine_result_value(
            dict(
                data=[
                    dict(
                        broadcaster_id='135',
                        broadcaster_login='other_streamer',
                        broadcaster_name='Other_Streamer',
                        game_name='The Other Best Game Ever',
                        game_id='579',
                        broadcaster_language='en',
                        title='My Other Stream',
                    )
                ]
            )
        ),
    )
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!shoutout')
    async def _caster(
        user_id, username, display_name, game_name, game_id, broadcaster_language, stream_title, user_link
    ):
        assert user_id == '135'
        assert username == 'other_streamer'
        assert game_id == '579'
        assert broadcaster_language == 'en'
        assert stream_title == 'My Other Stream'
        return f'User {display_name} was found playing {game_name} at {user_link}'

    trigger = FirstWordTrigger('!shoutout') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!shoutout @Other_Streamer'))
    )
    assert (
        result == 'User Other_Streamer was found playing The Other Best Game Ever at '
        'https://twitch.tv/other_streamer'
    )
    api_common.direct.get_users.assert_called_once_with(login='Other_Streamer')  # type: ignore[attr-defined]
    api_common.direct.get_channel_information.assert_called_once_with(  # type: ignore[attr-defined]
        broadcaster_id='135'
    )


async def test_register_caster_no_user_found(api_common: TwitchApiCommon, channel: Channel, mocker: MockerFixture):
    mocker.patch('green_eggs.api.direct.TwitchApiDirect.get_users', return_value=coroutine_result_value(dict(data=[])))
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!nope')
    def _caster():
        return None

    trigger = FirstWordTrigger('!nope') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!nope whoever'))
    )
    assert result == 'Could not find data for whoever'


async def test_register_command(api_common: TwitchApiCommon, channel: Channel):
    bot = ChatBot(channel='channel_user')

    @bot.register_command('!hello')
    def _hello():
        return 'World'

    trigger = FirstWordTrigger('!hello')
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api_common, channel=channel, message=priv_msg(handleable_kwargs=dict(message='!hello'))
    )
    assert result == 'World'
