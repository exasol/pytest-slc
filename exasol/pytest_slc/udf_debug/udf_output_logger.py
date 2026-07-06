"""
Support for capturing the output of UDFs.
"""

import multiprocessing as mp
from datetime import timedelta

from exasol.pytest_slc.udf_debug.consumer import Consumer
from exasol.pytest_slc.udf_debug.ip_address import IpAddress
from exasol.pytest_slc.udf_debug.log_server import LogServerProcess
from exasol.pytest_slc.udf_debug.types import (
    PrintFunc,
    QueryFunc,
)

DEFAULT_PORT = 3000
SERVER_START_TIMEOUT = timedelta(seconds=30)


def alter_session_sql(address: str | IpAddress) -> str:
    return f"ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='{address}'"


class UdfDebugException(Exception):
    """
    Raised in case the UDF Debug server could not be started.
    """


class UdfOutputLogger:
    """
    Context manager for temporary UDF output redirection.

    * Configures a UDF Script Output Redirect using sql statement ``ALTER
      SESSION SET SCRIPT_OUTPUT_ADDRESS``.
    * Starts a ``LogServerProcess`` and a ``Consumer`` connected via a
      ``multiprocessing.Queue``:

    Server -> Queue -> Consumer.
    """

    def __init__(
        self,
        query: QueryFunc,
        host: str | None = None,
        print_func: PrintFunc = print,
    ):
        self.ip_address = IpAddress.create(host, DEFAULT_PORT)
        self._query = query
        self._print = print_func
        self._log_server: LogServerProcess | None = None
        self._consumer: Consumer | None = None

    def activate(self) -> None:
        """
        Activates the Script Output Redirect.
        """

        queue: mp.Queue = mp.Queue()
        self._log_server = LogServerProcess(self.ip_address, queue)
        self._log_server.start()

        self._consumer = Consumer(queue, self._print)
        self._consumer.start()

        timeout = SERVER_START_TIMEOUT
        if not self._log_server.ready.wait(timeout.total_seconds()):
            self.disable()
            raise UdfDebugException(f"LogServerProcess not ready after {timeout}")
        try:
            self._query(alter_session_sql(self.ip_address))
        except:
            self.disable()
            raise

    def disable(self) -> None:
        """
        Disables the Script Output Redirect.
        """

        if self._log_server:
            self._log_server.shutdown()
            self._log_server.join(timeout=10)
            self._log_server = None
        if self._consumer:
            self._consumer.stop()
            self._consumer.join(timeout=10)

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, type_, value, trace_back):
        self.disable()
