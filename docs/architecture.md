# EA-AOL Architecture Notes

This repository starts with a four-layer boundary:

- `docs/`: human-facing explanation and architectural context
- `contracts/`: explicit system-facing agreements and invariants
- `src/`: implementation that is expected to honor those agreements
- `tests/`: verification that the contracts remain true

## Initial Architectural Rule

The implementation layer should not be the first place where project meaning is defined. The repository must be understandable from `README.md`, `docs/`, and `contracts/` before the codebase grows.

## Near-Term Direction

1. Define a concrete runtime or compiler entrypoint in `src/`.
2. Expand `contracts/system_contract.md` into executable constraints where possible.
3. Keep `tests/` focused on contract preservation before broad feature coverage.
