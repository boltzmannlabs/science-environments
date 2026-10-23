#!/usr/bin/env python3
"""Independent deterministic smoke grader for GeoOpt-Bench submissions."""
from __future__ import annotations
import json, sys
from pathlib import Path

REQUIRED = ("task_id", "decision", "checks", "provenance", "cost")

def grade(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED if key not in data]
    checks = data.get("checks", {})
    scientific = ("structure_valid", "energy_finite", "gradient_finite", "convergence_classified")
    failures = missing + [key for key in scientific if checks.get(key) is not True]
    ok = not failures and data.get("decision") in {"accept", "review", "reject"}
    print(json.dumps({"task_id": data.get("task_id"), "score": int(ok), "missing_or_failed": failures}, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(grade(Path(sys.argv[1])))
