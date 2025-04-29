import operator
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, Flag, auto
from fractions import Fraction
from functools import reduce
from typing import Any, Literal, Self, cast


class DriveSize(Enum):
    QUARTER_INCH = 0.25
    THREE_EIGHTH_INCH = 0.375
    HALF_INCH = 0.5
    THREE_QUARTER_INCH = 0.75
    ONE_INCH = 1

    @staticmethod
    def from_str(v: str) -> "DriveSize":
        for d in DriveSize:
            if d.value == float(Fraction(v)):
                return d
        raise ValueError(v)

    def __str__(self) -> str:
        return f'{Fraction(self.value)}"'


class SocketType(Flag):
    # Socket physical types
    STANDARD = auto()  # Regular hex socket
    DEEP = auto()  # Extended length socket

    # Socket measurement systems
    SAE = auto()
    METRIC = auto()

    # Socket geometry types
    TORX = auto()
    TORX_E = auto()
    TORX_TAMPER = auto()
    TORX_PLUS = auto()

    TWELVE_POINT = auto()
    SIX_POINT = auto()
    BIT = auto()

    # Custom/specialized socket type
    CUSTOM = auto()


type SocketSize = float


@dataclass
class _UnitFormatter:
    unit: str
    placement: Literal["start", "end"] = "start"
    formatter: Callable[[SocketSize], str] | None = None

    def format(self, v: SocketSize) -> str:
        formatted = self.formatter(v) if self.formatter else str(v)
        if self.placement == "start":
            return self.unit + formatted
        return formatted + self.unit


_TYPES_WITH_UNIT: dict[SocketType, _UnitFormatter] = {
    SocketType.SAE: _UnitFormatter('"', "end", lambda x: str(Fraction(x))),
    SocketType.METRIC: _UnitFormatter("mm", "end"),
    SocketType.TORX: _UnitFormatter("T", "start"),
    SocketType.TORX_E: _UnitFormatter("E", "start"),
    SocketType.TORX_PLUS: _UnitFormatter("TP", "start"),
    SocketType.TORX_TAMPER: _UnitFormatter("TT", "start"),
}


class SocketTypeCombinationError(Exception):
    def __init__(self, invalid: SocketType) -> None:
        super().__init__(f"invalid socket type combination found: {invalid}")


@dataclass
class Socket:
    socket_type: SocketType
    drive: DriveSize
    size: SocketSize
    name: str | None = None
    diameter_mm: float = 0
    height_mm: float = 0

    def __post_init__(self) -> None:
        # default to standard type
        if not (self.socket_type & SocketType.DEEP):
            self.socket_type |= SocketType.STANDARD

        self._validate()

    def _validate(self) -> None:
        # TODO should add more
        invalid_combinations = [
            reduce(operator.or_, _TYPES_WITH_UNIT.keys()),
        ]
        for c in invalid_combinations:
            result = self.socket_type & c
            if result.value.bit_count() > 1:
                raise SocketTypeCombinationError(result)

    @property
    def unit(self) -> SocketType | None:
        for k in _TYPES_WITH_UNIT:
            if self.socket_type & k:
                return k
        return None

    def has_type(self, socket_type: SocketType) -> bool:
        """Check if this socket has the specified type."""
        return bool(self.socket_type & socket_type)

    def get_description(self) -> str:
        types = [t.name.lower() for t in SocketType if self.socket_type & t and t.name]
        type_str = "/".join(types)
        return f'{self}[{self.drive}"] {type_str}'

    def get_print_label(self) -> str:
        if self.has_type(SocketType.METRIC):
            return str(self.size)
        if self.has_type(SocketType.SAE):
            return str(Fraction(self.size))
        return str(self)

    def __str__(self) -> str:
        for k, formatter in _TYPES_WITH_UNIT.items():
            if self.socket_type & k:
                return formatter.format(self.size)
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

    def size(self, value: float) -> Self:
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

    def type(self, value: SocketType) -> Self:
        """Set the unit parameter."""
        new_params = self._params.copy()
        new_params["socket_type"] = value
        return cast("Self", self.__class__(new_params))

    def add_type(self, value: SocketType) -> Self:
        if "socket_type" not in self._params:
            return self.type(value)
        t = self._params["socket_type"] | value
        return self.type(t)

    def drive(self, value: DriveSize | str) -> Self:
        """Set the drive parameter."""
        if isinstance(value, str):
            value = DriveSize.from_str(value)
        new_params = self._params.copy()
        new_params["drive"] = value
        return cast("Self", self.__class__(new_params))

    def metric(self, size: float) -> Self:
        """Set the unit to METRIC."""
        return self.add_type(SocketType.METRIC).size(size)

    def sae(self, size: Fraction | str) -> Self:
        """Set the unit to SAE."""
        if isinstance(size, str):
            size = Fraction(size)
        return self.add_type(SocketType.METRIC).size(float(size))

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
