from collections.abc import Generator

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Keep,
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
    split,
)

from pyfinity._gridfinity import (
    GF,
    OrganizerFrame,
)
from pyfinity.drive_socket._socket import Drive, Socket
from pyfinity.drive_socket._spec import OrganizerSpec

default_face_plate_color = Color(0x1F79E5)
default_base_color = Color(0x000000)
default_label_color = Color(0xFFFFFF)


def _next_insert(spec: OrganizerSpec) -> Generator[tuple[Socket, float]]:
    distance = spec.edge_padding_x
    for s in spec.sockets:
        yield s, distance
        distance += s.diameter_mm + spec.insert_diameter_offset + spec.insert_offset


class Organizer(BasePartObject):
    spec: OrganizerSpec
    name: str

    def __init__(
        self,
        spec: OrganizerSpec,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        self.spec = spec
        parts = []

        base = self._build_base(spec)
        if not base:
            return
        parts.append(base)

        if spec.insert_labels:
            labels = self._build_insert_labels(spec, base)
            if labels and labels.part:
                self.labels = labels.part
                parts.append(labels.part)

        if spec.organizer_label:
            label = self._build_face_label(spec, base)
            if label and label.part:
                self.label = label.part
                parts.append(label.part)

        self.name = self._generate_name() + spec.organizer_name_suffix
        super().__init__(Part(label=self.name, children=parts), rotation, align, mode)

    def _generate_name(self) -> str:
        spec = self.spec
        drives = {s.drive for s in spec.sockets if s.drive}
        units = {s.unit for s in spec.sockets if s.unit}

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
            sizes = [s.size for s in spec.sockets]
            smallest = min(sizes)
            largest = max(sizes)
            name += f"-{units.pop().name.lower()}[{smallest}-{largest}]"
        return name

    @staticmethod
    def _build_base(spec: OrganizerSpec, color: Color = default_base_color) -> Part | None:
        with BuildPart() as base:
            OrganizerFrame(
                height=spec.base_height,
                grid_x=spec.grid_x,
                grid_y=spec.grid_y,
                radius=spec.corner_radius,
                align=Align.MIN,
            )

            top_face = base.faces().sort_by(Axis.Z)[-1]
            fillet(top_face.edges(), radius=spec.edge_fillet)

            if spec.align == "center":
                origin_y = top_face.center().Y
                align = (Align.MIN, Align.CENTER)
                y_offset = 0
            elif spec.align == "bottom":
                origin_y = top_face.edges().sort_by(
                    Axis.Y)[0].edges()[0].vertices()[0].Y
                align = (Align.MIN, Align.MIN)
                y_offset = (spec.length_y -
                            max([s.diameter_mm for s in spec.sockets])) / 2
            origin_x = top_face.edges().sort_by(
                Axis.X)[0].edges()[0].vertices()[0].X
            origin_z = spec.base_height + GF.HEIGHT_UNIT
            origin = Vector(X=origin_x, Y=origin_y, Z=origin_z)

            y_offset += spec.align_offset
            if spec.insert_labels:
                y_offset += spec.insert_labels_size / 2

            with BuildSketch(Plane(origin=origin)):
                for s, distance in _next_insert(spec):
                    with Locations((distance, y_offset)):
                        Circle(radius=(s.diameter_mm +
                               spec.insert_diameter_offset) / 2, align=align)
            extrude(amount=-spec.insert_depth,
                    mode=Mode.SUBTRACT, target=base.part)
            if spec.insert_chamfer:
                edges = base.edges(Select.LAST).group_by(Axis.Z)
                chamfer(edges[0], length=spec.insert_chamfer_bottom)
                chamfer(edges[-1], length=spec.insert_chamfer_top)

            if spec.organizer_split_face_plate:
                split(bisect_by=Plane(base.faces().sort_by(Axis.Z)[-1]).offset(-spec.organizer_split_face_plate), keep=Keep.BOTH)

        solids = base.solids().sort_by(Axis.Z)
        if len(solids) == 0:
            return None

        solids[0].label = "Base"
        solids[0].color = color

        if spec.organizer_split_face_plate:
            solids[1].label = "Face Plate"
            solids[1].color = default_face_plate_color
        return Part(children=solids, label="Base")

    @staticmethod
    def _build_insert_labels(
        spec: OrganizerSpec,
        base: Part,
        color: Color = default_label_color,
    ) -> BuildPart | None:
        top_face = base.faces().sort_by(Axis.Z)[-1]
        origin_x = top_face.edges().sort_by(
            Axis.X)[0].edges()[0].vertices()[0].X
        origin_y = top_face.edges().sort_by(
            Axis.Y)[0].edges()[0].vertices()[0].Y
        origin_z = spec.base_height + GF.HEIGHT_UNIT
        origin = Vector(X=origin_x, Y=origin_y, Z=origin_z)

        with BuildPart() as labels:
            with BuildSketch(Plane(origin=origin)):
                for s, distance in _next_insert(spec):
                    x = distance + (s.diameter_mm + spec.insert_diameter_offset) / 2
                    with Locations((x, spec.edge_padding_y)):
                        Text(f"{s}", spec.insert_labels_size,
                             align=(Align.CENTER, Align.MIN), font=spec.font)
            extrude(amount=0.75)

        if not labels.part:
            return None

        labels.part.color = color
        labels.part.label = "Labels"
        return labels

    @staticmethod
    def _build_face_label(
        spec: OrganizerSpec,
        base: Part,
        color: Color = default_label_color,
    ) -> BuildPart | None:
        if spec.organizer_label_padding is None:
            padding_x, padding_y = spec.edge_padding_x, spec.edge_padding_y
        else:
            padding_x, padding_y = spec.organizer_label_padding

        top_face = base.faces().sort_by(Axis.Z)[-1]
        origin_x = top_face.edges().sort_by(
            Axis.X)[0].edges()[0].vertices()[0].X
        origin_y = top_face.edges().sort_by(
            Axis.Y)[-1].edges()[0].vertices()[0].Y
        origin_z = spec.base_height + GF.HEIGHT_UNIT
        origin = Vector(X=origin_x + padding_x,
                        Y=origin_y - padding_y, Z=origin_z)

        with BuildPart() as label:
            with BuildSketch(Plane(origin=origin)):
                Text(spec.organizer_label, 6, align=(Align.MIN, Align.MAX), font=spec.font)
            extrude(amount=0.75)

        if not label.part:
            return None

        label.part.color = color
        label.part.label = "Face Label"
        return label
