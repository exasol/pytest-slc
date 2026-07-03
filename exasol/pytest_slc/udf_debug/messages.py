from collections.abc import Callable
from datetime import timedelta
from typing import TypeAlias

from tenacity import (
    Retrying,
    TryAgain,
)
from tenacity.stop import stop_after_delay

LineReader: TypeAlias = Callable[[], str]


def wait_for_messages(
    read_line: LineReader,
    *expected_messages: str,
    timeout: timedelta = timedelta(seconds=10),
) -> None:
    """
    Wait until all of the ``expected_messages`` were found as substrings
    in the lines read by ``read_line``.

    A single line can lead to multiple expected_messages being found.

    Args:

        * read_line: function to read the next line of an input stream
        * expected_messages: list of expected messages
        * timeout: maximum time until all expected messages must be found

    Raises:

       TimeoutError if not all messages could be found before the specified
                    timeout.
    """

    messages = list(expected_messages)
    for attempt in Retrying(stop=stop_after_delay(timeout)):
        with attempt:
            line = read_line()
            # skip messages already found
            messages = [m for m in messages if m not in line]
            if messages:
                raise TryAgain()

    if messages:
        raise TimeoutError(f"Did not find expected messages {list(messages)}.")
