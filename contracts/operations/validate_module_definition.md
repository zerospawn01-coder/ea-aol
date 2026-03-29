# Operation Contract: `validate-module-definition`

## Responsibility

Validate an EA-AOL module definition against the canonical module descriptor contract and return the normalized descriptor without implying runtime registration.

## Input

- `operation`: must equal `validate-module-definition`
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
- `operation`: `validate-module-definition`
- `result.valid`: `true`
- `result.normalized_module`: canonical module definition containing:
  - `name`
  - `kind`
  - `capabilities`
  - `entrypoint.module`
  - `entrypoint.callable`

## Failure Conditions

Reject when:

- `payload.module_definition` is missing
- any required field is missing
- any field normalizes to an empty string
- `kind` is outside the supported EA-AOL module kinds
- unexpected fields appear anywhere in the payload contract

## Fail-Closed Rule

If the module definition cannot be normalized into a canonical EA-AOL module descriptor, return a contract-valid error response rather than a partial validation result.
