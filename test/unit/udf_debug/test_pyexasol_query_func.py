from typing import Any
from unittest.mock import (
    Mock,
    call,
)

import pytest

from exasol.pytest_slc.udf_debug import pyexasol_query_func


@pytest.fixture
def sql_statement() -> str:
    return "SELECT 1 from DUAL"


def connection_mock(rowcount: int, rows: list[list[Any]] | None = None) -> Mock:
    connection = Mock()
    statement = Mock()
    statement.rowcount.return_value = rowcount
    statement.fetchall.return_value = rows
    connection.execute = Mock(return_value=statement)
    return connection


def test_execute_called(sql_statement) -> None:
    connection = Mock()
    func = pyexasol_query_func(connection)
    func(sql_statement)
    assert connection.execute.call_args == call(sql_statement)


def test_rowcount_0(sql_statement) -> None:
    con = connection_mock(rowcount=0)
    func = pyexasol_query_func(con)
    assert func(sql_statement) == []


def test_fetchall(sql_statement) -> None:
    rows = [["a", 1], ["b", 2]]
    con = connection_mock(rowcount=2, rows=rows)
    func = pyexasol_query_func(con)
    assert func(sql_statement) == rows
