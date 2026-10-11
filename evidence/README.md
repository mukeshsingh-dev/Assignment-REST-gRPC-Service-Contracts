# Screenshot evidence

These ten locally captured images provide the assignment evidence:

1. `01-rest-inventory-service.png` — REST Inventory Service running on port `5001`.
2. `02-rest-order-service.png` — REST Order Service running on port `5000`.
3. `03-rest-success.png` — REST success response (`HTTP 201`).
4. `04-rest-timeout.png` — REST timeout handled with `HTTP 504`.
5. `05-rest-health-after-timeout.png` — REST Order Service health check returns `HTTP 200` after the timeout.
6. `06-grpc-success.png` — gRPC-backed success response (`HTTP 201`).
7. `07-grpc-deadline.png` — gRPC deadline failure returns `DEADLINE_EXCEEDED` and `HTTP 504`.
8. `08-grpc-health-after-deadline.png` — gRPC-backed Order Service health check returns `HTTP 200` after the deadline failure.
9. `09-rest-unavailable.png` — REST unavailable quantity returns `HTTP 409` and a rejected order.
10. `10-grpc-unavailable.png` — gRPC unavailable quantity returns `HTTP 409`, `FAILED_PRECONDITION`, and a rejected order.

Together they demonstrate successful REST and gRPC requests, clean timeout/deadline handling, and successful health checks proving that both Order Services remain running after failure.
