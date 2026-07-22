from inspect import cleandoc

import pytest

from exasol.pytest_slc.udf_debug import (
    LogPipe,
    UdfOutputLogger,
    pyexasol_query_func,
    retrieve_script_output_address,
    wait_for_messages,
)


@pytest.fixture
def db_schema():
    return "ITEST_PYTSLC"


@pytest.fixture
def query_func(pyexasol_connection) -> QueryFunc:
    return pyexasol_query_func(pyexasol_connection)


def test_udf_output_logger(db_schema, query_func):
    sql = cleandoc("""
        CREATE OR REPLACE python3 SCALAR SCRIPT
        print_something()
        RETURNS int AS

        def run(ctx):
            print("Hello from UDF", flush=True)
        /
    """)
    query = query_func
    former_script_output_address = retrieve_script_output_address(query)
    query(sql)
    pipe = LogPipe()
    with UdfOutputLogger(query, print_func=pipe.input):
        query("SELECT print_something() FROM DUAL")
        wait_for_messages(pipe.output, "Hello from UDF")
    assert retrieve_script_output_address(query) == former_script_output_address
