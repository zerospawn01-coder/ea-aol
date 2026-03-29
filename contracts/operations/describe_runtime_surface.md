# Operation Contract: `describe-runtime-surface`

## Responsibility

Return the bootstrap runtime surface without performing side effects.

## Input

- `operation`: must equal `describe-runtime-surface`
- `payload`: must be an empty mapping

## Output

On success, return:

- `ok`: `true`
- `operation`: `describe-runtime-surface`
- `surface`: object containing:
  - `project`
  - `status`
  - `contract`
  - `supported_operations`

## Failure Conditions

Reject when:

- `operation` is different from `describe-runtime-surface`
- `payload` is missing
- `payload` is not a mapping
- `payload` contains any keys

## Fail-Closed Rule

If the request does not match the documented contract exactly, stop with an explicit contract violation instead of attempting recovery.
