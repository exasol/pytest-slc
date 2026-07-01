import contextlib
import io
import logging
from datetime import timedelta

import pytest
import tenacity

from exasol.pytest_slc.udf_debug.messages import wait_for_messages

LOG = logging.getLogger(__name__)
LINES = ["line 1", "line 2"]
TIMING = {
    "interval": timedelta(seconds=0.01),
    "timeout": timedelta(seconds=0.02),
}


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
