#!/usr/bin/env python3
"""Check whether the pinned paper edge is ready for a real FEP execution.

This is a gate, not a simulator. It refuses to claim production readiness when
endpoint topologies, mapping, solvent coordinates, or trajectories are absent.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "inputs/input_manifest.json"
OUT = ROOT / "execution/endpoint_readiness.json"

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> dict:
    manifest = json.loads(MANIFEST.read_text())
    edge = manifest["selected_edge"]
    checks = {
        "selected_edge_pinned": bool(edge.get("ligand_a") and edge.get("ligand_b") and edge.get("direction")),
        "protein_structure_present": (ROOT / "inputs/source_cdk2/protein.pdb").is_file(),
        "ligand_source_present": (ROOT / "inputs/source_cdk2/ligands.mol2").is_file(),
        "source_protocol_present": (ROOT / "inputs/source_cdk2/Alchaware.cfg").is_file(),
        "atom_map_present": (ROOT / "inputs/atom_map.json").is_file(),
        "complex_endpoint_topology_present": (ROOT / "inputs/complex_endpoint_topology.xml").is_file(),
        "solvent_endpoint_topology_present": (ROOT / "inputs/solvent_endpoint_topology.xml").is_file(),
        "lambda_trajectories_present": (ROOT / "execution/trajectories").is_dir(),
    }
    missing = [name for name, ok in checks.items() if not ok]
    result = {
        "status": "PASS" if not missing else "REVIEW",
        "selected_edge": edge,
        "checks": checks,
        "missing": missing,
        "scientific_claim": "No production FEP claim; readiness gate only",
        "pdb_sha256": digest(ROOT / "inputs/cdk2_1H1Q.pdb"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    main()
