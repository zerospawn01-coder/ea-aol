# Operation Contract: `normalize-module-definition`

## Responsibility

Validate and normalize an EA-AOL module definition so runtime, compiler, or tooling surfaces can consume a deterministic module descriptor.

## Input

- `operation`: must equal `normalize-module-definition`
- `payload`: mapping with:
  - `module_definition`: mapping containing:
    - `name`: non-empty string
    - `kind`: one of `runtime`, `compiler`, `tooling`
    - `capabilities`: array of non-empty strings
    - `entrypoint`: mapping containing:
      - `module`: non-empty string
      - `callable`: non-empty string

## Output

On success, return:

- `status`: `ok`
- `operation`: `normalize-module-definition`
- `result.normalized_module`: normalized module definition containing:
  - `name`
  - `kind`
  - `capabilities`: trimmed, sorted unique capability names
  - `entrypoint.module`
  - `entrypoint.callable`
- `result.ready_for_runtime_registration`: boolean

## Canonicalization Invariants

- leading and trailing whitespace is removed from `name`, capability names, `entrypoint.module`, and `entrypoint.callable`
- `capabilities` is deduplicated and sorted lexicographically after trimming
- no implicit defaults are added
- `ready_for_runtime_registration` is `true` only when at least one capability remains after normalization
- fields that normalize to an empty string are rejected rather than preserved

## Failure Conditions

Reject when:

- `payload.module_definition` is missing
- `payload.module_definition` is not a mapping
- `kind` is outside the supported EA-AOL module kinds
- `capabilities` contains non-string values
- `entrypoint` is missing required fields
- any required string normalizes to an empty value
- unexpected fields appear anywhere in the payload contract

## Fail-Closed Rule

If the module definition does not satisfy the documented contract exactly, return a contract-valid error response rather than inferring defaults or registering a partial module.
