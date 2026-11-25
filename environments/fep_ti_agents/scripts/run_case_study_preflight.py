#!/usr/bin/env python3
"""Run conservative readiness checks for every FEP case study."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "benchmark/case_studies/catalogue.json"

def main() -> dict:
    data = json.loads(CATALOGUE.read_text())
    results = []
    for case in data["case_studies"]:
        directory = ROOT / "case_studies" / case["id"]
        required = ["TASK.md", "PAPER_REFERENCE.md", "README.md"]
        structure_ready = all((directory / name).exists() for name in required)
        canonical = case.get("canonical_task")
        canonical_ready = bool(canonical and (ROOT / canonical).exists())
        if case["status"] == "CATALOGUED":
            result = {
                "case_id": case["id"],
                "status": "CATALOGUED",
                "task_structure": structure_ready,
                "reference_ready": False,
                "execution": "NOT_RUN",
                "missing": ["frozen molecular inputs", "published computational reference metrics", "case-specific tests"]
            }
        else:
            result = {
                "case_id": case["id"],
                "status": case["status"],
                "task_structure": structure_ready,
                "canonical_task": canonical,
                "canonical_task_available": canonical_ready,
                "execution": "DELEGATED_TO_CANONICAL_TASK"
            }
        out = directory / "evaluation/preflight.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result, indent=2) + "\n")
        results.append(result)
    report = {"catalogue": str(CATALOGUE.relative_to(ROOT)), "cases": results,
              "anti_overclaim": "Preflight readiness is not production FEP execution."}
    (ROOT / "results/case_study_preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    main()
