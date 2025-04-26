from pyfinity import wrench


if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        ws = [
            wrench.Wrench(8),
            wrench.Wrench(13),
            wrench.Wrench(14),
            wrench.Wrench(15),
            wrench.Wrench(17),
        ]
        o = wrench.Organizer(ws)
        show_object(o)

    except ImportError:
        pass
