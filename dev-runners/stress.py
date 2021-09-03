import asyncio
import collections
import json
from pathlib import Path
import pprint
from typing import Dict, Set, Type

import aiologger

from green_eggs.client import TwitchChatClient
from green_eggs.data_types import BaseTags, HasTags, patterns

logger = aiologger.Logger.with_default_handlers()

unhandled_bits: Dict[Type[BaseTags], Dict[str, Set[str]]] = collections.defaultdict(
    lambda: collections.defaultdict(set)
)

secrets_file = Path(__file__).resolve().parent.parent / 'secrets.json'
secrets = json.loads(secrets_file.read_text())
username = secrets['username']
token = secrets['token']


def record_unhandled(tags: BaseTags):
    if len(tags.unhandled):
        unhandled_for_tags_type = unhandled_bits[type(tags)]
        for k, v in tags.unhandled.items():
            unhandled_for_tags_type[k].add(v)


async def stress():
    async with TwitchChatClient(username=username, token=token, logger=logger) as client:
        await client.join('LEC')
        await client.join('auronplay')
        await client.join('otplol_')
        await client.join('ESL_CSGO')
        await client.join('ESL_DOTA2')
        await client.join('xQcOW')
        await client.join('dota2mc_ru')
        await client.join('LVPes')
        await client.join('ZeratoR')
        await client.join('fps_shaka')

        async for raw, timestamp in client.incoming():
            for handle_type, pattern in patterns.items():
                match = pattern.match(raw)
                if match is not None:
                    # TODO curses view
                    try:
                        handle_able = handle_type.from_match_dict(
                            default_timestamp=timestamp, raw=raw, **match.groupdict()
                        )
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        print('Error handling matched message')
                        print(f'- HandleAble type: {handle_type.__name__}\nRaw message: {raw!r}')
                        print(f'- {e}')
                    else:
                        if isinstance(handle_able, HasTags):
                            record_unhandled(handle_able.tags)


async def main():
    try:
        await stress()
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task = None
    try:
        task = loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        if task:
            task.cancel()
    finally:
        pprint.pprint({handle_able.__name__: dict(unhandled) for handle_able, unhandled in unhandled_bits.items()})
        loop.close()
