from test.unit.udf_debug.ip_address import IpAddress

import pytest


@pytest.fixture
def client_address() -> IpAddress:
    return IpAddress("my-host", 123)
