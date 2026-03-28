# Operation Contract: `validate-request-envelope`

## Responsibility

Validate a candidate request envelope using the shared request contract and return the normalized result without dispatching it.

## Input

- `operation`: must equal `validate-request-envelope`
- `payload`: mapping with:
  - `candidate_request`: mapping to be validated as an EA-AOL request envelope

## Output

On success, return:

- `status`: `ok`
- `operation`: `validate-request-envelope`
- `result.valid`: `true`
- `result.normalized_request`: normalized request envelope containing:
  - `operation`
  - `payload`

## Failure Conditions

Reject when:

- `payload.candidate_request` is missing
- `payload.candidate_request` is not a mapping
- the candidate envelope violates the shared request contract

## Fail-Closed Rule

If the candidate request cannot be validated exactly, return a contract-valid error response rather than an inferred or partially normalized success response.
