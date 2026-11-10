#!/usr/bin/env python3
"""Prepare and validate the pinned CDK2 protein-only endpoint component."""
from __future__ import annotations
import json
from pathlib import Path
from openmm import XmlSerializer, app

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs/source_cdk2/protein.pdb"
PHOS = ROOT / "inputs/source_cdk2/protein.phosaa10.xml"
OUT = ROOT / "execution/endpoint_preparation"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pdb = app.PDBFile(str(INPUT))
    forcefield = app.ForceField("amber/protein.ff14SB.xml", str(PHOS))
    system = forcefield.createSystem(pdb.topology)
    (OUT / "cdk2_protein_system.xml").write_text(XmlSerializer.serialize(system))
    metrics = {
        "protein_atoms": pdb.topology.getNumAtoms(),
        "system_particles": system.getNumParticles(),
        "forcefields": ["amber/protein.ff14SB.xml", "inputs/source_cdk2/protein.phosaa10.xml"],
        "status": "REVIEW",
        "complex_endpoint": "not generated: ligand GAFF endpoint parameters required",
        "solvent_endpoint": "not generated: ligand GAFF endpoint parameters required",
        "scientific_claim": "protein-only topology validation; not a complete FEP endpoint",
    }
    (OUT / "protein_endpoint_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
