from build123d import (
    BuildPart,
    export_stl,
)
from ocp_vscode import show

from pyfinity import _wrench as wrench
from pyfinity._wrench import Wrench


if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        ws = [Wrench(10), Wrench(13), Wrench(14), Wrench(15), Wrench(17)]
        # ws = [Wrench(n) for n in range(8, 22)]

        with BuildPart() as part:
            o = wrench.Organizer(ws)
        show(o)
        export_stl(o, "organizer.stl")

    except ImportError:
        pass
