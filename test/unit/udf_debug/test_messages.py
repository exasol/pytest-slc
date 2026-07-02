import contextlib
import io
from datetime import timedelta
from pathlib import Path

import pytest
import tenacity

from exasol.pytest_slc.udf_debug.messages import wait_for_messages

TIMEOUT = timedelta(seconds=0.02)


@pytest.fixture
def sample_lines() -> str:
    return "line 1\nline 2\nline 3\n"


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


def test_failure(reading, sample_lines):
    expected_messages = ["line 1", "line 99"]
    with reading(sample_lines) as reader:
        with pytest.raises(tenacity.RetryError):
            wait_for_messages(reader, *expected_messages, timeout=TIMEOUT)


def test_success(reading, sample_lines):
    expected_messages = ["line 1", "line 3"]
    with reading(sample_lines) as reader:
        with not_raises(tenacity.RetryError):
            wait_for_messages(reader, *expected_messages, timeout=TIMEOUT)
