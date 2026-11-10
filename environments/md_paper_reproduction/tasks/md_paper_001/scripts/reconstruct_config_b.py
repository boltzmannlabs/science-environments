#!/usr/bin/env python3
"""Independently reconstruct Config B from the MD paper reference."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER_REFERENCE.md"
MANIFEST = ROOT / "inputs/input_manifest.json"
OUT = ROOT / "execution/generated_inputs/config_B_agent_generated.json"

def bullets(text):
    out = {}
    for line in text.splitlines():
        m = re.match(r"^- \*\*(.+?):\*\*\s*(.+)$", line.strip())
        if m: out[m.group(1).lower()] = m.group(2).strip()
    return out

def main():
    p, manifest = bullets(PAPER.read_text()), json.loads(MANIFEST.read_text())
    cfg = {
        "name": "agent_generated", "source": "independent_paper_interpretation",
        "engine": "GROMACS", "engine_version": "4.6.5 modified",
        "target": "CDK2-CS3", "pdb_id": manifest["pdb_id"], "ligand_resname": manifest["ligand_resname"],
        "electrostatics": "PME", "cutoff_A": 10, "constraints": "P-LINCS all bonds",
        "timestep_fs": 2, "equilibration_ps": {"nvt": 100, "npt": 100},
        "temperature_K": 298, "pressure_bar": 1, "production_ns": 100,
        "restraints": False,
        "thermostat": "stochastic velocity rescaling", "barostat": "Parrinello-Rahman",
        "unresolved": ["exact force-field revision", "complete CS3 topology", "hypersound supplementary parameters"],
    }
    result = {"status": "REVIEW", "configuration": cfg, "provenance": {"paper_sha256": hashlib.sha256(PAPER.read_bytes()).hexdigest(), "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), "read_config_A": False, "read_frozen_reference": False}}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2))

if __name__ == "__main__": main()
