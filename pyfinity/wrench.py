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
    RadiusArc,
    Rectangle,
    RectangleRounded,
    RotationLike,
    add,
    export_stl,
    extrude,
    fillet,
    make_face,
)

from pyfinity._gridfinity import (
    GF,
    BlockGrid,
)
from pyfinity._gridfinity.block import num_grid_for_mm

if TYPE_CHECKING:
    from collections.abc import Iterable


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
                self.grip_width_mm = self.__approximate_grip_width(float(self.size))
            else:
                raise NotImplementedError

    @staticmethod
    def __approximate_grip_width(wrench_size_mm: float) -> float:
        reference_size = 10.0
        reference_width = 9.0
        scaling_factor = (wrench_size_mm / reference_size) ** 0.6

        return reference_width * scaling_factor


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
        wrench_width = round(wrench.grip_width_mm, 2)

        width = wrench_width + 1  # padding
        height = wrench_width + 2  # padding
        angle_degrees = 40
        angle_radians = math.radians(angle_degrees)
        bottom_width = wrench_width * (2 / 5)
        angle_height = (width - bottom_width) * math.tan(angle_radians)

        lip_w = 3
        lip_h = 3
        l0 = (lip_w, 0)
        l1 = (lip_w, -lip_h / 2)
        l2 = (0, -lip_h)

        p0 = (0, 0)  # top left
        p1 = (0, -height)  # bottom left
        p2 = (bottom_width, -height)  # bottm middle
        p3 = (width, -angle_height)  # bottom right
        p4 = (width, 0)  # top right

        with BuildSketch() as profile:
            with BuildLine():
                Polyline(l0, l1, l2)
                RadiusArc(l2, p0, -100)
                Polyline(p0, p1, p2, p3, p4, l0)
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
    grid_x: int = 2
    min_grid_y: int = 1
    min_insert_offset: float = 2 * MM
    radius: float = 3
    front_offset: float = 0 * MM
    back_offset: float = 0 * MM


class OrganizerFrame(BasePartObject):
    __frame_height: float = 0
    __frame_width: float = 0

    def __init__(
        self,
        grid_x: int,
        grid_y: int,
        radius: float,
        height: float,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        self.__frame_width = grid_x * GF.GRID_UNIT
        self.__frame_height = grid_y * GF.GRID_UNIT
        with BuildPart() as part:
            base = BlockGrid(grid_x, grid_y)
            with BuildSketch(base.build_surface()) as base:
                RectangleRounded(self.frame_width, self.frame_height, radius)
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
        wrench_set: list[Wrench],
        spec: OrganizerSpec | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        spec = spec if spec else OrganizerSpec()

        profiles = WrenchInsertProfile.from_collection(
            wrench_set,
            align=(Align.MAX, Align.MAX),
            mode=Mode.PRIVATE,
        )

        min_height = max([p.profile_height for p in profiles])
        height = min_height + 3
        width_sum = sum([p.profile_width for p in profiles])
        grid_y = max(
            num_grid_for_mm(spec.front_offset + width_sum + (len(wrench_set) + 2) * spec.min_insert_offset),
            spec.min_grid_y,
        )
        offset = ((grid_y * GF.GRID_UNIT + spec.front_offset + spec.back_offset) - width_sum) / (len(profiles) + 0)
        offset = round(offset, 1)

        with BuildPart() as part:
            frame = OrganizerFrame(
                height=height,
                grid_x=spec.grid_x,
                grid_y=grid_y,
                radius=spec.radius,
                align=Align.MIN,
            )

            face = frame.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            show_object(face)
            with BuildSketch(face):
                distance = -frame.frame_height / 2 + (profiles[0].profile_width)
                distance += spec.front_offset + offset
                for p in profiles:
                    h = height / 2 + 1.5
                    with Locations((distance, h)):
                        added = add(p)
                        print(p.profile_width)
                        distance += p.profile_width + offset
                        fillet_vertices = added.vertices().filter_by(lambda v: v.Y != h)
                        fillet(fillet_vertices, radius=1)
            extrude(amount=-spec.grid_x * GF.GRID_UNIT, mode=Mode.SUBTRACT)
            e = part.edges().group_by(Axis.Z)[-1].filter_by(Axis.X)
            fillet(e, radius=0.3)

        if not part.part:
            return

        super().__init__(part.part, rotation, align, mode)


if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        ws = [Wrench(6), Wrench(7), Wrench(8), Wrench(10), Wrench(13), Wrench(14), Wrench(15), Wrench(17)]

        with BuildPart() as part:
            o = Organizer(ws)
            face = o.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face) as skt:
                Rectangle(3, 20)
            extrude(amount=-200, mode=Mode.INTERSECT)
        show_object(o)

        export_stl(o, "organizer.stl")
        export_stl(part.part, "cutout.stl")

    except ImportError:
        pass
