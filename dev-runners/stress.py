# -*- coding: utf-8 -*-
import asyncio
import collections
import contextlib
import json
from pathlib import Path
import pprint
from typing import Dict, Set, Type

import aiologger

from green_eggs.api import TwitchApi
from green_eggs.client import TwitchChatClient
from green_eggs.data_types import BaseTags, ClearChat, HasTags, PrivMsg, patterns

logger = aiologger.Logger.with_default_handlers(name='stress')

unhandled_bits: Dict[Type[BaseTags], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)

repo_dir = Path(__file__).resolve().parent.parent
secrets_file = repo_dir / 'secrets.json'
secrets = json.loads(secrets_file.read_text())
username = secrets['username']
client_id = secrets['client_id']
token = secrets['token']


def record_unhandled(tags: BaseTags):
    if len(tags.unhandled):
        unhandled_for_tags_type = unhandled_bits[type(tags)]
        for k, v in tags.unhandled.items():
            unhandled_for_tags_type[k].add(v)


@contextlib.asynccontextmanager
async def client():
    async with TwitchChatClient(username=username, token=token, logger=logger) as chat:
        try:
            yield chat
        except asyncio.CancelledError:
            pass


async def stress():
    async with TwitchApi(client_id=client_id, token=token) as api:
        streams = await api.get_streams(first=10)

    logins = [stream['user_login'] for stream in streams['data']]

    async with client() as chat:
        for login in logins:
            await chat.join(login)

        async for raw, timestamp in chat.incoming():
            for handle_type, pattern in patterns.items():
                match = pattern.match(raw)
                if match is not None:
                    # TODO curses view
                    try:
                        handle_able = handle_type.from_match_dict(
                            default_timestamp=timestamp, raw=raw, **match.groupdict()
                        )
                    except Exception as e:
                        print('Error handling matched message')
                        print(f'- HandleAble type: {handle_type.__name__}\nRaw message: {raw!r}')
                        print(f'- {e}')
                    else:
                        if isinstance(handle_able, HasTags):
                            record_unhandled(handle_able.tags)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task = None
    try:
        task = loop.create_task(stress())
        loop.run_forever()
    except KeyboardInterrupt:
        if task:
            task.cancel()
    finally:
        print()  # jump past the ^C in the terminal
        pprint.pprint({handle_able.__name__: dict(unhandled) for handle_able, unhandled in unhandled_bits.items()})
        if task is not None:
            loop.run_until_complete(task)
        loop.close()
