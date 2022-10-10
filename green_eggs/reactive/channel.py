# -*- coding: utf-8 -*-
import asyncio
from collections import defaultdict, deque
from logging import Logger
from types import TracebackType
from typing import Any, Callable, Deque, Dict, Iterator, List, Mapping, Optional, Set, Tuple, Type, Union

import reactivex as rx
from reactivex import abc
from reactivex import operators as ops

from green_eggs import constants as const
from green_eggs import data_types as dt
from green_eggs.config import Config
from green_eggs.reactive.api import TwitchApiCommon
from green_eggs.reactive.client import TwitchWebsocketClient
from green_eggs.reactive.operators import filter_is_instance


class UsersInChannel:
    def __init__(self):
        self._persistent: Set[dt.NormalizedUser] = set()
        self._temporary: Set[dt.NormalizedUser] = set()

    def update_from_code353(self, code353: dt.Code353) -> None:
        """
        Sets the current users from the given Code353 object.

        This is sent upon from the websocket joining a channel and represents the complete list of users in the chat.
        """
        current_users = self._persistent.union(self._temporary)
        final_users: Set[dt.NormalizedUser] = set()
        for user_from_353 in dt.NormalizedUser.from_code353(code353):
            matched_to_current_users = False
            if current_users:
                for current_user in current_users:
                    matched_user = current_user.match_to_other(user_from_353)
                    if matched_user is not None:
                        matched_to_current_users = True
                        final_users.add(matched_user)
                        break

            if not matched_to_current_users or not current_users:
                final_users.add(user_from_353)

        self._persistent = final_users
        self._temporary = set()

    def update_from_joinpart_list(self, joinpart_list: List[dt.JoinPart]) -> None:
        """
        Sets the current users from the given JoinPart objects.

        These are sent from the websocket periodically and represents the list of users who have joined or left the chat
        since the last JoinPart list was sent.
        """
        join_users = [dt.NormalizedUser.from_joinpart(joinpart) for joinpart in joinpart_list if joinpart.is_join]
        part_users = [dt.NormalizedUser.from_joinpart(joinpart) for joinpart in joinpart_list if not joinpart.is_join]

        remained: Set[dt.NormalizedUser] = set()
        if join_users:
            for temp_user in self._temporary:
                for join_user in join_users.copy():
                    matched_user = temp_user.match_to_other(join_user)
                    if matched_user is not None:
                        join_users.remove(join_user)
                        remained.add(matched_user)
                        break

        if join_users:
            for self_user in self._persistent:
                for join_user in join_users.copy():
                    matched_user = self_user.match_to_other(join_user)
                    if matched_user is not None:
                        join_users.remove(join_user)
                        remained.add(matched_user)
                        break
                else:
                    remained.add(self_user)
        else:
            remained.update(self._persistent)

        final_users = set(
            user
            for user in remained.union(join_users)
            if not any(user.is_same_user(part_user) for part_user in part_users)
        )

        self._persistent = final_users
        self._temporary = set()

    def update_from_privmsg(self, privmsg: dt.PrivMsg) -> None:
        user_from_privmsg = dt.NormalizedUser.from_privmsg(privmsg)

        def update_from_privmsg_user(user_set: Set[dt.NormalizedUser]) -> Tuple[Set[dt.NormalizedUser], bool]:
            updated_users: Set[dt.NormalizedUser] = set()
            matched_to_user_set = False
            for user in user_set:
                matched_user = user.match_to_other(user_from_privmsg)
                if matched_user is None:
                    updated_users.add(user)
                else:
                    matched_to_user_set = True
                    updated_users.add(matched_user)

            return updated_users, matched_to_user_set

        persistent, matched_to_persistent = update_from_privmsg_user(self._persistent)
        if matched_to_persistent:
            self._persistent = persistent
        else:
            temporary, matched_to_temporary = update_from_privmsg_user(self._temporary)
            if matched_to_temporary:
                self._temporary = temporary
            else:
                self._temporary.add(user_from_privmsg)


class UserLastMessagesCache(Mapping[dt.NormalizedUser, List[dt.PrivMsg]]):
    def __init__(self, max_privmsg_count: int):
        self._cache: Dict[dt.NormalizedUser, Deque[dt.PrivMsg]] = dict()
        self._max_privmsg_count = max_privmsg_count

    def __getitem__(self, key: dt.NormalizedUser) -> List[dt.PrivMsg]:
        found_user = next((user for user in self._cache.keys() if user.is_same_user(key)), None)
        if found_user is None:
            raise KeyError(key)
        return list(self._cache[found_user])

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> Iterator[dt.NormalizedUser]:
        return iter(self._cache.keys())

    def update_from_privmsg(self, privmsg: dt.PrivMsg) -> None:
        """
        Adds a privmsg to the cache for the correct user.

        The internal cache keys may change as a result of this so do not call this while looping through the cache
        without copying the iteration with `list(messages_cache.keys())` or equivalent.

        :param dt.PrivMsg privmsg: The privmsg to add to the cache
        """
        privmsg_user = dt.NormalizedUser.from_privmsg(privmsg)
        messages: Deque[dt.PrivMsg]

        for self_user in self:
            matched_user = self_user.match_to_other(privmsg_user)
            if matched_user is not None:
                messages = self._cache[self_user]
                if matched_user != self_user:
                    # The normalized user in the internal cache had incomplete or outdated info
                    del self._cache[self_user]
                    self._cache[matched_user] = messages
                break
        else:
            # no break
            messages = deque(maxlen=self._max_privmsg_count)
            self._cache[privmsg_user] = messages

        messages.appendleft(privmsg)


