"""Validate frozen CDK2 inputs and force-field sensitivity metadata."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    reference = json.loads((ROOT / "reference" / "parameters.json").read_text())
    inputs = {}
    for relative, expected in reference["input_sha256"].items():
        path = ROOT / "inputs" / relative
        actual = digest(path)
        inputs[relative] = {"sha256": actual, "matches_reference": actual == expected, "present": path.exists()}
    result = {
        "task_id": reference["task_id"],
        "system": reference["system"],
        "edge": reference["edge"],
        "reported_fields": reference["reported"],
        "inputs": inputs,
        "status": "PASS" if all(item["matches_reference"] for item in inputs.values()) else "FAIL",
        "scope": "input identity and sensitivity configuration; no production FEP claim",
    }
    (ROOT / "evaluation" / "input_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
