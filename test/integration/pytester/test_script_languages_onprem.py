import pytest
from exasol.pytest_backend import (
    BACKEND_ONPREM,
    BACKEND_OPTION,
)

from exasol.pytest_slc import SCRIPT_LANGUAGES_OPTION

pytest_plugins = ["pytester"]


@pytest.mark.pytester
def test_no_option_for_script_languages_raises_wrapper(pytester):
    pytester.makepyfile("""
import pytest

def test_no_option_for_script_languages_raises(script_languages):
    assert True
""")
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ONPREM)
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    result.assert_outcomes(errors=1)


@pytest.mark.pytester
def test_empty_value_for_script_languages_raises_wrapper(pytester):
    pytester.makepyfile("""
import pytest

def test_empty_value_for_script_languages_raises(script_languages):
    assert True
""")
    result = pytester.runpytest(
        BACKEND_OPTION, BACKEND_ONPREM, SCRIPT_LANGUAGES_OPTION, ""
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    result.assert_outcomes(errors=1)


@pytest.mark.pytester
@pytest.mark.parametrize(
    "fixture_under_test",
    [
        "activate_script_languages_for_session",
        "activate_script_languages_for_module",
        "activate_script_languages_for_function",
    ],
)
def test_setting_script_languages_wrapper(pytester, fixture_under_test):
    expected_script_languages = r"PYTHON3=PYTEST_SCL_INTEGRATION_TEST"
    pytester.makepyfile(f"""
    import pytest
    from exasol.python_extension_common.deployment.language_container_deployer import (
        LanguageActivationLevel,
        get_language_settings,
    )

    def test_empty_value_for_script_languages_raises({fixture_under_test}, pyexasol_connection):
        current_script_languages = get_language_settings(
            pyexasol_connection, LanguageActivationLevel.Session
        )
        assert current_script_languages == "{expected_script_languages}"
    """)
    result = pytester.runpytest(
        BACKEND_OPTION,
        BACKEND_ONPREM,
        SCRIPT_LANGUAGES_OPTION,
        expected_script_languages,
    )
    # testing against SaaS API is skipped
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1, skipped=1)


@pytest.mark.pytester
def test_script_languages_for_function_is_reset_wrapper(pytester):
    expected_script_languages = r"PYTHON3=PYTEST_SCL_INTEGRATION_TEST"
    pytester.makepyfile(f"""
    import pytest
    from exasol.python_extension_common.deployment.language_container_deployer import (
        LanguageActivationLevel,
        get_language_settings,
    )

    def test_script_languages_for_function_is_reset(
        activate_script_languages_for_function,
        pyexasol_connection,
    ):
        current_script_languages = get_language_settings(
            pyexasol_connection, LanguageActivationLevel.Session
        )
        assert current_script_languages == "{expected_script_languages}"

    def test_script_languages_for_function_was_reset(pyexasol_connection):
        current_script_languages = get_language_settings(
            pyexasol_connection, LanguageActivationLevel.Session
        )
        assert current_script_languages != "{expected_script_languages}"
    """)
    result = pytester.runpytest(
        BACKEND_OPTION,
        BACKEND_ONPREM,
        SCRIPT_LANGUAGES_OPTION,
        expected_script_languages,
    )
    # testing against SaaS API is skipped
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=2)


@pytest.mark.pytester
def test_script_languages_for_module_is_reset_wrapper(pytester):
    expected_script_languages = r"PYTHON3=PYTEST_SCL_INTEGRATION_TEST"
    pytester.makepyfile(test_module1=f"""
    import pytest
    from exasol.python_extension_common.deployment.language_container_deployer import (
        LanguageActivationLevel,
        get_language_settings,
    )

    def test_script_languages_for_module_is_reset(
        activate_script_languages_for_module,
        pyexasol_connection,
    ):
        current_script_languages = get_language_settings(
            pyexasol_connection, LanguageActivationLevel.Session
        )
        assert current_script_languages == "{expected_script_languages}"
    """)

    pytester.makepyfile(test_module2=f"""
    import pytest
    from exasol.python_extension_common.deployment.language_container_deployer import (
        LanguageActivationLevel,
        get_language_settings,
    )

    def test_script_languages_for_module_was_reset(pyexasol_connection):
        current_script_languages = get_language_settings(
            pyexasol_connection, LanguageActivationLevel.Session
        )
        assert current_script_languages != "{expected_script_languages}"
    """)
    result = pytester.runpytest(
        BACKEND_OPTION,
        BACKEND_ONPREM,
        SCRIPT_LANGUAGES_OPTION,
        expected_script_languages,
    )
    # testing against SaaS API is skipped
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=2)


@pytest.mark.pytester
@pytest.mark.parametrize(
    "fixture_under_test",
    [
        "activate_script_languages_for_session",
        "activate_script_languages_for_module",
    ],
)
def test_script_languages_is_not_reset_wrapper(pytester, fixture_under_test):
    expected_script_languages = r"PYTHON3=PYTEST_SCL_INTEGRATION_TEST"
    pytester.makepyfile(f"""
    import pytest
    from exasol.python_extension_common.deployment.language_container_deployer import (
        LanguageActivationLevel,
        get_language_settings,
    )

    def test_script_languages_is_not_reset(
        {fixture_under_test},
        pyexasol_connection,
    ):
        current_script_languages = get_language_settings(
            pyexasol_connection, LanguageActivationLevel.Session
        )
        assert current_script_languages == "{expected_script_languages}"

    def test_script_languages_was_not_reset(pyexasol_connection):
        current_script_languages = get_language_settings(
            pyexasol_connection, LanguageActivationLevel.Session
        )
        assert current_script_languages == "{expected_script_languages}"
    """)
    result = pytester.runpytest(
        BACKEND_OPTION,
        BACKEND_ONPREM,
        SCRIPT_LANGUAGES_OPTION,
        expected_script_languages,
    )
    # testing against SaaS API is skipped
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=2)
