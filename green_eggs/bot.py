# -*- coding: utf-8 -*-
import asyncio
import datetime
from typing import Any, Dict, List, Mapping, Optional, Tuple

from aiologger import Logger
import asyncstdlib as a

from green_eggs import data_types as dt
from green_eggs.api import TwitchApiCommon
from green_eggs.api.common import validate_client_id
from green_eggs.channel import Channel
from green_eggs.client import TwitchChatClient
from green_eggs.commands import CommandRegistry, FirstWordTrigger, SenderIsModTrigger
from green_eggs.config import Config
from green_eggs.data_types import PrivMsg
from green_eggs.exceptions import CooldownNotElapsed
from green_eggs.types import RegisterAbleFunc
from green_eggs.utils import catch_all

_unset: Any = object()


async def _main_handler(
    *,
    api: TwitchApiCommon,
    channel: Channel,
    commands: CommandRegistry,
    config: Config,
    logger: Logger,
    raw: str,
    default_timestamp: datetime.datetime,
) -> Optional[dt.HandleAble]:
    handleable: Optional[dt.HandleAble] = None

    for handle_type, pattern in dt.patterns.items():
        found = pattern.match(raw)
        if found is not None:
            handleable = handle_type.from_match_dict(default_timestamp=default_timestamp, raw=raw, **found.groupdict())
            break

    if handleable is None:
        logger.warning(f'Incoming message could not be parsed: {raw!r}')
        return None

    if isinstance(handleable, dt.HasTags):
        if handleable.tags.unhandled:
            type_name = type(handleable).__qualname__
            unhandled = handleable.tags.unhandled
            logger.warning(f'Unhandled tags on {type_name}: {unhandled!r}')
        if isinstance(handleable.tags, dt.UserNoticeTags):
            if handleable.tags.msg_params.unhandled:
                type_name = type(handleable).__qualname__
                unhandled = handleable.tags.msg_params.unhandled
                logger.warning(f'Unhandled msg params on {type_name}: {unhandled!r}')
        if isinstance(handleable.tags, dt.UserBaseTags):
            if handleable.tags.badges.unhandled:
                type_name = type(handleable).__qualname__
                unhandled = handleable.tags.badges.unhandled
                logger.warning(f'Unhandled badges on {type_name}: {unhandled!r}')
        if isinstance(handleable.tags, dt.UserChatBaseTags):
            if handleable.tags.badge_info.unhandled:
                type_name = type(handleable).__qualname__
                unhandled = handleable.tags.badge_info.unhandled
                logger.warning(f'Unhandled badge info on {type_name}: {unhandled!r}')

    if isinstance(handleable, dt.PrivMsg):
        channel.handle_message(handleable)
        if not await channel.check_for_links(handleable):
            command = await commands.find(handleable, channel)
            if command is not None:
                try:
                    result = await command.run(api=api, channel=channel, message=handleable)
                except CooldownNotElapsed as e:
                    if config.should_notify_if_cooldown_has_not_elapsed:
                        remaining = f'{e.remaining:.1f}'.rstrip('0').rstrip('.')
                        plural = '' if remaining == '1' else 's'
                        response = (
                            f'@{handleable.tags.display_name} - '
                            f'That command is on cooldown for {remaining} more second{plural}'
                        )
                        await channel.send(response)
                else:
                    if isinstance(result, str):
                        await channel.send(result)

    elif isinstance(handleable, dt.JoinPart):
        channel.handle_join_part(handleable)

    elif isinstance(handleable, dt.ClearChat):
        pass

    elif isinstance(handleable, dt.UserNotice):
        pass

    elif isinstance(handleable, dt.RoomState):
        channel.handle_room_state(handleable)

    elif isinstance(handleable, dt.UserState):
        pass

    elif isinstance(handleable, dt.ClearMsg):
        pass

    elif isinstance(handleable, dt.Notice):
        pass

    elif isinstance(handleable, dt.HostTarget):
        pass

    elif isinstance(handleable, dt.Code353):
        channel.handle_code_353(handleable)

    elif isinstance(handleable, dt.Code366):
        pass

    elif isinstance(handleable, dt.Whisper):
        pass

    return handleable


