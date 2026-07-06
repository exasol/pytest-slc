from test.integration.pytester.util.itest_common import load_test_code

import pytest
from exasol.pytest_backend import (
    BACKEND_ONPREM,
    BACKEND_OPTION,
)

pytest_plugins = ["pytester"]


@pytest.mark.pytester
def test_plugin_slc_onprem(pytester):
    pytester.makepyfile(load_test_code())
    # Technically, CLI option --project-short-tag is only required as
    # distinctive prefix for SaaS instances.  See
    # test/integration/pytest_slc_saas_test.py.
    result = pytester.runpytest(
        BACKEND_OPTION, BACKEND_ONPREM, "--project-short-tag", "PYSLC"
    )
    assert result.ret == pytest.ExitCode.OK
    # Expect SaaS backend is skipped
    result.assert_outcomes(passed=1, skipped=1)
