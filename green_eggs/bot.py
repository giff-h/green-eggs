# -*- coding: utf-8 -*-
import asyncio
import datetime
from typing import List, Mapping, Optional

from aiologger import Logger

from green_eggs import data_types as dt
from green_eggs.api import TwitchApi
from green_eggs.channel import Channel
from green_eggs.client import TwitchChatClient
from green_eggs.commands import CommandRegistry, FirstWordTrigger, SenderIsModTrigger
from green_eggs.types import RegisterAbleFunc
from green_eggs.utils import catch_all


async def _main_handler(
    *,
    api: TwitchApi,
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
            type_name = type(handle_able.tags).__name__
            unhandled = handle_able.tags.unhandled
            logger.warning(f'Unhandled on {type_name}: {unhandled!r}')
        if isinstance(handle_able.tags, dt.UserNoticeTags):
            if len(handle_able.tags.msg_params.unhandled):
                type_name = type(handle_able.tags.msg_params).__name__
                unhandled = handle_able.tags.msg_params.unhandled
                logger.warning(f'Unhandled on {type_name}: {unhandled!r}')

    if isinstance(handle_able, dt.PrivMsg):
        channel.handle_message(handle_able)
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
    def __init__(self, *, channel: str):
        self._channel: str = channel
        self._commands = CommandRegistry()

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
            async def command(api: TwitchApi, channel: Channel, message: dt.PrivMsg) -> Optional[str]:
                if len(message.words) <= 1:
                    return 'I need a name for that'

                callback_kwargs = dict()
                name = message.words[1]
                last_message = channel.user_latest_message(name)
                if last_message is None:
                    user_result = await api.get_users(login=name.lstrip('@'))
                    if not len(user_result['data']):
                        return f'Could not find user data for {name}'

                    user = user_result['data'][0]
                    user_id = user['id']
                    user_display = user['display_name']
                    user_login = user['login']
                else:
                    user_id = last_message.tags.user_id
                    user_display = last_message.tags.display_name
                    user_login = last_message.who

                streams = await api.get_channel_information(broadcaster_id=user_id)
                stream = streams['data'][0]

                if 'name' in callback_keywords:
                    callback_kwargs['name'] = user_display
                if 'link' in callback_keywords:
                    callback_kwargs['link'] = 'https://twitch.tv/' + user_login
                if 'game' in callback_keywords:
                    game = stream['game_name']
                    callback_kwargs['game'] = None if game == '' else game
                if 'api_result' in callback_keywords:
                    callback_kwargs['api_result'] = stream

                output = callback(**callback_kwargs)
                if output is None or isinstance(output, str):
                    return output
                else:
                    return await output

            return command

        return self._commands.decorator(
            trigger, target_keywords=['name', 'link', 'game', 'api_result'], command_factory=factory
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
            async with TwitchApi(client_id=client_id, token=token, logger=logger) as api:
                await chat.join(self._channel)
                channel = Channel(login=self._channel, api=api, chat=chat, logger=logger)

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
