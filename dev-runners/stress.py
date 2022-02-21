# -*- coding: utf-8 -*-
import asyncio
import collections
import json
from pathlib import Path
import pprint
from typing import Dict, Set, Tuple, Type, Union

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


def record_unhandled(data_type: Union[dt.HandleAble, dt.BaseTags]):
    if isinstance(data_type, dt.BaseTags):
        if data_type.unhandled:
            print('Caught unhandled')
            for key, value in data_type.unhandled.items():
                unhandled_bits[type(data_type)][key].add(value)

    if isinstance(data_type, dt.HasTags):
        record_unhandled(data_type.tags)
    if isinstance(data_type, dt.UserNoticeTags):
        record_unhandled(data_type.msg_params)


# Holders for actions later
unhandled_bits: Dict[Union[Type[dt.HandleAble], Type[dt.BaseTags]], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)

badges_set: Set[Tuple[str, str]] = set()
badge_info_set: Set[Tuple[str, str]] = set()


async def stress():
    logger = aiologger.Logger.with_default_handlers(name='stress')

    async with TwitchApiDirect(client_id=client_id, token=token, logger=logger) as api:
        streams = await api.get_streams(first=10)

    logins = [stream['user_login'] for stream in streams['data']]

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
                        record_unhandled(handle_able)

                        if isinstance(handle_able, dt.PrivMsg):
                            badges_set.update((key, value) for key, value in handle_able.tags.badges.items())
                            badge_info_set.update((key, value) for key, value in handle_able.tags.badge_info.items())


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

        if unhandled_bits:
            print('Unhandled:')
            pprint.pprint({type_.__qualname__: dict(unhandled) for type_, unhandled in list(unhandled_bits.items())})
        if badges_set:
            print('Badges:')
            pprint.pprint(sorted(badges_set))
        if badge_info_set:
            print('Badge info:')
            pprint.pprint(sorted(badge_info_set))

        pending = asyncio.all_tasks(loop=loop)
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
