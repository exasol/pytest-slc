"""
Support for capturing the output of UDFs.
"""

import multiprocessing as mp
import threading
import traceback
from threading import Thread

from exasol.pytest_slc.udf_debug.types import PrintFunc


class Consumer(Thread):
    """
    Consumes the log messages from the specified ``queue`` and forwards
    them to the specified print function ``print_func``.
    """

    def __init__(self, queue: mp.Queue, print_func: PrintFunc):
        super().__init__()
        self._queue = queue
        self._stop_request = threading.Event()
        self._print = print_func

    def stop(self) -> None:
        self._stop_request.set()
        self._queue.put("Cancel")  # Send message to cancel thread

    def run(self):
        while not self._stop_request.is_set():
            try:
                message = self._queue.get()
                # was before: output.write(f"UDF DEBUG {msg}\n")
                self._print(f"UDF Debug {message}")
            except (OSError, ValueError):
                traceback.print_exc()
        self._queue.close()
