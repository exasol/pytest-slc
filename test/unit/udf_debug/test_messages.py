import contextlib
import io
import logging
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Callable

import pytest
import tenacity

LOG = logging.getLogger(__name__)

from exasol.pytest_slc.udf_debug.messages import wait_for_messages


def test_x1() -> None:
    data = io.StringIO("line 1\nline 2\n")
    data = Path("~/tmp/c").expanduser()
    wait_for_messages(data, "line 1", "line 3")


TIMING = {
    "interval": timedelta(seconds=0.01),
    "timeout": timedelta(seconds=0.02),
}


LINES = ["line 1", "line 2"]


@pytest.mark.parametrize("location_type", ["file", "buffer"])
def test_failure(tmp_path, location_type):
    content = "line 1\nline 3\n"
    if location_type == "file":
        location = tmp_path / "file.txt"
        location.write_text(content)
    else:
        location = io.StringIO(content)

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
    if location_type == "file":
        location = tmp_path / "file.txt"
        location.write_text(content)
    else:
        location = io.StringIO(content)

    with not_raises(tenacity.RetryError):
        wait_for_messages(location, *LINES, **TIMING)
