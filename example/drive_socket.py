# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ocp-vscode",
#     "pyfinity",
# ]
#
# [tool.uv.sources]
# pyfinity = { path = "../", editable = true }
# ///

import argparse
from fractions import Fraction
from typing import NamedTuple

from build123d import Axis, Location, Mesher, export_stl
from ocp_vscode import show_object
from pyfinity import drive_socket as socket
from pyfinity.drive_socket import SocketType


class Dimension(NamedTuple):
    size: float | str
    diameter: float


SHORT_DEPTH = 6
LONG_DEPTH = 12


def make_sockets(dimensions: list[Dimension], drive: str, socket_type: socket.SocketType) -> list[socket.Socket]:
    sockets = []
    builder = socket.SocketBuilder().drive(drive)
    for d in dimensions:
        builder = builder.diameter(d.diameter).add_type(socket_type)
        builder = builder.size(float(Fraction(d.size))) if isinstance(d.size, str) else builder.size(d.size)
        sockets.append(builder.build())
    return sockets


def make_spec(drive: str, socket_type: socket.SocketType, dimensions: list[Dimension]) -> socket.OrganizerSpec:
    sockets = make_sockets(dimensions, drive, socket_type)

    depth = 6
    if socket_type & socket.SocketType.DEEP:
        depth = 12

    insert_labels_size = 5
    if socket_type & SocketType.SAE:
        insert_labels_size = 5

    return socket.OrganizerSpec(
        sockets,
        base_height=depth,
        insert_depth=depth,
        insert_diameter_offset=0.5,
        insert_offset_min=3,
        insert_labels_size=insert_labels_size,
        align="bottom",
        edge_padding_y=1,
        organizer_label=str(socket.DriveSize.from_str(drive)),
        organizer_split_face_plate=2,
    )


def metric_organizers() -> list[socket.Organizer]:
    return [
        socket.Organizer(
            make_spec(
                "1/4",
                SocketType.METRIC | SocketType.SIX_POINT,
                [
                    Dimension(4, 11.9),
                    Dimension(5, 11.9),
                    Dimension(6, 11.9),
                    Dimension(7, 11.9),
                    Dimension(8, 11.9),
                    Dimension(9, 13.1),
                    Dimension(10, 14.6),
                    Dimension(11, 15.9),
                    Dimension(12, 16.8),
                    Dimension(13, 17.7),
                ],
            ),
        ),
        socket.Organizer(
            make_spec(
                "1/4",
                SocketType.METRIC | SocketType.SIX_POINT | SocketType.DEEP,
                [
                    Dimension(7, 11.8),
                    Dimension(8, 11.8),
                    Dimension(9, 12.8),
                    Dimension(10, 14.5),
                    Dimension(11, 15.6),
                    Dimension(12, 16.6),
                    Dimension(13, 17.6),
                ],
            )
        ),
        socket.Organizer(
            make_spec(
                "1/2",
                SocketType.METRIC | SocketType.SIX_POINT,
                [
                    Dimension(10, 17.16),
                    Dimension(11, 17.21),
                    Dimension(12, 17.30),
                    Dimension(13, 18.26),
                    Dimension(14, 19.70),
                    Dimension(15, 20.56),
                    Dimension(16, 22.17),
                    Dimension(17, 23.49),
                    Dimension(18, 24.27),
                    Dimension(19, 25.79),
                ],
            )
        ),
        socket.Organizer(
            make_spec(
                "1/2",
                SocketType.METRIC | SocketType.SIX_POINT | SocketType.DEEP,
                [
                    Dimension(10, 17.16),
                    Dimension(11, 17.21),
                    Dimension(12, 17.30),
                    Dimension(13, 18.26),
                    Dimension(14, 19.70),
                    Dimension(15, 20.56),
                    Dimension(16, 22.17),
                    Dimension(17, 23.49),
                    Dimension(18, 24.27),
                ],
            ),
        ),
        socket.Organizer(
            make_spec(
                "3/8",
                SocketType.METRIC | SocketType.TWELVE_POINT,
                [
                    Dimension(10, 16.8),
                    Dimension(11, 16.8),
                    Dimension(12, 16.8),
                    Dimension(13, 17.8),
                    Dimension(14, 19.8),
                    Dimension(15, 21.9),
                    Dimension(16, 21.9),
                    Dimension(17, 23.6),
                    Dimension(19, 25.5),
                    Dimension(22, 29.8),
                ],
            ),
        ),
    ]


