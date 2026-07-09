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


def alter_session_statement_pattern(address_regexp: str) -> re.Pattern:
    sql = alter_session_sql(address_regexp)
    regexp = sql.replace(" ", " +").replace("=", " *= *")
    return re.compile(regexp)


@dataclass
class IpParser:
    ip: IpAddress | None = None
    _pattern = alter_session_statement_pattern("(.*):([0-9]+)")

    def _parse_script_output_address(self, statement: str) -> IpAddress | None:
        if m := self._pattern.match(statement):
            host = m.group(1)
            port = int(m.group(2))
            return IpAddress(host, port)
        return None

    def query(self, query: str) -> pyexasol.ExaStatement:
        if self.ip is None:
            self.ip = self._parse_script_output_address(query)
        return Mock(fetchone=Mock(return_value=[""]))


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
