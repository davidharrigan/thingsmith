from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction
from typing import TYPE_CHECKING

from build123d import (
    MM,
    Align,
    Axis,
    BasePartObject,
    BaseSketchObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Polyline,
    RectangleRounded,
    RotationLike,
    add,
    extrude,
    make_face,
)

from pyfinity._gridfinity import (
    GF,
    BlockGrid,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


class WrenchUnit(Enum):
    METRIC = auto()
    SAE = auto()


@dataclass
class Wrench:
    size: int | float | Fraction | str
    handle_width: float = 0
    handle_depth: float = 0

    def __post_init__(self) -> None:
        if not self.size:
            msg = "size is required"
            raise ValueError(msg)
        if isinstance(self.size, str):
            self.size = Fraction(self.size)


def approximate_wrench_dimensions(wrench_size_mm: float) -> tuple[float, float]:
    reference_size = 10.0
    reference_width = 9.0
    reference_depth = 3.0

    scaling_factor = (wrench_size_mm / reference_size) ** 0.6

    handle_width = reference_width * scaling_factor
    handle_depth = reference_depth * scaling_factor

    return (round(handle_width, 1), round(handle_depth, 1))


class WrenchInsertProfile(BaseSketchObject):
    __profile_width: float
    __profile_height: float

    def __init__(
        self,
        wrench: Wrench,
        rotation: float = 0,
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        wrench_width, _ = approximate_wrench_dimensions(float(wrench.size))  # TODO

        long_width = wrench_width / math.sqrt(2) + 1  # padding
        short_width = long_width * 0.6
        width = long_width + short_width
        height = width

        lip = 2
        l0 = (lip, 0)
        l1 = (0, -lip / 2)

        p0 = (0, 0)  # top left
        p1 = (0, -height)  # bottom left
        p2 = (short_width, -height)  # bottm middle
        p3 = (width, -short_width)  # bottom right
        p4 = (width, 0)  # top right

        with BuildSketch() as profile:
            with BuildLine():
                Polyline(l0, l1, p0, p1, p2, p3, p4, close=True)
            make_face()

        self.__profile_width = width
        self.__profile_height = height
        super().__init__(profile.face(), rotation, align, mode)

    @property
    def profile_width(self) -> float:
        return self.__profile_width

    @property
    def profile_height(self) -> float:
        return self.__profile_height

    @staticmethod
    def from_collection(
        ws: Iterable[Wrench],
        rotation: float = 0,
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> list[WrenchInsertProfile]:
        profiles: list[WrenchInsertProfile] = []
        for w in ws:
            profile = WrenchInsertProfile(w, rotation, align, mode)
            profiles.append(profile)
        return profiles


@dataclass
class OrganizerSpec:
    x: int = 2
    y: int = 3
    radius: float = 3
    insert_offset: float = 5 * MM
    min_spacing: float = 10 * MM
    unit: WrenchUnit = WrenchUnit.METRIC


class OrganizerFrame(BasePartObject):
    __frame_height: float = 0
    __frame_width: float = 0

    def __init__(
        self,
        height: float,
        spec: OrganizerSpec | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        spec = spec if spec else OrganizerSpec()
        self.__frame_width = spec.x * GF.GRID_UNIT
        self.__frame_height = spec.y * GF.GRID_UNIT
        with BuildPart() as part:
            base = BlockGrid(spec.x, spec.y)
            with BuildSketch(base.build_surface()) as base:
                RectangleRounded(self.frame_width, self.frame_height, spec.radius)
            extrude(amount=height)
        if not part.part:
            return
        super().__init__(part.part, rotation, align, mode)

    @property
    def frame_height(self) -> float:
        return self.__frame_height

    @property
    def frame_width(self) -> float:
        return self.__frame_width


class Organizer(BasePartObject):
    def __init__(
        self,
        wrench_set: Iterable[Wrench],
        spec: OrganizerSpec | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        spec = spec if spec else OrganizerSpec()

        with BuildPart() as part:
            profiles = WrenchInsertProfile.from_collection(
                wrench_set,
                align=(Align.MAX, Align.MAX),
                mode=Mode.PRIVATE,
            )
            min_height = max([p.profile_height for p in profiles])
            height = min_height + 3

            frame = OrganizerFrame(height, spec, align=Align.MIN)

            face = frame.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            with BuildSketch(face):
                distance = -frame.frame_height / 2 + profiles[0].profile_width
                distance += spec.insert_offset - 1
                for p in profiles:
                    h = height / 2 + 1.5
                    with Locations((distance, h)):
                        distance += p.profile_width + spec.insert_offset
                        add(p)
            extrude(amount=-spec.x * GF.GRID_UNIT, mode=Mode.SUBTRACT)

        if not part.part:
            return

        super().__init__(part.part, rotation, align, mode)


if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        ws = [Wrench(10), Wrench(13), Wrench(14), Wrench(15), Wrench(17)]
        o = Organizer(ws)
        show_object(o)
    except ImportError:
        pass
