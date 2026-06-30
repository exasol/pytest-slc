import io
import logging
import queue
import re
from dataclasses import dataclass
from inspect import cleandoc
from queue import Queue
from test.unit.udf_debug.ip_address import IpAddress
from unittest.mock import (
    Mock,
    call,
)

from exasol.pytest_slc import udf_debug


def log_handler(data: str, client_address: IpAddress, server: Mock = Mock()):
    """
    Return an instance of LogHandler with the specified host and port as
    client_address, and simulating the specified data to be received.
    """

    stream = io.BytesIO("\r\n".join(data).encode("utf-8"))
    request = Mock(makefile=Mock(return_value=stream))
    return udf_debug.LogHandler(
        request,
        client_address=client_address.as_tuple,
        server=server,
    )


def test_no_data(client_address):
    without_newline = ["line one"]
    handler = log_handler(without_newline, client_address)
    assert not handler.server.output.put_nowait.called


def test_two_lines(client_address):
    data = ["line one", "line two"]
    handler = log_handler(data + [""], client_address)
    expected = [call(f"{client_address}> {line}\n") for line in data]
    call_args_list = handler.server.output.put_nowait.call_args_list
    assert call_args_list == expected


def test_queue_full(client_address, caplog):
    """
    Simulate queue.Full exception to be raised when sending data to the
    server output and verify the log messages.
    """

    data = ["line one", "line two"]
    server = Mock()
    server.output.put_nowait.side_effect = queue.Full
    handler = log_handler(data + [""], client_address, server=server)
    actual = [rt[1:] for rt in caplog.record_tuples]
    expected = [(logging.ERROR, "UDF debugging queue is full: ")] * 2
    assert actual == expected

