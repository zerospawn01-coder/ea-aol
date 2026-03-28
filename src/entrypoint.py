"""Bootstrap runtime stub for the EA-AOL project boundary."""

from typing import Any

from src.contract_runtime import (
    OPERATION_CONTRACTS,
    assert_contract_completeness,
    build_error_response,
    normalize_success_response,
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


def validate_request_envelope(candidate_request: object) -> dict[str, Any]:
    """Validate and normalize a candidate request envelope."""

    normalized = validate_operation_envelope(candidate_request)
    normalized["payload"] = validate_payload(normalized["operation"], normalized["payload"])
    return {
        "valid": True,
        "normalized_request": normalized,
    }


def _handle_describe_runtime_surface(_payload: dict[str, Any]) -> dict[str, Any]:
    return describe_runtime_surface()


def _handle_list_supported_operations(_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "operations": list_supported_operations(),
    }


def _handle_validate_request_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    return validate_request_envelope(payload.get("candidate_request"))


HANDLERS = {
    "describe-runtime-surface": _handle_describe_runtime_surface,
    "list-supported-operations": _handle_list_supported_operations,
    "validate-request-envelope": _handle_validate_request_envelope,
}


def run_entrypoint(request: object) -> dict[str, Any]:
    """Validate a bootstrap request and return a structured contract-valid response."""
    operation = "unknown"
    if isinstance(request, dict):
        requested_operation = request.get("operation")
        if isinstance(requested_operation, str) and requested_operation.strip():
            operation = requested_operation

    try:
        assert_contract_completeness(HANDLERS)
        validated_request = validate_operation_envelope(request)
        operation = validated_request["operation"]
        payload = validate_payload(operation, validated_request["payload"])
        handler = HANDLERS.get(operation)
        if handler is None:
            return build_error_response(operation, "unsupported_operation", f"Unsupported operation: {operation}")

        result = handler(payload)
        return normalize_success_response(operation, result)
    except Exception as error:
        message = str(error)
        if "Unsupported operation:" in message:
            return build_error_response(operation, "unsupported_operation", message)
        if "Request." in message or "Operation '" in message or "Unexpected" in message:
            return build_error_response(operation, "validation_error", message)
        return build_error_response(operation, "internal_error", message or "Internal runtime error.")
