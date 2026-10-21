from __future__ import annotations

from typing import Any, Mapping


DISPLAY_METRICS = (
    ("Valid completion rate", "valid_completion_rate"),
    ("Median reference-energy error (Ha)", "median_reference_error_hartree"),
    ("Recovery success rate", "recovery_success_rate"),
    ("Safe terminal-failure handling", "safe_failure_handling_rate"),
    ("Median runtime (s)", "median_runtime_seconds"),
    ("Compute seconds per valid result", "compute_seconds_per_valid_result"),
    ("Held-out cases passed", "held_out_cases_passed"),
    ("SPE backend-call count", "tool_call_count"),
    ("Recovery decision count", "decision_call_count"),
    ("Agent API-call count", "agent_api_call_count"),
    ("Agent total tokens", "agent_total_tokens"),
    ("Agent-reported estimated cost (USD)", "agent_reported_estimated_cost_usd"),
    ("Decision quality", "decision_quality"),
)


def markdown_report(
    metrics: Mapping[str, Mapping[str, Any]],
    *,
    benchmark_id: str,
    reference_scope: str,
    run_status: str,
) -> str:
    approaches = (
        "fixed",
        "agent-scientist",
        "agent-scientist-plus-specialist",
    )
    labels = {
        "fixed": "Fixed SPE workflow",
        "agent-scientist": "Agent Scientist",
        "agent-scientist-plus-specialist": "Agent + SPE specialist",
    }
    lines = [
        f"# {benchmark_id}",
        "",
        f"Run status: **{run_status}**",
        "",
        f"Reference scope: {reference_scope}",
        "",
        "| Metric | " + " | ".join(labels[item] for item in approaches) + " |",
        "|---|---:|---:|---:|",
    ]
    for display, key in DISPLAY_METRICS:
        values = [_format(metrics.get(approach, {}).get(key)) for approach in approaches]
        lines.append(f"| {display} | " + " | ".join(values) + " |")
    lines.extend(
        [
            "",
            "Only measured values are shown. `not measured` means that approach was not executed in this run.",
            "Reference errors in this reliability track compare identical Boltzmann SPE settings against frozen regression outputs; they are not independent absolute-accuracy claims.",
            "A reported agent cost of zero is not a claim of free execution when the saved usage record has `cost_source=none`; it means the launcher supplied no priced cost estimate.",
        ]
    )
    return "\n".join(lines) + "\n"


def _format(value: Any) -> str:
    if value is None:
        return "not measured"
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)
