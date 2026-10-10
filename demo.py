"""Run success, unavailable-inventory, and timeout/deadline demonstrations."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import requests


ROOT = Path(__file__).resolve().parent


@contextmanager
def service(script: Path, environment: dict[str, str]):
    env = os.environ.copy()
    env.update(environment)
    process = subprocess.Popen(
        [sys.executable, str(script)],
        cwd=script.parent,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        yield process
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


def wait_for_port(port: int, timeout: float = 8) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as connection:
            connection.settimeout(0.2)
            if connection.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"service on port {port} did not start")


def show(label: str, response: requests.Response) -> None:
    print(f"{label}: HTTP {response.status_code}")
    print(json.dumps(response.json(), indent=2, sort_keys=True))


def rest_demo() -> None:
    print("\n=== REST SUCCESS AND FAILURE DEMO ===")
    inventory_script = ROOT / "rest" / "inventory_service.py"
    order_script = ROOT / "rest" / "order_service.py"
    order_env = {
        "PORT": "5100",
        "INVENTORY_URL": "http://127.0.0.1:5101/inventory/check",
        "INVENTORY_TIMEOUT_SECONDS": "0.5",
    }

    with service(order_script, order_env):
        wait_for_port(5100)
        with service(inventory_script, {"PORT": "5101"}):
            wait_for_port(5101)
            show(
                "REST success",
                requests.post(
                    "http://127.0.0.1:5100/orders",
                    json={"item_id": "book", "quantity": 2},
                    timeout=3,
                ),
            )
            show(
                "REST unavailable item quantity",
                requests.post(
                    "http://127.0.0.1:5100/orders",
                    json={"item_id": "laptop", "quantity": 5},
                    timeout=3,
                ),
            )

        with service(
            inventory_script,
            {"PORT": "5101", "INVENTORY_DELAY_SECONDS": "1.5"},
        ):
            wait_for_port(5101)
            show(
                "REST timeout",
                requests.post(
                    "http://127.0.0.1:5100/orders",
                    json={"item_id": "book", "quantity": 1},
                    timeout=3,
                ),
            )
            show(
                "REST Order Service after timeout",
                requests.get("http://127.0.0.1:5100/health", timeout=3),
            )


def grpc_demo() -> None:
    print("\n=== gRPC SUCCESS AND FAILURE DEMO ===")
    inventory_script = ROOT / "grpc_version" / "inventory_server.py"
    order_script = ROOT / "grpc_version" / "order_service.py"
    order_env = {
        "PORT": "6100",
        "INVENTORY_GRPC_TARGET": "127.0.0.1:51051",
        "INVENTORY_DEADLINE_SECONDS": "0.5",
    }

    with service(order_script, order_env):
        wait_for_port(6100)
        with service(inventory_script, {"PORT": "51051"}):
            wait_for_port(51051)
            show(
                "gRPC success",
                requests.post(
                    "http://127.0.0.1:6100/orders",
                    json={"item_id": "book", "quantity": 2},
                    timeout=3,
                ),
            )
            show(
                "gRPC unavailable item quantity",
                requests.post(
                    "http://127.0.0.1:6100/orders",
                    json={"item_id": "laptop", "quantity": 5},
                    timeout=3,
                ),
            )

        with service(
            inventory_script,
            {"PORT": "51051", "INVENTORY_DELAY_SECONDS": "1.5"},
        ):
            wait_for_port(51051)
            show(
                "gRPC deadline",
                requests.post(
                    "http://127.0.0.1:6100/orders",
                    json={"item_id": "book", "quantity": 1},
                    timeout=3,
                ),
            )
            show(
                "gRPC Order Service after deadline",
                requests.get("http://127.0.0.1:6100/health", timeout=3),
            )


if __name__ == "__main__":
    rest_demo()
    grpc_demo()

