"""Minimal entrypoint stub for the EA-AOL project boundary."""


def describe_runtime_surface() -> dict[str, str]:
    """Return the initial project surface in a machine-readable form."""

    return {
        "project": "ea-aol",
        "status": "bootstrap",
        "contract": "contracts/system_contract.md",
    }
