#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation/config_matrix.json"
def main():
    configs = {}
    for path in sorted((ROOT / "configs").glob("config_*.json")):
        cfg = json.loads(path.read_text()); name = path.stem
        if name == "config_D_perturbed": status, reason = "FAIL", "5 fs timestep and 310 K deviate from the paper protocol"
        elif name == "config_C_alternative": status, reason = "REVIEW", "OpenMM/HBonds/short production is a declared alternative, not paper reproduction"
        else: status, reason = "REVIEW", "configuration setup only; topology and 100 ns scientific evidence are absent"
        configs[name] = {"status": status, "reason": reason, "name": cfg["name"]}
    result = {"configs": configs, "status": "REVIEW", "scope": "paper protocol configuration benchmark; not 100 ns outcome reproduction"}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
