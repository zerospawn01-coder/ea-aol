"""Bootstrap runtime stub for the EA-AOL project boundary."""

from typing import Any

from src.contract_runtime import (
    ContractViolationError,
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


def _normalize_non_empty_text(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ContractViolationError(f"{path} must be a string.")
    normalized = value.strip()
    if not normalized:
        raise ContractViolationError(f"{path} must not be empty after normalization.")
    return normalized


def canonicalize_module_definition(module_definition: object) -> dict[str, Any]:
    """Canonicalize an EA-AOL module definition."""

    if not isinstance(module_definition, dict):
        raise ContractViolationError("payload.module_definition must be a mapping.")

    capabilities_value = module_definition["capabilities"]
    if not isinstance(capabilities_value, list):
        raise ContractViolationError("payload.module_definition.capabilities must be an array.")

    normalized_capabilities = sorted(
        {
            _normalize_non_empty_text(
                capability,
                f"payload.module_definition.capabilities[{index}]",
            )
            for index, capability in enumerate(capabilities_value)
        }
    )

    entrypoint_value = module_definition["entrypoint"]
    if not isinstance(entrypoint_value, dict):
        raise ContractViolationError("payload.module_definition.entrypoint must be a mapping.")

    return {
        "name": _normalize_non_empty_text(module_definition["name"], "payload.module_definition.name"),
        "kind": module_definition["kind"],
        "capabilities": normalized_capabilities,
        "entrypoint": {
            "module": _normalize_non_empty_text(
                entrypoint_value["module"],
                "payload.module_definition.entrypoint.module",
            ),
            "callable": _normalize_non_empty_text(
                entrypoint_value["callable"],
                "payload.module_definition.entrypoint.callable",
            ),
        },
    }


def normalize_module_definition(module_definition: object) -> dict[str, Any]:
    """Normalize an EA-AOL module definition into a deterministic descriptor."""

    normalized_module = canonicalize_module_definition(module_definition)
    return {
        "normalized_module": normalized_module,
        "ready_for_runtime_registration": bool(normalized_module["capabilities"]),
    }


def validate_module_definition(module_definition: object) -> dict[str, Any]:
    """Validate an EA-AOL module definition against the canonical descriptor contract."""

    return {
        "valid": True,
        "normalized_module": canonicalize_module_definition(module_definition),
    }


def _handle_describe_runtime_surface(_payload: dict[str, Any]) -> dict[str, Any]:
    return describe_runtime_surface()


def _handle_list_supported_operations(_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "operations": list_supported_operations(),
    }


def _handle_validate_request_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    return validate_request_envelope(payload.get("candidate_request"))


def _handle_normalize_module_definition(payload: dict[str, Any]) -> dict[str, Any]:
    return normalize_module_definition(payload.get("module_definition"))


def _handle_validate_module_definition(payload: dict[str, Any]) -> dict[str, Any]:
    return validate_module_definition(payload.get("module_definition"))


HANDLERS = {
    "describe-runtime-surface": _handle_describe_runtime_surface,
    "list-supported-operations": _handle_list_supported_operations,
    "validate-request-envelope": _handle_validate_request_envelope,
    "normalize-module-definition": _handle_normalize_module_definition,
    "validate-module-definition": _handle_validate_module_definition,
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
    except ContractViolationError as error:
        message = str(error)
        if "Unsupported operation:" in message:
            return build_error_response(operation, "unsupported_operation", message)
        return build_error_response(operation, "validation_error", message)
    except Exception as error:
        message = str(error)
        return build_error_response(operation, "internal_error", message or "Internal runtime error.")
