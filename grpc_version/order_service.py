"""HTTP-facing Order Service that calls Inventory over gRPC."""

import os
import uuid

import grpc
from flask import Flask, jsonify, request

import inventory_pb2
import inventory_pb2_grpc


app = Flask(__name__)


def inventory_target() -> str:
    return os.getenv("INVENTORY_GRPC_TARGET", "127.0.0.1:50051")


def inventory_deadline() -> float:
    return float(os.getenv("INVENTORY_DEADLINE_SECONDS", "1"))


@app.get("/health")
def health():
    return jsonify(service="grpc-order", status="ok"), 200


@app.post("/orders")
def create_order():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="request body must be a JSON object"), 400

    item_id = payload.get("item_id")
    quantity = payload.get("quantity")
    if not isinstance(item_id, str) or not item_id:
        return jsonify(error="item_id must be a non-empty string"), 400
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        return jsonify(error="quantity must be a positive integer"), 400

    try:
        with grpc.insecure_channel(inventory_target()) as channel:
            stub = inventory_pb2_grpc.InventoryServiceStub(channel)
            inventory = stub.CheckInventory(
                inventory_pb2.CheckInventoryRequest(
                    item_id=item_id,
                    quantity=quantity,
                ),
                timeout=inventory_deadline(),
            )
    except grpc.RpcError as error:
        code = error.code()
        details = error.details() or "inventory request failed"

        if code == grpc.StatusCode.DEADLINE_EXCEEDED:
            app.logger.warning("Inventory gRPC deadline exceeded")
            return (
                jsonify(
                    error="inventory_deadline_exceeded",
                    grpc_status=code.name,
                    message=details,
                    order_status="pending",
                ),
                504,
            )

        status_map = {
            grpc.StatusCode.INVALID_ARGUMENT: 400,
            grpc.StatusCode.NOT_FOUND: 404,
            grpc.StatusCode.FAILED_PRECONDITION: 409,
            grpc.StatusCode.UNAVAILABLE: 503,
        }
        return (
            jsonify(
                error="inventory_rejected",
                grpc_status=code.name,
                message=details,
                order_status=(
                    "rejected"
                    if code in (grpc.StatusCode.NOT_FOUND, grpc.StatusCode.FAILED_PRECONDITION)
                    else "pending"
                ),
            ),
            status_map.get(code, 502),
        )

    return (
        jsonify(
            inventory={
                "available": inventory.available,
                "available_quantity": inventory.available_quantity,
                "item_id": inventory.item_id,
                "message": inventory.message,
            },
            item_id=item_id,
            order_id=str(uuid.uuid4()),
            order_status="accepted",
            quantity=quantity,
        ),
        201,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "6000"))
    app.run(host="127.0.0.1", port=port, threaded=True)

