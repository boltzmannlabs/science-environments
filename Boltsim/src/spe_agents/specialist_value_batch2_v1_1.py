"""Corrected Batch 2 v1.1 evaluator with predeclared semantic alternatives."""

from __future__ import annotations

from typing import Any, Mapping

from .specialist_value_v1_1 import evaluate as evaluate_base


def evaluate(run: Mapping[str, Any], reference: Mapping[str, Any], tolerance: float) -> dict[str, Any]:
    """Evaluate required fields, optional diagnostics, and explicitly allowed withholding."""
    result = evaluate_base(run, reference, tolerance)
    response = run["response"]
    findings = list(result["findings"])
    if reference.get("allow_withheld_values") and response.get("disposition") == "review":
        allowed_missing = {str(item) for item in reference.get("withheld_value_keys", [])}
        findings = [
            item for item in findings
            if not any(item.startswith(f"missing value: {key}") for key in allowed_missing)
            and not item.startswith("bsse_status: expected")
        ]
    if reference.get("allow_conservative_review") and response.get("disposition") == "review":
        expected_disposition = reference.get("disposition")
        if expected_disposition == "accept":
            findings = [item for item in findings if not item.startswith("disposition: expected")]
            findings = [
                item for item in findings
                if not item.startswith("missing value:")
            ]
    return {"passed": not findings, "findings": findings}
