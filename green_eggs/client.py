# -*- coding: utf-8 -*-
import asyncio
import datetime
from types import TracebackType
from typing import AsyncIterator, Dict, List, Optional, Pattern, Tuple, Type, Union

from aiologger import Logger
import websockets

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
    host = 'wss://irc-ws.chat.twitch.tv:443'
    expectation_patterns: Dict[str, Pattern[str]] = {
        AUTH_EXPECT: const.AUTH_EXPECT_PATTERN,
        CAP_REQ_EXPECT: const.CAP_ACK_PATTERN,
        JOIN_EXPECT: const.JOIN_EXPECT_PATTERN,
        PART_EXPECT: const.PART_EXPECT_PATTERN,
    }

    def __init__(self, *, username: str, token: str, logger: Logger):
        # Initial data
        self.logger = logger
        self.token = format_oauth(token)
        self.username = username.lower()

        # Awaitable holders
        self.buffer_task: Optional[asyncio.Task] = None
        self.expectations: Dict[str, Dict[str, asyncio.Future]] = {}
        self.message_buffer: 'asyncio.Queue[BufferData]' = asyncio.Queue()

        # Other placeholders
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.ws_exc: Optional[Exception] = None
        self._expect_timeout: Union[float, int] = 5

    async def buffer_messages(self):
        """
        Infinite loop to fetch incoming data and buffer filtered messages.

        Adds the UTC timestamp of when they were received for the data types.

        :return: Generator of messages for consumption
        :rtype: AsyncIterator[Tuple[str, datetime.datetime]]
        """
        assert self.websocket is not None  # typing
        await self.websocket.ensure_open()

        while True:
            # noinspection PyBroadException
            try:
                data = await self.recv()
                now = datetime.datetime.utcnow()
                async for line in self.filter_expected(data):
                    await self.message_buffer.put((line, now))
            except asyncio.CancelledError:
                break
            except websockets.ConnectionClosedError:
                self.logger.debug('Caught a closed connection. Reconnecting...')
                await self.connect()
                await self.initialize()
            except Exception:
                self.logger.exception('Unhandled exception in listen loop')

    async def connect(self):
        """
        Connects to the IRC server and sets the websocket property.

        :raises Exception: from the websocket connect if any happened
        """
        try:
            self.websocket = await websockets.connect(self.host, timeout=10)
        except Exception as e:
            self.ws_exc = e
            self.logger.exception('Websocket connection failed')
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
            self.logger.error(f'Timed out {label} expectation')
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
                assert self.websocket is not None
                await self.websocket.close()
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
            yield await self.message_buffer.get()

    async def initialize(self):
        """
        Initializes the client connection once opened.

        Authorizes, registers capabilities, and joins initial channels.
        """
        if not await self.is_connected():
            return

        if self.buffer_task is None:
            self.buffer_task = asyncio.create_task(self.buffer_messages())

        expects = self.queue_expectations(AUTH_EXPECT, *const.EXPECTED_AUTH_CODES, timeout=self._expect_timeout)
        await self.send(f'PASS {self.token}', redact_log='PASS ******')
        await self.send(f'NICK {self.username}')
        await asyncio.gather(*expects)

        expects = self.queue_expectations(CAP_REQ_EXPECT, *const.CAP_REQ_MODES, timeout=self._expect_timeout)
        await self.send('CAP REQ :' + ' '.join(f'twitch.tv/{mode}' for mode in const.CAP_REQ_MODES))
        await asyncio.gather(*expects)

    async def is_connected(self) -> bool:
        """
        :return: Is the connection open?
        :rtype: bool
        """
        if self.websocket is None:
            return False

        await self.websocket.ensure_open()
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
        self.logger.info(f'Joining channel #{channel}')

        if channel in self.expectations.get(JOIN_EXPECT, tuple()):
            self.logger.debug(f'Attempted to join #{channel} but was already joining')
            return False

        if channel in self.expectations.get(PART_EXPECT, tuple()):
            self.logger.debug(f'Attempted to join #{channel} but it was just left and is unconfirmed')
            if action_if_leaving == 'wait':
                self.logger.debug('Waiting on leave confirmation then joining')
                try:
                    await asyncio.wait_for(self.expectations[PART_EXPECT][channel], self._expect_timeout)
                except asyncio.TimeoutError:
                    self.logger.warning('Earlier leave did not succeed. Abandoning the join')
                    return False
            elif action_if_leaving == 'raise':
                self.logger.debug('Raising exception due to race condition')
                raise ChannelPresenceRaceCondition('Tried to join while leaving')
            elif action_if_leaving == 'abort':
                self.logger.debug('Abandoning the join')
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
        self.logger.info(f'Leaving channel #{channel}')

        if channel in self.expectations.get(PART_EXPECT, tuple()):
            self.logger.debug(f'Attempted to leave #{channel} but was already leaving')
            return False

        if channel in self.expectations.get(JOIN_EXPECT, tuple()):
            self.logger.debug(f'Attempted to leave #{channel} but it was just joined and is unconfirmed')
            if action_if_joining == 'raise':
                self.logger.debug('Raising exception due to race condition')
                raise ChannelPresenceRaceCondition('Tried to leave while joining')
            elif action_if_joining == 'wait':
                self.logger.debug('Waiting on join confirmation then leaving')
                try:
                    await asyncio.wait_for(self.expectations[JOIN_EXPECT][channel], self._expect_timeout)
                except asyncio.TimeoutError:
                    self.logger.warning('Earlier join did not succeed. Abandoning the leave')
                    return False
            elif action_if_joining == 'abort':
                self.logger.debug('Abandoning the leave')
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
        for expect in self.expectations.keys():
            pattern = self.expectation_patterns[expect]

            if expect == AUTH_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    code = match.group('code')
                    self.logger.debug(f'Auth resp: {match.group("msg")!r}')
                    self.resolve_expectations(expect, code)
                    return False

            elif expect == CAP_REQ_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    acknowledged = match.group('cap')
                    self.logger.debug(f'Capacities acknowledged: {acknowledged}')
                    capacities = [cap[10:] for cap in acknowledged.split(' ')]
                    self.resolve_expectations(expect, *capacities)
                    return False

            elif expect == JOIN_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    if match.group('who') == self.username:
                        self.resolve_expectations(expect, match.group('joined'))
                        return True

            elif expect == PART_EXPECT:
                match = pattern.match(data)
                if match is not None:
                    if match.group('who') == self.username:
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
            category_dict = self.expectations.setdefault(category, dict())
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
        assert self.websocket is not None  # typing
        data = ensure_str(await self.websocket.recv())

        while data.startswith('PING '):
            self.logger.debug('PING?')
            asyncio.create_task(self.send(f'PONG {data.rstrip()[5:]}'))
            self.logger.debug('PONG!')
            data = ensure_str(await self.websocket.recv())

        return data

    def resolve_expectations(self, category: str, *parts: str):
        """
        Resolves and deletes the `asyncio.Future` in `self.expectations` by category and parts, then deletes the
        category if it's empty after.

        :param str category: Main category name
        :param str parts: Category part names
        """
        for part in parts:
            future = self.expectations[category][part]
            if not future.done():
                self.expectations[category][part].set_result(None)
            del self.expectations[category][part]
            self.logger.debug(f'Resolved expectation {category}:{part}')

        if not len(self.expectations[category]):
            del self.expectations[category]

    async def send(self, data: str, redact_log: Optional[str] = None):
        """
        Sends data to the server.

        If the data is sensitive, i.e. PASS login, then set `redact_log` and that will be the logged value. Adds its own
        carriage return for IRC.

        :param str data: Message to send
        :param redact_log: Optional value to log instead of the data
        :type redact_log: str or None
        """
        if self.websocket is None:
            return

        if redact_log is None:
            self.logger.debug(f'Sending data: {data!r}')
        else:
            self.logger.debug(f'Sending data: {redact_log!r}')
        await self.websocket.send(data + '\r\n')

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
        if self.buffer_task is not None:
            self.buffer_task.cancel()

        if self.websocket is not None:
            websocket = self.websocket
            self.websocket = None
            await websocket.close()

        for category, expectations in list(self.expectations.items()):
            self.resolve_expectations(category, *list(expectations.keys()))
