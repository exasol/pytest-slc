import multiprocessing

import pyexasol

from exasol.pytest_slc.udf_debug.types import (
    QueryFunc,
    QueryResult,
)


class LogPipe:
    """
    Small wrapper around ``multiprocessing.Pipe`` to be used with
    ``UdfOutputLogger`` and ``wait_for_messages()``.
    """

    def __init__(self):
        self._conn1, self._conn2 = multiprocessing.Pipe()

    def input(self, data: str) -> None:
        self._conn1.send(data)

    def output(self) -> str:
        con = self._conn2
        return con.recv() if con.poll(timeout=1) else ""


def pyexasol_query_func(con: pyexasol.ExaConnection) -> QueryFunc:
    def query(sql: str) -> QueryResult:
        stmt = con.execute(sql)
        return [] if stmt.rowcount() == 0 else stmt.fetchall()

    return query
