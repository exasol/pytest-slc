from dataclasses import dataclass


@dataclass
class IpAddress:
    host: str
    port: int

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def as_tuple(self) -> tuple[str, int]:
        return (self.host, self.port)
