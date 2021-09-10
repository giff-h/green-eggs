import inspect
from typing import Any, Awaitable, Callable, List

from aiologger import Logger as Logger

async def catch_all(_logger: Logger, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any: ...
def validate_function_signature(func: Callable[..., Any], expected_keywords: List[str]) -> List[inspect.Parameter]: ...
