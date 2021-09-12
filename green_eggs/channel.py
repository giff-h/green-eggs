# -*- coding: utf-8 -*-
from collections import defaultdict, deque
from logging import Logger
from typing import Any, Deque, Dict, Optional, Set

from green_eggs import constants as const
from green_eggs.api import TwitchApi
from green_eggs.client import TwitchChatClient
from green_eggs.data_types import Code353, JoinPart, PrivMsg, RoomState


class Channel:
    def __init__(self, *, login: str, api: TwitchApi, chat: TwitchChatClient, logger: Logger):
        self._api: TwitchApi = api
        self._api_results_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._chat: TwitchChatClient = chat
        self._last_five_for_user_id: Dict[str, Deque[PrivMsg]] = defaultdict(lambda: deque(maxlen=5))
        self._logger: Logger = logger
        self._login: str = login.lower()
        self._room_state: Optional[RoomState] = None
        self._users_in_channel: Set[str] = set()
        self._users_in_channel_tmp: Set[str] = set()

    @property
    def broadcaster_id(self) -> str:
        """
        Get the ID of the broadcaster user.

        :return: ID from the room state, or empty string before it's been set
        """
        return '' if self._room_state is None else self._room_state.tags.room_id

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

        :param join_part: JOIN or PART from Twitch
        """
        if self._login != join_part.where:
            raise ValueError(f'Channel for {self._login} was given a join/part from {join_part.where}')

        if len(self._users_in_channel_tmp):
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

    async def is_user_subscribed(self, user_id: str) -> bool:
        """
        Is the user indicated as subscribed in this channel.

        This can come from the `user_id` tag on a `PrivMsg`

        :param str user_id: The ID of the user, not login
        :return: True if the user is subscribed
        :rtype: bool
        """
        if user_id in self._last_five_for_user_id:
            return any(m.is_sender_subscribed for m in self._last_five_for_user_id[user_id])
        else:
            if 'is_subscribed' in self._api_results_cache[user_id]:
                return self._api_results_cache[user_id]['is_subscribed']

            results = await self._api.check_user_subscription(broadcaster_id=self.broadcaster_id, user_id=user_id)
            is_subscribed = len(results['data']) > 0 and 'tier' in results['data'][0]
            self._api_results_cache[user_id]['is_subscribed'] = is_subscribed
            return is_subscribed

    def user_latest_message(self, user: str) -> Optional[PrivMsg]:
        """
        Get the latest message the user sent in this channel, or None if they haven't sent yet.

        Can be searched by either display name case insensitive or login. This distinction is important for non-ascii
        display names.

        :param str user: The display or login name of the user
        :return: The user's latest message or None
        :rtype: PrivMsg or None
        """
        return next((q[0] for q in self._last_five_for_user_id.values() if len(q) and q[0].is_from_user(user)), None)

    async def send(self, message: str):
        """
        Send a message to this channel's chat.

        :param str message: The message to send. Can be a command if it starts with `'/'`
        """
        message = message.rstrip()
        if len(message) > const.MESSAGE_MAX_LENGTH:
            raise ValueError(f'Messages cannot exceed {const.MESSAGE_MAX_LENGTH} characters')
        await self._chat.send(f'PRIVMSG #{self._login} :{message}')
