from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction
from typing import Any, Self, cast


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


class MissingParamError(Exception):
    def __init__(self, param: str) -> None:
        super().__init__(f"{param} is required")


class SocketBuilder:
    """
    Builder class for creating Socket instances with a fluent interface.

    Example usage:
        builder = SocketBuilder().size(10).height_mm(26).metric()
        socket1 = builder.build()  # Socket with size=10, height_mm=26, unit=METRIC
        socket2 = builder.size(11).build()  # Socket with size=11, height_mm=26, unit=METRIC
    """

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        """
        Initialize a new SocketBuilder with optional parameters.

        Args:
            params: Optional dictionary of parameters to initialize the builder with

        """
        self._params: dict[str, Any] = params.copy() if params else {}

    def size(self, value: float | Fraction) -> Self:
        """Set the size parameter."""
        new_params = self._params.copy()
        new_params["size"] = value
        return cast("Self", self.__class__(new_params))

    def diameter(self, value: float) -> Self:
        """Set the diameter_mm parameter."""
        new_params = self._params.copy()
        new_params["diameter_mm"] = value
        return cast("Self", self.__class__(new_params))

    def height(self, value: float) -> Self:
        """Set the height_mm parameter."""
        new_params = self._params.copy()
        new_params["height_mm"] = value
        return cast("Self", self.__class__(new_params))

    def unit(self, value: Unit) -> Self:
        """Set the unit parameter."""
        new_params = self._params.copy()
        new_params["unit"] = value
        return cast("Self", self.__class__(new_params))

    def drive(self, value: str | None) -> Self:
        """Set the drive parameter."""
        new_params = self._params.copy()
        new_params["drive"] = value
        return cast("Self", self.__class__(new_params))

    def metric(self) -> Self:
        """Set the unit to METRIC."""
        return self.unit(Unit.METRIC)

    def sae(self) -> Self:
        """Set the unit to SAE."""
        return self.unit(Unit.SAE)

    def build(self) -> Socket:
        """
        Build a Socket instance with the current parameters.

        Returns:
            A new Socket instance

        Raises:
            MissingParamError: If the size parameter is not set

        """
        required = ["size"]
        for r in required:
            if r not in self._params:
                raise MissingParamError(r)
        return Socket(**self._params)
