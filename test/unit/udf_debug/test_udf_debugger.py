import time
import io
import re
import socket
from queue import Queue
from test.unit.udf_debug.ip_address import IpAddress
from unittest.mock import Mock

import pyexasol
import pytest

from exasol.pytest_slc import udf_debug


@pytest.mark.skip
def test_x01(monkeypatch, client_address) -> None:
    original_class = udf_debug.LogHandler
    def constructor(request, client_address, server):
        # print(f'constructor has been called')
        return original_class(request, client_address, Mock())

    monkeypatch.setattr(udf_debug, "LogHandler", constructor)

    data = ["line one", "line two", ""]
    stream = io.BytesIO("\r\n".join(data).encode("utf-8"))
    request = Mock(makefile=Mock(return_value=stream))
    handler = udf_debug.LogHandler(request, client_address.as_tuple, None)
    queue = Queue()

    # try:
    #     log_server = udf_debug.LogServer(client_address.as_tuple, queue)
    # except KeyboardInterrupt:
    #     pass
    # message = queue.get()
    # # Server address: ('my-host', 123)
    # print(f'{message}')

    udf_debug._output_service(queue, *client_address.as_tuple)


@pytest.mark.skip
def test_x02(client_address):
    queue = Queue()
    t = udf_debug.ScriptOutputThread(client_address.as_tuple, queue)
    t.server = Mock()
    print(f'{t.server}')
    # t.run()


def script_output_address_pattern() -> re.Pattern:
    command = "ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='(.*):([0-9]+)'"
    pattern = command.replace(" ", " +").replace("=", " *= *")
    return re.compile(pattern)


SCRIPT_OUTPUT_ADDRESS_PATTERN = script_output_address_pattern()


def parse_script_output_address(statement: str) -> IpAddress:
    if m := SCRIPT_OUTPUT_ADDRESS_PATTERN.match(statement):
        host = m.group(1)
        port = int(m.group(2))
        return IpAddress(host, port)
    raise RuntimeError(f'Couldn\'t parse ip-address from statement "{statement}"')


def send(ip: IpAddress, message: str):
    # ip = IpAddress("192.168.5.2", 3000)
    # ip = IpAddress("localhost", 3000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ip.as_tuple)
        result = s.sendall(message.encode())
        udf_debug.LOG.debug(f'sendall() returned {result}')


def test_x1(client_address) -> None:
    ip = None
    # class
    def query_executor(query: str) -> pyexasol.ExaStatement:
        nonlocal ip
        ip = parse_script_output_address(query)
        # print(f'{ip}')
        return Mock()

    # result = query_executor(f"ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS='{client_address}'")
    output = io.StringIO()
    with udf_debug.UdfDebugger(query_executor, output=output):
    # with udf_debug.UdfDebugger(query_executor, "127.0.0.1"):
        udf_debug.LOG.debug(f'sending to {ip}')
        send(ip, "message one\n")
        send(ip, "message two\n")
        send(ip, "message three\n")

    line = output.getvalue()
    print(f'{line}')
    return
    expected = 3
    result = []
    while True: # plus timeout
        if line := output.readline():
            result.append(line)
            udf_debug.LOG.debug(f"{line} {result}")
        if len(result) == expected:
            break
