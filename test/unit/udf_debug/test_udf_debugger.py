import contextlib
import multiprocessing
import re
import socket
from dataclasses import dataclass
from unittest.mock import Mock

import pyexasol

from exasol.pytest_slc.udf_debug import (
    IpAddress,
    UdfDebugger,
    wait_for_messages,
)
from exasol.pytest_slc.udf_debug.script_output_redirect import alter_session_sql


@dataclass
class IpParser:
    ip: IpAddress | None = None
    _pattern: re.Pattern | None = None

    def _match(self, statement: str) -> re.Match:
        if not self._pattern:
            sql = alter_session_sql("(.*):([0-9]+)")
            pattern = sql.replace(" ", " +").replace("=", " *= *")
            self._pattern = re.compile(pattern)
        return self._pattern.match(statement)

    def _parse_script_output_address(self, statement: str) -> IpAddress:
        if m := self._match(statement):
            host = m.group(1)
            port = int(m.group(2))
            return IpAddress(host, port)
        raise RuntimeError(f'Couldn\'t parse ip-address from statement "{statement}"')

    def query(self, query: str) -> pyexasol.ExaStatement:
        if self.ip is None:
            self.ip = self._parse_script_output_address(query)
        return Mock()


def send(ip: IpAddress, message: str):
    with socket.socket() as s:
        s.connect(ip.as_tuple)
        result = s.sendall(message.encode() + b"\n")


@contextlib.contextmanager
def socket_sender(ip: IpAddress):
    with socket.socket() as my_socket:
        my_socket.connect(ip.as_tuple)
        yield my_socket


def test_udf_debugger(client_address) -> None:
    con1, con2 = multiprocessing.Pipe()

    def pipe_in(data: str) -> None:
        con1.send(data)

    def pipe_out() -> str:
        return con2.recv()

    messages = [
        "message one",
        "message two",
        "message three",
    ]
    ip_parser = IpParser()
    with UdfDebugger(ip_parser.query, print_func=pipe_in):
        with socket_sender(ip_parser.ip) as my_socket:
            for m in messages:
                my_socket.sendall(m.encode() + b"\n")
        wait_for_messages(pipe_out, *messages)
