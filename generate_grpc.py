"""Generate Python gRPC modules from the inventory contract."""

from pathlib import Path
import sys

from grpc_tools import protoc


ROOT = Path(__file__).resolve().parent
PROTO_DIR = ROOT / "grpc_version"

result = protoc.main(
    [
        "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={PROTO_DIR}",
        f"--grpc_python_out={PROTO_DIR}",
        str(PROTO_DIR / "inventory.proto"),
    ]
)

if result != 0:
    raise SystemExit(result)

print("Generated grpc_version/inventory_pb2.py and inventory_pb2_grpc.py")
sys.exit(0)

