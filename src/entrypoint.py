"""Bootstrap runtime stub for the EA-AOL project boundary."""

from collections.abc import Mapping
from typing import Any


class ContractViolationError(ValueError):
    """Raised when a request violates the repository contract."""

def describe_runtime_surface() -> dict[str, str]:
    """Return the initial project surface in a machine-readable form."""

    return {
        "project": "ea-aol",
        "status": "bootstrap",
        "contract": "contracts/system_contract.md",
        "supported_operations": "describe-runtime-surface",
    }


def run_entrypoint(request: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a bootstrap request and return a structured response."""

    if not isinstance(request, Mapping):
        raise ContractViolationError("Request must be a mapping.")

    operation = request.get("operation")
    if not isinstance(operation, str) or not operation.strip():
        raise ContractViolationError("Request.operation must be a non-empty string.")

    if "payload" not in request:
        raise ContractViolationError("Request.payload is required.")

    payload = request["payload"]
    if not isinstance(payload, Mapping):
        raise ContractViolationError("Request.payload must be a mapping.")

    if operation != "describe-runtime-surface":
        raise ContractViolationError(f"Unsupported operation: {operation}")

    if payload:
        raise ContractViolationError(
            "Operation 'describe-runtime-surface' does not accept payload fields."
        )

    return {
        "ok": True,
        "operation": operation,
        "surface": describe_runtime_surface(),
    }
