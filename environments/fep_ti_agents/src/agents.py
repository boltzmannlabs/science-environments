"""FEP specialist selection and auditable tool-event helpers.

This module records deterministic orchestration decisions. It does not claim
that a language model autonomously executed a scientific workflow.
"""
from __future__ import annotations
from datetime import datetime, timezone

SPECIALIST_ROLES = {
    "FEP-AG01": "mapping",
    "FEP-AG02": "transformation_feasibility",
    "FEP-AG03": "parameterization",
    "FEP-AG04": "lambda_schedule",
    "FEP-AG05": "system_preparation",
    "FEP-AG15": "independent_qualification",
}

def select_setup_roles() -> list[str]:
    """Select roles required for endpoint setup and independent review."""
    return ["FEP-AG01", "FEP-AG02", "FEP-AG03", "FEP-AG05", "FEP-AG15"]

def tool_event(agent_role: str, command: str, outputs: list[str]) -> dict:
    """Create a serializable execution event for a real local tool call."""
    if agent_role not in SPECIALIST_ROLES:
        raise ValueError(f"unknown role: {agent_role}")
    return {
        "agent_role": agent_role,
        "command": command,
        "outputs": outputs,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "deterministic_specialist_harness",
    }
