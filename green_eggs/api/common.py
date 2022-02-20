# -*- coding: utf-8 -*-
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Dict, Optional, Type

from aiohttp import ClientResponseError
from aiologger import Logger

from .direct import TwitchApiDirect

__all__ = ('TwitchApiCommon',)


@dataclass
class ShoutoutInfo:
    user_id: str = ''
    username: str = ''
    display_name: str = ''
    game_name: str = ''
    game_id: str = ''
    broadcaster_language: str = ''
    stream_title: str = ''

    @property
    def user_link(self) -> str:
        return f'https://twitch.tv/{self.username}'

    def update_from_stream_result(self, stream: Dict[str, Any]):
        self.user_id = stream['broadcaster_id']
        self.username = stream['broadcaster_login']
        self.display_name = stream['broadcaster_name']
        self.game_name = stream['game_name']
        self.game_id = stream['game_id']
        self.broadcaster_language = stream['broadcaster_language']
        self.stream_title = stream['title']


class TwitchApiCommon:
    def __init__(self, *, client_id: str, token: str, logger: Logger):
        self._api = TwitchApiDirect(client_id=client_id, token=token, logger=logger)
        self._logger: Logger = logger

    @property
    def direct(self) -> TwitchApiDirect:
        return self._api

    async def __aenter__(self) -> 'TwitchApiCommon':
        self._api = await self._api.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        await self._api.__aexit__(exc_type, exc_val, exc_tb)

    async def get_shoutout_info(self, *, username: str = None, user_id: str = None) -> Optional[ShoutoutInfo]:
        """
        Gets shoutout information for the given user, either by username or user ID.

        At least one must be provided, if both are provided the user ID is used.

        If info could not be found, returns `None`.

        :param str username: The login of the user
        :param str user_id: The ID of the user
        :return: The object with the shoutout info if it succeeded, `None` if not
        :rtype: ShoutoutInfo or None
        """
        shoutout_info = ShoutoutInfo()

        if user_id is None:
            if username is None:
                raise ValueError('Most provide either username or user_id')

            user_result = await self._api.get_users(login=username)
            if not user_result['data']:
                return None
            user_id = user_result['data'][0]['id']

        assert user_id is not None
        streams = await self._api.get_channel_information(broadcaster_id=user_id)
        if not streams['data']:
            return None
        shoutout_info.update_from_stream_result(streams['data'][0])
        return shoutout_info

    async def is_user_subscribed_to_channel(self, *, broadcaster_id: str, user_id: str) -> bool:
        """
        Checks the user given by user ID is subscribed to the channel given by broadcaster ID.

        :param str broadcaster_id: The user ID of the channel
        :param str user_id: The user ID of the potential subscriber
        :return: Whether the user is subscribed to the channel
        :rtype: bool
        """
        try:
            results = await self._api.check_user_subscription(broadcaster_id=broadcaster_id, user_id=user_id)
            return bool(results['data']) and 'tier' in results['data'][0]
        except ClientResponseError as e:
            if e.status == 404:
                return False
            raise
