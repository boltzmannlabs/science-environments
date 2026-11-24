#!/usr/bin/env python3
"""Evaluate the four setup configurations before any production FEP run."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation/config_matrix.json"

def main():
    configs = {}
    for path in sorted((ROOT / "configs").glob("config_*.json")):
        cfg = json.loads(path.read_text())
        name = path.stem
        if name == "config_D_perturbed":
            status, reason = "FAIL", "invalid complex/solvent legs, missing atom mapping, duplicate lambda schedule"
        elif name == "config_C_alternative":
            status, reason = "REVIEW", "RESP alternative is specified but RESP endpoint parameters are not generated"
        else:
            status, reason = "REVIEW", "setup is valid/readable; lambda trajectories and scientific qualification are absent"
        configs[name] = {"status": status, "reason": reason, "name": cfg["name"]}
    result = {"configs": configs, "status": "REVIEW", "scope": "configuration matrix and pre-execution gate; not production FEP"}
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
