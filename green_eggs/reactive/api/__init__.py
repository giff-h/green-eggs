# -*- coding: utf-8 -*-
from aiohttp import ClientSession

from green_eggs.reactive.api.common import TwitchApiCommon
from green_eggs.reactive.api.direct import TwitchApiDirect

__all__ = ('validate_client_id', 'TwitchApiCommon', 'TwitchApiDirect')


async def validate_client_id(api_token: str) -> str:
    api_token = api_token.lstrip('oauth:')
    async with ClientSession(headers={'Authorization': f'Bearer {api_token}'}) as session:
        async with session.get('https://id.twitch.tv/oauth2/validate') as response:
            response.raise_for_status()
            data = await response.json()
    return data['client_id']
