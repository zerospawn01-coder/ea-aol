# Operation Contract: `describe-module-surface`

## Responsibility

Extract a stable external surface from a canonical EA-AOL module descriptor so runtime or tooling callers can inspect the module boundary without reinterpreting the raw descriptor.

## Input

- `operation`: must equal `describe-module-surface`
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
- `operation`: `describe-module-surface`
- `result.module_surface`: mapping containing:
  - `module_key`: `<kind>:<name>`
  - `kind`
  - `name`
  - `entrypoint_ref`: `<module>:<callable>`
  - `capability_count`
  - `capability_surface`: sorted capability names
  - `ready_for_runtime_registration`

## Surface Invariants

- surface extraction must use the same canonicalization boundary as `normalize-module-definition` and `validate-module-definition`
- `module_key` is derived only from canonical `kind` and canonical `name`
- `entrypoint_ref` is derived only from canonical entrypoint fields
- `capability_surface` preserves canonical ordering and uniqueness
- `capability_count` equals the length of `capability_surface`

## Failure Conditions

Reject when:

- `payload.module_definition` is missing
- the module definition cannot be canonicalized
- unexpected fields appear anywhere in the payload contract

## Fail-Closed Rule

If a caller provides a descriptor that cannot be canonicalized exactly, return a contract-valid error response rather than a partial or inferred module surface.
