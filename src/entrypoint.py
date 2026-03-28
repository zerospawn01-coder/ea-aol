"""Bootstrap runtime stub for the EA-AOL project boundary."""

from typing import Any

from src.contract_runtime import (
    ContractViolationError,
    validate_operation_envelope,
    validate_payload,
)

def describe_runtime_surface() -> dict[str, Any]:
    """Return the initial project surface in a machine-readable form."""

    return {
        "project": "ea-aol",
        "status": "bootstrap",
        "contract": "contracts/system_contract.md",
        "supported_operations": ["describe-runtime-surface"],
    }


def run_entrypoint(request: object) -> dict[str, Any]:
    """Validate a bootstrap request and return a structured response."""
    validated_request = validate_operation_envelope(request)
    operation = validated_request["operation"]
    payload = validate_payload(operation, validated_request["payload"])

    return {
        "ok": True,
        "operation": operation,
        "payload": payload,
        "surface": describe_runtime_surface(),
    }
