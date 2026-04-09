"""Fail-closed CI gates for EA-AOL."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from src.contract_runtime import (  # noqa: E402
    CONTRACT_ROOT,
    OPERATION_ROOT,
    RESPONSE_CONTRACTS,
    SCHEMA_ROOT,
    ContractViolationError,
    assert_contract_completeness,
    load_operation_manifest,
    load_schema,
    validate_response_envelope,
)
from src.entrypoint import HANDLERS, run_entrypoint  # noqa: E402


class GateFailure(RuntimeError):
    """Raised when a CI gate must fail closed."""

    def __init__(
        self,
        gate: str,
        violation_type: str,
        reason: str,
        file: str | None = None,
        violation_id: str | None = None,
    ) -> None:
        super().__init__(reason)
        self.gate = gate
        self.violation_type = violation_type
        self.reason = reason
        self.file = file
        self.violation_id = violation_id or gate


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _pass(gate: str, details: dict[str, Any] | None = None) -> int:
    payload = {"gate": gate, "status": "PASS"}
    if details:
        payload["details"] = details
    _emit(payload)
    return 0


def _fail(gate: str, error: GateFailure) -> int:
    _emit(
        {
            "gate": gate,
            "status": "FAIL",
            "violations": [
                {
                    "type": error.violation_type,
                    "id": error.violation_id,
                    "file": error.file or "",
                    "reason": error.reason,
                }
            ],
        }
    )
    return 1


def _sample_module_definition() -> dict[str, Any]:
    return {
        "name": "runtime.bootstrap",
        "kind": "runtime",
        "capabilities": ["contracts", "dispatch"],
        "entrypoint": {
            "module": "src.entrypoint",
            "callable": "run_entrypoint",
        },
    }


def _sample_request_for_operation(operation: str) -> dict[str, Any]:
    if operation == "describe-runtime-surface":
        return {"operation": operation, "payload": {}}
    if operation == "list-supported-operations":
        return {"operation": operation, "payload": {}}
    if operation == "validate-request-envelope":
        return {
            "operation": operation,
            "payload": {
                "candidate_request": {
                    "operation": "list-supported-operations",
                    "payload": {},
                }
            },
        }
    if operation in {
        "normalize-module-definition",
        "validate-module-definition",
        "describe-module-surface",
    }:
        return {
            "operation": operation,
            "payload": {"module_definition": _sample_module_definition()},
        }
    raise GateFailure(
        gate="validate-response-contract",
        violation_type="RESPONSE_CONTRACT_VIOLATION",
        violation_id=operation,
        file=str(CONTRACT_ROOT / "operation_manifest.json"),
        reason=f"No representative request is defined for operation: {operation}",
    )


def _validate_manifest_shape() -> dict[str, Any]:
    manifest = load_operation_manifest()
    operations = manifest.get("operations")
    if not isinstance(operations, dict) or not operations:
        raise GateFailure(
            gate="validate-schema",
            violation_type="SCHEMA_VIOLATION",
            violation_id="operation-manifest",
            file=str(CONTRACT_ROOT / "operation_manifest.json"),
            reason="Operation manifest must declare at least one operation mapping.",
        )
    return manifest


def run_validate_schema() -> int:
    gate = "validate-schema"
    try:
        manifest = _validate_manifest_shape()
        load_schema("operation.schema.json")
        load_schema("response_envelope.schema.json")
        load_schema("error.schema.json")
        for operation, entry in manifest["operations"].items():
            load_schema(entry["request_schema"])
            load_schema(entry["response_schema"])
        return _pass(gate, {"operations": sorted(manifest["operations"].keys())})
    except FileNotFoundError as error:
        return _fail(
            gate,
            GateFailure(
                gate=gate,
                violation_type="SCHEMA_VIOLATION",
                violation_id="missing-schema",
                file=str(error.filename or ""),
                reason=str(error),
            ),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ContractViolationError) as error:
        return _fail(
            gate,
            GateFailure(
                gate=gate,
                violation_type="SCHEMA_VIOLATION",
                violation_id="schema-load",
                file=str(CONTRACT_ROOT / "operation_manifest.json"),
                reason=str(error),
            ),
        )


def run_validate_completeness() -> int:
    gate = "validate-completeness"
    try:
        assert_contract_completeness(HANDLERS)
        return _pass(gate, {"handlers": sorted(HANDLERS.keys())})
    except ContractViolationError as error:
        return _fail(
            gate,
            GateFailure(
                gate=gate,
                violation_type="COMPLETENESS_VIOLATION",
                violation_id="operation-completeness",
                file=str(CONTRACT_ROOT / "operation_manifest.json"),
                reason=str(error),
            ),
        )


def run_validate_response_contract() -> int:
    gate = "validate-response-contract"
    try:
        manifest = _validate_manifest_shape()
        validated_operations: list[str] = []
        for operation in manifest["operations"].keys():
            request = _sample_request_for_operation(operation)
            response = run_entrypoint(request)
            validate_response_envelope(response)
            if response["status"] != "ok":
                raise GateFailure(
                    gate=gate,
                    violation_type="RESPONSE_CONTRACT_VIOLATION",
                    violation_id=request["operation"],
                    file=str(REPO_ROOT / "src" / "entrypoint.py"),
                    reason=f"Representative request for {request['operation']} did not succeed.",
                )
            validated_operations.append(request["operation"])

        failure = run_entrypoint({"payload": {}})
        validate_response_envelope(failure)
        if failure["status"] != "error" or failure["error"]["code"] != "validation_error":
            raise GateFailure(
                gate=gate,
                violation_type="RESPONSE_CONTRACT_VIOLATION",
                violation_id="error-envelope",
                file=str(REPO_ROOT / "src" / "entrypoint.py"),
                reason="Validation failure did not normalize into the expected error envelope.",
            )
        return _pass(gate, {"operations": validated_operations})
    except GateFailure as error:
        return _fail(gate, error)
    except ContractViolationError as error:
        return _fail(
            gate,
            GateFailure(
                gate=gate,
                violation_type="RESPONSE_CONTRACT_VIOLATION",
                violation_id="response-envelope",
                file=str(SCHEMA_ROOT / "response_envelope.schema.json"),
                reason=str(error),
            ),
        )


def _assert_no_orphan_operation_artifacts(manifest: dict[str, Any]) -> None:
    declared_docs = {
        (REPO_ROOT / entry["contract_doc"]).resolve()
        for entry in manifest["operations"].values()
    }
    actual_docs = {path.resolve() for path in OPERATION_ROOT.glob("*.md")}
    if declared_docs != actual_docs:
        raise GateFailure(
            gate="validate-governance",
            violation_type="GOVERNANCE_VIOLATION",
            violation_id="operation-doc-set",
            file=str(OPERATION_ROOT),
            reason="Operation contracts on disk must exactly match the manifest.",
        )

    declared_schemas = {
        (SCHEMA_ROOT / entry["request_schema"]).resolve()
        for entry in manifest["operations"].values()
    } | {
        (SCHEMA_ROOT / entry["response_schema"]).resolve()
        for entry in manifest["operations"].values()
    } | {
        (SCHEMA_ROOT / "operation.schema.json").resolve(),
        (SCHEMA_ROOT / "response_envelope.schema.json").resolve(),
        (SCHEMA_ROOT / "error.schema.json").resolve(),
    }
    actual_schemas = {path.resolve() for path in SCHEMA_ROOT.glob("*.json")}
    if declared_schemas != actual_schemas:
        raise GateFailure(
            gate="validate-governance",
            violation_type="GOVERNANCE_VIOLATION",
            violation_id="schema-set",
            file=str(SCHEMA_ROOT),
            reason="Schema files on disk must exactly match manifest-declared request/response contracts.",
        )


def run_validate_governance() -> int:
    gate = "validate-governance"
    try:
        manifest = _validate_manifest_shape()
        if manifest.get("contract_version") != "ea-aol/0.1":
            raise GateFailure(
                gate=gate,
                violation_type="GOVERNANCE_VIOLATION",
                violation_id="contract-version",
                file=str(CONTRACT_ROOT / "operation_manifest.json"),
                reason="Operation manifest contract_version must match the runtime contract version.",
            )
        _assert_no_orphan_operation_artifacts(manifest)
        if set(manifest["operations"].keys()) != set(RESPONSE_CONTRACTS.keys()):
            raise GateFailure(
                gate=gate,
                violation_type="GOVERNANCE_VIOLATION",
                violation_id="operation-registry",
                file=str(CONTRACT_ROOT / "operation_manifest.json"),
                reason="Operation manifest keys must match the runtime response contract registry.",
            )
        return _pass(gate, {"operations": sorted(manifest["operations"].keys())})
    except GateFailure as error:
        return _fail(gate, error)


def run_unit_tests() -> int:
    gate = "unit-tests"
    command = [
        sys.executable,
        "-m",
        "unittest",
        "tests.test_contract_smoke",
        "tests.test_entrypoint_contract",
        "tests.test_ci_gate",
        "-v",
    ]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        reason = (completed.stdout + "\n" + completed.stderr).strip()
        return _fail(
            gate,
            GateFailure(
                gate=gate,
                violation_type="TEST_FAILURE",
                violation_id="unittest",
                file="tests/",
                reason=reason or "Unit tests failed.",
            ),
        )
    return _pass(gate, {"command": " ".join(command[1:])})


GATES = {
    "validate-schema": run_validate_schema,
    "validate-completeness": run_validate_completeness,
    "validate-response-contract": run_validate_response_contract,
    "validate-governance": run_validate_governance,
    "unit-tests": run_unit_tests,
}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in GATES:
        print("Usage: python tools/ci_gate.py <gate>", file=sys.stderr)
        print("Available gates:", ", ".join(sorted(GATES.keys())), file=sys.stderr)
        return 2
    gate = argv[1]
    try:
        return GATES[gate]()
    except GateFailure as error:
        return _fail(gate, error)
    except Exception as error:
        return _fail(
            gate,
            GateFailure(
                gate=gate,
                violation_type="INTERNAL_CI_ERROR",
                violation_id=gate,
                reason=str(error) or "Unexpected CI gate failure.",
            ),
        )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
