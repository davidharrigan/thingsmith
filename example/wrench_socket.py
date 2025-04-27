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
from build123d import (
    Axis,
    Location,
)

from ocp_vscode import show_object
from pyfinity import drive_socket as socket


def quarter_in_mm_sockets() -> socket.Organizer:
    builder = socket.SocketBuilder().height(25)
    sockets = [
        builder.metric(4).diameter(11.9).build(),
        builder.metric(5).diameter(11.9).build(),
        builder.metric(6).diameter(11.9).build(),
        builder.metric(7).diameter(11.9).build(),
        builder.metric(8).diameter(11.9).build(),
        builder.metric(9).diameter(13.1).build(),
        builder.metric(10).diameter(14.6).build(),
        builder.metric(11).diameter(15.9).build(),
        builder.metric(12).diameter(16.8).build(),
        builder.metric(13).diameter(17.2).build(),
    ]
    spec = socket.OrganizerSpec(
        sockets,
        organizer_label='CENTER',
        base_height=8,
        insert_depth=4,
        align='center',
        organizer_split_face_plate=2,
    )
    return socket.Organizer(spec)

def quarter_in_mm_sockets_bottom() -> socket.Organizer:
    builder = socket.SocketBuilder().height(25)
    sockets = [
        builder.metric(4).diameter(11.9).build(),
        builder.metric(5).diameter(11.9).build(),
        builder.metric(6).diameter(11.9).build(),
        builder.metric(7).diameter(11.9).build(),
        builder.metric(8).diameter(11.9).build(),
        builder.metric(9).diameter(13.1).build(),
        builder.metric(10).diameter(14.6).build(),
        builder.metric(11).diameter(15.9).build(),
        builder.metric(12).diameter(16.8).build(),
        builder.metric(13).diameter(17.2).build(),
    ]
    spec = socket.OrganizerSpec(
        sockets,
        organizer_label='BOTTOM',
        base_height=8,
        insert_depth=4,
        align='bottom',
        organizer_name_suffix='-bottom',
    )
    return socket.Organizer(spec)


def half_in_mm_sockets() -> socket.Organizer:
    builder = socket.SocketBuilder()
    sockets = [
        builder.metric(10).diameter(17.16).build(),
        builder.metric(11).diameter(17.21).build(),
        builder.metric(12).diameter(17.30).build(),
        builder.metric(13).diameter(18.26).build(),
        builder.metric(14).diameter(19.70).build(),
        builder.metric(15).diameter(20.56).build(),
        builder.metric(16).diameter(22.17).build(),
        builder.metric(17).diameter(23.49).build(),
        builder.metric(18).diameter(24.27).build(),
        builder.metric(19).diameter(25.79).build(),
    ]
    spec = socket.OrganizerSpec(
        sockets,
        base_height=10,
        insert_depth=5,
    )
    return socket.Organizer(spec)

def half_in_sae() -> socket.Organizer:
    builder = socket.SocketBuilder().half_in()
    sockets = [
        builder.sae("1/4").diameter(15).build(),
        builder.sae("1/2").diameter(20).build(),
        builder.sae("3/4").diameter(25).build(),
    ]
    spec = socket.OrganizerSpec(
        sockets,
        base_height=10,
        insert_depth=5,
    )
    return socket.Organizer(spec)

if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        objs = [
            quarter_in_mm_sockets(),
            quarter_in_mm_sockets_bottom(),
            half_in_mm_sockets(),
            half_in_sae(),
        ]
        offset = 10
        for i, o in enumerate(objs):
            if i != 0:
                prev = objs[i - 1]
                v = prev.edges().sort_by(Axis.Y)[-1].vertices()[0]
                o.move(Location((0, v.Y + offset, 0)))
            show_object(o)

    except ImportError:
        pass
