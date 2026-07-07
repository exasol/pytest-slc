from inspect import cleandoc

import pyexasol
import pytest

from exasol.pytest_slc.udf_debug import (
    LogPipe,
    UdfOutputLogger,
    wait_for_messages,
)


@pytest.fixture
def db_schema():
    return "ITEST_PYTSLC"


def test_udf_output_logger(db_schema, pyexasol_connection):
    def query(sql: str) -> pyexasol.ExaStatement:
        return pyexasol_connection.execute(sql)

    sql = cleandoc("""
        CREATE OR REPLACE python3 SCALAR SCRIPT
        print_something()
        RETURNS int AS

        def run(ctx):
            print("Hello from UDF", flush=True)
        /
    """)
    query(sql)
    pipe = LogPipe()
    with UdfOutputLogger(query, print_func=pipe.input):
        query("SELECT print_something() FROM DUAL")
        wait_for_messages(pipe.output, "Hello from UDF")
