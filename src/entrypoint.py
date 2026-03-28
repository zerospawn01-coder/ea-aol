"""Bootstrap runtime stub for the EA-AOL project boundary."""

from typing import Any

from src.contract_runtime import (
    ContractViolationError,
    OPERATION_CONTRACTS,
    validate_operation_envelope,
    validate_payload,
)

def describe_runtime_surface() -> dict[str, Any]:
    """Return the initial project surface in a machine-readable form."""

    return {
        "project": "ea-aol",
        "status": "bootstrap",
        "contract": "contracts/system_contract.md",
        "supported_operations": list(OPERATION_CONTRACTS.keys()),
    }


def list_supported_operations() -> list[str]:
    """Return the currently supported operation names."""

    return list(OPERATION_CONTRACTS.keys())


def _handle_describe_runtime_surface(_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface": describe_runtime_surface(),
    }


def _handle_list_supported_operations(_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "operations": list_supported_operations(),
    }


HANDLERS = {
    "describe-runtime-surface": _handle_describe_runtime_surface,
    "list-supported-operations": _handle_list_supported_operations,
}


def run_entrypoint(request: object) -> dict[str, Any]:
    """Validate a bootstrap request and return a structured response."""
    validated_request = validate_operation_envelope(request)
    operation = validated_request["operation"]
    payload = validate_payload(operation, validated_request["payload"])
    handler = HANDLERS.get(operation)
    if handler is None:
        raise ContractViolationError(f"Unsupported operation: {operation}")

    response = {
        "ok": True,
        "operation": operation,
        "payload": payload,
    }
    response.update(handler(payload))
    return response
