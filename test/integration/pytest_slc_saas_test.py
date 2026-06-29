import pytest
from exasol.pytest_backend import (
    BACKEND_OPTION,
    BACKEND_SAAS,
)

from test.integration.pytest_slc_test_common import load_test_code


def test_pytest_slc_saas(pytester):
    pytester.makepyfile(load_test_code())
    result = pytester.runpytest(
        BACKEND_OPTION, BACKEND_SAAS, "--project-short-tag", "PYSLC"
    )
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1, skipped=0)