def sae_organizers() -> list[socket.Organizer]:
    return [
        socket.Organizer(
            make_spec(
                "1/4",
                SocketType.SAE | SocketType.SIX_POINT,
                [
                    Dimension("3/16", 11.8),
                    Dimension("7/32", 11.8),
                    Dimension("1/4", 11.9),
                    Dimension("9/32", 11.9),
                    Dimension("5/16", 11.9),
                    Dimension("11/32", 13.1),
                    Dimension("3/8", 14.6),
                    Dimension("7/16", 15.9),
                    Dimension("1/2", 17.5),
                ],
            ),
        ),
        socket.Organizer(
            make_spec(
                "1/4",
                SocketType.SAE | SocketType.SIX_POINT | SocketType.DEEP,
                [
                    Dimension("1/4", 11.8),
                    Dimension("9/32", 11.8),
                    Dimension("5/16", 11.8),
                    Dimension("11/32", 12.8),
                    Dimension("3/8", 14.5),
                    Dimension("7/16", 15.6),
                    Dimension("1/2", 17.6),
                ],
            ),
        ),
        socket.Organizer(
            make_spec(
                "1/2",
                SocketType.SAE | SocketType.SIX_POINT,
                [
                    Dimension("3/8", 17.2),
                    Dimension("7/16", 17.2),
                    Dimension("1/2", 18.3),
                    Dimension("9/16", 19.6),
                    Dimension("5/8", 22.2),
                    Dimension("11/16", 24.3),
                    Dimension("3/4", 25.7),
                    Dimension("13/16", 27.9),
                    Dimension("7/8", 30),
                ],
            ),
        ),
        socket.Organizer(
            make_spec(
                "1/2",
                SocketType.SAE | SocketType.SIX_POINT | SocketType.DEEP,
                [
                    Dimension("3/8", 16.7),
                    Dimension("7/16", 16.7),
                    Dimension("1/2", 18.6),
                    Dimension("9/16", 19.5),
                    Dimension("5/8", 21.9),
                    Dimension("11/16", 24.2),
                    Dimension("3/4", 25.65),
                ],
            ),
        ),
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate socket organizers")
    parser.add_argument("-show", action="store_true", help="Show objects in viewer")
    parser.add_argument("-output", type=str, action="append", choices=["3mf", "stl"], default=[])
    parser.add_argument("types", nargs="+", type=str, choices=["metric", "sae"])
    args = parser.parse_args()

    objs = []
    for t in args.types:
        if t == "metric":
            objs.extend(metric_organizers())
        elif t == "sae":
            objs.extend(sae_organizers())

    offset = 10
    for i, o in enumerate(objs):
        if i != 0:
            prev = objs[i - 1]
            v = prev.edges().sort_by(Axis.Y)[-1].vertices()[0]
            o.move(Location((0, v.Y + offset, 0)))
        if args.show:
            show_object(o)
        for output in args.output:
            if output == "stl":
                f = f"stl/{o.name}.stl"
                ok = export_stl(o, f)
                print(f"{'✅' if ok else '🚫'} {f}")
            if output == "3mf":
                f = f"3mf/{o.name}.model.3mf"
                exporter = Mesher()
                exporter.add_shape(o, part_number=o.name)
                exporter.add_code_to_metadata()
                try:
                    exporter.write(f)
                    print(f"✅ {f}")
                except ValueError as ex:
                    print(f"🚫 {f}: {ex}")
