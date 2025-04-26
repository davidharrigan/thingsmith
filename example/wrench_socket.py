from pyfinity import socket


if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        sockets = [
            socket.Socket(10, diameter_mm=17.16,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(11, diameter_mm=17.21,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(12, diameter_mm=17.30,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(13, diameter_mm=18.26,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(14, diameter_mm=19.70,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(15, diameter_mm=20.56,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(16, diameter_mm=22.17,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(17, diameter_mm=23.49,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(18, diameter_mm=24.27,
                          unit=socket.SocketUnit.METRIC),
            socket.Socket(19, diameter_mm=25.79,
                          unit=socket.SocketUnit.METRIC),
        ]
        o = socket.Organizer(sockets)
        show_object(o)

    except ImportError:
        pass
