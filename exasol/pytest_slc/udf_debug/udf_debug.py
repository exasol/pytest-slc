"""
Support for capturing the output of UDFs.
"""

import io
import logging
import multiprocessing as mp
import os
import queue
import signal
import socket
import socketserver
import sys
import threading
import time
import traceback
from collections.abc import Callable
from multiprocessing import (
    Process,
    Queue,
)
from threading import Thread
from typing import (
    TextIO,
    TypeAlias,
)

import pyexasol

from exasol.pytest_slc.udf_debug.ip_address import IpAddress

TextStream: TypeAlias = TextIO | io.TextIOBase
QueryExecutor: TypeAlias = Callable[[str], pyexasol.ExaStatement]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
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
        LOG.debug("LogHandler.handle()")
        address = f"{self.client_address[0]}:{self.client_address[1]}"
        buffer = []
        while True:
            data = self.rfile.readline()
            LOG.debug(f'handle(): data = {data}')
            if not data:
                break
            buffer.append(data.decode("utf-8", "replace").rstrip("\r\n"))
            if data.endswith(b"\n"):
                message = f"{address}> {''.join(buffer).rstrip()}\n"
                try:
                    self.server.output.put_nowait(message)
                except queue.Full as ex:
                    LOG.error(f"UDF debugging queue is full: {ex}")
                buffer = []


class LogServer(socketserver.ThreadingTCPServer):
    """
    Background socket server that forwards messages into a queue.
    """

    allow_reuse_address = True
    daemon_threads = True
    block_on_close = False

    def __init__(self, server_address: IpAddress, output: Queue):
        output.put_nowait(f"Server address: {server_address}\n")
        self.output = output
        LOG.debug("initializing ThreadingTCPServer with LogHandler")
        super().__init__(server_address.as_tuple, LogHandler)


class ServerThread(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class LogServerProcess(Process):
    def __init__(
        self,
        queue: Queue,
        server: IpAddress,
        server_ready: mp.Event,
        shutdown_server : mp.Event,
    ):
        self.queue = queue
        self.server = server
        self.server_ready = server_ready
        self.shutdown_server = shutdown_server
        super().__init__()

    def run(self):
        _output_service(
            self.queue,
            self.server,
            self.server_ready,
            self.shutdown_server,
        )


# class ScriptOutputThread(Thread):
#     """
#     Serve UDF output in a background thread.
#     """
#
#     def __init__(self, server_address: tuple[str, int], output: Queue):
#         super().__init__()
#         self.server_address = server_address
#         LOG.debug("ScriptOutputThread.__init__()")
#         # self.finished = False
#
#     def run(self):
#         server = LogServer(self.server_address, output)
#         try:
#             LOG.debug("server.serve_forever()")
#             server.serve_forever(poll_interval=1)
#         finally:
#             server.shutdown()
#             server.server_close()
#             del server


# def default_host() -> str:
#     try:
#         return socket.gethostbyname(socket.gethostname())
#     except OSError:
#         return "0.0.0.0"


def _output_service(
    queue: Queue,
    server_address: IpAddress,
    # host: str | None,
    # port: int | None,
    server_ready: mp.Event,
    shutdown_server: mp.Event,
):
    """
    Start a standalone output service.

    This service can be used in another Python or R instance, for Python
    instances the connection parameter externalClient need to be specified.
    """

    # handling of default host has been removed.
    # Function now requires a valid server_address to be passed.
    queue.put_nowait(f">>> bind the output to {server_address}")

    # server = LogServer(server_address=(host, port), output=queue)
    server = LogServer(server_address=server_address, output=queue)
    server_ready.set()
    try:
        LOG.debug("_output_service: server.serve_forever()")
        t = Thread(target=server.serve_forever, kwargs={"poll_interval": 1})
        t.start()
        LOG.debug("_output_service: after start")

        shutdown_server.wait()
        LOG.debug(f"_output_service: shutting down the server")
        server.shutdown()

        t.join()
        # server.serve_forever(poll_interval=1)
        LOG.debug("After server.serve_forever()")
    finally:
        LOG.debug("_output_service(): finally ")
        sys.stdout.flush()
        # server.shutdown()
        server.server_close()
        del server
    LOG.debug("_output_service: End of _output_service()")


class Consumer(Thread):
    def __init__(self, queue: Queue, output: TextStream):
        LOG.debug("Consumer.__init__()")
        super().__init__()
        self._queue = queue
        self._stop = threading.Event()
        self._output = output

    def stop(self) -> None:
        self._stop.set()
        self._queue.put("Cancel")  # Send message to cancel thread

    def run(self):
        while not self._stop.is_set():
            try:
                message = self._queue.get()
                LOG.debug(f"Consumer: message = {message}")
                # try to keep messages identical
                self._output.write(f"UDF Debug {message}\n")
                self._output.flush()
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

    server = IpAddress.create(host, 3000)
    # host = local_ip() if host is None else host
    # port = 3000
    LOG.info("Sending UDF output to: %s", server)

    queue: Queue = Queue()
    # events to enable process to signal being ready and
    # caller to request server shutdown
    server_ready = mp.Event()
    shutdown_server = mp.Event()
    process = LogServerProcess(
        queue,
        server,
        server_ready,
        shutdown_server,
    )
    process.start()

    stdout_thread = Consumer(queue, output)
    stdout_thread.start()

    if not server_ready.wait(30):
        raise Exception("timeout")

    # Create socket writer client simulating the database and a UDF
    # running inside.
    query(f"ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='{server}'")
    return process, queue, stdout_thread, shutdown_server

    # Failure: time out required
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
        output: TextStream | None = None,
        # output: TextStream | None = sys.stdout,
    ):
        self.output = output or sys.stdout
        self.query = query
        self.server = server
        self._process = None
        self._queue = None
        self._stdout_thread: Consumer | None = None
        self._shutdown_server = None

    def __enter__(self):
        return self._activate()

    def start(self):
        """
        Enter the debugger context explicitly.
        """
        return self._activate()

    def _activate(self):
        self._process, self._queue, self._stdout_thread, self._shutdown_server = (
            start_udf_output_redirect_consumer(
                query=self.query, host=self.server, output=self.output
            )
        )
        return self

    def __exit__(self, type_, value, trace_back):
        if self._process is not None:
            # self._process.terminate()
            # os.kill(self._process.pid, signal.SIGINT)
            self._shutdown_server.set()
            # Wait 1 second to give socket time to process all remaining messages.
            self._stdout_thread.stop()

        self._process = None
        self._queue = None

    def stop(self, type_=None, value=None, trace_back=None):
        """
        Exit the debugger context explicitly.
        """
        return self.__exit__(type_, value, trace_back)
