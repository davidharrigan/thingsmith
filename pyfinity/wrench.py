from build123d import (
    BuildPart,
)

from pyfinity import _wrench as wrench
from pyfinity._wrench import Wrench


if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        ws = [Wrench(8), Wrench(13), Wrench(14), Wrench(15), Wrench(17)]

        with BuildPart() as part:
            o = wrench.Organizer(ws)
        show_object(o)

    except ImportError:
        pass
