# -*- coding: utf-8 -*-
import datetime
import json
from pathlib import Path
import sys

import pytest
from pytest_mock import MockerFixture

from green_eggs import data_types as dt
from green_eggs.api import TwitchApi

# noinspection PyProtectedMember
from green_eggs.bot import ChatBot, _main_handler
from green_eggs.channel import Channel
from green_eggs.commands import CommandRegistry, FirstWordTrigger, SenderIsModTrigger
from tests import logger
from tests.fixtures import *  # noqa
from tests.utils.data_types import priv_msg

raw_data = json.loads((Path(__file__).resolve().parent / 'utils' / 'raw_data.json').read_text())


@pytest.mark.asyncio
async def test_main_loop_not_handled(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api, channel=channel, commands=registry, logger=logger, raw='', default_timestamp=datetime.datetime.utcnow()
    )
    assert result is None


@pytest.mark.asyncio
async def test_main_loop_message(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    registry.add(FirstWordTrigger('any'), lambda: 'result message')
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['message'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.PrivMsg), type(result)
    sent = channel._chat._websocket._send_buffer.get_nowait()  # type: ignore[union-attr]
    assert sent == 'PRIVMSG #channel_user :result message'


@pytest.mark.asyncio
async def test_main_loop_join_part(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['join part'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.JoinPart), type(result)


@pytest.mark.asyncio
async def test_main_loop_clear_chat(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['clear chat'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.ClearChat), type(result)


@pytest.mark.asyncio
async def test_main_loop_user_notice(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    raw = (
        '@badge-info=;badges=;color=#0000FF;display-name=User2;emotes=;flags=;id=d029028b-6061-414c-8a80-ddc296fe92fd;'
        'login=user2;mod=0;msg-id=raid;msg-param-unhandled-value=hello;room-id=123;subscriber=0;'
        'system-msg=3\\sraiders\\sfrom\\sRaiding_Channel\\shave\\sjoined!;tmi-sent-ts=1630899958631;user-id=2;'
        'user-type=;unhandled-tag=hello :tmi.twitch.tv USERNOTICE #channel_user'
    )
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw,
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.UserNotice), type(result)


@pytest.mark.asyncio
async def test_main_loop_room_state(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['room state'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.RoomState), type(result)


@pytest.mark.asyncio
async def test_main_loop_user_state(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['user state'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.UserState), type(result)


@pytest.mark.asyncio
async def test_main_loop_clear_msg(api: TwitchApi, channel: Channel):
    raw = (
        '@login=user1;target-msg-id=57ee3aef-209e-4ca4-a010-a4ddf9e4a536;tmi-sent-ts=1630898681696 '
        ':tmi.twitch.tv CLEARMSG #channel_user :deleted'
    )
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw,
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.ClearMsg), type(result)


@pytest.mark.asyncio
async def test_main_loop_notice(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['notice'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Notice), type(result)


@pytest.mark.asyncio
async def test_main_loop_host_target(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['host target'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.HostTarget), type(result)


@pytest.mark.asyncio
async def test_main_loop_353(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw_data['code 353'][0],
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Code353), type(result)


@pytest.mark.asyncio
async def test_main_loop_366(api: TwitchApi, channel: Channel):
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=':bot_user.tmi.twitch.tv 366 bot_user #channel_user :End of /NAMES list',
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Code366), type(result)


@pytest.mark.asyncio
async def test_main_loop_whisper(api: TwitchApi, channel: Channel):
    raw = (
        '@badges=;color=#ABCDEF;display-name=User1;emotes=;message-id=1;thread-id=2;user-id=3 '
        ':user1!user1@user1.tmi.twitch.tv WHISPER #channel_user :psst'
    )
    registry = CommandRegistry()
    result = await _main_handler(
        api=api,
        channel=channel,
        commands=registry,
        logger=logger,
        raw=raw,
        default_timestamp=datetime.datetime.utcnow(),
    )
    assert isinstance(result, dt.Whisper), type(result)


@pytest.mark.asyncio
async def test_register_basic(api: TwitchApi, channel: Channel):
    bot = ChatBot(channel='channel_user')
    bot.register_basic_commands({'!command': 'Response message'})
    trigger = FirstWordTrigger('!command')
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(api=api, channel=channel, message=priv_msg(handle_able_kwargs=dict(message='!command')))
    assert result == 'Response message'


@pytest.mark.asyncio
async def test_register_caster_with_no_name(api: TwitchApi, channel: Channel):
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!caster')
    def _caster():
        return 'Never'

    trigger = FirstWordTrigger('!caster') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(api=api, channel=channel, message=priv_msg(handle_able_kwargs=dict(message='!caster')))
    assert result == 'I need a name for that'


@pytest.mark.asyncio
async def test_register_caster_with_prior_message(api: TwitchApi, channel: Channel, mocker: MockerFixture):
    channel.handle_message(
        priv_msg(
            handle_able_kwargs=dict(where='channel_user', who='streamer'), tags_kwargs=dict(display_name='Streamer')
        )
    )

    async def get_channel_information():
        return dict(data=[dict(game_name='The Best Game Ever')])

    if sys.version_info[:2] == (3, 7):
        mocker.patch('green_eggs.api.TwitchApi.get_channel_information', return_value=get_channel_information())
    else:
        mocker.patch('green_eggs.api.TwitchApi.get_channel_information', return_value=await get_channel_information())
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!so')
    def _caster(name, link, game):
        return f'User {name} was playing {game} at {link}'

    trigger = FirstWordTrigger('!so') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api, channel=channel, message=priv_msg(handle_able_kwargs=dict(message='!so streamer'))
    )
    assert result == 'User Streamer was playing The Best Game Ever at https://twitch.tv/streamer'
    api.get_channel_information.assert_called_once_with(broadcaster_id='1')  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_register_caster_without_prior_message(api: TwitchApi, channel: Channel, mocker: MockerFixture):
    async def get_users():
        return dict(data=[dict(id='123', display_name='Other_Streamer', login='other_streamer')])

    async def get_channel_information():
        return dict(data=[dict(game_name='The Next Best Game Ever')])

    if sys.version_info[:2] == (3, 7):
        mocker.patch('green_eggs.api.TwitchApi.get_users', return_value=get_users())
        mocker.patch('green_eggs.api.TwitchApi.get_channel_information', return_value=get_channel_information())
    else:
        mocker.patch('green_eggs.api.TwitchApi.get_users', return_value=await get_users())
        mocker.patch('green_eggs.api.TwitchApi.get_channel_information', return_value=await get_channel_information())
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!shoutout')
    async def _caster(name, link, game, api_result):
        assert api_result == dict(game_name='The Next Best Game Ever')
        return f'User {name} was found playing {game} at {link}'

    trigger = FirstWordTrigger('!shoutout') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api, channel=channel, message=priv_msg(handle_able_kwargs=dict(message='!shoutout Other_Streamer'))
    )
    assert result == 'User Other_Streamer was found playing The Next Best Game Ever at https://twitch.tv/other_streamer'
    api.get_users.assert_called_once_with(login='Other_Streamer')  # type: ignore[attr-defined]
    api.get_channel_information.assert_called_once_with(broadcaster_id='123')  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_register_caster_no_user_found(api: TwitchApi, channel: Channel, mocker: MockerFixture):
    async def get_users():
        return dict(data=[])

    if sys.version_info[:2] == (3, 7):
        mocker.patch('green_eggs.api.TwitchApi.get_users', return_value=get_users())
    else:
        mocker.patch('green_eggs.api.TwitchApi.get_users', return_value=await get_users())
    bot = ChatBot(channel='channel_user')

    @bot.register_caster_command('!nope')
    def _caster():
        return None

    trigger = FirstWordTrigger('!nope') & SenderIsModTrigger()
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(
        api=api, channel=channel, message=priv_msg(handle_able_kwargs=dict(message='!nope whoever'))
    )
    assert result == 'Could not find user data for whoever'


@pytest.mark.asyncio
async def test_register_command(api: TwitchApi, channel: Channel):
    bot = ChatBot(channel='channel_user')

    @bot.register_command('!hello')
    def _hello():
        return 'World'

    trigger = FirstWordTrigger('!hello')
    assert trigger in bot._commands
    runner = bot._commands[trigger]
    result = await runner.run(api=api, channel=channel, message=priv_msg(handle_able_kwargs=dict(message='!hello')))
    assert result == 'World'
