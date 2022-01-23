# -*- coding: utf-8 -*-
import asyncio
import collections
import contextlib
import json
from pathlib import Path
import pprint
from typing import Dict, Set, Type, Union

import aiologger

from green_eggs.api import TwitchApi
from green_eggs.client import TwitchChatClient
from green_eggs.data_types import BaseTags, HandleAble, HasTags, UserNoticeTags, patterns

unhandled_bits: Dict[Union[Type[HandleAble], Type[BaseTags]], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)

repo_dir = Path(__file__).resolve().parent.parent
secrets_file = repo_dir / 'secrets.json'
secrets = json.loads(secrets_file.read_text())
username = secrets['username']
client_id = secrets['client_id']
token = secrets['token']


def record_unhandled(data_type: Union[HandleAble, BaseTags]):
    if isinstance(data_type, HasTags):
        record_unhandled(data_type.tags)
    if isinstance(data_type, UserNoticeTags):
        record_unhandled(data_type.msg_params)


@contextlib.asynccontextmanager
async def client(logger: aiologger.Logger):
    async with TwitchChatClient(username=username, token=token, logger=logger) as chat:
        yield chat


async def stress():
    logger = aiologger.Logger.with_default_handlers(name='stress')

    async with TwitchApi(client_id=client_id, token=token, logger=logger) as api:
        streams = await api.get_streams(first=10)

    logins = [stream['user_login'] for stream in streams['data']]

    async with client(logger) as chat:
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
                        record_unhandled(handle_able)


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
        pprint.pprint({type_.__name__: dict(unhandled) for type_, unhandled in list(unhandled_bits.items())})
        pending = asyncio.all_tasks(loop=loop)
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
