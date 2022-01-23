# -*- coding: utf-8 -*-
import asyncio
import datetime
from types import TracebackType
from typing import AsyncIterator, ClassVar, Dict, List, Optional, Pattern, Tuple, Type, Union

from aiologger import Logger
import websockets
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.client import WebSocketClientProtocol

from green_eggs import constants as const
from green_eggs.exceptions import ChannelPresenceRaceCondition

BufferData = Tuple[str, datetime.datetime]
AUTH_EXPECT = 'auth'
CAP_REQ_EXPECT = 'cap_req'
JOIN_EXPECT = 'join'
PART_EXPECT = 'part'


def ensure_str(raw: Union[str, bytes]) -> str:
    """
    Decodes to string if given bytes.

    Intended for use to coerce the return type of websocket connection received data.
    """
    if isinstance(raw, str):
        return raw
    else:
        return raw.decode('utf-8')


def format_oauth(oauth_token: str) -> str:
    """
    Format an oauth token for IRC auth.
    """
    return oauth_token if oauth_token.startswith('oauth:') else f'oauth:{oauth_token}'


class TwitchChatClient:
    host: ClassVar[str] = 'wss://irc-ws.chat.twitch.tv:443'
    expectation_patterns: ClassVar[Dict[str, Pattern[str]]] = {
        AUTH_EXPECT: const.AUTH_EXPECT_PATTERN,
        CAP_REQ_EXPECT: const.CAP_ACK_PATTERN,
        JOIN_EXPECT: const.JOIN_EXPECT_PATTERN,
        PART_EXPECT: const.PART_EXPECT_PATTERN,
    }

    ws_exc: Optional[Exception]

    def __init__(self, *, username: str, token: str, logger: Logger):
        self.ws_exc = None

        self._buffer_task: Optional[asyncio.Task] = None
        self._expect_timeout: Union[float, int] = 5
        self._expectations: Dict[str, Dict[str, asyncio.Future]] = dict()
        self._logger: Logger = logger
        self._message_buffer: 'asyncio.Queue[BufferData]' = asyncio.Queue()
        self._token: str = format_oauth(token)
        self._username: str = username.lower()
        self._websocket: Optional[WebSocketClientProtocol] = None

    async def buffer_messages(self):
        """
        Infinite loop to fetch incoming data and buffer filtered messages.

        Adds the UTC timestamp of when they were received for the data types.

        :return: Generator of messages for consumption
        :rtype: AsyncIterator[Tuple[str, datetime.datetime]]
        """
        assert self._websocket is not None  # typing
        await self._websocket.ensure_open()

        while True:
            # noinspection PyBroadException
            try:
                data = await self.recv()
                now = datetime.datetime.utcnow()
                async for line in self.filter_expected(data):
                    await self._message_buffer.put((line, now))
            except RuntimeError as e:
                # This allows the tests to be run on python 3.10 without falling into an endless loop
                # due to some bizarre scenario where multiple event loops are used inside the test runner (?)
                assert e.args != ('Event loop is closed',)
                self._logger.exception('Unhandled exception in listen loop')
            except asyncio.CancelledError:
                raise
            except ConnectionClosedError:
                self._logger.debug('Caught a closed connection. Reconnecting...')
                await self.connect()
                await self.initialize()
            except Exception:
                self._logger.exception('Unhandled exception in listen loop')

    async def connect(self):
        """
        Connects to the IRC server and sets the websocket property.

        :raises Exception: from the websocket connect if any happened
        """
        try:
            self._websocket = await websockets.connect(self.host)
        except Exception as e:
            self.ws_exc = e
            self._logger.exception('Websocket connection failed')
            raise

    async def expect(self, expectation: asyncio.Future, label: str, timeout: int = 5):
        """
        Takes an `asyncio.Future` and expects it to resolve within `timeout` seconds.

        This should be tasked, not awaited, as it's normal to set expectations before you perform the action that
        results in the expectation, and awaiting will time out before you attempt to perform the action.

        :param asyncio.Future expectation: Can be any Future, coroutine, or other awaitable
        :param str label: An identifier for logging purposes on timeout
        :param int timeout: Amount of time to wait before timing out
        :raises asyncio.TimeoutError: from the expectation if it timed out
        """
        try:
            await asyncio.wait_for(expectation, timeout=timeout)
        except asyncio.TimeoutError:
            self._logger.error(f'Timed out {label} expectation')
            raise

    async def filter_expected(self, data: str) -> AsyncIterator[str]:
        """
        A generator that takes raw websocket messages and only yields lines that weren't expected, i.e. no expectation
        manager returned `True`.

        :param str data: Received value from `self.recv()`
        :return: Generator of messages for consumption
        :rtype: AsyncIterator[str]
        """
        for line in filter(None, data.splitlines()):
            if const.RECONNECT_PATTERN.match(line):
                assert self._websocket is not None
                await self._websocket.close()
                await self.connect()
                await self.initialize()
                break
            elif self.manage_expectations(line):
                yield line

    async def incoming(self) -> AsyncIterator[BufferData]:
        """
        The main infinite loop of incoming messages.

        Adds the UTC timestamp of when they were received for the data types.

        :return: Generator of messages for consumption
        :rtype: AsyncIterator[Tuple[str, datetime.datetime]]
        """
        while True:
            yield await self._message_buffer.get()

    async def initialize(self):
        """
        Initializes the client connection once opened.

        Authorizes, registers capabilities, and joins initial channels.
        """
        if not await self.is_connected():
            return

        if self._buffer_task is None:
            self._buffer_task = asyncio.create_task(self.buffer_messages())

        expects = self.queue_expectations(AUTH_EXPECT, *const.EXPECTED_AUTH_CODES, timeout=self._expect_timeout)
        await self.send(f'PASS {self._token}', redact_log='PASS ******')
        await self.send(f'NICK {self._username}')
        await asyncio.gather(*expects)

        expects = self.queue_expectations(CAP_REQ_EXPECT, *const.CAP_REQ_MODES, timeout=self._expect_timeout)
        await self.send('CAP REQ :' + ' '.join(f'twitch.tv/{mode}' for mode in const.CAP_REQ_MODES))
        await asyncio.gather(*expects)

    async def is_connected(self) -> bool:
        """
        :return: Is the connection open?
        :rtype: bool
        """
        if self._websocket is None:
            return False

        await self._websocket.ensure_open()
        return True

    async def join(self, channel: str, action_if_leaving: str = 'wait') -> bool:
        """
        Joins one channel.

        Does nothing if the channel is waiting to join or the `action_if_leaving` is to abort.

        If the connection is waiting to leave this channel, these are the available actions to take:
        - `'wait'` will join after leaving
        - `'raise'` will raise a `ChannelPresenceRaceCondition` exception
        - `'abort'` will not join

        :param str channel: Raw name of the channel
        :param str action_if_leaving: The action to take if leaving the channel
        :return: `True` if the channel was joined, `False` if not
        :rtype: bool
        """
        channel = channel.lower()
        self._logger.info(f'Joining channel #{channel}')

        if channel in self._expectations.get(JOIN_EXPECT, tuple()):
            self._logger.debug(f'Attempted to join #{channel} but was already joining')
            return False

        if channel in self._expectations.get(PART_EXPECT, tuple()):
            self._logger.debug(f'Attempted to join #{channel} but it was just left and is unconfirmed')
            if action_if_leaving == 'wait':
                self._logger.debug('Waiting on leave confirmation then joining')
                try:
                    await asyncio.wait_for(self._expectations[PART_EXPECT][channel], self._expect_timeout)
                except asyncio.TimeoutError:
                    self._logger.warning('Earlier leave did not succeed. Abandoning the join')
                    return False
            elif action_if_leaving == 'raise':
                self._logger.debug('Raising exception due to race condition')
                raise ChannelPresenceRaceCondition('Tried to join while leaving')
            elif action_if_leaving == 'abort':
                self._logger.debug('Abandoning the join')
                return False

        self.queue_expectations(JOIN_EXPECT, channel)
        await self.send(f'JOIN #{channel}')
        return True

    async def leave(self, channel: str, action_if_joining: str = 'wait') -> bool:
        """
        Leaves one channel.

        Does nothing if the channel is waiting to leave or the `action_if_joining` is to abort.

        If the connection is waiting to leave this channel, these are the available actions to take:
        - `'wait'` will leave after joining
        - `'raise'` will raise a `ChannelPresenceRaceCondition` exception
        - `'abort'` will not leave

        :param str channel: Raw name of the channel
        :param str action_if_joining: The action to take if joining the channel
        :return: `True` if the channel was left, `False` if not
        :rtype: bool
        """
        channel = channel.lower()
        self._logger.info(f'Leaving channel #{channel}')

        if channel in self._expectations.get(PART_EXPECT, tuple()):
            self._logger.debug(f'Attempted to leave #{channel} but was already leaving')
            return False

        if channel in self._expectations.get(JOIN_EXPECT, tuple()):
            self._logger.debug(f'Attempted to leave #{channel} but it was just joined and is unconfirmed')
            if action_if_joining == 'raise':
                self._logger.debug('Raising exception due to race condition')
                raise ChannelPresenceRaceCondition('Tried to leave while joining')
            elif action_if_joining == 'wait':
                self._logger.debug('Waiting on join confirmation then leaving')
                try:
                    await asyncio.wait_for(self._expectations[JOIN_EXPECT][channel], self._expect_timeout)
                except asyncio.TimeoutError:
                    self._logger.warning('Earlier join did not succeed. Abandoning the leave')
                    return False
            elif action_if_joining == 'abort':
                self._logger.debug('Abandoning the leave')
                return False

        self.queue_expectations(PART_EXPECT, channel)
        await self.send(f'PART #{channel}')
        return True

    def manage_expectations(self, data: str) -> bool:
        """
        Checks the data against any expectations.

        :param str data: Single line of data from the websocket
        :return: `True` if the data should be dispatched to workers, `False` if not
        :rtype: bool
        """
        for expect in self._expectations.keys():
            pattern = self.expectation_patterns[expect]

            if expect == AUTH_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    code = match.group('code')
                    self._logger.debug(f'Auth resp: {match.group("msg")!r}')
                    self.resolve_expectations(expect, code)
                    return False

            elif expect == CAP_REQ_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    acknowledged = match.group('cap')
                    self._logger.debug(f'Capacities acknowledged: {acknowledged}')
                    capacities = [cap[10:] for cap in acknowledged.split(' ')]
                    self.resolve_expectations(expect, *capacities)
                    return False

            elif expect == JOIN_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    if match.group('who') == self._username:
                        self.resolve_expectations(expect, match.group('joined'))
                        return True

            elif expect == PART_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    if match.group('who') == self._username:
                        self.resolve_expectations(expect, match.group('left'))
                        return True

        return True

    def queue_expectations(self, category: str, *parts: str, timeout: int = 5) -> List[asyncio.Task]:
        """
        Tasks an expectation for each part of `parts` in the category, and puts the `asyncio.Future` in
        `self.expectations[category][part]`.

        The resulting log, if the expectation times out, will be `f'{category}:{part}'`.

        :param str category: Main category name
        :param str parts: Category part names
        :param int timeout: Amount of time to wait before timing out
        :return: List of expectation tasks
        :rtype: List[asyncio.Task]
        """
        expects: List[asyncio.Task] = []

        if len(parts):
            category_dict = self._expectations.setdefault(category, dict())
            for part in parts:
                category_dict[part] = asyncio.Future()
                expects.append(
                    asyncio.create_task(self.expect(category_dict[part], f'{category}:{part}', timeout=timeout))
                )

        return expects

    async def recv(self) -> str:
        """
        Waits for and returns the next message from the server.

        Internally handles ping pong and waits for the next one to return.

        :return: Raw data from the server, possibly multiline?
        :rtype: str
        """
        assert self._websocket is not None  # typing
        data = ensure_str(await self._websocket.recv())

        while data.startswith('PING '):
            self._logger.debug('PING?')
            asyncio.create_task(self.send(f'PONG {data.rstrip()[5:]}'))
            self._logger.debug('PONG!')
            data = ensure_str(await self._websocket.recv())

        return data

    def resolve_expectations(self, category: str, *parts: str):
        """
        Resolves and deletes the `asyncio.Future` in `self.expectations` by category and parts, then deletes the
        category if it's empty after.

        :param str category: Main category name
        :param str parts: Category part names
        """
        for part in parts:
            future = self._expectations[category][part]
            if not future.done():
                self._expectations[category][part].set_result(None)
            del self._expectations[category][part]
            self._logger.debug(f'Resolved expectation {category}:{part}')

        if not len(self._expectations[category]):
            del self._expectations[category]

    async def send(self, data: str, redact_log: Optional[str] = None):
        """
        Sends data to the server.

        If the data is sensitive, i.e. PASS login, then set `redact_log` and that will be the logged value. Adds its own
        carriage return for IRC.

        :param str data: Message to send
        :param redact_log: Optional value to log instead of the data
        :type redact_log: str or None
        """
        if self._websocket is None:
            return

        if redact_log is None:
            self._logger.debug(f'Sending data: {data!r}')
        else:
            self._logger.debug(f'Sending data: {redact_log!r}')
        await self._websocket.send(data + '\r\n')

    async def __aenter__(self) -> 'TwitchChatClient':
        await self.connect()
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        if self._buffer_task is not None:
            self._buffer_task.cancel()

        if self._websocket is not None:
            websocket = self._websocket
            self._websocket = None
            await websocket.close()

        for category, expectations in list(self._expectations.items()):
            self.resolve_expectations(category, *list(expectations.keys()))
