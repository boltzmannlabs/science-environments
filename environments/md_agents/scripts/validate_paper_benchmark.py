#!/usr/bin/env python3
"""Validate MD paper benchmark packet structure without claiming reproduction."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    manifest = json.loads((ROOT / "benchmark/paper_manifest.json").read_text())
    results = []
    for case in manifest["cases"]:
        directory = ROOT / case["directory"]
        required = ["README.md", "PAPER_REFERENCE.md", "TASK.md"]
        input_path = ROOT / case["input"]
        result = {
            "case_id": case["id"],
            "status": case["status"],
            "task_files": {name: (directory / name).exists() for name in required},
            "input_exists": input_path.exists(),
            "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest() if input_path.exists() else None,
            "qualification": "REVIEW",
            "anti_overclaim": "A bounded local run is not paper reproduction.",
        }
        results.append(result)
    report = {"manifest": "benchmark/paper_manifest.json", "cases": results}
    out = ROOT / "results/paper_benchmark_preflight.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not all(all(r["task_files"].values()) and r["input_exists"] for r in results):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
