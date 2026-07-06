from importlib import resources

MAIN_LANGUAGE_ALIAS = "PYTHON3_PYTEST_SLC"
ALT_LANGUAGE_ALIAS = "PYTHON3_PYTEST_SLC_ALT"


def load_test_code() -> str:
    template = resources.files(__package__).joinpath("inner_test_case.py.txt")
    return template.read_text(encoding="utf-8").format(
        project_file=__file__,
        main_language_alias=MAIN_LANGUAGE_ALIAS,
        alt_language_alias=ALT_LANGUAGE_ALIAS,
    )
