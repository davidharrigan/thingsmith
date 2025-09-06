# pyfinity

- uv sync

```sh
$ uv run ./example/drive_socket.py -output stl metric
✅ example/stl/socket-organizer-METRIC[4-13]-drive[0.25]-type[STANDARD,SIX_POINT].stl
✅ example/stl/socket-organizer-METRIC[7-13]-drive[0.25]-type[DEEP,SIX_POINT].stl
✅ example/stl/socket-organizer-METRIC[10-19]-drive[0.5]-type[STANDARD,SIX_POINT].stl
✅ example/stl/socket-organizer-METRIC[10-18]-drive[0.5]-type[DEEP,SIX_POINT].stl
✅ example/stl/socket-organizer-METRIC[10-22]-drive[0.375]-type[STANDARD,TWELVE_POINT].stl
```

```sh
$ uv run -m ocp_vscode
```
then
```sh
# open http://127.0.0.1:3939/viewer to see the model
$ uv run ./example/drive_socket.py -show metric
```