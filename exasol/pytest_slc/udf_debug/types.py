from collections.abc import Callable
from typing import (
    TypeAlias,
)

import pyexasol

PrintFunc: TypeAlias = Callable[[str], None]
QueryFunc: TypeAlias = Callable[[str], pyexasol.ExaStatement]
