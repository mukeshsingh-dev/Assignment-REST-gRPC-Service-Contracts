# Screenshot capture checklist

Save four terminal screenshots in this directory:

1. `01-rest-success.png` — REST success response (`HTTP 201`).
2. `02-rest-timeout-health.png` — REST timeout (`HTTP 504`) and the subsequent successful health check (`HTTP 200`).
3. `03-grpc-success.png` — gRPC-backed success response (`HTTP 201`).
4. `04-grpc-deadline-health.png` — gRPC deadline failure (`DEADLINE_EXCEEDED`/`HTTP 504`) and the subsequent successful health check (`HTTP 200`).

On macOS, press **Command + Shift + 4**, then press **Space**, click the Terminal window, and rename the resulting PNG. Make sure each screenshot shows the command and output, but does not reveal credentials or tokens.
