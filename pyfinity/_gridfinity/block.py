from __future__ import annotations

from math import ceil

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Face,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    RectangleRounded,
    RotationLike,
    extrude,
    make_face,
    sweep,
)

from pyfinity._gridfinity.profile import BaseplateSections, Profile
from pyfinity._gridfinity.spec import GF


def num_grid_for_mm(length_mm: float) -> int:
    return ceil(length_mm / GF.GRID_UNIT)


class Block(BasePartObject):
    def __init__(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        sections = BaseplateSections()
        with BuildPart() as part:
            with BuildSketch(Plane.XZ) as profile, Locations((-GF.GRID_UNIT / 2, 0)):
                Profile(sections)

            with BuildSketch() as grid:
                RectangleRounded(GF.GRID_UNIT, GF.GRID_UNIT,
                                 GF.BLOCK_OUTER_RADIUS)
            extrude(amount=sections.total_height)

            path = grid.wires().sort_by(Axis.Z)[-1]
            sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)

            with BuildSketch(part.faces().sort_by(Axis.Z)[-1]):
                Rectangle(GF.GRID_UNIT, GF.GRID_UNIT)
            extrude(amount=GF.HEIGHT_UNIT - sections.total_height)

        if part.part is None:
            return
        super().__init__(part.part, rotation, align, mode)


class BlockGrid(BasePartObject):
    def __init__(
        self,
        x: int,
        y: int,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        locations: list[Location] = []
        for row in range(x):
            locations.extend(
                [Location((row * GF.GRID_UNIT, col * GF.GRID_UNIT)) for col in range(y)])

        with BuildPart() as part:
            with Locations(locations):
                Block()

            top_face = part.faces().sort_by(Axis.Z)[-1]
            with BuildPart(top_face, mode=Mode.SUBTRACT):
                with BuildSketch():
                    outer = top_face.outer_wire()
                    inner = outer.fillet_2d(
                        GF.BLOCK_OUTER_RADIUS, outer.vertices())
                    make_face(outer.edges())
                    make_face(inner.edges(), mode=Mode.SUBTRACT)
                extrude(amount=GF.HEIGHT_UNIT)

        if part.part is None:
            return
        self._build_surface = part.faces().sort_by(Axis.Z)[-1]
        super().__init__(part.part, rotation, align, mode)

    def build_surface(self) -> Face:
        return self._build_surface


if __name__ == "__main__":
    b = BlockGrid(2, 2)
    try:
        from ocp_vscode import show_object

        show_object(b)

    except ImportError:
        pass
