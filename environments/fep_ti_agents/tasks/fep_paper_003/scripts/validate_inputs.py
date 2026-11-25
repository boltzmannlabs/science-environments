"""Independently validate frozen SAMPL6 input identity and edge metadata."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    reference = json.loads((ROOT / "reference" / "parameters.json").read_text())
    inputs = {}
    for relative, expected in reference["input_sha256"].items():
        path = ROOT / "inputs" / relative
        actual = sha256(path)
        inputs[relative] = {
            "present": path.exists(),
            "sha256": actual,
            "matches_reference": actual == expected,
            "atom_records": sum(1 for line in path.read_text().splitlines() if line.startswith(("ATOM", "HETATM"))),
        }
    result = {
        "task_id": reference["task_id"],
        "edge": {
            "direction": reference["transformation"],
            "experimental_ddg_kcal_mol": reference["experimental_ddg_kcal_mol"],
            "sign_convention": reference["sign_convention"],
        },
        "inputs": inputs,
        "status": "PASS" if all(v["matches_reference"] for v in inputs.values()) else "FAIL",
        "scope": "input identity and edge validation; no production FEP claim",
    }
    output = ROOT / "evaluation" / "input_validation.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
