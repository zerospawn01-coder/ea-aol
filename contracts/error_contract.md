# EA-AOL Error Contract

All public entrypoint failures must be normalized into a contract-valid error envelope.

## Error Object Shape

- `code`: stable machine-facing error code
- `message`: human-readable explanation
- `category`: one of `validation`, `unsupported`, or `internal`
- `retryable`: boolean

## Initial Taxonomy

- `validation_error`
  - category: `validation`
  - retryable: `false`
- `unsupported_operation`
  - category: `unsupported`
  - retryable: `false`
- `internal_error`
  - category: `internal`
  - retryable: `false`

## Fail-Closed Rule

If an error cannot be classified more specifically, it must collapse to `internal_error` rather than leaking an unstructured exception shape.
