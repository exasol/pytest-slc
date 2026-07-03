"""
Support for capturing the output of UDFs.
"""

import multiprocessing as mp
import threading
import traceback
from collections.abc import Callable
from threading import Thread
from typing import TypeAlias

import pyexasol

from exasol.pytest_slc.udf_debug.ip_address import IpAddress
from exasol.pytest_slc.udf_debug.log_server import LogServerProcess

PrintFunc: TypeAlias = Callable[[str], None]
QueryFunc: TypeAlias = Callable[[str], pyexasol.ExaStatement]


class UdfDebugException(Exception):
    """
    Raised in case the UDF Debug server could not be started.
    """


class Consumer(Thread):
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
    def __init__(
        self,
        query: QueryFunc,
        host: str | None,
        print_func: PrintFunc,
    ):
        self.ip_address = IpAddress.create(host, 3000)
        self._query = query
        self._print = print_func or print
        self._log_server: LogServerProcess | None = None
        self._consumer: Consumer | None = None

    def activate(self) -> None:
        queue = mp.Queue()
        self._log_server = LogServerProcess(self.ip_address, queue)
        self._log_server.start()

        self._consumer = Consumer(queue, self._print)
        self._consumer.start()

        if not self._log_server.ready.wait(30):
            raise UdfDebugException("LogServerProcess did not signal readyness")
        self._query(f"ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='{self.ip_address}'")

    def disable(self) -> None:
        if self._log_server is None:
            return
        self._log_server.shutdown()
        self._consumer.stop()
        self._log_server.queue = None
        self._log_server = None
