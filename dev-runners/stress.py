# -*- coding: utf-8 -*-
import asyncio
import collections
import json
from pathlib import Path
import pprint
from typing import Dict, Set, Type

import aiologger

from green_eggs import data_types as dt
from green_eggs.api import TwitchApiDirect
from green_eggs.client import TwitchChatClient

repo_dir = Path(__file__).resolve().parent.parent
secrets_file = repo_dir / 'secrets.json'
secrets = json.loads(secrets_file.read_text())
username = secrets['username']
client_id = secrets['client_id']
token = secrets['token']


# Holders for actions later
unhandled_tags: Dict[Type[dt.HandleAble], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)
unhandled_badges: Dict[Type[dt.HandleAble], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)
unhandled_badge_info: Dict[Type[dt.HandleAble], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)
unhandled_msg_params: Dict[Type[dt.HandleAble], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)


async def stress():
    logger = aiologger.Logger.with_default_handlers(name='stress')
    logins = []

    async with TwitchApiDirect(client_id=client_id, token=token, logger=logger) as api:
        streams = await api.get_streams(first=20 - len(logins))

    logins.extend(stream['user_login'] for stream in streams['data'])

    async with TwitchChatClient(username=username, token=token, logger=logger) as chat:
        for login in logins:
            await chat.join(login)

        async for raw, timestamp in chat.incoming():
            for handle_type, pattern in dt.patterns.items():
                match_result = pattern.match(raw)
                if match_result is not None:
                    # TODO curses view
                    try:
                        handle_able = handle_type.from_match_dict(
                            default_timestamp=timestamp, raw=raw, **match_result.groupdict()
                        )
                    except Exception as e:
                        print('Error handling matched message')
                        print(f'- HandleAble type: {handle_type.__qualname__}\nRaw message: {raw!r}')
                        print(f'- {e}')
                    else:
                        # Actions here
                        if isinstance(handle_able, dt.HasTags):
                            for key, value in handle_able.tags.unhandled.items():
                                if key not in unhandled_tags[handle_type]:
                                    print(f'Unhandled {handle_type.__name__} tag: {key!r}')
                                unhandled_tags[handle_type][key].add(value)

                            if isinstance(handle_able.tags, dt.UserBaseTags):
                                for key, value in handle_able.tags.badges.unhandled.items():
                                    if key not in unhandled_badges[handle_type]:
                                        print(f'Unhandled {handle_type.__name__} badge: {key!r}')
                                    unhandled_badges[handle_type][key].add(value)

                            if isinstance(handle_able.tags, dt.UserChatBaseTags):
                                for key, value in handle_able.tags.badge_info.unhandled.items():
                                    if key not in unhandled_badge_info[handle_type]:
                                        print(f'Unhandled {handle_type.__name__} badge info: {key!r}')
                                    unhandled_badge_info[handle_type][key].add(value)

                            if isinstance(handle_able.tags, dt.UserNoticeTags):
                                for key, value in handle_able.tags.msg_params.unhandled.items():
                                    if key not in unhandled_msg_params[handle_type]:
                                        print(f'Unhandled {handle_type.__name__} msg_param: {key!r}')
                                    unhandled_msg_params[handle_type][key].add(value)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task = None
    try:
        task = loop.create_task(stress())
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        if task:
            task.cancel()
    finally:
        print()  # jump past the ^C in the terminal

        if unhandled_tags:
            print('Unhandled tags:')
            pprint.pprint({type_.__qualname__: dict(unhandled) for type_, unhandled in list(unhandled_tags.items())})
        if unhandled_badges:
            print('Unhandled badges:')
            pprint.pprint({type_.__qualname__: dict(unhandled) for type_, unhandled in list(unhandled_badges.items())})
        if unhandled_badge_info:
            print('Unhandled badge info:')
            pprint.pprint(
                {type_.__qualname__: dict(unhandled) for type_, unhandled in list(unhandled_badge_info.items())}
            )
        if unhandled_msg_params:
            print('Unhandled msg_params:')
            pprint.pprint(
                {type_.__qualname__: dict(unhandled) for type_, unhandled in list(unhandled_msg_params.items())}
            )

        pending = asyncio.all_tasks(loop=loop)
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
