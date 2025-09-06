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

from build123d import export_stl
from ocp_vscode import show_object
from pyfinity import wrench

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate socket organizers")
    parser.add_argument("-show", action="store_true", help="Show objects in viewer")
    parser.add_argument("-output", type=str, action="append", choices=["stl"], default=[])
    args = parser.parse_args()

    ws = [
        wrench.Wrench(8),
        wrench.Wrench(13),
        wrench.Wrench(14),
        wrench.Wrench(15),
        wrench.Wrench(17),
    ]
    o = wrench.Organizer(ws)

    if args.show:
        show_object(o)
    for output in args.output:
        if output == "stl":
            f = "example/stl/wrench-organizer.stl"
            ok = export_stl(o, f)
            print(f"{'✅' if ok else '🚫'} {f}")
        else:
            print(f"output {output} not supported")