class ChatBot:
    def __init__(self, *, channel: str, config: Dict[str, Any] = None):
        self._channel: str = channel
        self._commands = CommandRegistry()
        self._config = Config.from_python(**(config or dict()))

        if self._config.should_purge_links:
            self._register_permit_command()

    def _get_cooldowns(
        self, global_cooldown: Optional[int], user_cooldown: Optional[int]
    ) -> Tuple[Optional[int], Optional[int]]:
        if global_cooldown is _unset:
            global_cooldown = self._config.default_command_global_cooldown
        if user_cooldown is _unset:
            user_cooldown = self._config.default_command_user_cooldown
        return global_cooldown, user_cooldown

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
        self._commands.add(trigger, permit, global_cooldown=None, user_cooldown=None)

    def register_basic_commands(
        self,
        commands: Mapping[str, str],
        *,
        case_sensitive=False,
        global_cooldown: Optional[int] = _unset,
        user_cooldown: Optional[int] = _unset,
    ):
        """
        Register basic message response commands.

        :param commands: Mapping of invoke to response strings
        :param bool case_sensitive: Whether the command should trigger on exact case or any case
        :param global_cooldown: Optional global cooldown for these responses to override config
        :param user_cooldown: Optional user cooldown for these responses to override config
        """
        global_cooldown, user_cooldown = self._get_cooldowns(global_cooldown, user_cooldown)

        # This factory is necessary to keep the namespace of `output` from getting overwritten in the loop
        def factory(output):
            def basic():
                return output

            return basic

        for invoke, response in commands.items():
            trigger = FirstWordTrigger(invoke, case_sensitive)
            self._commands.add(trigger, factory(response), global_cooldown=global_cooldown, user_cooldown=user_cooldown)

    def register_caster_command(
        self,
        invoke: str,
        *,
        case_sensitive=False,
        global_cooldown: Optional[int] = _unset,
        user_cooldown: Optional[int] = _unset,
    ):
        """
        Decorator to register a function as a caster command handler.

        :param str invoke: The command part in the chat message
        :param bool case_sensitive: Whether the command should trigger on exact case or any case
        :param global_cooldown: Optional global cooldown for these responses to override config
        :param user_cooldown: Optional user cooldown for these responses to override config
        :return: The decorator
        """
        trigger = FirstWordTrigger(invoke, case_sensitive) & SenderIsModTrigger()
        global_cooldown, user_cooldown = self._get_cooldowns(global_cooldown, user_cooldown)

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

                return await a.sync(callback)(**callback_kwargs)  # type: ignore[return-value]

            return command

        return self._commands.decorator(
            trigger,
            global_cooldown=global_cooldown,
            user_cooldown=user_cooldown,
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

    def register_command(
        self,
        invoke: str,
        *,
        case_sensitive=False,
        global_cooldown: Optional[int] = _unset,
        user_cooldown: Optional[int] = _unset,
    ):
        """
        Decorator to register a function as a command handler.

        :param str invoke: The command part in the chat message
        :param bool case_sensitive: Whether the command should trigger on exact case or any case
        :param global_cooldown: Optional global cooldown for these responses to override config
        :param user_cooldown: Optional user cooldown for these responses to override config
        :return: The decorator
        """
        trigger = FirstWordTrigger(invoke, case_sensitive)
        global_cooldown, user_cooldown = self._get_cooldowns(global_cooldown, user_cooldown)
        return self._commands.decorator(trigger, global_cooldown=global_cooldown, user_cooldown=user_cooldown)

    def run_sync(
        self, *, chat_bot_username: str, chat_bot_token: str, api_client_id: str = None, api_token: str
    ):  # pragma: no cover
        """
        Main synchronous blocking function to run the bot after configuring.

        :param str chat_bot_username: Login of the bot
        :param str chat_bot_token: Oauth token of the bot
        :param str api_client_id: Client ID of the API user, optional
        :param str api_token: Oauth token of the API user
        """
        loop = asyncio.get_event_loop()
        task = None
        try:
            task = loop.create_task(
                self.run_async(
                    chat_bot_username=chat_bot_username,
                    chat_bot_token=chat_bot_token,
                    api_client_id=api_client_id,
                    api_token=api_token,
                )
            )
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            if task:
                task.cancel()
        finally:
            pending = asyncio.all_tasks(loop=loop)
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

    async def run_async(
        self, *, chat_bot_username: str, chat_bot_token: str, api_client_id: str = None, api_token: str
    ):  # pragma: no cover
        """
        Main async forever loop to run the bot after configuring.

        :param str chat_bot_username: Login of the bot
        :param str chat_bot_token: Oauth token of the bot
        :param str api_client_id: Client ID of the API user, optional
        :param str api_token: Oauth token of the API user
        """
        logger = Logger.with_default_handlers(name='green_eggs')
        if not api_client_id:
            api_client_id = await validate_client_id(api_token)

        async with TwitchChatClient(username=chat_bot_username, token=chat_bot_token, logger=logger) as chat:
            async with TwitchApiCommon(client_id=api_client_id, token=api_token, logger=logger) as api:
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
                            config=self._config,
                            logger=logger,
                            raw=raw,
                            default_timestamp=default_timestamp,
                        )
                    )
