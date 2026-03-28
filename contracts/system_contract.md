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

## Initial Validation Contract

The repository must retain at least one smoke test that checks:

- the expected top-level directories exist
- the contract document is present
- the implementation entrypoint can be imported
