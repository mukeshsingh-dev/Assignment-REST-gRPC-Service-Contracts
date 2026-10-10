"""gRPC Inventory Service."""

from concurrent import futures
import logging
import os
import time

import grpc

import inventory_pb2
import inventory_pb2_grpc


INVENTORY = {
    "book": 10,
    "headphones": 0,
    "laptop": 2,
}


class InventoryService(inventory_pb2_grpc.InventoryServiceServicer):
    def CheckInventory(self, request, context):
        if not request.item_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "item_id is required")
        if request.quantity <= 0:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "quantity must be a positive integer",
            )

        delay = float(os.getenv("INVENTORY_DELAY_SECONDS", "0"))
        if delay:
            logging.info("Simulating %.2f seconds of inventory latency", delay)
            time.sleep(delay)

        if request.item_id not in INVENTORY:
            context.abort(grpc.StatusCode.NOT_FOUND, "item not found")

        available_quantity = INVENTORY[request.item_id]
        if request.quantity > available_quantity:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                f"only {available_quantity} units are available",
            )

        return inventory_pb2.CheckInventoryResponse(
            available=True,
            available_quantity=available_quantity,
            item_id=request.item_id,
            message="inventory is available",
        )


def serve():
    port = int(os.getenv("PORT", "50051"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(
        InventoryService(), server
    )
    server.add_insecure_port(f"127.0.0.1:{port}")
    server.start()
    logging.info("gRPC Inventory Service listening on 127.0.0.1:%s", port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    serve()

