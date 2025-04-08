from dataclasses import dataclass

from build123d import (
    MM,
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Plane,
    RectangleRounded,
    RotationLike,
    Select,
    extrude,
    fillet,
)

from pyfinity._gridfinity import (
    GF,
    BlockGrid,
)
from pyfinity._gridfinity.block import num_grid_for_mm
from pyfinity._wrench._profile import InsertProfile
from pyfinity._wrench._wrench import Wrench


@dataclass
class OrganizerSpec:
    grid_x: int = 2
    min_grid_y: int = 1
    min_insert_offset: float = 3 * MM
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

        min_height = max([w.profile_height for w in wrench_set])
        height = min_height + 3
        width_sum = sum([w.profile_width for w in wrench_set])
        grid_y = max(
            num_grid_for_mm(spec.front_offset + width_sum + (len(wrench_set) + 2) * spec.min_insert_offset),
            spec.min_grid_y,
        )
        offset = ((grid_y * GF.GRID_UNIT + spec.front_offset + spec.back_offset) - width_sum) / (len(wrench_set) + 2)

        with BuildPart() as part:
            OrganizerFrame(
                height=height,
                grid_x=spec.grid_x,
                grid_y=grid_y,
                radius=spec.radius,
                align=Align.MIN,
            )

            with BuildSketch(Plane.XZ):
                distance = offset + spec.front_offset
                for w in wrench_set:
                    h = (height - w.profile_height) + (height / 2) - 1
                    with Locations((distance, h)):
                        p = InsertProfile(w.profile_width, w.profile_height, align=((Align.MIN, Align.MIN)))
                        distance += p.profile_width + offset

            extrude(amount=-spec.grid_x * GF.GRID_UNIT, mode=Mode.SUBTRACT)
            edges = part.edges(Select.LAST)
            top_edges = edges.group_by(Axis.Z)[-1]
            inner_edges = edges.filter_by(lambda v: v not in top_edges).filter_by(Axis.Y)
            fillet(top_edges, radius=0.4)
            fillet(inner_edges, radius=0.3)

        if not part.part:
            return

        super().__init__(part.part, rotation, align, mode)
