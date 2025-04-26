from dataclasses import dataclass

from build123d import (
    MM,
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Color,
    Locations,
    Mode,
    Part,
    Plane,
    RotationLike,
    Select,
    Text,
    extrude,
    fillet,
)

from pyfinity._gridfinity import (
    GF,
    OrganizerFrame,
)
from pyfinity._gridfinity.block import num_grid_for_mm
from pyfinity.wrench._profile import InsertProfile
from pyfinity.wrench._wrench import Wrench


@dataclass
class OrganizerSpec:
    grid_y: int = 2
    min_grid_x: int = 1
    min_insert_offset: float = 3 * MM
    radius: float = 3
    front_offset: float = 0 * MM
    back_offset: float = 0 * MM
    add_labels: bool = True


class Organizer(BasePartObject):
    def __init__(
        self,
        wrench_set: list[Wrench],
        spec: OrganizerSpec | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        parts = []
        spec = spec or OrganizerSpec()

        min_height = max([w.profile_height for w in wrench_set])
        height = min_height + 3
        width_sum = sum([w.profile_width for w in wrench_set])
        grid_x = max(
            num_grid_for_mm(spec.front_offset + width_sum +
                            (len(wrench_set) + 2) * spec.min_insert_offset),
            spec.min_grid_x,
        )
        offset = ((grid_x * GF.GRID_UNIT + spec.front_offset +
                  spec.back_offset) - width_sum) / (len(wrench_set) + 2)

        with BuildPart() as organizer:
            OrganizerFrame(
                height=height,
                grid_x=grid_x,
                grid_y=spec.grid_y,
                radius=spec.radius,
                align=Align.MIN,
            )

            # cut inserts
            with BuildSketch(Plane.XZ):
                distance = offset + spec.front_offset
                for w in wrench_set:
                    h = (height - w.profile_height) + (height / 2) - 1
                    with Locations((distance, h)):
                        InsertProfile(w.profile_width, w.profile_height, align=(
                            (Align.MIN, Align.MIN)))
                        distance += w.profile_width + offset
            extrude(amount=-spec.grid_y * GF.GRID_UNIT, mode=Mode.SUBTRACT)

            # apply filley to the edges
            edges = organizer.edges(Select.LAST)
            top_edges = edges.group_by(Axis.Z)[-1]
            inner_edges = edges.filter_by(
                lambda v: v not in top_edges).filter_by(Axis.Y)
            fillet(top_edges, radius=0.4)
            fillet(inner_edges, radius=0.3)
        if not organizer.part:
            return
        organizer.part.color = Color(0xB3B3B3)
        organizer.part.label = "organizer"
        parts.append(organizer.part)

        # add labels
        if spec.add_labels:
            topf = organizer.faces().group_by(Axis.Z)[-1].sort_by(Axis.X)
            with BuildPart() as labels:
                for i, w in enumerate(wrench_set):
                    face = topf[i]
                    with BuildSketch(face):
                        Text(f"{w}", 6, rotation=-90)
                    extrude(amount=0.75)
            if labels.part:
                labels.part.color = Color("white")
                labels.part.label = "labels"
                parts.append(labels.part)

        part = Part(children=parts)
        super().__init__(part, rotation, align, mode)
