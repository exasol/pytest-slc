import contextlib
import re
import socket as socketlib
from dataclasses import dataclass
from unittest.mock import Mock

import pyexasol

from exasol.pytest_slc.udf_debug import (
    IpAddress,
    LogPipe,
    UdfOutputLogger,
    alter_session_sql,
    wait_for_messages,
)


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


@contextlib.contextmanager
def open_socket(ip: IpAddress):
    with socketlib.socket() as socket:
        socket.connect(ip.as_tuple)
        yield socket


def test_udf_output_logger(client_address) -> None:
    messages = [
        "message one",
        "message two",
        "message three",
    ]
    pipe = LogPipe()
    ip_parser = IpParser()
    with UdfOutputLogger(ip_parser.query, print_func=pipe.input):
        with open_socket(ip_parser.ip) as socket:
            for m in messages:
                socket.sendall(m.encode() + b"\n")
        wait_for_messages(pipe.output, *messages)
