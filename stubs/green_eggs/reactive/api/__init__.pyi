from green_eggs.reactive.api.common import TwitchApiCommon as TwitchApiCommon
from green_eggs.reactive.api.direct import TwitchApiDirect as TwitchApiDirect

async def validate_client_id(api_token: str) -> str: ...
