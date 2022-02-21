# -*- coding: utf-8 -*-
import asyncio
import datetime
from typing import Any, Dict, List, Mapping, Optional

from aiologger import Logger

from green_eggs import data_types as dt
from green_eggs.api import TwitchApiCommon
from green_eggs.channel import Channel
from green_eggs.client import TwitchChatClient
from green_eggs.commands import CommandRegistry, FirstWordTrigger, SenderIsModTrigger
from green_eggs.config import Config
from green_eggs.data_types import PrivMsg
from green_eggs.types import RegisterAbleFunc
from green_eggs.utils import catch_all


async def _main_handler(
    *,
    api: TwitchApiCommon,
    channel: Channel,
    commands: CommandRegistry,
    logger: Logger,
    raw: str,
    default_timestamp: datetime.datetime,
) -> Optional[dt.HandleAble]:
    handle_able: Optional[dt.HandleAble] = None

    for handle_type, pattern in dt.patterns.items():
        found = pattern.match(raw)
        if found is not None:
            handle_able = handle_type.from_match_dict(default_timestamp=default_timestamp, raw=raw, **found.groupdict())
            break

    if handle_able is None:
        logger.warning(f'Incoming message could not be parsed: {raw!r}')
        return None

    if isinstance(handle_able, dt.HasTags):
        if len(handle_able.tags.unhandled):
            type_name = type(handle_able.tags).__qualname__
            unhandled = handle_able.tags.unhandled
            logger.warning(f'Unhandled on {type_name}: {unhandled!r}')
        if isinstance(handle_able.tags, dt.UserNoticeTags):
            if len(handle_able.tags.msg_params.unhandled):
                type_name = type(handle_able.tags.msg_params).__qualname__
                unhandled = handle_able.tags.msg_params.unhandled
                logger.warning(f'Unhandled on {type_name}: {unhandled!r}')

    if isinstance(handle_able, dt.PrivMsg):
        channel.handle_message(handle_able)
        if not await channel.check_for_links(handle_able):
            command = await commands.find(handle_able, channel)
            if command is not None:
                result = await command.run(api=api, channel=channel, message=handle_able)
                if isinstance(result, str):
                    await channel.send(result)

    elif isinstance(handle_able, dt.JoinPart):
        channel.handle_join_part(handle_able)

    elif isinstance(handle_able, dt.ClearChat):
        pass

    elif isinstance(handle_able, dt.UserNotice):
        pass

    elif isinstance(handle_able, dt.RoomState):
        channel.handle_room_state(handle_able)

    elif isinstance(handle_able, dt.UserState):
        pass

    elif isinstance(handle_able, dt.ClearMsg):
        pass

    elif isinstance(handle_able, dt.Notice):
        pass

    elif isinstance(handle_able, dt.HostTarget):
        pass

    elif isinstance(handle_able, dt.Code353):
        channel.handle_code_353(handle_able)

    elif isinstance(handle_able, dt.Code366):
        pass

    elif isinstance(handle_able, dt.Whisper):
        pass

    return handle_able


