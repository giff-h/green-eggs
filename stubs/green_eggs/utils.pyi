import inspect
from typing import Any, Awaitable, Callable, List, Optional

from aiologger import Logger as Logger

async def catch_all(_logger: Logger, func: Callable[..., Awaitable[_T]], *args, **kwargs) -> Optional[_T]: ...
def validate_function_signature(func: Callable[..., Any], expected_keywords: List[str]) -> List[inspect.Parameter]: ...
