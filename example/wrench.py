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

from ocp_vscode import show_object
from pyfinity import wrench

if __name__ == "__main__":
    ws = [
        wrench.Wrench(8),
        wrench.Wrench(13),
        wrench.Wrench(14),
        wrench.Wrench(15),
        wrench.Wrench(17),
    ]
    o = wrench.Organizer(ws)
    show_object(o)

