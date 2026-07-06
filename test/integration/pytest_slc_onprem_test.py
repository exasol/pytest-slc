from test.integration.pytest_slc_test_common import load_test_code

import pytest
from exasol.pytest_backend import (
    BACKEND_ONPREM,
    BACKEND_OPTION,
)


def test_pytest_slc_onprem(pytester):
    pytester.makepyfile(load_test_code())
    # Technically, CLI option --project-short-tag is only required as
    # distinctive prefix for SaaS instances.  See
    # test/integration/pytest_slc_saas_test.py.
    result = pytester.runpytest(
        BACKEND_OPTION, BACKEND_ONPREM, "--project-short-tag", "PYSLC"
    )
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1, skipped=0)
