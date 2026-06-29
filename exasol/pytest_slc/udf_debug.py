"""
Support for capturing the output of UDFs.
"""

import io
import logging
import socket
import socketserver
import sys
import time
import traceback
from collections.abc import Callable
from multiprocessing import (
    Process,
    Queue,
)
from queue import Full
from threading import (
    Event,
    Thread,
)
from typing import (
    TextIO,
    TypeAlias,
)

TextStream: TypeAlias = TextIO | io.TextIOBase
QueryExecutor: TypeAlias = Callable[[str], None]


LOG = logging.getLogger(__name__)


class UdfDebugException(Exception):
    """
    Raised in case the UDF Debug server could not be started.
    """


class LogHandler(socketserver.StreamRequestHandler):
    """
    Read output lines from the UDF log socket.
    """

    def handle(self):
        address = f"{self.client_address[0]}:{self.client_address[1]}"
        buffer = []
        while True:
            data = self.rfile.readline()
            if not data:
                break
            buffer.append(data.decode("utf-8", "replace").rstrip("\r\n"))
            if data.endswith(b"\n"):
                message = f"{address}> {''.join(buffer).rstrip()}\n"
                try:
                    self.server.output.put_nowait(message)
                except Full as full_ex:
                    LOG.error(f"UDF debugging queue is full: {full_ex}")
                buffer = []


class LogServer(socketserver.ThreadingTCPServer):
    """
    Background socket server that forwards messages into a queue.
    """

    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], output: Queue):
        output.put_nowait(f"Server address:{server_address}\n")
        self.output = output
        super().__init__(server_address, LogHandler)


class ScriptOutputThread(Thread):
    """
    Serve UDF output in a background thread.
    """

    def __init__(self, server_address: tuple[str, int], output: Queue):
        super().__init__()
        self.server_address = server_address
        self.server = LogServer(server_address, output)
        self.finished = False

    def run(self):
        try:
            self.server.serve_forever(poll_interval=1)
        finally:
            self.server.shutdown()
            self.server.server_close()
            del self.server


def default_host() -> str:
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "0.0.0.0"


def _output_service(queue: Queue, host: str | None, port: int | None):
    """
    Start a standalone output service.

    This service can be used in another Python or R instance, for Python
    instances the connection parameter externalClient need to be specified.
    """

    host = default_host() if host is None else host
    port = 3000 if port is None else port
    thread = ScriptOutputThread(server_address=(host, port), output=queue)
    queue.put_nowait(f">>> bind the output to {host}:{port}")
    try:
        thread.run()
    except KeyboardInterrupt:
        sys.stdout.flush()


class Consumer(Thread):
    def __init__(self, queue: Queue, output: TextStream):
        super().__init__(target=self.print)
        self._queue = queue
        self._stop = Event()
        self._output = output

    def stop(self) -> None:
        self._stop.set()
        queue.put("Cancel")  # Send message to cancel stdout_thread

    def print(self):
        while not self._stop.is_set():
            try:
                message = self._queue.get()
                self._output.write(f"UDF DEBUG {message}\n")
            except (OSError, ValueError):
                traceback.print_exc()
        self._queue.close()


def start_udf_output_redirect_consumer(
    query: QueryExecutor,
    host: str | None,
    output: io.TextIOBase,
):
    """
    Start the output forwarding process and its consumer thread.
    """

    def local_ip() -> str:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    host = local_ip() if host is None else host
    LOG.info("Sending UDF output to: %s", host)

    port = 3000

    queue: Queue = Queue()
    process = Process(target=_output_service, args=(queue, host, port))
    process.start()

    stdout_thread = Consumer(queue, output)
    stdout_thread.start()
    time.sleep(10)
    if process.is_alive():
        query(f"ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='{host}:{port}';")
        return process, queue, stdout_thread

    # Failure
    stdout_thread.stop()
    raise UdfDebugException("Could not start udf_debug.py")
    return None, None, None


class UdfDebugger:
    """
    Context manager for temporary UDF output redirection.
    """

    def __init__(
        self,
        query: QueryExecutor,
        server: str | None = None,
        output: TextStream | None = sys.stdout,
    ):
        self.output = output
        self.query = query
        self.server = server
        self._process = None
        self._queue = None
        self._stdout_thread: Consumer | None = None

    def __enter__(self):
        return self._activate()

    def start(self):
        """
        Enter the debugger context explicitly.
        """
        return self._activate()

    def _activate(self):
        self._process, self._queue, self._stdout_thread = (
            start_udf_output_redirect_consumer(
                query=self.query, host=self.server, output=self.output
            )
        )
        return self

    def __exit__(self, type_, value, trace_back):
        if self._process is not None:
            self._process.terminate()
            # Wait 1 second to give socket time to process all remaining messages.
            self._stdout_thread.stop()

        self._process = None
        self._queue = None

    def stop(self, type_=None, value=None, trace_back=None):
        """
        Exit the debugger context explicitly.
        """
        return self.__exit__(type_, value, trace_back)
