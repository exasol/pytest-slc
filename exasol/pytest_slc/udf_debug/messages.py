import contextlib
import io
import logging
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import cast

from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

LOG = logging.getLogger(__name__)


class UnsupportedLocationType(Exception):
    pass


@dataclass
class Accessor:
    label: str
    stream: io.TextIOBase | io.StringIO


@contextlib.contextmanager
def access(location: io.StringIO | Path) -> Accessor:
    if isinstance(location, io.StringIO):
        yield Accessor("String Buffer", io.StringIO(location.getvalue()))
    elif isinstance(location, Path):
        with location.open("r") as stream:
            yield Accessor(str(location), stream)
    else:
        raise UnsupportedLocationType(f"{type(location)}")



def _wait_with_retry(location: Path | io.StringIO, messages: list[str]) -> None:
    """
    Search ``location`` for lines containing the expected messages using
    the specified tenacity.Retrying options.
    """

def _remaining(line: str, messages: list[str]) -> list[str]:
    # Return the messages not contained in the current line.
    return [m for m in messages if m not in line]

    with access(location) as accessor:
        LOG.debug(f"Searching lines {list(messages)}")
        while line := accessor.stream.readline():
            line = line.strip()
            messages = _remaining(line, messages)
        if messages:
            raise TimeoutError(
                f"{accessor.label} did not contain expected messages {list(messages)}."
            )


def wait_for_messages(
    location: io.StringIO | Path,
    *messages: str,
    timeout: timedelta = timedelta(seconds=2),
    interval: timedelta = timedelta(seconds=1),
) -> None:
    retrying = Retrying(
            stop=stop_after_delay(timeout),
            wait=wait_fixed(interval),
        )
    for attempt in retrying:
        with attempt:
            _wait_with_retry(location, messages)
