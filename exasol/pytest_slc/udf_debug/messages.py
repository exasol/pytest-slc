import contextlib
import io
import logging
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import (
    Callable,
    TypeAlias,
    cast,
)

from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

LOG = logging.getLogger(__name__)
LineReader: TypeAlias = Callable[[], str]


def wait_for_messages(
    read_line: LineReader,
    *expected_messages: str,
    timeout: timedelta = timedelta(seconds=10),
) -> None:
    retrying = Retrying(
            stop=stop_after_delay(timeout),
        )
    messages = expected_messages
    for attempt in retrying:
        with attempt:
            line = read_line()
            # skip messages already found
            messages = [m for m in messages if m not in line]
            if messages:
                raise TimeoutError(
                    f"Did not find expected messages {list(messages)}."
                )
