import pytest
from build123d import Axis
from pyfinity import drive_socket as socket


@pytest.fixture
def sockets():
    builder = socket.SocketBuilder().drive(socket.DriveSize.QUARTER_INCH)
    return [
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


def test_align_bottom(sockets):
    o = socket.Organizer(
        socket.OrganizerSpec(
            sockets=sockets,
            align="bottom",
            insert_labels=False,
        ),
    )
    face = o.faces().sort_by(Axis.Z)[-1]
    wires = face.inner_wires()
    first_insert = wires[0].bounding_box()
    last_insert = wires[-1].bounding_box()

    assert pytest.approx(last_insert.min.Y) == first_insert.min.Y


def test_align_center(sockets):
    o = socket.Organizer(
        socket.OrganizerSpec(
            sockets=sockets,
            align="center",
            insert_labels=False,
        ),
    )
    face = o.faces().sort_by(Axis.Z)[-1]
    wires = face.inner_wires()
    first_insert = wires[0]
    last_insert = wires[-1]

    assert pytest.approx(last_insert.center().Y) == first_insert.center().Y
