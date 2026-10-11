# Screenshot evidence

These four images contain output from a verified `python demo.py` run:

1. `01-rest-success.png` — REST success response (`HTTP 201`).
2. `02-rest-timeout-health.png` — REST timeout (`HTTP 504`) and the subsequent successful health check (`HTTP 200`).
3. `03-grpc-success.png` — gRPC-backed success response (`HTTP 201`).
4. `04-grpc-deadline-health.png` — gRPC deadline failure (`DEADLINE_EXCEEDED`/`HTTP 504`) and the subsequent successful health check (`HTTP 200`).

Together they demonstrate successful REST and gRPC requests, clean timeout/deadline handling, and successful health checks proving that both Order Services remain running after failure.
