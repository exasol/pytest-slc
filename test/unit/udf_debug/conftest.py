import pytest

from exasol.pytest_slc.udf_debug.ip_address import IpAddress


@pytest.fixture
def client_address() -> IpAddress:
    return IpAddress("my-host", 123)
