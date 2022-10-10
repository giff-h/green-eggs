# -*- coding: utf-8 -*-
import asyncio
import datetime
from types import TracebackType
from typing import Awaitable, Callable, ClassVar, List, Match, Optional, Pattern, Type, Union

import reactivex as rx
import websockets
from aiologger import Logger
from reactivex import operators as ops
from reactivex.internal import DisposedException, SequenceContainsNoElementsError
from websockets.legacy.client import WebSocketClientProtocol

from green_eggs import constants as const
from green_eggs import data_types as dt
from green_eggs.reactive.operators import filter_is_not_none


def ensure_str(val: Union[str, bytes]) -> str:
    """
    Decodes to string if given bytes.

    :param val: The value of unknown stringiness
    :type val: str or bytes
    :return: Always a string
    :rtype: str
    """
    if isinstance(val, str):
        return val
    else:
        return val.decode('utf-8')


def format_oauth(token: str) -> str:
    """
    Format an auth token for websocket auth.

    :param str token: The auth token of the user
    :return: The token formatted for websocket auth
    :rtype: str
    """
    return token if token.startswith('oauth:') else f'oauth:{token}'


def pattern_match_mapper(pattern: Pattern[str]) -> rx.typing.Mapper[dt.StampedData, Optional[Match[str]]]:
    """
    Creates a mapper function that will match data on a `StampedData` object on the given pattern.
    """

    def mapper(data: dt.StampedData) -> Optional[Match[str]]:
        return pattern.match(data.data)

    return mapper


