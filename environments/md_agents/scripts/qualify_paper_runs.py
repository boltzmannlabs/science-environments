#!/usr/bin/env python3
"""Evaluate bounded paper-system runs against conservative qualification gates."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "results/real_system_production"
REPLICAS = ROOT / "results/replica_uncertainty/summary.json"

def main() -> None:
    replica_data = {r["system"]: r for r in json.loads(REPLICAS.read_text())["systems"]} if REPLICAS.exists() else {}
    records = []
    for path in sorted(PROD.glob("*.pdb.json")):
        data = json.loads(path.read_text())
        steps = data.get("steps", 0)
        finite = data.get("status") == "PASS" and data.get("final_energy_kj_mol") is not None
        replica = replica_data.get(data.get("system"), {})
        records.append({
            "system": data.get("system"),
            "bounded_execution": "PASS" if finite else "FAIL",
            "trajectory_present": bool(data.get("trajectory") and Path(data["trajectory"]).exists()),
            "replicas": replica.get("replicas", 1),
            "steps": steps,
            "uncertainty": "PASS" if replica.get("uncertainty_status") == "PASS" else "INSUFFICIENT",
            "scientific_qualification": "REVIEW",
            "reasons": ["single bounded replica", f"only {steps} production steps", "paper-matched sampling duration and reference observable are unavailable"],
        })
    out = ROOT / "results/paper_scientific_qualification.json"
    out.write_text(json.dumps({"systems": records, "qualification": "REVIEW", "anti_overclaim": "Finite energy and a short trajectory do not establish paper reproduction."}, indent=2) + "\n")
    print(json.dumps({"systems": len(records), "bounded_pass": sum(r["bounded_execution"] == "PASS" for r in records), "scientific_qualification": "REVIEW", "output": str(out)}, indent=2))

if __name__ == "__main__":
    main()
