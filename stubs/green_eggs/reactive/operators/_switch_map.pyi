from typing import Callable, Optional

from reactivex import Observable
from reactivex.typing import Mapper

def switch_map_(
    mapper: Optional[Mapper[_T1, Observable[_T2]]] = ...
) -> Callable[[Observable[_T1]], Observable[_T2]]: ...
