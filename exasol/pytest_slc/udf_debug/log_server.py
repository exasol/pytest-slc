import logging
import multiprocessing as mp
import queue
import socketserver
import sys
from multiprocessing import (
    Process,
    Queue,
)
from threading import Thread

from exasol.pytest_slc.udf_debug.ip_address import IpAddress

LOG = logging.getLogger(__name__)


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
                except queue.Full:
                    logging.exception("UDF debugging queue is full")
                buffer = []


class LogServer(socketserver.ThreadingTCPServer):
    """
    Background socket server that forwards messages into a queue.
    """

    allow_reuse_address = True
    daemon_threads = True
    block_on_close = False

    def __init__(self, address: IpAddress, queue: Queue):
        queue.put_nowait(f"Server address: {address}\n")
        self.output = queue
        super().__init__(address.as_tuple, LogHandler)


class LogServerProcess(Process):
    def __init__(self, ip_address: IpAddress, queue: Queue):
        self.queue = queue
        self.ip_address = ip_address
        self.ready = mp.Event()
        self._shutdown = mp.Event()
        super().__init__()

    def shutdown(self) -> None:
        self._shutdown.set()

    def run(self):
        self.queue.put_nowait(f">>> bind the output to {self.ip_address}")
        server = LogServer(address=self.ip_address, queue=self.queue)
        self.ready.set()
        try:
            thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 1})
            thread.start()
            self._shutdown.wait()
            server.shutdown()
            thread.join()
        finally:
            sys.stdout.flush()
            server.server_close()
            del server
