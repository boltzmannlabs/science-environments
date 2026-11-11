"""Human-readable report generation for paper-task evidence."""
from __future__ import annotations

def markdown_summary(task_id: str, summary: dict) -> str:
    return (
        f"# {task_id} setup assessment\n\n"
        "This report assesses paper-to-environment setup, not production FEP.\n\n"
        f"- Reference: **{summary['reference']}**\n"
        f"- Agent setup: **{summary['agent']}**\n"
        f"- Alternative: **{summary['alternative']}**\n"
        f"- Perturbed case: **{summary['perturbed']}**\n"
        f"- Scientific qualification: **{summary['scientific_qualification']}**\n"
    )
