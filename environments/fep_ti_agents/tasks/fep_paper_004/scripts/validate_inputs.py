"""Validate frozen source inputs and the second PTP1B edge."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    reference = json.loads((ROOT / "reference" / "parameters.json").read_text())
    validated = {
        name: {"sha256": digest(ROOT / "inputs" / name), "matches_reference": digest(ROOT / "inputs" / name) == expected}
        for name, expected in reference["input_sha256"].items()
    }
    with (ROOT / "inputs" / "ptp1b_edges.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    edge = next(row for row in rows if row["Ligand 1"] == "23477" and row["Ligand 2"] == "23479")
    result = {
        "task_id": reference["task_id"],
        "edge": {"direction": reference["edge"], "ddg_kcal_mol": round(float(edge["ddG (kcal/mol)"]), 2)},
        "inputs": validated,
        "status": "PASS" if all(item["matches_reference"] for item in validated.values()) and abs(float(edge["ddG (kcal/mol)"]) - reference["experimental_ddg_kcal_mol"]) < 1e-9 else "FAIL",
        "scope": "source identity and edge validation; no production FEP claim",
    }
    (ROOT / "evaluation" / "input_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
