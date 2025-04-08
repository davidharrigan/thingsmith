from build123d import (
    Axis,
    BuildPart,
    BuildSketch,
    Mode,
    Rectangle,
    export_stl,
    extrude,
)

from pyfinity import _wrench as wrench
from pyfinity._wrench import Wrench

if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        ws = [Wrench(8), Wrench(13), Wrench(14), Wrench(15), Wrench(17)]

        with BuildPart() as part:
            o = wrench.Organizer(ws)
            face = o.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face) as skt:
                Rectangle(3, 20)
            extrude(amount=-200, mode=Mode.INTERSECT)
        show_object(o)

        export_stl(o, "organizer.stl")
        export_stl(part.part, "cutout.stl")

    except ImportError:
        pass
