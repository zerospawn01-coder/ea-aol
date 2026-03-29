"""Helpers for schema-backed bootstrap contract validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "contracts"
SCHEMA_ROOT = CONTRACT_ROOT / "schemas"
OPERATION_ROOT = CONTRACT_ROOT / "operations"
REPO_ROOT = Path(__file__).resolve().parents[1]

OPERATION_CONTRACTS = {
    "describe-runtime-surface": (
        OPERATION_ROOT / "describe_runtime_surface.md",
        "describe_runtime_surface.schema.json",
    ),
    "list-supported-operations": (
        OPERATION_ROOT / "list_supported_operations.md",
        "list_supported_operations.schema.json",
    ),
    "validate-request-envelope": (
        OPERATION_ROOT / "validate_request_envelope.md",
        "validate_request_envelope.schema.json",
    ),
    "normalize-module-definition": (
        OPERATION_ROOT / "normalize_module_definition.md",
        "normalize_module_definition.schema.json",
    ),
    "validate-module-definition": (
        OPERATION_ROOT / "validate_module_definition.md",
        "validate_module_definition.schema.json",
    ),
    "describe-module-surface": (
        OPERATION_ROOT / "describe_module_surface.md",
        "describe_module_surface.schema.json",
    ),
}

RESPONSE_CONTRACTS = {
    "describe-runtime-surface": "describe_runtime_surface.response.schema.json",
    "list-supported-operations": "list_supported_operations.response.schema.json",
    "validate-request-envelope": "validate_request_envelope.response.schema.json",
    "normalize-module-definition": "normalize_module_definition.response.schema.json",
    "validate-module-definition": "validate_module_definition.response.schema.json",
    "describe-module-surface": "describe_module_surface.response.schema.json",
}

CONTRACT_VERSION = "ea-aol/0.1"


class ContractViolationError(ValueError):
    """Raised when a request violates the repository contract."""


ERROR_REGISTRY = {
    "validation_error": {"category": "validation", "retryable": False},
    "unsupported_operation": {"category": "unsupported", "retryable": False},
    "internal_error": {"category": "internal", "retryable": False},
}


def load_schema(schema_name: str) -> dict[str, Any]:
    schema_path = SCHEMA_ROOT / schema_name
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_operation_manifest() -> dict[str, Any]:
    manifest_path = CONTRACT_ROOT / "operation_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate_against_schema(value: Any, schema: dict[str, Any], path: str) -> None:
    schema_type = schema.get("type")

    if "const" in schema and value != schema["const"]:
        raise ContractViolationError(f"{path} must equal {schema['const']!r}.")

    if "enum" in schema and value not in schema["enum"]:
        raise ContractViolationError(f"{path} must be one of {schema['enum']}.")

    if schema_type == "object":
        require_mapping(value, f"{path} must be a mapping.")
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ContractViolationError(f"{path}.{key} is required.")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value.keys()) - set(properties.keys())
            if extra:
                unexpected = ", ".join(sorted(extra))
                raise ContractViolationError(f"Unexpected fields at {path}: {unexpected}")

        for key, subschema in properties.items():
            if key in value:
                _validate_against_schema(value[key], subschema, f"{path}.{key}")
        return

    if schema_type == "array":
        if not isinstance(value, list):
            raise ContractViolationError(f"{path} must be an array.")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                _validate_against_schema(item, item_schema, f"{path}[{index}]")
        return

    if schema_type == "string":
        if not isinstance(value, str):
            raise ContractViolationError(f"{path} must be a string.")
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            raise ContractViolationError(f"{path} must be at least {min_length} characters.")
        return

    if schema_type == "boolean":
        if not isinstance(value, bool):
            raise ContractViolationError(f"{path} must be a boolean.")
        return


def require_mapping(value: Any, message: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractViolationError(message)
    return value


def validate_operation_envelope(request: Any) -> dict[str, Any]:
    require_mapping(request, "Request must be a mapping.")
    schema = load_schema("operation.schema.json")

    for key in schema["required"]:
        if key not in request:
            raise ContractViolationError(f"Request.{key} is required.")

    allowed_keys = set(schema["properties"].keys())
    extra_keys = set(request.keys()) - allowed_keys
    if extra_keys:
        unexpected = ", ".join(sorted(extra_keys))
        raise ContractViolationError(f"Unexpected request fields: {unexpected}")

    operation = request.get("operation")
    if not isinstance(operation, str) or not operation.strip():
        raise ContractViolationError("Request.operation must be a non-empty string.")

    payload = require_mapping(request["payload"], "Request.payload must be a mapping.")
    return {"operation": operation, "payload": dict(payload)}


def validate_payload(operation: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    if operation not in OPERATION_CONTRACTS:
        raise ContractViolationError(f"Unsupported operation: {operation}")

    operation_doc, schema_name = OPERATION_CONTRACTS[operation]
    if not operation_doc.is_file():
        raise ContractViolationError(f"Missing operation contract: {operation_doc}")

    schema = load_schema(schema_name)
    if schema.get("type") != "object":
        raise ContractViolationError(f"Unsupported payload schema type for operation: {operation}")

    _validate_against_schema(dict(payload), schema, "payload")

    return dict(payload)


def normalize_success_response(operation: str, result: Mapping[str, Any]) -> dict[str, Any]:
    if operation not in RESPONSE_CONTRACTS:
        raise ContractViolationError(f"Missing response schema for operation: {operation}")

    result_dict = dict(require_mapping(result, "Result must be a mapping."))
    _validate_against_schema(result_dict, load_schema(RESPONSE_CONTRACTS[operation]), "result")

    envelope = {
        "status": "ok",
        "operation": operation,
        "contract_version": CONTRACT_VERSION,
        "result": result_dict,
    }
    validate_response_envelope(envelope)
    return envelope


def build_error_response(operation: str, code: str, message: str) -> dict[str, Any]:
    if code not in ERROR_REGISTRY:
        code = "internal_error"
        message = "Unclassified error."

    error = {
        "code": code,
        "message": message,
        "category": ERROR_REGISTRY[code]["category"],
        "retryable": ERROR_REGISTRY[code]["retryable"],
    }
    _validate_against_schema(error, load_schema("error.schema.json"), "error")

    envelope = {
        "status": "error",
        "operation": operation or "unknown",
        "contract_version": CONTRACT_VERSION,
        "error": error,
    }
    validate_response_envelope(envelope)
    return envelope


def validate_response_envelope(response: Mapping[str, Any]) -> None:
    response_dict = dict(require_mapping(response, "Response must be a mapping."))
    _validate_against_schema(response_dict, load_schema("response_envelope.schema.json"), "response")

    has_result = "result" in response_dict
    has_error = "error" in response_dict
    if has_result == has_error:
        raise ContractViolationError("Response must contain exactly one of result or error.")

    if response_dict["status"] == "ok" and not has_result:
        raise ContractViolationError("Successful responses must contain result.")
    if response_dict["status"] == "error" and not has_error:
        raise ContractViolationError("Error responses must contain error.")


def assert_contract_completeness(handler_registry: Mapping[str, Any]) -> None:
    manifest = load_operation_manifest()
    operations = require_mapping(manifest.get("operations"), "Operation manifest.operations must be a mapping.")

    if set(operations.keys()) != set(OPERATION_CONTRACTS.keys()):
        raise ContractViolationError("Operation manifest keys must match request contract registry.")
    if set(operations.keys()) != set(RESPONSE_CONTRACTS.keys()):
        raise ContractViolationError("Operation manifest keys must match response contract registry.")
    if set(operations.keys()) != set(handler_registry.keys()):
        raise ContractViolationError("Operation manifest keys must match handler registry.")

    for operation, manifest_entry in operations.items():
        entry = require_mapping(
            manifest_entry,
            f"Operation manifest entry for {operation} must be a mapping.",
        )
        expected_doc, expected_request_schema = OPERATION_CONTRACTS[operation]
        expected_response_schema = RESPONSE_CONTRACTS[operation]

        contract_doc = REPO_ROOT / entry["contract_doc"]
        if contract_doc != expected_doc or not contract_doc.is_file():
            raise ContractViolationError(f"Incomplete operation contract doc for {operation}.")

        request_schema = entry["request_schema"]
        if request_schema != expected_request_schema:
            raise ContractViolationError(f"Request schema mismatch for {operation}.")
        load_schema(request_schema)

        response_schema = entry["response_schema"]
        if response_schema != expected_response_schema:
            raise ContractViolationError(f"Response schema mismatch for {operation}.")
        load_schema(response_schema)

        handler_name = entry["handler"]
        handler = handler_registry.get(operation)
        if handler is None or getattr(handler, "__name__", None) != handler_name:
            raise ContractViolationError(f"Handler registry mismatch for {operation}.")

        test_file = REPO_ROOT / entry["test_file"]
        if not test_file.is_file():
            raise ContractViolationError(f"Missing declared test file for {operation}.")
