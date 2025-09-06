from build123d import (
    Align,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Mode,
    RectangleRounded,
    RotationLike,
    extrude,
)

from thingsmith._gridfinity.block import BlockGrid
from thingsmith._gridfinity.spec import GF


class OrganizerFrame(BasePartObject):
    __frame_y: float = 0
    __frame_x: float = 0

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
        self.__frame_x = grid_x * GF.GRID_UNIT
        self.__frame_y = grid_y * GF.GRID_UNIT
        with BuildPart() as part:
            base = BlockGrid(grid_x, grid_y)
            with BuildSketch(base.build_surface()) as base:
                RectangleRounded(self.frame_length_x,
                                 self.frame_length_y, radius)
            extrude(amount=height)
        if not part.part:
            return
        super().__init__(part.part, rotation, align, mode)

    @property
    def frame_length_y(self) -> float:
        return self.__frame_y

    @property
    def frame_length_x(self) -> float:
        return self.__frame_x
