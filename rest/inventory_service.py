"""REST Inventory Service."""

import os
import time

from flask import Flask, jsonify, request


app = Flask(__name__)

INVENTORY = {
    "book": 10,
    "headphones": 0,
    "laptop": 2,
}


def configured_delay() -> float:
    return float(os.getenv("INVENTORY_DELAY_SECONDS", "0"))


@app.get("/health")
def health():
    return jsonify(service="rest-inventory", status="ok"), 200


@app.post("/inventory/check")
def check_inventory():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="request body must be a JSON object"), 400

    item_id = payload.get("item_id")
    quantity = payload.get("quantity")

    if not isinstance(item_id, str) or not item_id:
        return jsonify(error="item_id must be a non-empty string"), 400
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        return jsonify(error="quantity must be a positive integer"), 400

    delay = configured_delay()
    if delay:
        app.logger.info("Simulating %.2f seconds of inventory latency", delay)
        time.sleep(delay)

    if item_id not in INVENTORY:
        return jsonify(error="item not found", item_id=item_id), 404

    available_quantity = INVENTORY[item_id]
    if quantity > available_quantity:
        return (
            jsonify(
                available=False,
                available_quantity=available_quantity,
                item_id=item_id,
                message="requested quantity is unavailable",
            ),
            409,
        )

    return (
        jsonify(
            available=True,
            available_quantity=available_quantity,
            item_id=item_id,
            message="inventory is available",
        ),
        200,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="127.0.0.1", port=port, threaded=True)

