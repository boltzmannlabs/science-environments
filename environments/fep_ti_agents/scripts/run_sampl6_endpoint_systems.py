"""Run bounded CUDA endpoint checks for the pinned SAMPL6 OA-G3/OA-G6 systems."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import openmm
from openmm import app, unit


def run(root: Path, output: Path, steps: int = 10) -> None:
    platform_obj = openmm.Platform.getPlatformByName("CUDA")
    records = []
    for guest in ("OA-G3-0", "OA-G6-0"):
        for leg in ("complex", "solvent"):
            base = root / "host_guest" / "SAMPLing" / guest
            system = openmm.XmlSerializer.deserialize((base / "OPENMM" / f"{leg}.xml").read_text())
            pdb = app.PDBFile(str(base / "PDB" / f"{leg}.pdb"))
            if system.getNumParticles() != pdb.topology.getNumAtoms():
                raise ValueError(f"particle/coordinate mismatch for {guest} {leg}")
            integrator = openmm.LangevinMiddleIntegrator(300 * unit.kelvin, 1 / unit.picosecond, 0.002 * unit.picoseconds)
            simulation = app.Simulation(pdb.topology, system, integrator, platform_obj)
            simulation.context.setPositions(pdb.positions)
            simulation.minimizeEnergy(maxIterations=5)
            simulation.step(steps)
            energy = simulation.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
            records.append({"guest": guest, "leg": leg, "particles": system.getNumParticles(), "steps": steps, "final_energy_kj_mol": float(energy), "finite_energy": bool(energy == energy)})
    result = {
        "task_id": "fep_sampl6_endpoint_systems_001",
        "status": "PASS" if all(r["finite_energy"] for r in records) else "FAIL",
        "source": {"repository": "https://github.com/samplchallenges/SAMPL6", "revision": "c661d3985af7fa0ba8c64a1774cfb2363cd31bda", "systems": "host_guest/SAMPLing/OA-G3-0 and OA-G6-0 OPENMM complex/solvent XML"},
        "engine": {"name": "OpenMM", "version": openmm.__version__, "platform": platform_obj.getName(), "host": platform.platform()},
        "protocol": {"minimization_iterations": 5, "steps": steps, "temperature_K": 300, "timestep_ps": 0.002},
        "records": records,
        "interpretation": "Endpoint systems execute with finite energies; this is not a free-energy estimate and does not establish lambda-window sampling or binding qualification.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sampl6-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=10)
    args = parser.parse_args()
    run(args.sampl6_root, args.output, args.steps)
