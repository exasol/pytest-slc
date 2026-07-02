from collections.abc import Callable
from datetime import timedelta
from typing import (
    TypeAlias,
)

from tenacity import Retrying
from tenacity.stop import stop_after_delay

LineReader: TypeAlias = Callable[[], str]


def wait_for_messages(
    read_line: LineReader,
    *expected_messages: str,
    timeout: timedelta = timedelta(seconds=10),
) -> None:
    messages = list(expected_messages)
    for attempt in Retrying(stop=stop_after_delay(timeout)):
        with attempt:
            line = read_line()
            # skip messages already found
            messages = [m for m in messages if m not in line]
            if messages:
                raise TimeoutError(f"Did not find expected messages {list(messages)}.")