class TwitchWebsocketClient:
    host: ClassVar[str] = 'wss://irc-ws.chat.twitch.tv:443'
    incoming_data: rx.Observable[dt.HandleAble]

    def __init__(self, *, username: str, token: str, logger: Logger):
        self._expected_patterns: List[Pattern[str]] = []
        self._authorize_task: Optional[asyncio.Task] = None
        self._logger: Logger = logger
        self._internal_subject: rx.Subject[dt.StampedData] = rx.Subject()
        self._external_subject: rx.Subject[dt.HandleAble] = rx.Subject()
        self._token: str = format_oauth(token)
        self._username: str = username.lower()
        self._websocket_loop_task: Optional[asyncio.Task] = None
        self._websocket_send_func: asyncio.Future[Callable[[str], Awaitable[None]]] = asyncio.Future()

        self._connect_subjects()
        self.incoming_data = self._external_subject.pipe(ops.as_observable())

    def _connect_subjects(self) -> None:
        observable: rx.Observable[dt.HandleAble] = self._internal_subject.pipe(
            ops.filter(self._filter_was_not_expecting),
            ops.map(self._map_handleable_from_data),
            filter_is_not_none(dt.HandleAble),
        )
        observable.subscribe(on_next=self._external_subject.on_next)

    def _filter_was_not_expecting(self, data: dt.StampedData) -> bool:
        return all(pattern.match(data.data) is None for pattern in self._expected_patterns)

    def _map_handleable_from_data(self, data: dt.StampedData) -> Optional[dt.HandleAble]:
        try:
            for pattern, handleable_type in dt.pattern_mapping.items():
                match_result = pattern.match(data.data)
                if match_result:
                    return handleable_type.from_match_dict(
                        default_timestamp=data.stamp, raw=data.data, **match_result.groupdict()
                    )
        except Exception as e:
            self._logger.exception(f'Error parsing data into handleable: {data.data!r}', exc_info=e)
        else:
            self._logger.warning(f'Incoming message could not be matched: {data.data!r}')

        return None

    async def __aenter__(self) -> 'TwitchWebsocketClient':
        self._websocket_loop_task = asyncio.create_task(self._websocket_manager())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._teardown()

    def _teardown(self) -> None:
        """
        Resets the client to the state it was when it was first created.

        This happens during context exit, so please consider using context management.
        """
        self._websocket_send_func = asyncio.Future()

        subject = self._internal_subject
        self._internal_subject = rx.Subject()
        self._connect_subjects()
        try:
            subject.on_completed()
        except (DisposedException, SequenceContainsNoElementsError):
            pass
        subject.dispose()

        # Cancel all potentially running tasks, they could be hanging?
        if self._authorize_task:
            task = self._authorize_task
            self._authorize_task = None
            task.cancel()
        if self._websocket_loop_task:
            task = self._websocket_loop_task
            self._websocket_loop_task = None
            task.cancel()

        self._expected_patterns.clear()

    async def _login(self) -> None:
        """
        Authenticates to Twitch on the websocket.

        Blocks until Twitch has acknowledged the authentication.
        """
        expected_codes = const.EXPECTED_AUTH_CODES.copy()
        self._expected_patterns.append(const.AUTH_EXPECT_PATTERN)
        resolved: 'asyncio.Future[None]' = asyncio.Future()

        def resolve_expected(match_result: Match[str]) -> None:
            code = match_result.group('code')
            self._logger.debug(f'Auth resp: {match_result.group("msg")!r}')
            expected_codes.remove(code)
            if not expected_codes:
                # HACK: since this observable is likely to emit before external pipes, delay the removal of the pattern
                # in the hope that the last emitted item will still be filtered
                asyncio.get_running_loop().call_soon(self._expected_patterns.remove, const.AUTH_EXPECT_PATTERN)
                resolved.set_result(None)

        observable: rx.Observable[Match[str]] = self._internal_subject.pipe(
            ops.map(pattern_match_mapper(const.AUTH_EXPECT_PATTERN)),
            filter_is_not_none(Match[str]),
            ops.take(len(const.EXPECTED_AUTH_CODES)),
        )
        observable.subscribe(on_next=resolve_expected)
        await self.send(f'PASS {self._token}', redact_log='PASS ******')
        await self.send(f'NICK {self._username}')
        await resolved

    async def _capability_request(self) -> None:
        """
        Requests IRC capabilities to Twitch on the websocket.

        Blocks until Twitch has acknowledged the capabilities.
        """
        expected_modes = const.CAP_REQ_MODES.copy()
        self._expected_patterns.append(const.CAP_ACK_PATTERN)
        resolved: 'asyncio.Future[None]' = asyncio.Future()

        def resolve_expected(match_result: Match[str]) -> None:
            acknowledged = match_result.group('cap')
            self._logger.debug(f'Capacities acknowledged: {acknowledged}')
            for mode in acknowledged.split(' '):
                expected_modes.remove(mode[10:])  # trim 'twitch.tv/' from the left
            if not expected_modes:
                # HACK: since this observable is likely to emit before external pipes, delay the removal of the pattern
                # in the hope that the last emitted item will still be filtered
                asyncio.get_running_loop().call_soon(self._expected_patterns.remove, const.CAP_ACK_PATTERN)
                resolved.set_result(None)

        observable: rx.Observable[Match[str]] = self._internal_subject.pipe(
            ops.map(pattern_match_mapper(const.CAP_ACK_PATTERN)), filter_is_not_none(Match[str]), ops.first()
        )
        observable.subscribe(on_next=resolve_expected)
        await self.send('CAP REQ :' + ' '.join(f'twitch.tv/{mode}' for mode in const.CAP_REQ_MODES))
        await resolved

    async def _authorize_and_join(self) -> None:
        await self._login()
        await self._capability_request()

        if self._authorize_task:
            self._authorize_task = None

    async def _websocket_manager(self) -> None:
        """
        This runs forever.

        Task it.
        """
        try:
            while True:
                # mypy doesn't like websockets lazy importing
                async with websockets.connect(self.host) as websocket:  # type: ignore[attr-defined]
                    self._websocket_send_func.set_result(websocket.send)
                    self._authorize_task = asyncio.create_task(self._authorize_and_join())
                    await self._websocket_loop(websocket)
                    self._logger.debug('Reconnecting...')
        except asyncio.CancelledError:
            raise
        except Exception as e:
            asyncio.get_running_loop().call_soon(self._internal_subject.on_error, e)
        finally:
            asyncio.get_running_loop().call_soon(self._internal_subject.on_completed)
            self._websocket_loop_task = None

    async def _websocket_loop(self, websocket: WebSocketClientProtocol) -> None:
        """
        Puts incoming data from the websocket into the observable.

        This runs until a reconnect request is received, then returns.

        :param WebSocketClientProtocol websocket: The websocket client to listen for data
        """
        async for data in websocket:
            now = datetime.datetime.utcnow()
            messages = ensure_str(data).splitlines()
            for message in filter(None, messages):
                if message.startswith('PING '):
                    self._logger.debug('Ping? Pong!')
                    await self.send(f'PONG {message[5:]}')  # trim 'PING ' from the left
                elif const.RECONNECT_PATTERN.match(message):
                    self._websocket_send_func = asyncio.Future()
                    return
                else:
                    stamped = dt.StampedData(data=message, stamp=now)
                    asyncio.get_running_loop().call_soon(self._internal_subject.on_next, stamped)

    async def _channel_presence_action(self, action: str, channel_name: str, match_channel_group_name: str, expect_pattern: Pattern[str]) -> None:
        """
        Joins or leaves a channel on Twitch.

        Blocks until Twitch has acknowledged the action.
        """
        resolved: 'asyncio.Future[None]' = asyncio.Future()

        def is_for_this_user_and_in_this_channel(match_result: Match[str]) -> bool:
            return match_result.group('who') == self._username and match_result.group(match_channel_group_name) == channel_name

        def resolve_expected(_match_result: Match[str]) -> None:
            resolved.set_result(None)

        observable: rx.Observable[Match[str]] = self._internal_subject.pipe(
            ops.map(pattern_match_mapper(expect_pattern)),
            filter_is_not_none(Match[str]),
            ops.filter(is_for_this_user_and_in_this_channel),
            ops.first(),
        )
        observable.subscribe(on_next=resolve_expected)
        await self.send(f'{action} #{channel_name}')
        await resolved

    async def join_channel(self, channel_name: str) -> None:
        """
        Joins the channel on Twitch.

        Blocks until Twitch has acknowledged the join.
        """
        await self._channel_presence_action(action='JOIN', channel_name=channel_name.lower(), match_channel_group_name='joined', expect_pattern=const.JOIN_EXPECT_PATTERN)

    async def leave_channel(self, channel_name: str) -> None:
        """
        Leaves the channel on Twitch.

        Blocks until Twitch has acknowledged the join.
        """
        await self._channel_presence_action(action='PART', channel_name=channel_name.lower(), match_channel_group_name='left', expect_pattern=const.PART_EXPECT_PATTERN)

    async def send(self, data: str, *, redact_log: Optional[str] = None) -> None:
        """
        Sends data to the server.

        If the data is sensitive, i.e. PASS login, then set `redact_log` and that will be the logged value. Adds its own
        carriage return for IRC.

        :param str data: Message to send
        :param redact_log: Optional value to log instead of the data
        :type redact_log: str or None
        """
        send_func = await self._websocket_send_func
        if redact_log is None:
            self._logger.debug(f'Sending data: {data!r}')
        else:
            self._logger.debug(f'Sending data: {redact_log!r}')
        await send_func(data + '\r\n')


__all__ = ('TwitchWebsocketClient', 'ensure_str', 'format_oauth', 'pattern_match_mapper')
