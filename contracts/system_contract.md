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

The bootstrap contract supports exactly one operation:

- `describe-runtime-surface`

The canonical operation contract lives in:

- `contracts/operations/describe_runtime_surface.md`

The machine-readable schemas live in:

- `contracts/schemas/operation.schema.json`
- `contracts/schemas/describe_runtime_surface.schema.json`

### Output

On success, `run_entrypoint` returns a mapping with:

- `ok`: `true`
- `operation`: echoed operation name
- `surface`: structured runtime surface description

The `surface` object must contain:

- `project`
- `status`
- `contract`
- `supported_operations`

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

### Non-goals

- Executing real EA-AOL runtime work
- Accepting multiple operation types before the contract is expanded
- Auto-correcting malformed requests

## Initial Validation Contract

The repository must retain tests that check:

- the expected top-level directories exist
- the contract document is present
- operation-level contract documents are present
- machine-readable schemas are present
- the implementation entrypoint can be imported
- valid requests succeed
- malformed requests fail closed
- unsupported operations fail closed
