#!/usr/bin/env python3
"""Run bounded OpenMM minimization smoke tests for generated endpoints."""
from __future__ import annotations
import json
from pathlib import Path
import openmm
from openmm import app, unit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "execution/config_runs"

def run(label: str, leg: str):
    prmtop = ROOT / f"execution/endpoints/{label}/{leg}.prmtop"
    inpcrd = ROOT / f"execution/endpoints/{label}/{leg}.inpcrd"
    top = app.AmberPrmtopFile(str(prmtop))
    coords = app.AmberInpcrdFile(str(inpcrd))
    system = top.createSystem(nonbondedMethod=app.NoCutoff, constraints=None)
    integrator = openmm.VerletIntegrator(0.001 * unit.picoseconds)
    simulation = app.Simulation(top.topology, system, integrator)
    simulation.context.setPositions(coords.positions)
    before = simulation.context.getState(getEnergy=True).getPotentialEnergy()
    simulation.minimizeEnergy(maxIterations=50)
    after = simulation.context.getState(getEnergy=True).getPotentialEnergy()
    return {"status": "PASS", "before_kj_mol": before.value_in_unit(unit.kilojoule_per_mole), "after_kj_mol": after.value_in_unit(unit.kilojoule_per_mole), "particles": system.getNumParticles()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = {}
    for label in ("a", "b"):
        records[label] = {}
        for leg in ("complex", "solvent"):
            try:
                records[label][leg] = run(label, leg)
            except Exception as exc:
                records[label][leg] = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
    result = {"configs_executed": ["config_A_reference", "config_B_agent"], "records": records, "status": "PASS" if all(v["status"] == "PASS" for legs in records.values() for v in legs.values()) else "FAIL", "scope": "bounded endpoint minimization smoke test; not lambda-window FEP"}
    (OUT / "endpoint_smoke.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
