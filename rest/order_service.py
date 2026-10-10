"""Order Service that calls Inventory over REST."""

import os
import uuid

import requests
from flask import Flask, jsonify, request


app = Flask(__name__)


def inventory_url() -> str:
    return os.getenv("INVENTORY_URL", "http://127.0.0.1:5001/inventory/check")


def inventory_timeout() -> float:
    return float(os.getenv("INVENTORY_TIMEOUT_SECONDS", "1"))


@app.get("/health")
def health():
    return jsonify(service="rest-order", status="ok"), 200


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
        inventory_response = requests.post(
            inventory_url(),
            json={"item_id": item_id, "quantity": quantity},
            timeout=inventory_timeout(),
        )
    except requests.Timeout:
        app.logger.warning("Inventory REST request timed out")
        return (
            jsonify(
                error="inventory_timeout",
                message="inventory did not respond before the timeout",
                order_status="pending",
            ),
            504,
        )
    except requests.ConnectionError:
        app.logger.exception("Inventory REST service is unavailable")
        return (
            jsonify(
                error="inventory_unavailable",
                message="inventory service could not be reached",
                order_status="pending",
            ),
            503,
        )

    inventory_body = inventory_response.json()
    if inventory_response.status_code == 200:
        return (
            jsonify(
                inventory=inventory_body,
                item_id=item_id,
                order_id=str(uuid.uuid4()),
                order_status="accepted",
                quantity=quantity,
            ),
            201,
        )

    if inventory_response.status_code in (404, 409):
        return (
            jsonify(
                inventory=inventory_body,
                item_id=item_id,
                order_status="rejected",
                quantity=quantity,
            ),
            inventory_response.status_code,
        )

    return (
        jsonify(
            error="inventory_error",
            message="inventory returned an unexpected response",
            order_status="pending",
        ),
        502,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, threaded=True)

