from test.integration.pytest_slc_test_common import load_test_code

import pytest
from exasol.pytest_backend import (
    BACKEND_OPTION,
    BACKEND_SAAS,
)


def test_pytest_slc_saas(pytester):
    pytester.makepyfile(load_test_code())
    # CLI option --project-short-tag is required as distinctive prefix for
    # SaaS instances.  In case of a left-over database instance the prefix
    # supports further analysis by indicating the project scope in which the
    # database instance was created.
    result = pytester.runpytest(
        BACKEND_OPTION, BACKEND_SAAS, "--project-short-tag", "PYSLC"
    )
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1, skipped=0)
