# EA-AOL

`ea-aol` is a standalone design and implementation repository for the EA-AOL runtime and language/tooling direction. It should be treated as an independent systems project, not as a catch-all experiment bucket, so its specifications, runtime assumptions, compiler surface, and demonstrations can be defined on their own terms.

## Scope

- Primary: runtime, compiler, specification, and demo assets for the EA-AOL project.
- Includes: language or runtime implementation work that directly defines EA-AOL.
- Excludes: unrelated research experiments, generic governance manuals, and mixed-project scratch work.

## Non-goals

- Acting as overflow storage for experiments that do not yet have a stable project identity.
- Mixing in cross-repository process knowledge better kept in `project-manuals`.
- Remaining a README-only shell after the project boundary has been defined.

## Inputs

- Project-specific specifications and design decisions.
- Runtime or compiler implementation work.
- Minimal demos or examples that prove the project boundary is real.

## Outputs

- A self-contained systems repository with its own architecture and runnable surfaces.
- Documentation that explains what EA-AOL is without relying on outside repo context.
- A clear path toward `src/`, `docs/`, and `tests/` or equivalent project-native structure.

## Validation

- `python -m unittest tests.test_contract_smoke -v`

## Promotion Path

- Inbound: work only when it directly defines the EA-AOL project boundary.
- Outbound: generic experiments belong in `lab-experiments`; shared procedure belongs in `project-manuals`.
- Repository role: independent project repository with explicit project-scoped maintenance.

## Initial Layout

- `docs/`: human-readable overview and architecture decisions.
- `contracts/`: repository-level contracts, invariants, and fail-closed boundaries.
- `src/`: implementation entrypoints and project code.
- `tests/`: contract smoke tests and early regression coverage.
