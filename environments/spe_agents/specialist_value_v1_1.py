"""Scientifically corrected Batch 1 v1.1 evaluator."""

from __future__ import annotations

from typing import Any, Mapping

from .specialist_value import evaluate as evaluate_v1


def evaluate(
    run: Mapping[str, Any], reference: Mapping[str, Any], tolerance: float
) -> dict[str, Any]:
    """Score required warnings while permitting only predeclared optional warnings."""
    result = evaluate_v1(run, reference, tolerance)
    findings = [
        item for item in result["findings"] if not item.startswith("warning_codes:")
    ]
    response = run["response"]
    actual_value = response.get("warning_codes")
    if not isinstance(actual_value, list) or not all(
        isinstance(item, str) for item in actual_value
    ):
        findings.append("warning_codes must be an array of strings")
    else:
        actual = set(actual_value)
        required = set(reference.get("warning_codes", []))
        optional = set(reference.get("optional_warning_codes", []))
        missing = sorted(required - actual)
        unexpected = sorted(actual - required - optional)
        if missing:
            findings.append(f"missing required warning codes: {missing!r}")
        if unexpected:
            findings.append(f"unexpected warning codes: {unexpected!r}")
    return {"passed": not findings, "findings": findings}
