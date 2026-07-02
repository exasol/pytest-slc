import contextlib
import io
import logging
from datetime import timedelta
from pathlib import Path

import pytest
import tenacity

from exasol.pytest_slc.udf_debug.messages import (
    UnsupportedLocationType,
    wait_for_messages,
)

LOG = logging.getLogger(__name__)
LINES = ["line 1", "line 2"]
TIMING = {
    "interval": timedelta(seconds=0.01),
    "timeout": timedelta(seconds=0.02),
}


def create_location(
    location_type: str, tmp_path: Path, content: str
) -> Path | io.StringIO:
    if location_type == "buffer":
        return io.StringIO(content)
    location = tmp_path / "file.txt"
    location.write_text(content)
    return location


@pytest.mark.parametrize("location_type", ["file", "buffer"])
def test_failure(tmp_path, location_type):
    location = create_location(location_type, tmp_path, "line 1\nline 3\n")
    with pytest.raises(tenacity.RetryError):
        wait_for_messages(location, *LINES, **TIMING)


@contextlib.contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail(f"Did raise {exception}")


@pytest.mark.parametrize("location_type", ["file", "buffer"])
def test_success(tmp_path, location_type):
    content = "\n".join(LINES)
    location = create_location(location_type, tmp_path, content)
    with not_raises(tenacity.RetryError):
        wait_for_messages(location, *LINES, **TIMING)


def test_unsupported_location_type():
    illegal_location = ["list"]
    with pytest.raises(UnsupportedLocationType):
        wait_for_messages(illegal_location)
