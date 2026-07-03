from __future__ import annotations

import socket
from dataclasses import dataclass


def default_host() -> str:
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except OSError:
        return "0.0.0.0"


@dataclass
class IpAddress:
    host: str
    port: int

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def as_tuple(self) -> tuple[str, int]:
        return (self.host, self.port)

    @classmethod
    def create(cls, host: str | None, port: int) -> IpAddress:
        host = default_host() if host is None else host
        return cls(host, port)
