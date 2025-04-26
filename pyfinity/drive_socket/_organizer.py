from collections.abc import Generator
from dataclasses import asdict, dataclass
from typing import Literal

from build123d import (
    MM,
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Locations,
    Mode,
    Part,
    Plane,
    RotationLike,
    Select,
    Text,
    Vector,
    chamfer,
    extrude,
    fillet,
)

from pyfinity._gridfinity import (
    GF,
    OrganizerFrame,
)
from pyfinity._gridfinity.block import num_grid_for_mm
from pyfinity.drive_socket._socket import Drive, Socket

default_base_color = Color(0x8B9DAA)
default_label_color = Color(0xFFFFFF)


@dataclass
class OrganizerSpec:
    align: Literal["center", "bottom"] = "center"
    align_y_offset: float = 0

    min_grid_x: int = 1
    grid_y: int = 1
    radius: float = 3
    height: float = 10 * MM  # + GF.HEIGHT_UNIT

    insert_depth: float = 5 * MM
    insert_labels: bool = True
    insert_labels_size: float = 6
    insert_chamfer: bool = True

    diameter_offset: float = 1 * MM

    # minimum amount of gap between each insert
    min_offset_gap: float = 2 * MM

    # padding on each side
    padding_edge_x: float = 5 * MM
    padding_edge_y: float = 2 * MM

    face_label: str = ""
    face_label_padding_xy: tuple[float, float] | None = None


@dataclass(kw_only=True)
class InternalSpec(OrganizerSpec):
    socket_set: list[Socket]

    top_fillet: float = 0.5
    insert_top_chamfer: float = 0.8
    insert_bottom_chamfer: float = 0.4

    @staticmethod
    def from_spec(socket_set: list[Socket], spec: OrganizerSpec) -> "InternalSpec":
        return InternalSpec(socket_set=socket_set, **asdict(spec))

    @property
    def sum_insert_widths(self) -> float:
        return sum([s.diameter_mm + self.diameter_offset for s in self.socket_set])

    @property
    def grid_x(self) -> int:
        min_offset_total = (len(self.socket_set) - 1) * self.min_offset_gap
        required_grid_x = num_grid_for_mm(
            self.sum_insert_widths + min_offset_total + (self.padding_edge_x * 2))
        return max(required_grid_x, self.min_grid_x)

    @property
    def length_y(self) -> float:
        return self.grid_y * GF.GRID_UNIT

    @property
    def length_x(self) -> float:
        return self.grid_x * GF.GRID_UNIT

    @property
    def actual_offset(self) -> float:
        total_free = self.length_x - self.padding_edge_x * 2 - self.sum_insert_widths
        return total_free / (len(self.socket_set) - 1)


