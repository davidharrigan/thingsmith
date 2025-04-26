from collections.abc import Generator
from dataclasses import asdict, dataclass

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
    extrude,
    fillet,
)

from pyfinity._gridfinity import (
    GF,
    OrganizerFrame,
)
from pyfinity._gridfinity.block import num_grid_for_mm
from pyfinity.drive_socket._socket import Socket

default_base_color = Color(0x8B9DAA)
default_label_color = Color(0xFFFFFF)


@dataclass
class OrganizerSpec:
    min_grid_x: int = 1
    grid_y: int = 1
    radius: float = 3
    height: float = 10 * MM # on top of the grid base

    insert_depth: float = 5 * MM
    insert_labels: bool = True
    insert_labels_offset: float = 2 * MM

    diameter_offset: float = 1 * MM

    # minimum amount of gap between each insert
    min_insert_gap: float = 2 * MM

    # padding on each side
    side_padding: float = 3 * MM

    # how much to offset from center
    center_offset: float = 3 * MM


@dataclass(kw_only=True)
class InternalSpec(OrganizerSpec):
    socket_set: list[Socket]

    top_fillet: float = 0.5
    insert_fillet: float = 0.4

    @staticmethod
    def from_spec(socket_set: list[Socket], spec: OrganizerSpec) -> "InternalSpec":
        return InternalSpec(socket_set=socket_set, **asdict(spec))

    @property
    def total_width(self) -> float:
        return sum([s.diameter_mm + self.diameter_offset for s in self.socket_set])

    @property
    def grid_x(self) -> int:
        min_offset_total = len(self.socket_set) * self.min_insert_gap
        required_grid_x = num_grid_for_mm(
            self.total_width + min_offset_total + (self.side_padding * 2))
        return max(required_grid_x, self.min_grid_x)

    @property
    def actual_offset(self) -> float:
        return (self.grid_x * GF.GRID_UNIT - self.total_width - self.side_padding) / (len(self.socket_set))


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

        self.name = self._generate_name(spec)

        super().__init__(Part(label=self.name, children=parts), rotation, align, mode)

    def _generate_name(self, spec: InternalSpec) -> str:
        units = {s.unit for s in spec.socket_set if s.unit}

        name = "socket-organizer"
        if len(units) == 1:
            sizes = [s.size for s in spec.socket_set]
            smallest = min(sizes)
            largest = max(sizes)
            name += f"-{units.pop().name.lower()}[{smallest}-{largest}]"
        return name


    @staticmethod
    def _next_insert(spec: InternalSpec) -> Generator[tuple[Socket, float]]:
        distance = spec.side_padding + \
            ((spec.socket_set[0].diameter_mm + spec.diameter_offset) / 4)
        for s in spec.socket_set:
            yield s, distance
            distance += s.diameter_mm + spec.actual_offset

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

            origin_y = top_face.center()
            top_face.center()
            origin_xz = top_face.edges().sort_by(Axis.X)[0].vertices()[0]
            with BuildSketch(Plane(origin=(origin_xz.X, origin_y.Y, origin_xz.Z))):
                for s, distance in self._next_insert(spec):
                    with Locations((distance, spec.center_offset)):
                        Circle(radius=(s.diameter_mm + spec.diameter_offset) /
                               2, align=(Align.MIN, Align.CENTER))
            extrude(amount=-spec.insert_depth, mode=Mode.SUBTRACT, target=base.part)
            edges = base.edges(Select.LAST).group_by(Axis.Z)
            fillet(edges[0], radius=spec.insert_fillet)
            fillet(edges[-1], radius=spec.insert_fillet)

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
        origin = top_face.edges().group_by(
            Axis.X)[0].sort_by(Axis.Y)[0].vertices()[0]

        with BuildPart() as labels:
            with BuildSketch(Plane(origin=(origin.X, origin.Y, origin.Z))):
                for s, distance in self._next_insert(spec):
                    with Locations(
                        (distance + ((s.diameter_mm + spec.diameter_offset) / 2),
                         spec.insert_labels_offset),
                    ):
                        Text(f"{s}", 6)
            extrude(amount=0.75)

        if not labels.part:
            return None

        labels.part.color = color
        labels.part.label = "Labels"
        return labels
