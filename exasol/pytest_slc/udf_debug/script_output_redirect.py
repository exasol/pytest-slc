"""
Support for capturing the output of UDFs.
"""

import multiprocessing as mp
import threading
import traceback
from collections.abc import Callable
from datetime import timedelta
from threading import Thread
from typing import TypeAlias

import pyexasol

from exasol.pytest_slc.udf_debug.ip_address import IpAddress
from exasol.pytest_slc.udf_debug.log_server import LogServerProcess

PrintFunc: TypeAlias = Callable[[str], None]
QueryFunc: TypeAlias = Callable[[str], pyexasol.ExaStatement]


DEFAULT_PORT = 3000
SERVER_START_TIMEOUT = timedelta(seconds=30)


def alter_session_sql(address: str | IpAddress) -> str:
    return f"ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='{address}'"


class UdfDebugException(Exception):
    """
    Raised in case the UDF Debug server could not be started.
    """


class Consumer(Thread):
    """
    Consumes the log messages from the specified ``queue`` and forwards
    them to the specified print function ``print_func``.
    """

    def __init__(self, queue: mp.Queue, print_func: PrintFunc):
        super().__init__()
        self._queue = queue
        self._stop = threading.Event()
        self._print = print_func

    def stop(self) -> None:
        self._stop.set()
        self._queue.put("Cancel")  # Send message to cancel thread

    def run(self):
        while not self._stop.is_set():
            try:
                message = self._queue.get()
                # was before: output.write(f"UDF DEBUG {msg}\n")
                self._print(f"UDF Debug {message}")
            except (OSError, ValueError):
                traceback.print_exc()
        self._queue.close()


class ScriptOutputRedirect:
    """
    Configures a UDF Script Output Redirect using sql statement ``ALTER
    SESSION SET SCRIPT_OUTPUT_ADDRESS``.

    Starts a ``LogServerProcess`` and a ``Consumer`` connected via a
    ``multiprocessing.Queue``:

    Server -> Queue -> Consumer.
    """

    def __init__(
        self,
        query: QueryFunc,
        host: str | None,
        print_func: PrintFunc | None,
    ):
        self.ip_address = IpAddress.create(host, 3000)
        self._query = query
        self._print = print_func or print
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
        self._query(alter_session_sql(self.ip_address))

    def disable(self) -> None:
        """
        Disables the Script Output Redirect.
        """

        if self._log_server:
            self._log_server.shutdown()
            # advised by codex review but blocks the test from terminating:
            # self._log_server.join()
            self._log_server = None
        if self._consumer:
            self._consumer.stop()
