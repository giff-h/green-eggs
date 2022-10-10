# -*- coding: utf-8 -*-
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Callable, Dict, List, Optional, Type, cast

from aiohttp import ClientResponseError
from aiologger import Logger
import reactivex as rx
from reactivex import operators as ops

from green_eggs import data_types as dt
from green_eggs.reactive.api.direct import TwitchApiDirect

__all__ = ('ShoutoutInfo', 'TwitchApiCommon')


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

    @staticmethod
    def from_channel_info(channel: Dict[str, Any]) -> 'ShoutoutInfo':
        return ShoutoutInfo(
            user_id=channel['broadcaster_id'],
            username=channel['broadcaster_login'],
            display_name=channel['broadcaster_name'],
            game_name=channel['game_name'],
            game_id=channel['game_id'],
            broadcaster_language=channel['broadcaster_language'],
            stream_title=channel['title'],
        )


MaybeShoutout = Optional[ShoutoutInfo]


class TwitchApiCommon:
    def __init__(self, *, client_id: str, token: str, logger: Logger):
        self._api = TwitchApiDirect(client_id=client_id, token=token, logger=logger)
        self._logger: Logger = logger
        self._moderator_cache: Dict[str, List[dt.NormalizedUser]] = dict()

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
    ) -> None:
        await self._api.__aexit__(exc_type, exc_val, exc_tb)

    def get_is_user_subscribed_to_channel(self, *, broadcaster_id: str, user_id: str) -> rx.Observable[bool]:
        """
        Gets an observable that emits whether the user given by user ID is subscribed to the channel given by
        broadcaster ID.

        :param str broadcaster_id: The user ID of the channel
        :param str user_id: The user ID of the potential subscriber
        :return: An observable that emits once with whether the user is subscribed to the channel
        :rtype: rx.Observable[bool]
        """

        def error_handler(err: Exception, _source: rx.Observable) -> rx.Observable[bool]:
            if isinstance(err, ClientResponseError) and err.status == 404:
                return rx.of(False)
            raise err

        def is_subscribed(results: Dict[str, Any]) -> bool:
            return bool(results['data']) and 'tier' in results['data'][0]

        return self._api.check_user_subscription(broadcaster_id=broadcaster_id, user_id=user_id).pipe(
            ops.map(is_subscribed), ops.catch(error_handler)
        )

    def get_shoutout_info(self, *, username: str = None, user_id: str = None) -> rx.Observable[MaybeShoutout]:
        """
        Gets an observable that emits shoutout information for the given user, either by username or user ID.

        At least one must be provided, if both are provided the user ID is used.

        If info could not be found, emits `None`.

        :param str username: The login of the user
        :param str user_id: The ID of the user
        :return: An observable that emits once with the maybe shoutout info
        :rtype: rx.Observable[Optional[ShoutoutInfo]]
        """
        of_user_id: rx.Observable[Optional[str]]

        def user_id_from_user_results(user_results: Dict[str, Any]) -> Optional[str]:
            return user_results['data'][0]['id'] if user_results['data'] else None

        def shoutout_from_channel_info(channel_info: Dict[str, Any]) -> MaybeShoutout:
            return ShoutoutInfo.from_channel_info(channel_info['data'][0]) if channel_info['data'] else None

        def shoutout_info_from_user_id(val: Optional[str]) -> rx.Observable[MaybeShoutout]:
            if val:
                return self._api.get_channel_information(broadcaster_id=val).pipe(ops.map(shoutout_from_channel_info))
            else:
                return rx.of(None)

        if user_id is not None:
            of_user_id = rx.of(user_id)
        else:
            if username is None:
                raise ValueError('Most provide either username or user_id')
            of_user_id = self._api.get_users(login=username).pipe(ops.map(user_id_from_user_results))

        switch_latest = cast(
            Callable[[rx.Observable[rx.Observable[MaybeShoutout]]], rx.Observable[MaybeShoutout]], ops.switch_latest()
        )
        return of_user_id.pipe(ops.map(shoutout_info_from_user_id), switch_latest)
