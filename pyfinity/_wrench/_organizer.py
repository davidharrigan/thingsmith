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
    RectangleRounded,
    RotationLike,
    add,
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

        profiles = InsertProfile.from_collection(
            [w.grip_width_mm for w in wrench_set],
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

        with BuildPart() as part:
            frame = OrganizerFrame(
                height=height,
                grid_x=spec.grid_x,
                grid_y=grid_y,
                radius=spec.radius,
                align=Align.MIN,
            )

            face = frame.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            with BuildSketch(face):
                distance = -frame.frame_height / 2 + (profiles[0].profile_width)
                distance += spec.front_offset + offset
                for p in profiles:
                    h = height / 2 + 1.5
                    with Locations((distance, h)):
                        added = add(p)
                        distance += p.profile_width + offset
                        # fillet_vertices = added.vertices().filter_by(lambda v: v != v.Y)
                        # fillet(fillet_vertices, radius=1)
            extrude(amount=-spec.grid_x * GF.GRID_UNIT, mode=Mode.SUBTRACT)
            e = part.edges().group_by(Axis.Z)[-1].filter_by(Axis.X)
            fillet(e, radius=0.3)

        if not part.part:
            return

        super().__init__(part.part, rotation, align, mode)
