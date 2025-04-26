from build123d import (
    Axis,
    Location,
)
from pyfinity import drive_socket as socket


def quarter_in_mm_sockets() -> socket.Organizer:
    builder = socket.SocketBuilder().metric().height(25)
    sockets = [
        builder.size(4).diameter(11.9).build(),
        builder.size(5).diameter(11.9).build(),
        builder.size(6).diameter(11.9).build(),
        builder.size(7).diameter(11.9).build(),
        builder.size(8).diameter(11.9).build(),
        builder.size(9).diameter(13.1).build(),
        builder.size(10).diameter(14.6).build(),
        builder.size(11).diameter(15.9).build(),
        builder.size(12).diameter(16.8).build(),
        builder.size(13).diameter(17.2).build(),
    ]
    spec = socket.OrganizerSpec(
        face_label='C',
        height=8,
        insert_depth=4,
    )
    return socket.Organizer(sockets, spec)

def quarter_in_mm_sockets_bottom() -> socket.Organizer:
    builder = socket.SocketBuilder().metric().height(25)
    sockets = [
        builder.size(4).diameter(11.9).build(),
        builder.size(5).diameter(11.9).build(),
        builder.size(6).diameter(11.9).build(),
        builder.size(7).diameter(11.9).build(),
        builder.size(8).diameter(11.9).build(),
        builder.size(9).diameter(13.1).build(),
        builder.size(10).diameter(14.6).build(),
        builder.size(11).diameter(15.9).build(),
        builder.size(12).diameter(16.8).build(),
        builder.size(13).diameter(17.2).build(),
    ]
    spec = socket.OrganizerSpec(
        face_label='B',
        height=8,
        insert_depth=4,
        align='bottom',
    )
    o = socket.Organizer(sockets, spec)
    o.label += '-bottom'
    return o


def half_in_mm_sockets() -> socket.Organizer:
    builder = socket.SocketBuilder().metric()
    sockets = [
        builder.size(10).diameter(17.16).build(),
        builder.size(11).diameter(17.21).build(),
        builder.size(12).diameter(17.30).build(),
        builder.size(13).diameter(18.26).build(),
        builder.size(14).diameter(19.70).build(),
        builder.size(15).diameter(20.56).build(),
        builder.size(16).diameter(22.17).build(),
        builder.size(17).diameter(23.49).build(),
        builder.size(18).diameter(24.27).build(),
        builder.size(19).diameter(25.79).build(),
    ]
    spec = socket.OrganizerSpec(
        height=10,
        insert_depth=5,
    )

    return socket.Organizer(sockets, spec)


if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        objs = [
            quarter_in_mm_sockets(),
            quarter_in_mm_sockets_bottom(),
            half_in_mm_sockets(),
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
