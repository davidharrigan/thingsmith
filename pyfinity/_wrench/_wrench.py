from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction


class WrenchUnit(Enum):
    METRIC = auto()
    SAE = auto()


@dataclass
class Wrench:
    size: int | float | Fraction | str
    grip_width_mm: float = 0
    unit: WrenchUnit = WrenchUnit.METRIC

    def __post_init__(self) -> None:
        if not self.size:
            msg = "size is required"
            raise ValueError(msg)
        if isinstance(self.size, str):
            self.size = Fraction(self.size)

        if not self.grip_width_mm:
            if self.unit == WrenchUnit.METRIC:
                self.grip_width_mm = self.__approximate_grip_width(
                    float(self.size))
            elif self.unit == WrenchUnit.SAE:
                self.grip_width_mm = self.__approximate_grip_width(
                    self.__in_to_mm(float(self.size)))
            else:
                raise NotImplementedError

    @staticmethod
    def __approximate_grip_width(wrench_size_mm: float) -> float:
        reference_size = 10.0
        reference_width = 9.0
        scaling_factor = (wrench_size_mm / reference_size) ** 0.6
        return reference_width * scaling_factor

    @staticmethod
    def __in_to_mm(size_in: float) -> float:
        return size_in * 25.4

    @property
    def profile_width(self):
        return self.grip_width_mm + 1  # padding

    @property
    def profile_height(self):
        return self.grip_width_mm + 2  # padding

    def __str__(self) -> str:
        unit = "mm" if self.unit == WrenchUnit.METRIC else '"'
        return f"{self.size}{unit}"
