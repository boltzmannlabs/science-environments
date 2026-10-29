"""Evidence gate shared by scientific-agent environments.

This module deliberately does not infer scientific validity from a successful
process exit or a parsed input.  Callers provide the evidence required by the
specific environment and task.
"""
from __future__ import annotations

from typing import Any, Iterable


def qualify(
    evidence: dict[str, Any],
    required_evidence: Iterable[str] = (),
    required_checks: Iterable[str] = (),
) -> dict[str, Any]:
    """Return a conservative ``PASS``, ``REVIEW``, or ``FAIL`` decision.

    ``adapter_status`` must be ``PASS`` before scientific evidence is assessed.
    A missing or false required item yields ``REVIEW`` (unless the adapter or
    an explicit scientific check failed, which yields ``FAIL``).  The result
    includes the missing/failed keys so reports remain auditable.
    """
    adapter = evidence.get("adapter_status")
    if adapter != "PASS":
        return {
            "status": "FAIL",
            "reason": "adapter execution failed",
            "missing_evidence": [],
            "failed_checks": ["adapter_status"],
        }

    failed = [key for key in required_checks if evidence.get(key) is False]
    if failed:
        return {
            "status": "FAIL",
            "reason": "required scientific check failed",
            "missing_evidence": [],
            "failed_checks": failed,
        }

    missing = [
        key for key in required_evidence
        if key not in evidence or evidence.get(key) in (None, False, "")
    ]
    if missing or evidence.get("independent_evaluator") is not True:
        if evidence.get("independent_evaluator") is not True:
            missing.append("independent_evaluator")
        return {
            "status": "REVIEW",
            "reason": "scientific evidence is incomplete",
            "missing_evidence": sorted(set(missing)),
            "failed_checks": [],
        }

    return {
        "status": "PASS",
        "reason": "required evidence and independent checks are present",
        "missing_evidence": [],
        "failed_checks": [],
    }
