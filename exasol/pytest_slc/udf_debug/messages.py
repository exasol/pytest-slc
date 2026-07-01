import contextlib
import io
import logging
from datetime import timedelta
from pathlib import Path

from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

LOG = logging.getLogger(__name__)


def wait_for_expected_messages(
    source: str | Path,
    stream: io.TextIOBase,
    expected: dict[str, bool],
    retrying: Retrying,
):
    for attempt in retrying:
        with attempt:
            stream.seek(0)
            LOG.debug(f"Searching messages {list(expected)}")
            while line := stream.readline():
                line = line.strip()
                expected.pop(line, None)
            if expected:
                raise TimeoutError(
                    f"{source} did not contain" f" expected messages {list(expected)}."
                )


def wait_for_messages(
    location: io.TextIOBase | Path,
    *messages: str,
    timeout: timedelta = timedelta(seconds=2),
    interval: timedelta = timedelta(seconds=1),
):
    def wait(source: str, stream: io.TextIOBase):
        retrying = Retrying(
            stop=stop_after_delay(timeout),
            wait=wait_fixed(interval),
        )
        expected = {m: False for m in messages}
        wait_for_expected_messages(source, stream, expected, retrying)

    with contextlib.ExitStack() as stack:
        if isinstance(location, Path):
            with location.open("r") as stream:
                wait(location, stream)
        elif isinstance(location, io.StringIO):
            stream = io.StringIO(location.getvalue())
            wait("StringIO buffer", stream)
        else:
            raise Exception(f"Unsupported location type {type(location)}.")
