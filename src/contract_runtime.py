"""Helpers for schema-backed bootstrap contract validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "contracts"
SCHEMA_ROOT = CONTRACT_ROOT / "schemas"
OPERATION_ROOT = CONTRACT_ROOT / "operations"


class ContractViolationError(ValueError):
    """Raised when a request violates the repository contract."""


def load_schema(schema_name: str) -> dict[str, Any]:
    schema_path = SCHEMA_ROOT / schema_name
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
    operation_docs = {
        "describe-runtime-surface": (
            OPERATION_ROOT / "describe_runtime_surface.md",
            "describe_runtime_surface.schema.json",
        )
    }

    if operation not in operation_docs:
        raise ContractViolationError(f"Unsupported operation: {operation}")

    operation_doc, schema_name = operation_docs[operation]
    if not operation_doc.is_file():
        raise ContractViolationError(f"Missing operation contract: {operation_doc}")

    schema = load_schema(schema_name)
    if schema.get("type") != "object":
        raise ContractViolationError(f"Unsupported payload schema type for operation: {operation}")

    if schema.get("additionalProperties") is False and payload:
        raise ContractViolationError(
            "Operation 'describe-runtime-surface' does not accept payload fields."
        )

    return dict(payload)
