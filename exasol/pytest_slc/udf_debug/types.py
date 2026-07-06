from typing import (
    Callable,
    TypeAlias,
)

import pyexasol

PrintFunc: TypeAlias = Callable[[str], None]
QueryFunc: TypeAlias = Callable[[str], pyexasol.ExaStatement]
