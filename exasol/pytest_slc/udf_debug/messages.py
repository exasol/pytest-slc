import io
import logging
from datetime import timedelta
from pathlib import Path
from typing import cast

from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

LOG = logging.getLogger(__name__)


class UnsupportedLocationType(Exception):
    pass


def _wait_with_retry(
    source: str | Path,
    stream: io.TextIOBase,
    expected: dict[str, bool],
    retrying: Retrying,
) -> None:
    """
    Search ``stream`` for the expected lines using the specified
    tenacity.Retrying options.
    """

    for attempt in retrying:
        with attempt:
            stream.seek(0)
            LOG.debug(f"Searching lines {list(expected)}")
            while line := stream.readline():
                line = line.strip()
                expected.pop(line, None)
            if expected:
                raise TimeoutError(
                    f"{source} did not contain expected lines {list(expected)}."
                )


def wait_for_messages(
    location: io.TextIOBase | Path,
    *messages: str,
    timeout: timedelta = timedelta(seconds=2),
    interval: timedelta = timedelta(seconds=1),
) -> None:
    """
    Search (repeatedly) in the specified location for all of the specified
    messages.

    Args:
        location: Instance of io.TextIOBase or pathlib.Path.

    Raise:
        TimeoutError: if one or multiple of the messages could not be found
                      after the specified timeout.
    """

    def wait(source: str, stream: io.TextIOBase):
        retrying = Retrying(
            stop=stop_after_delay(timeout),
            wait=wait_fixed(interval),
        )
        expected = dict.fromkeys(messages, False)
        _wait_with_retry(source, stream, expected, retrying)

    if isinstance(location, Path):
        with location.open("r") as stream:
            wait(str(location), stream)
    elif isinstance(location, io.StringIO):
        stream = cast(io.TextIOWrapper, io.StringIO(location.getvalue()))
        wait("StringIO buffer", stream)
    else:
        raise UnsupportedLocationType(f"{type(location)}")
