import io
from inspect import cleandoc

# import LogHandler
from unittest.mock import Mock

from exasol.pytest_slc import udf_debug


def test_x1():
    rfile = io.StringIO("abc\ndef\n")
    while line := rfile.readline():
        print(line, end="")


def log_handler(host: str, port: int, data: str):
    """
    Return an instance of LogHandler with the specified host and port as
    client_address, and simulating the specified data to be received.
    """

    handler = udf_debug.LogHandler()
    handler.rfile = io.StringIO(cleandoc(data))
    handler.client_address = [host, port]
    handler.server = Mock(output=Mock())
    return handler


def test_x2():
    payload = ["line one", "line two"]
    data = io.BytesIO("\r\n".join(payload).encode("utf-8"))
    while d := data.readline():
        s = d.decode("utf-8", "replace").rstrip("\r\n")
        print(s)
    request = Mock(makefile=Mock(return_value=data))
    server = Mock(output=Mock())
    handler = udf_debug.LogHandler(request, client_address=["host", 123], server=server)
    handler.server.output.put_nowait("")
    assert handler.server.output.put_nowait.called


def test_x3():
    data = cleandoc("""
        line one
        line two
        """)
    handler = log_handler(host="host", port=123, data=data)
    handler.server.output.put_nowait("Hello")
    # monkeypatch.setattr(udf_debug.socketserver.StreamRequestHandler, "rfile", "hello")
