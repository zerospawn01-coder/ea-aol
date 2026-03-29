# Operation Contract: `list-supported-operations`

## Responsibility

Return the currently supported operation names without executing any project-specific work.

## Input

- `operation`: must equal `list-supported-operations`
- `payload`: must be an empty mapping

## Output

On success, return:

- `ok`: `true`
- `operation`: `list-supported-operations`
- `payload`: empty mapping
- `operations`: ordered list of supported operation names

## Failure Conditions

Reject when:

- `operation` is different from `list-supported-operations`
- `payload` is missing
- `payload` is not a mapping
- `payload` contains any keys

## Fail-Closed Rule

If the request does not match the documented contract exactly, stop with an explicit contract violation instead of attempting recovery.
