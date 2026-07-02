import contextlib
import io
from datetime import timedelta
from pathlib import Path

import pytest
import tenacity

from exasol.pytest_slc.udf_debug.messages import (
    wait_for_messages,
)

LINES = ["line 1", "line 2"]
TIMEOUT = {"timeout": timedelta(seconds=0.02)}


@contextlib.contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail(f"Did raise {exception}")


@pytest.fixture(params=[Path, io.StringIO])
def reading(tmp_path, request):
    @contextlib.contextmanager
    def file_reading(content: str):
       file = tmp_path / "file.txt"
       file.write_text(content)
       with file.open("r") as f:
           yield f.readline

    @contextlib.contextmanager
    def string_reading(content):
        buffer = io.StringIO(content)
        yield buffer.readline

    if isinstance(request.param, Path):
        return file_reading
    else:
        return string_reading


def test_failure(reading):
    content = "line 1\nline 3\n"
    with reading(content) as reader:
        with pytest.raises(tenacity.RetryError):
            wait_for_messages(reader, *LINES, **TIMEOUT)


def test_success(reading):
    content = "\n".join(LINES)
    with reading(content) as reader:
        with not_raises(tenacity.RetryError):
            wait_for_messages(reader, *LINES, **TIMEOUT)
