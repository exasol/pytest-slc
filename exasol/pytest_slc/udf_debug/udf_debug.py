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
Printer: TypeAlias = Callable[[str], None]

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
        # LOG.debug("LogHandler.handle()")
        address = f"{self.client_address[0]}:{self.client_address[1]}"
        buffer = []
        while True:
            data = self.rfile.readline()
            # LOG.debug(f'handle(): data = {data}')
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

    # rename output: to queue
    def __init__(self, server_address: IpAddress, output: Queue):
        output.put_nowait(f"Server address: {server_address}\n")
        self.output = output
        super().__init__(server_address.as_tuple, LogHandler)


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

    server = LogServer(server_address=server_address, output=queue)
    server_ready.set()
    try:
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 1})
        thread.start()
        shutdown_server.wait()
        server.shutdown()
        thread.join()
    finally:
        sys.stdout.flush()
        server.server_close()
        del server


class Consumer(Thread):
    def __init__(self, queue: Queue, printer: Printer):
        super().__init__()
        self._queue = queue
        self._stop = threading.Event()
        self._printer = printer

    def stop(self) -> None:
        self._stop.set()
        self._queue.put("Cancel")  # Send message to cancel thread

    def run(self):
        while not self._stop.is_set():
            try:
                message = self._queue.get()
                # LOG.debug(f"Consumer: message = {message.strip()}")
                # try to keep messages identical
                # Removed trailing newline
                self._printer(f"UDF Debug {message}")
            except (OSError, ValueError):
                traceback.print_exc()
        self._queue.close()


def start_udf_output_redirect_consumer(
    query: QueryExecutor,
    host: str | None,
    printer: Printer,
):
    """
    Start the output forwarding process and its consumer thread.
    """

    server = IpAddress.create(host, 3000)
    queue: Queue = Queue()
    # events to enable LogServerProcess to signal being ready and
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

    consumer = Consumer(queue, printer)
    consumer.start()

    if not server_ready.wait(30):
        raise TimeoutError("LogServerProcess did not signal readyness")

    # Create socket writer client simulating the database and a UDF
    # running inside.
    query(f"ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='{server}'")
    return process, queue, consumer, shutdown_server


class UdfDebugger:
    """
    Context manager for temporary UDF output redirection.
    """

    def __init__(
        self,
        query: QueryExecutor,
        server: str | None = None,
        # output: TextStream | None = None,
        printer: Printer | None = None,
    ):
        self.printer = printer or print
        self.query = query
        self.server = server
        self._process = None
        self._queue = None
        self._consumer: Consumer | None = None
        self._shutdown_server = None

    def __enter__(self):
        return self._activate()

    def start(self):
        """
        Enter the debugger context explicitly.
        """
        return self._activate()

    def _activate(self):
        self._process, self._queue, self._consumer, self._shutdown_server = (
            start_udf_output_redirect_consumer(
                query=self.query, host=self.server, printer=self.printer
            )
        )
        return self

    def __exit__(self, type_, value, trace_back):
        if self._process is not None:
            self._shutdown_server.set()
            self._consumer.stop()

        self._process = None
        self._queue = None

    def stop(self, type_=None, value=None, trace_back=None):
        """
        Exit the debugger context explicitly.
        """
        return self.__exit__(type_, value, trace_back)
