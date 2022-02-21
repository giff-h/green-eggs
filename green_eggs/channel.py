# -*- coding: utf-8 -*-
import asyncio
from collections import defaultdict, deque
from logging import Logger
from typing import Any, Deque, Dict, Optional, Set

from green_eggs import constants as const
from green_eggs.api import TwitchApiCommon
from green_eggs.client import TwitchChatClient
from green_eggs.config import Config, LinkAllowUserConditions, LinkPurgeActions
from green_eggs.constants import URL_PATTERN
from green_eggs.data_types import Code353, JoinPart, PrivMsg, RoomState


class Channel:
    def __init__(self, *, login: str, api: TwitchApiCommon, chat: TwitchChatClient, config: Config, logger: Logger):
        self._api: TwitchApiCommon = api
        self._api_results_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._chat: TwitchChatClient = chat
        self._config: Config = config
        self._last_five_for_user_id: Dict[str, Deque[PrivMsg]] = defaultdict(lambda: deque(maxlen=5))
        self._logger: Logger = logger
        self._login: str = login.lower()
        self._moderator_cache: Optional[Set[str]] = None
        self._permit_cache: Dict[str, asyncio.Task] = dict()
        self._room_state: Optional[RoomState] = None
        self._users_in_channel: Set[str] = set()
        self._users_in_channel_tmp: Set[str] = set()

    def add_permit_for_user(self, username: str) -> bool:
        """
        Adds a link permit for the given user by username.

        If the permit was added, returns `True`.
        If a permit already existed, returns `False`.

        :param str username: The username or display name of the user to permit
        :return: Whether the permit was added
        :rtype: bool
        """
        username = username.lower()
        if username in self._permit_cache:
            return False

        async def permit_clear():
            await asyncio.sleep(self._config.link_permit_duration)
            if username in self._permit_cache:
                del self._permit_cache[username]

        self._permit_cache[username] = asyncio.create_task(permit_clear())
        return True

    @property
    def broadcaster_id(self) -> str:
        """
        Get the ID of the broadcaster user.

        :return: ID from the room state, or empty string before it's been set
        """
        return '' if self._room_state is None else self._room_state.tags.room_id

    async def check_for_links(self, message: PrivMsg) -> bool:
        """
        Check for any URLs in the message and take action if necessary.

        Never takes any action on moderators.

        :param PrivMsg message: PRIVMSG from Twitch
        :return: `True` if action was taken, `False` if not.
        :rtype: bool
        """
        if not self._config.purge_links:
            return False  # Don't purge links, short circuit
        links = URL_PATTERN.findall(message.message)
        if not links:
            return False  # No link found, short circuit
        allowed_links = []
        disallowed_links = []
        for link in links:
            if self._config.does_link_pass_conditions(link):
                allowed_links.append(link)
            else:
                disallowed_links.append(link)
        if allowed_links:
            self._logger.debug(f'Link(s) allowed by target format: {allowed_links!r}')
        if not disallowed_links:
            return False  # All links allowed by target format, short circuit
        found_permit_username = next(
            (username for username in self._permit_cache.keys() if message.is_from_user(username)), None
        )
        if found_permit_username is not None:
            self._permit_cache.pop(found_permit_username).cancel()
            self._logger.debug(f'Link(s) allowed because permit: {disallowed_links!r}')
            return False  # User is permitted, short circuit
        if message.is_sender_moderator or await self.is_user_moderator(message.tags.user_id):
            self._logger.debug(f'Link(s) allowed because moderator: {disallowed_links!r}')
            return False  # User is moderator, short circuit
        if self._config.link_allow_user_condition & LinkAllowUserConditions.USER_VIP:
            if message.is_sender_vip or self.is_user_vip(message.tags.user_id):
                self._logger.debug(f'Link(s) allowed because VIP: {disallowed_links!r}')
                return False  # User is allowed by VIP, short circuit
        if self._config.link_allow_user_condition & LinkAllowUserConditions.USER_SUBSCRIBED:
            if message.is_sender_subscribed or await self.is_user_subscribed(message.tags.user_id):
                self._logger.debug(f'Link(s) allowed because subscribed: {disallowed_links!r}')
                return False  # User is allowed by subscription, short circuit

        # Action must be taken
        self._logger.debug(f'Purging link(s) from {message.who}: {disallowed_links!r}')

        if self._config.link_purge_action == LinkPurgeActions.DELETE:
            await self.send(message.action_delete())
            if self._config.link_purge_message_after_action:
                await self.send(f'@{message.tags.display_name} - {self._config.link_purge_message_after_action}')
        elif self._config.link_purge_action == LinkPurgeActions.TIMEOUT_FLAT:
            await self.send(message.action_timeout(self._config.link_purge_timeout_duration, 'Link detected'))
            if self._config.link_purge_message_after_action:
                await self.send(f'@{message.tags.display_name} - {self._config.link_purge_message_after_action}')
        else:
            raise ValueError(f'Unhandled link purge action: {self._config.link_purge_action!r}')

        return True

    def handle_code_353(self, code353: Code353):
        """
        Performs any necessary actions with the `Code353` in this channel.

        :param code353: 353 from Twitch
        """
        if self._login != code353.where:
            raise ValueError(f'Channel for {self._login} was given a code353 from {code353.where}')

        self._users_in_channel.update(code353.users)

    def handle_join_part(self, join_part: JoinPart):
        """
        Performs any necessary actions with the `JoinPart` in this channel.

        :param JoinPart join_part: JOIN or PART from Twitch
        """
        if self._login != join_part.where:
            raise ValueError(f'Channel for {self._login} was given a join/part from {join_part.where}')

        if self._users_in_channel_tmp:
            self._users_in_channel_tmp.clear()

        if join_part.is_join:
            self._users_in_channel.add(join_part.who)
        else:
            self._users_in_channel.discard(join_part.who)

    def handle_message(self, message: PrivMsg):
        """
        Performs any necessary actions with the `PrivMsg` in this channel.

        :param PrivMsg message: PRIVMSG from Twitch
        """
        if self._login != message.where:
            raise ValueError(f'Channel for {self._login} was given a message from {message.where}')

        self._last_five_for_user_id[message.tags.user_id].appendleft(message)
        self._users_in_channel_tmp.add(message.who)

    def handle_room_state(self, room_state: RoomState):
        """
        Performs any necessary actions with the `RoomState` in this channel.

        :param RoomState room_state: ROOMSTATE from Twitch
        """
        if self._login != room_state.where:
            raise ValueError(f'Channel for {self._login} was given a room state from {room_state.where}')

        self._room_state = room_state

    def is_user_in_channel(self, user_login: str) -> bool:
        """
        Is the user currently in the channel, according to IRC.

        :param str user_login: The login of the user, not display name
        :return: True if IRC thinks the user is in the channel or has otherwise sent a message recently
        :rtype: bool
        """
        return user_login in (self._users_in_channel | self._users_in_channel_tmp)

    async def is_user_moderator(self, user_id: str) -> bool:
        """
        Returns whether the user is a moderator in this channel.

        If the user hasn't sent any messages in chat, and an API call to get the list of moderators hasn't happened yet,
        an API call is made.

        Special case: If the user ID is the current channel ID, the result is always True

        :param str user_id: The ID of the user, not login
        :return: True if the user is a moderator
        :rtype: bool
        """
        if user_id == self.broadcaster_id:
            return True

        if user_id in self._last_five_for_user_id:
            return any(m.is_sender_moderator for m in self._last_five_for_user_id[user_id])
        else:
            if self._moderator_cache is None:
                results = await self._api.direct.get_moderators(broadcaster_id=self.broadcaster_id, first='100')
                self._moderator_cache = set(result['user_id'] for result in results['data'])
            return user_id in self._moderator_cache

    async def is_user_subscribed(self, user_id: str) -> bool:
        """
        Returns whether the user is subscribed to this channel.

        If the user hasn't sent any messages in chat, an API call is made.

        :param str user_id: The ID of the user, not login
        :return: True if the user is subscribed
        :rtype: bool
        """
        if user_id in self._last_five_for_user_id:
            return any(m.is_sender_subscribed for m in self._last_five_for_user_id[user_id])
        else:
            if 'is_subscribed' in self._api_results_cache[user_id]:
                return self._api_results_cache[user_id]['is_subscribed']

            is_subscribed = await self._api.is_user_subscribed_to_channel(
                broadcaster_id=self.broadcaster_id, user_id=user_id
            )
            self._api_results_cache[user_id]['is_subscribed'] = is_subscribed
            return is_subscribed

    def is_user_vip(self, user_id: str) -> bool:
        """
        Returns whether the user is a VIP in this channel.

        If the user hasn't sent any messages in chat, the result is False.

        :param str user_id: The ID of the user, not login
        :return: True if the user is a VIP
        :rtype: bool
        """
        return user_id in self._last_five_for_user_id and any(
            m.is_sender_vip for m in self._last_five_for_user_id[user_id]
        )

    def user_latest_message(self, user: str) -> Optional[PrivMsg]:
        """
        Gets the latest message the user sent in this channel, or None if they haven't sent yet.

        Can be searched by either display name case-insensitive or login. This distinction is important for non-ascii
        display names.

        :param str user: The display or login name of the user
        :return: The user's latest message or None
        :rtype: PrivMsg or None
        """
        return next(
            (
                messages[0]
                for messages in self._last_five_for_user_id.values()
                if messages and messages[0].is_from_user(user)
            ),
            None,
        )

    async def send(self, message: str):
        """
        Sends a message to this channel's chat.

        :param str message: The message to send. Can be a command if it starts with `'/'`
        """
        message = message.rstrip()
        if len(message) > const.MESSAGE_MAX_LENGTH:
            raise ValueError(f'Messages cannot exceed {const.MESSAGE_MAX_LENGTH} characters')
        await self._chat.send(f'PRIVMSG #{self._login} :{message}')
