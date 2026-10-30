"""Diagnose FEP window failures and plan bounded, non-destructive recovery."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


FAILURE_PATTERNS = (
    ("non_finite_energy", re.compile(r"(?:nan|inf|non[- ]finite)", re.I)),
    ("constraint_failure", re.compile(r"(?:constraint|lincs|shake).*(?:fail|warning|error)", re.I)),
    ("gpu_failure", re.compile(r"(?:gpu|cuda).*(?:out of memory|error|unavailable)", re.I)),
    ("scheduler_interruption", re.compile(r"(?:walltime|scheduler|preempt|cancel)", re.I)),
    ("checkpoint_incompatible", re.compile(r"checkpoint.*(?:mismatch|incompat)", re.I)),
    ("missing_output", re.compile(r"(?:missing|truncated).*(?:trajectory|energy|output)", re.I)),
)


def _first_step(log: str) -> int | None:
    candidates: list[int] = []
    for line in log.splitlines():
        if any(p.search(line) for _, p in FAILURE_PATTERNS):
            match = re.search(r"step\s+(\d+)", line, re.I)
            if match:
                candidates.append(int(match.group(1)))
            elif "fatal" in line.lower() or "error" in line.lower():
                # A fatal line without a step is still actionable, but has no exact step.
                return min(candidates) if candidates else None
    return min(candidates) if candidates else None


def _cause(log: str, samples: list[Any], checkpoint: dict[str, Any]) -> str:
    for name, pattern in FAILURE_PATTERNS:
        if pattern.search(log):
            return name
    if any(x is None or (isinstance(x, float) and not math.isfinite(x)) for x in samples):
        return "non_finite_energy"
    if checkpoint.get("present") and checkpoint.get("valid") is False:
        return "checkpoint_invalid"
    return "unknown_failure"


def diagnose(config: Path, output_dir: Path) -> dict[str, Any]:
    raw = config.read_bytes()
    data = json.loads(raw)
    protocol = data.get("engine", {}).get("protocol_sha256")
    max_retries = int(data.get("retry_policy", {}).get("max_retries", 0))
    cases = []
    for case in data.get("cases", []):
        log = str(case.get("log", ""))
        checkpoint = case.get("checkpoint", {})
        samples = case.get("energy_samples", [])
        cause = _cause(log, samples, checkpoint)
        compatible = bool(checkpoint.get("present") and checkpoint.get("valid") and checkpoint.get("protocol_sha256") == protocol)
        recoverable = compatible and cause in {"constraint_failure", "scheduler_interruption", "gpu_failure"}
        action = "restart_from_last_valid_checkpoint" if recoverable else "stop_no_safe_restart"
        status = "PASS" if recoverable else "FAIL"
        evidence = {
            "first_failure_step": _first_step(log),
            "failure_cause": cause,
            "checkpoint_present": bool(checkpoint.get("present")),
            "checkpoint_valid": bool(checkpoint.get("valid")),
            "checkpoint_protocol_matches": compatible,
            "finite_energy_samples": all(isinstance(x, (int, float)) and math.isfinite(float(x)) for x in samples),
            "trajectory_frames": case.get("trajectory_frames", 0),
        }
        cases.append({
            "case_id": case.get("case_id"), "window": case.get("window"), "replica": case.get("replica"),
            "status": status, "failure_cause": cause, "first_failure_step": evidence["first_failure_step"],
            "allowed_action": action, "retry_limit": max_retries if recoverable else 0,
            "evidence": evidence,
            "original_input_preserved": True,
        })
    result = {
        "task_id": data.get("task_id"), "status": "PASS" if all(c["status"] == "PASS" for c in cases) else "REVIEW",
        "engine": data.get("engine"), "input_sha256": hashlib.sha256(raw).hexdigest(),
        "max_retries": max_retries, "cases": cases,
        "scientific_scope": "diagnosis and bounded restart planning; restarted production sampling is not claimed",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "failure_report.json").write_text(json.dumps(result, indent=2) + "\n")
    plans = [{"case_id": c["case_id"], "action": c["allowed_action"], "retry_limit": c["retry_limit"], "rollback": "original immutable input"} for c in cases]
    (output_dir / "recovery_plan.json").write_text(json.dumps({"task_id": result["task_id"], "plans": plans}, indent=2) + "\n")
    history = [{"case_id": c["case_id"], "attempt": 0, "action": c["allowed_action"], "status": "planned", "input_sha256": result["input_sha256"]} for c in cases]
    (output_dir / "recovery_history.jsonl").write_text("".join(json.dumps(x) + "\n" for x in history))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(diagnose(args.config, args.output_dir), indent=2))
