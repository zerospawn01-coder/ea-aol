# EA-AOL System Contract

## Repository Contract

This repository exists to hold EA-AOL-specific system design and implementation work. Anything that cannot justify itself as part of that boundary should live elsewhere.

## Initial Invariants

1. `docs/` explains the project in human terms.
2. `contracts/` defines the system boundary and fail-closed assumptions.
3. `src/` contains implementation code rather than repository policy.
4. `tests/` verifies that the documented boundary still exists.

## Fail-Closed Rule

If a new addition cannot be placed clearly into one of these layers, it should not be added until its role is explicit.

## Entrypoint Contract

The initial runtime surface is `src.entrypoint.run_entrypoint`.

### Responsibility

- Accept a single request object.
- Resolve the requested operation against the documented operation set.
- Validate whether the request matches the supported bootstrap contract and schema.
- Return a structured success result for valid input.
- Reject unsupported or malformed input explicitly instead of guessing.

### Input

`run_entrypoint` accepts a mapping with these required fields:

- `operation`: bootstrap operation selector
- `payload`: operation-specific data

### Supported Operation

The bootstrap contract currently supports these operations:

- `describe-runtime-surface`
- `list-supported-operations`
- `validate-request-envelope`
- `normalize-module-definition`

The canonical operation contract lives in:

- `contracts/operations/describe_runtime_surface.md`
- `contracts/operations/list_supported_operations.md`
- `contracts/operations/validate_request_envelope.md`
- `contracts/operations/normalize_module_definition.md`

The machine-readable schemas live in:

- `contracts/operation_manifest.json`
- `contracts/schemas/operation.schema.json`
- `contracts/schemas/response_envelope.schema.json`
- `contracts/schemas/error.schema.json`
- `contracts/schemas/describe_runtime_surface.schema.json`
- `contracts/schemas/describe_runtime_surface.response.schema.json`
- `contracts/schemas/list_supported_operations.schema.json`
- `contracts/schemas/list_supported_operations.response.schema.json`
- `contracts/schemas/validate_request_envelope.schema.json`
- `contracts/schemas/validate_request_envelope.response.schema.json`
- `contracts/schemas/normalize_module_definition.schema.json`
- `contracts/schemas/normalize_module_definition.response.schema.json`

### Output

Every entrypoint call must return a response envelope with:

- `status`
- `operation`: echoed operation name
- `contract_version`
- exactly one of `result` or `error`

Successful calls return `status: "ok"` and a `result` object validated against the operation-specific response schema.

### Error Contract

Error responses return `status: "error"` and an `error` object with:

- `code`
- `message`
- `category`
- `retryable`

The bootstrap taxonomy currently distinguishes:

- `validation_error`
- `unsupported_operation`
- `internal_error`

### Operation Response Requirements

For `describe-runtime-surface`, the result object must contain:

- `project`
- `status`
- `contract`
- `supported_operations`

For `list-supported-operations`, the result object must contain:

- `operations`

For `validate-request-envelope`, the result object must contain:

- `valid`
- `normalized_request`

For `normalize-module-definition`, the result object must contain:

- `normalized_module`
- `ready_for_runtime_registration`

### Failure Conditions

The entrypoint must reject requests when:

- the input is not a mapping
- `operation` is missing
- `operation` is not a string
- `payload` is missing
- `payload` is not a mapping
- `operation` is not supported
- `payload` violates the supported operation contract

### Fail-Closed Behavior

All unsupported, malformed, or not-yet-implemented requests must stop with an explicit exception.
The bootstrap runtime must not infer missing fields, silently coerce invalid values, or continue on unknown operations.
The entrypoint must only dispatch operations that are documented and schema-backed.
If a handler or normalizer fails unexpectedly, the runtime must still return a contract-valid `internal_error` envelope.
If an operation is partially added but missing its contract document, schema, registry entry, or declared test file, the completeness check must reject the runtime before dispatch.

### Non-goals

- Executing real EA-AOL runtime work
- Accepting multiple operation types before the contract is expanded
- Auto-correcting malformed requests

## Initial Validation Contract

The repository must retain tests that check:

- the expected top-level directories exist
- the contract document is present
- the error contract document is present
- operation-level contract documents are present
- machine-readable schemas are present
- the implementation entrypoint can be imported
- valid requests succeed
- malformed requests fail closed with the error envelope shape intact
- unsupported operations fail closed with the error envelope shape intact
