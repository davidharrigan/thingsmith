from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction


class SocketUnit(Enum):
    METRIC = auto()
    SAE = auto()


@dataclass
class Socket:
    size: float | Fraction
    diameter_mm: float = 0
    height_mm: float = 0
    unit: SocketUnit = SocketUnit.METRIC

    def __str__(self) -> str:
        return f"{self.size}"
