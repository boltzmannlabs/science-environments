"""Agent-facing dispatch. Runtime configuration is read for the current profile."""

import json
import sqlite3

from .common import WorkflowError
from .harness import Harness


def dispatch(name, args, *, config=None, authorized=None):
    if authorized is not None and not authorized():
        return json.dumps({"authorization_required": True, "error": "Authorize Boltzmann for this profile using /Add_boltz"})
    try:
        settings = config() if config is not None else {}
        harness = Harness(bindings=settings.get("bindings"), extensions=settings.get("contracts"))
        method = name.removeprefix("enzyme_workflow_")
        if method == "catalog":
            result = {"tools": harness.registry, "remote_execution": "existing Boltzmann connector only"}
        elif method in {"start", "next", "status", "report"}:
            result = getattr(harness, method)(**args)
        else:
            raise WorkflowError("Unknown enzyme workflow operation")
        return json.dumps(result, allow_nan=False)
    except (WorkflowError, OSError, TypeError, KeyError, ValueError, sqlite3.Error) as exc:
        # Scientific errors are deliberately actionable, but raw filesystem /
        # JSON parse exceptions can contain user data. Do not echo those.
        message = str(exc) if isinstance(exc, WorkflowError) else "Workflow operation failed. Check the supplied schema, local artifact permissions and profile state."
        return json.dumps({"error": message, "remote_submission_performed": False})
