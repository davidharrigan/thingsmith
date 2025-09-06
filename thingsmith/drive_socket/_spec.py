from dataclasses import dataclass
from typing import Literal

from build123d import (
    MM,
    Color,
)

from thingsmith._gridfinity import (
    GF,
)
from thingsmith._gridfinity.block import num_grid_for_mm
from thingsmith.drive_socket._socket import Socket

default_face_plate_color = Color(0x1F79E5)


@dataclass
class OrganizerSpec:
    """
    Specifications for a gridfinity drive socket organizer.

    This class defines the configuration parameters for creating a 3D model
    of a gridfinity-compatible drive socket organizer. It controls dimensions,
    socket placement, labeling options, and visual appearance.

    Attributes:
        sockets: Sockets to create inserts for.

        align: Vertical alignment of sockets.
        align_offset: Additional Y-axis offset for socket alignment in mm.

        grid_x_min: Minimum number of grid units in X direction.
        grid_y: Number of grid units in Y direction.
        base_height: Height of the organizer base in mm.
        corner_radius: Radius for the organizer frame corners in mm.

        insert_depth: Depth of socket inserts in mm.
        insert_labels: Whether to show labels for sockets.
        insert_label_size: Font size for socket labels.
        insert_chamfer: Whether to chamfer socket insert edges.
        insert_chamfer_top: Chamfer length of top socket insert edges.
        insert_chamfer_bottom: Chamfer length of bottom socket insert edges.
        insert_offset_min: Minimum gap between adjacent socket inserts in mm.
        insert_diameter_offset: Additional clearance for socket diameter in mm.

        edge_padding_x: Horizontal padding from edge to first/last socket in mm.
        edge_padding_y: Vertical padding from edge in mm.
        edge_fillet: Radius of the fillet applied to the top face edges.

        organizer_label: Text label for the organizer face.
        organizer_label_padding: Custom (x,y) padding for organizer label in mm. Defaults to edge_padding.
        organizer_split_face_plate: Split a part of the base as a separate part. Useful to select for coloring.

    """

    sockets: list[Socket]
    name: str | None = None
    font: str = "Arial Rounded MT Bold"

    align: Literal["center", "bottom"] = "bottom"
    align_offset: float = 0

    grid_x_min: int = 1
    grid_y: int = 1
    corner_radius: float = 3
    base_height: float = 10 * MM  # + GF.HEIGHT_UNIT

    insert_depth: float = 5 * MM
    insert_labels: bool = True
    insert_labels_size: float = 6
    insert_chamfer: bool = True
    insert_chamfer_top: float = 0.8
    insert_chamfer_bottom: float = 0.4
    insert_offset_min: float = 2 * MM
    insert_diameter_offset: float = 1 * MM

    edge_padding_x: float = 5 * MM
    edge_padding_y: float = 2 * MM
    edge_fillet: float = 0.5

    organizer_label: str = ""
    organizer_label_padding: tuple[float, float] | None = None
    organizer_split_face_plate: float = 0
    organizer_name_suffix: str = ""
    face_color: Color = default_face_plate_color

    @property
    def grid_x(self) -> int:
        min_offset_total = (len(self.sockets) - 1) * self.insert_offset_min
        required_grid_x = num_grid_for_mm(self.insert_width_total + min_offset_total + (self.edge_padding_x * 2))
        return max(required_grid_x, self.grid_x_min)

    @property
    def length_y(self) -> float:
        return self.grid_y * GF.GRID_UNIT

    @property
    def length_x(self) -> float:
        return self.grid_x * GF.GRID_UNIT

    @property
    def insert_width_total(self) -> float:
        return sum([s.diameter_mm + self.insert_diameter_offset for s in self.sockets])

    @property
    def insert_offset(self) -> float:
        total_free = self.length_x - self.edge_padding_x * 2 - self.insert_width_total
        if len(self.sockets) == 1:
            return 0
        return total_free / (len(self.sockets) - 1)
