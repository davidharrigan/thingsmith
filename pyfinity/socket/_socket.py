from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction


class Unit(Enum):
    METRIC = auto()
    SAE = auto()


@dataclass
class Socket:
    size: float | Fraction
    diameter_mm: float = 0
    height_mm: float = 0
    unit: Unit = Unit.METRIC
    drive: str | None = None

    def __str__(self) -> str:
        return f"{self.size}"
