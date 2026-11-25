"""Small, shared FEP status and evidence contracts."""

STATUSES = {"PASS", "REVIEW", "FAIL", "UNRESOLVED"}

def qualify(status: str, required_evidence: dict) -> str:
    """Return a conservative status; missing required evidence cannot PASS."""
    if status not in STATUSES:
        raise ValueError(f"unknown status: {status}")
    if status == "PASS" and not all(required_evidence.values()):
        return "REVIEW"
    return status
