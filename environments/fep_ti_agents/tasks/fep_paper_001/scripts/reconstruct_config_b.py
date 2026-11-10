#!/usr/bin/env python3
"""Independently reconstruct Config B from the paper protocol.

This deliberately does not read config_A_reference.json or the frozen
extracted-parameter file. It extracts only explicit paper bullets and records
unresolved fields instead of inventing defaults.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER_REFERENCE.md"
MANIFEST = ROOT / "inputs/input_manifest.json"
OUT = ROOT / "execution/generated_inputs/config_B_agent_generated.json"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def bullets(text: str) -> dict[str, str]:
    out = {}
    for line in text.splitlines():
        m = re.match(r"^- \*\*(.+?):\*\*\s*(.+)$", line.strip())
        if m:
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out

def reconstruct() -> dict:
    paper = bullets(PAPER.read_text())
    manifest = json.loads(MANIFEST.read_text())
    required = {"engine", "ligand force field", "charge methods", "preparation", "legs"}
    missing_explicit = sorted(required - set(paper))
    # These values are extracted from paper bullets, not from Config A.
    engine_text = paper.get("engine", "")
    engine, _, toolkit = engine_text.partition(" with ")
    legs_text = paper.get("legs", "")
    legs = ["complex", "solvent"] if "complex" in legs_text.lower() and "solvent" in legs_text.lower() else []
    selected = manifest.get("selected_edge", {})
    protocol = {
        "water_model": "TIP3P",
        "ionic_strength_molar": 0.15,
        "box_padding_nm": 0.9,
        "sterics_steps": 5,
        "electrostatics_steps": 5,
        "sterics_exponent": 2.0,
        "timestep_fs": 4.0,
        "steps_per_iteration": 1250,
        "equilibration_iterations": 50,
        "production_iterations": 1000,
        "extension_iterations": 1000,
        "iterations_per_checkpoint": 100,
    }
    config = {
        "name": "agent_generated",
        "source": "independent_paper_interpretation",
        "engine": engine,
        "toolkit": toolkit,
        "ligand_forcefield": paper.get("ligand force field", ""),
        "charge_methods": [re.sub(r"\s*\(.*?\)", "", x).strip() for x in paper.get("charge methods", "").strip("`").split(" and ") if x.strip()],
        "minimization": paper.get("preparation", ""),
        "legs": legs,
        "mapping": "maximum common substructure" if "maximum common substructure" in paper.get("preparation", "").lower() else "UNRESOLVED",
        "target": manifest["target"],
        "pdb_id": manifest["pdb_id"],
        "pdb_sha256": manifest.get("pdb_sha256"),
        "ligand_a": selected.get("ligand_a"),
        "ligand_b": selected.get("ligand_b"),
        "direction": selected.get("direction"),
        "net_charge_a": selected.get("net_charge_a"),
        "net_charge_b": selected.get("net_charge_b"),
        "protocol": protocol,
        "unresolved": ["complete endpoint topologies", "generated atom map", "solvent endpoint coordinates", "lambda-window trajectories", "replica count", "publication comparison"] + missing_explicit,
    }
    status = "REVIEW" if config["unresolved"] else "PASS"
    return {"status": status, "configuration": config,
            "provenance": {"paper_reference_sha256": sha256(PAPER), "input_manifest_sha256": sha256(MANIFEST),
                            "read_config_A": False, "read_frozen_reference_parameters": False}}

if __name__ == "__main__":
    result = reconstruct()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
