from textwrap import dedent

import pytest
from exasol.pytest_backend import (
    BACKEND_ONPREM,
    BACKEND_OPTION,
)

from exasol.pytest_slc import SKIP_SLC_OPTION

pytest_plugins = ["pytester"]

_TEST_CODE_SKIP = dedent("""
    import pytest
    from exasol.python_extension_common.deployment.language_container_builder import (
        LanguageContainerBuilder)

    @pytest.fixture(scope='session')
    def slc_builder() -> LanguageContainerBuilder:
        with LanguageContainerBuilder('test_container') as container_builder:
            yield container_builder

    def test_deploy_slc_skipped(export_slc):
        assert export_slc is None
    """)


def test_plugin_skip_slc_option(pytester):
    """
    Validates the CLI option SKIP_SLC_OPTION (--skip-slc) skips exporting
    the SLC.
    """

    pytester.makepyfile(_TEST_CODE_SKIP)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ONPREM, SKIP_SLC_OPTION)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1, skipped=0)