class Organizer(BasePartObject):
    parts: list[Part]
    base: BuildPart
    name: str

    def __init__(
        self,
        socket_set: list[Socket],
        spec: OrganizerSpec | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        parts = []
        spec = InternalSpec.from_spec(socket_set, spec or OrganizerSpec())

        base = self._build_base(spec)
        if not base:
            return
        parts.append(base.part)

        if spec.insert_labels:
            labels = self._build_insert_labels(spec, base)
            if labels:
                parts.append(labels.part)

        if spec.face_label:
            label = self._build_face_label(spec, base)
            if label:
                parts.append(label.part)

        self.name = self._generate_name(spec)

        super().__init__(Part(label=self.name, children=parts), rotation, align, mode)

    def _generate_name(self, spec: InternalSpec) -> str:
        drives = {s.drive for s in spec.socket_set if s.drive}
        units = {s.unit for s in spec.socket_set if s.unit}

        name = "socket-organizer"
        if len(drives) == 1:
            drive = drives.pop()
            if drive == Drive.QUARTER:
                name += "-drive[q]"
            elif drive == Drive.HALF:
                name += "-drive[h]"
            else:
                name += f"-drive[{drive}]"

        if len(units) == 1:
            sizes = [s.size for s in spec.socket_set]
            smallest = min(sizes)
            largest = max(sizes)
            name += f"-{units.pop().name.lower()}[{smallest}-{largest}]"
        return name

    @staticmethod
    def _next_insert(spec: InternalSpec) -> Generator[tuple[Socket, float]]:
        distance = spec.padding_edge_x
        for s in spec.socket_set:
            yield s, distance
            distance += s.diameter_mm + spec.diameter_offset + spec.actual_offset

    def _build_base(self, spec: InternalSpec, color: Color = default_base_color) -> BuildPart | None:
        with BuildPart() as base:
            OrganizerFrame(
                height=spec.height,
                grid_x=spec.grid_x,
                grid_y=spec.grid_y,
                radius=spec.radius,
                align=Align.MIN,
            )

            top_face = base.faces().sort_by(Axis.Z)[-1]
            fillet(top_face.edges(), radius=spec.top_fillet)

            if spec.align == "center":
                origin_y = top_face.center().Y
                align = (Align.MIN, Align.CENTER)
                y_offset = 0
            elif spec.align == "bottom":
                origin_y = top_face.edges().sort_by(
                    Axis.Y)[0].edges()[0].vertices()[0].Y
                align = (Align.MIN, Align.MIN)
                y_offset = (spec.length_y -
                            max([s.diameter_mm for s in spec.socket_set])) / 2
            origin_x = top_face.edges().sort_by(
                Axis.X)[0].edges()[0].vertices()[0].X
            origin_z = spec.height + GF.HEIGHT_UNIT
            origin = Vector(X=origin_x, Y=origin_y, Z=origin_z)

            y_offset += spec.align_y_offset
            if spec.insert_labels:
                y_offset += spec.insert_labels_size / 2

            with BuildSketch(Plane(origin=origin)):
                for s, distance in self._next_insert(spec):
                    with Locations((distance, y_offset)):
                        Circle(radius=(s.diameter_mm +
                               spec.diameter_offset) / 2, align=align)
            extrude(amount=-spec.insert_depth,
                    mode=Mode.SUBTRACT, target=base.part)
            if spec.insert_chamfer:
                edges = base.edges(Select.LAST).group_by(Axis.Z)
                chamfer(edges[0], length=spec.insert_bottom_chamfer)
                chamfer(edges[-1], length=spec.insert_top_chamfer)

        if not base.part:
            return None

        base.part.color = color
        base.part.label = "Base"
        return base

    def _build_insert_labels(
        self,
        spec: InternalSpec,
        base: BuildPart,
        color: Color = default_label_color,
    ) -> BuildPart | None:
        top_face = base.faces().sort_by(Axis.Z)[-1]
        origin_x = top_face.edges().sort_by(
            Axis.X)[0].edges()[0].vertices()[0].X
        origin_y = top_face.edges().sort_by(
            Axis.Y)[0].edges()[0].vertices()[0].Y
        origin_z = spec.height + GF.HEIGHT_UNIT
        origin = Vector(X=origin_x, Y=origin_y, Z=origin_z)

        with BuildPart() as labels:
            with BuildSketch(Plane(origin=origin)):
                for s, distance in self._next_insert(spec):
                    x = distance + (s.diameter_mm + spec.diameter_offset) / 2
                    with Locations((x, spec.padding_edge_y)):
                        Text(f"{s}", spec.insert_labels_size,
                             align=(Align.CENTER, Align.MIN))
            extrude(amount=0.75)

        if not labels.part:
            return None

        labels.part.color = color
        labels.part.label = "Labels"
        return labels

    def _build_face_label(
        self,
        spec: InternalSpec,
        base: BuildPart,
        color: Color = default_label_color,
    ) -> BuildPart | None:
        if spec.face_label_padding_xy is None:
            padding_x, padding_y = spec.padding_edge_x, spec.padding_edge_y
        else:
            padding_x, padding_y = spec.face_label_padding_xy

        top_face = base.faces().sort_by(Axis.Z)[-1]
        origin_x = top_face.edges().sort_by(
            Axis.X)[0].edges()[0].vertices()[0].X
        origin_y = top_face.edges().sort_by(
            Axis.Y)[-1].edges()[0].vertices()[0].Y
        origin_z = spec.height + GF.HEIGHT_UNIT
        origin = Vector(X=origin_x + padding_x,
                        Y=origin_y - padding_y, Z=origin_z)

        with BuildPart() as label:
            with BuildSketch(Plane(origin=origin)):
                Text(spec.face_label, 6, align=(Align.MIN, Align.MAX))
            extrude(amount=0.75)

        if not label.part:
            return None

        label.part.color = color
        label.part.label = "Face Label"
        return label
