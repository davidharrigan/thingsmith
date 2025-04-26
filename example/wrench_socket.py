from pyfinity import drive_socket as socket

if __name__ == "__main__":
    try:
        from ocp_vscode import show_object

        builder = socket.SocketBuilder().metric().height(26)
        sockets = [
            builder.size(10).diameter(17.16).build(),
            builder.size(11).diameter(17.21).build(),
            builder.size(12).diameter(17.30).build(),
            builder.size(13).diameter(18.26).build(),
            builder.size(14).diameter(19.70).build(),
            builder.size(15).diameter(20.56).build(),
        ]

        builder = builder.height(29)
        sockets.extend([
            builder.size(16).diameter(22.17).build(),
            builder.size(17).diameter(23.49).build(),
            builder.size(18).diameter(24.27).build(),
            builder.size(19).diameter(25.79).build(),
        ])

        o = socket.Organizer(sockets)
        show_object(o)

    except ImportError:
        pass