class ChatBot:
    def __init__(self, *, channel: str, config: Dict[str, Any] = None):
        self._channel: str = channel
        self._commands = CommandRegistry()
        self._config = Config.from_python(**(config or dict()))

        if self._config.purge_links:
            self._register_permit_command()

    def _register_permit_command(self):
        def permit(channel: Channel, message: PrivMsg):
            if len(message.words) > 1:
                username = message.words[1].lstrip('@')
                if username:
                    if channel.add_permit_for_user(username):
                        return (
                            f'{username} - You have {self._config.link_permit_duration} seconds '
                            f'to post one message with links that will not get bopped'
                        )
                    else:
                        return f'@{message.tags.display_name} - That user already has a standing permit'
            return f'@{message.tags.display_name} - Who do I permit exactly?'

        trigger = FirstWordTrigger(self._config.link_permit_command_invoke) & SenderIsModTrigger()
        self._commands.decorator(trigger)(permit)

    def register_basic_commands(self, commands: Mapping[str, str], *, case_sensitive=False):
        """
        Register basic message response commands.

        :param commands: Mapping of invoke to response strings
        :param bool case_sensitive: Whether the command should trigger on exact case or any case
        """

        # This factory is necessary to keep the namespace of `output` from getting overwritten in the loop
        def factory(output):
            def basic():
                return output

            return basic

        for invoke, response in commands.items():
            trigger = FirstWordTrigger(invoke, case_sensitive)
            self._commands.add(trigger, factory(response))

    def register_caster_command(self, invoke: str, *, case_sensitive=False):
        """
        Decorator to register a function as a caster command handler.

        :param str invoke: The command part in the chat message
        :param bool case_sensitive: Whether the command should trigger on exact case or any case
        :return: The decorator
        """
        trigger = FirstWordTrigger(invoke, case_sensitive) & SenderIsModTrigger()

        def factory(callback: RegisterAbleFunc, callback_keywords: List[str]) -> RegisterAbleFunc:
            async def command(api: TwitchApiCommon, channel: Channel, message: dt.PrivMsg) -> Optional[str]:
                if len(message.words) <= 1:
                    return 'No name was given'

                callback_kwargs = dict()
                name = message.words[1].lstrip('@')
                last_message = channel.user_latest_message(name)
                if last_message is None:
                    shoutout_info = await api.get_shoutout_info(username=name)
                else:
                    shoutout_info = await api.get_shoutout_info(user_id=last_message.tags.user_id)

                if shoutout_info is None:
                    return f'Could not find data for {name}'

                if 'user_id' in callback_keywords:
                    callback_kwargs['user_id'] = shoutout_info.user_id
                if 'username' in callback_keywords:
                    callback_kwargs['username'] = shoutout_info.username
                if 'display_name' in callback_keywords:
                    callback_kwargs['display_name'] = shoutout_info.display_name
                if 'game_name' in callback_keywords:
                    callback_kwargs['game_name'] = shoutout_info.game_name
                if 'game_id' in callback_keywords:
                    callback_kwargs['game_id'] = shoutout_info.game_id
                if 'broadcaster_language' in callback_keywords:
                    callback_kwargs['broadcaster_language'] = shoutout_info.broadcaster_language
                if 'stream_title' in callback_keywords:
                    callback_kwargs['stream_title'] = shoutout_info.stream_title
                if 'user_link' in callback_keywords:
                    callback_kwargs['user_link'] = shoutout_info.user_link

                output = callback(**callback_kwargs)
                if output is None or isinstance(output, str):
                    return output
                else:
                    return await output

            return command

        return self._commands.decorator(
            trigger,
            target_keywords=[
                'user_id',
                'username',
                'display_name',
                'game_name',
                'game_id',
                'broadcaster_language',
                'stream_title',
                'user_link',
            ],
            command_factory=factory,
        )

    def register_command(self, invoke: str, *, case_sensitive=False):
        """
        Decorator to register a function as a command handler.

        :param str invoke: The command part in the chat message
        :param bool case_sensitive: Whether the command should trigger on exact case or any case
        :return: The decorator
        """
        trigger = FirstWordTrigger(invoke, case_sensitive)
        return self._commands.decorator(trigger)

    def run_sync(self, *, username: str, token: str, client_id: str):  # pragma: no cover
        """
        Main synchronous blocking function to run the bot after configuring.

        :param username: Login of the bot
        :param token: Oauth token of the bot
        :param client_id: Client ID of the bot
        """
        loop = asyncio.get_event_loop()
        task = None
        try:
            task = loop.create_task(self.run_async(username=username, token=token, client_id=client_id))
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            if task:
                task.cancel()
        finally:
            pending = asyncio.all_tasks(loop=loop)
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

    async def run_async(self, *, username: str, token: str, client_id: str):  # pragma: no cover
        """
        Main async forever loop to run the bot after configuring.

        :param username: Login of the bot
        :param token: Oauth token of the bot
        :param client_id: Client ID of the bot
        """
        logger = Logger.with_default_handlers(name='green_eggs')

        async with TwitchChatClient(username=username, token=token, logger=logger) as chat:
            async with TwitchApiCommon(client_id=client_id, token=token, logger=logger) as api:
                await chat.join(self._channel)
                channel = Channel(login=self._channel, api=api, chat=chat, config=self._config, logger=logger)

                async for raw, default_timestamp in chat.incoming():
                    asyncio.create_task(
                        catch_all(
                            logger,
                            _main_handler,
                            api=api,
                            channel=channel,
                            commands=self._commands,
                            logger=logger,
                            raw=raw,
                            default_timestamp=default_timestamp,
                        )
                    )