class Channel:
    def __init__(
        self, *, channel_name: str, api: TwitchApiCommon, chat: TwitchWebsocketClient, config: Config, logger: Logger
    ):
        self._api: TwitchApiCommon = api
        self._api_results_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._channel_name: str = channel_name.lower()
        self._chat: TwitchWebsocketClient = chat
        self._config: Config = config
        self._disposables: List[abc.DisposableBase] = []
        self._is_setup = False
        self._logger: Logger = logger
        self._moderator_user_id_cache: Optional[Set[str]] = None
        self._permit_cache: Dict[str, asyncio.Task] = dict()
        self._roomstate: Optional[dt.RoomState] = None
        self._users_in_channel = UsersInChannel()
        self._users_last_messages = UserLastMessagesCache(5)
        self._userstate: Optional[dt.UserState] = None

        self._setup()

    def _setup(self) -> None:
        incoming_data = self._chat.incoming_data.pipe(self.filter_for_channel)
        joinpart_observable = incoming_data.pipe(filter_is_instance(dt.JoinPart))

        def closing_mapper() -> rx.Observable[Any]:
            return joinpart_observable.pipe(ops.debounce(0.25))

        self._disposables = [
            incoming_data.pipe(filter_is_instance(dt.Code353)).subscribe(on_next=self._handle_code353),
            joinpart_observable.pipe(ops.buffer_when(closing_mapper)).subscribe(on_next=self._handle_joinpart_list),
            incoming_data.pipe(filter_is_instance(dt.PrivMsg)).subscribe(on_next=self._handle_privmsg),
            incoming_data.pipe(filter_is_instance(dt.RoomState)).subscribe(on_next=self._handle_roomstate),
            incoming_data.pipe(filter_is_instance(dt.UserState)).subscribe(on_next=self._handle_userstate),
        ]

    def _handle_code353(self, code353: dt.Code353) -> None:
        self._users_in_channel.update_from_code353(code353)

    def _handle_joinpart_list(self, joinpart_list: List[dt.JoinPart]) -> None:
        self._users_in_channel.update_from_joinpart_list(joinpart_list)

    def _handle_privmsg(self, privmsg: dt.PrivMsg) -> None:
        self._users_in_channel.update_from_privmsg(privmsg)
        self._users_last_messages.update_from_privmsg(privmsg)

    def _handle_roomstate(self, roomstate: dt.RoomState) -> None:
        self._roomstate = roomstate

    def _handle_userstate(self, userstate: dt.UserState) -> None:
        self._userstate = userstate

    async def __aenter__(self) -> 'Channel':
        await self._chat.join_channel(self._channel_name)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self._chat.leave_channel(self._channel_name)

        for user in list(self._permit_cache.keys()):
            self._permit_cache[user].cancel()
        self._permit_cache.clear()

        disposables = self._disposables
        self._disposables = []
        for disposable in disposables:
            disposable.dispose()

    @staticmethod
    def _users_from_query(query: Union[str, dt.NormalizedUser, dt.PrivMsg]) -> List[dt.NormalizedUser]:
        users: List[dt.NormalizedUser]
        if isinstance(query, dt.PrivMsg):
            users = [dt.NormalizedUser.from_privmsg(query)]
        elif isinstance(query, str):
            if query.startswith('@'):
                query = query[1:]
            users = [
                dt.NormalizedUser(user_id=query),
                dt.NormalizedUser(username=query.lower()),
                dt.NormalizedUser(display_name=query),
            ]
        else:
            if not isinstance(query, dt.NormalizedUser):
                raise ValueError('Query value must be a string, NormalizedUser, or PrivMsg')
            users = [query]
        return users

    @property
    def actionable_messages_operator(self) -> Callable[[rx.Observable[dt.HandleAble]], rx.Observable[dt.PrivMsg]]:
        # TODO allow messages that weren't bopped for link
        return rx.compose(self.filter_for_channel, filter_is_instance(dt.PrivMsg))

    def add_permit_for_user(self, user: str) -> bool:
        """
        Adds a link permit for the given user by username or display name.

        If the permit was added, returns `True`.
        If a permit already existed, returns `False`.

        :param str user: The username or display name of the user to permit
        :return: Whether the permit was added
        :rtype: bool
        """
        user = user.lower()
        if user in self._permit_cache:
            return False

        async def permit_clear():
            await asyncio.sleep(self._config.link_permit_duration)
            if user in self._permit_cache:
                del self._permit_cache[user]

        self._permit_cache[user] = asyncio.create_task(permit_clear())
        return True

    @property
    def broadcaster_id(self) -> str:
        """
        Get the ID of the broadcaster user.

        :return: ID from the room state, or empty string before it's been set
        """
        return '' if self._roomstate is None else self._roomstate.tags.room_id

    @property
    def filter_for_channel(self) -> Callable[[rx.Observable[dt.HandleAble]], rx.Observable[dt.HandleAble]]:
        """
        Filters the elements of an observable that emits handleable objects to handleable objects for this channel.

        :return: An operator function that filters handleable objects to those for this channel.
        :rtype: (rx.Observable[dt.HandleAble]) -> rx.Observable[dt.HandleAble]
        """

        def is_for_this_channel(handleable: dt.HandleAble) -> bool:
            return isinstance(handleable, dt.InChannel) and handleable.where == self._channel_name

        return ops.filter(is_for_this_channel)

    # These three functions can wait on an upcoming API client redesign

    # def is_user_moderator(self, query: Union[str, dt.NormalizedUser, dt.PrivMsg]) -> bool:
    #     """
    #     Returns whether the user is a moderator in this channel.
    #
    #     The result is always True for the broadcaster.
    #
    #     If the user hasn't sent any messages in chat, the result is False.
    #
    #     The query can either be a string, a normalized user, or a privmsg the user sent.
    #     If it's a string, it will match messages on either user id or username or display name.
    #
    #     :param query: The query of the user
    #     :return: True if the user is a moderator
    #     :rtype: bool
    #     """
    #     if isinstance(query, dt.PrivMsg) and query.is_sender_moderator:
    #         return True
    #
    #     users = self._users_from_query(query)
    #     if any(user.user_id == self.broadcaster_id for user in users):
    #         return True
    #
    #     for user in users:
    #         messages = self._users_last_messages.get(user)
    #         if messages is not None:
    #             return any(privmsg.is_sender_moderator for privmsg in messages)
    #
    #     # TODO find out wtf is happening with the user oauth token
    #     return False

    # def is_user_subscribed(self, query: Union[str, dt.NormalizedUser, dt.PrivMsg]) -> rx.Observable[bool]:
    #     """
    #     Returns an observable that emits with whether the user is subscribed to this channel.
    #
    #     The result is always True for the broadcaster.
    #
    #     If the user hasn't sent any messages in chat, an API call is made.
    #
    #     The query can either be a string, a normalized user, or a privmsg the user sent.
    #     If it's a string, it will match messages on either user id or username or display name, if it has to make an api
    #     call it will expect the value to be the user id.
    #
    #     :param query: The query of the user
    #     :return: An observable that emits True if the user is subscribed, False if not
    #     :rtype: rx.Observable[bool]
    #     """
    #     if isinstance(query, dt.PrivMsg) and query.is_sender_subscribed:
    #         return rx.of(True)
    #
    #     users = self._users_from_query(query)
    #     if any(user.user_id == self.broadcaster_id for user in users):
    #         return rx.of(True)
    #
    #     for user in users:
    #         messages = self._users_last_messages.get(user)
    #         if messages is not None:
    #             return rx.of(any(privmsg.is_sender_subscribed for privmsg in messages))
    #
    #     return self._api.get_is_user_subscribed_to_channel(broadcaster_id=self.broadcaster_id, user_id=users[0].user_id)

    # def is_user_vip(self, query: Union[str, dt.NormalizedUser, dt.PrivMsg]) -> bool:
    #     """
    #     Returns whether the user is a VIP in this channel.
    #
    #     The result is always True for the broadcaster.
    #
    #     If the user hasn't sent any messages in chat, the result is False.
    #
    #     The query can either be a string, a normalized user, or a privmsg the user sent.
    #     If it's a string, it will match messages on either user id or username or display name.
    #
    #     :param query: The query of the user
    #     :return: True if the user is a VIP
    #     :rtype: bool
    #     """
    #     if isinstance(query, dt.PrivMsg) and query.is_sender_vip:
    #         return True
    #     users = self._users_from_query(query)
    #     if any(user.user_id == self.broadcaster_id for user in users):
    #         return True
    #     return any(privmsg.is_sender_vip for user in users for privmsg in self._users_last_messages.get(user, []))

    async def send_message(self, message: str) -> None:
        """
        Sends a message to this channel's chat.

        :param str message: The message to send. Can be an action if it starts with `'/'`
        """
        message = message.rstrip()
        if len(message) > const.MESSAGE_MAX_LENGTH:
            raise ValueError(f'Messages cannot exceed {const.MESSAGE_MAX_LENGTH} characters')
        await self._chat.send(f'PRIVMSG #{self._channel_name} :{message}')
