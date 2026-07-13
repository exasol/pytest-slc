from collections.abc import Callable
from typing import (
    Any,
    TypeAlias,
)

PrintFunc: TypeAlias = Callable[[str], None]
QueryResult: TypeAlias = list[tuple[Any, ...]]
QueryFunc: TypeAlias = Callable[[str], QueryResult]
