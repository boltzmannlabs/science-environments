"""Installed, account-free support paths for the portable environment."""
from pathlib import Path


def bundled_workflow_source():
    """Return the executor snapshot without installing a second top-level plugin.

    Active Agent-Scientist profiles may instead configure their existing executor
    source. Do not mix two different loaded ``enzyme_workflow`` implementations.
    """
    return Path(__file__).resolve().parent / "_support" / "enzyme_workflow"
