#!/usr/bin/env python3
"""Evaluate paper-derived environment construction matrices locally."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = [
    ROOT / "environments/md_paper_reproduction/tasks/md_paper_001",
    ROOT / "environments/fep_paper_reproduction/tasks/fep_paper_001",
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def evaluate(task: Path) -> dict:
    manifest = json.loads((task / "inputs/input_manifest.json").read_text())
    ref = json.loads((task / "reference/extracted_parameters.json").read_text())
    records = []
    for config in sorted((task / "configs").glob("config_*.json")):
        data = json.loads(config.read_text())
        errors = []
        if config.name == "config_D_perturbed.json":
            if task.name == "md_paper_001" and data.get("timestep_fs", 0) > 2:
                errors.append("timestep deviates from reported 2 fs")
            if task.name == "fep_paper_001" and ("solvent" not in data.get("legs", []) or "missing" in data.get("mapping", "")):
                errors.append("invalid FEP legs or atom mapping")
        status = "FAIL" if errors else "REVIEW"
        records.append({"config": config.name, "status": status, "errors": errors,
                        "parameters": data, "reference_keys": sorted(ref.keys())})
    return {"task": task.name, "input_manifest": manifest,
            "input_manifest_sha256": digest(task / "inputs/input_manifest.json"),
            "records": records,
            "scope": "paper protocol reconstruction; not outcome qualification"}

def main() -> None:
    payload = {"benchmark": "paper-environment-reconstruction-v1",
               "tasks": [evaluate(task) for task in TASKS]}
    for task, record in zip(TASKS, payload["tasks"]):
        out = task / "expected_outputs" / "local_evaluation.json"
        out.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
