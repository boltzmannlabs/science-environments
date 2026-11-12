#!/usr/bin/env python3
"""Run short independent replicas and estimate bounded-run uncertainty."""
from pathlib import Path
import json, math, time
import openmm
from openmm import unit
from openmm.app import PDBFile, ForceField, PME, HBonds, Simulation

ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "results/real_system_smoke"
OUT = ROOT / "results/replica_uncertainty"
OUT.mkdir(exist_ok=True)
systems = ["villin_headpiece.pdb", "barnase_barstar.pdb", "dna_duplex.pdb"]
seeds = [20261101, 20261102, 20261103]
all_results = []
for name in systems:
    src = SMOKE / (name + ".repaired.pdb")
    values = []
    for replica, seed in enumerate(seeds, 1):
        rec = {"system": name, "replica": replica, "steps": 200, "seed": seed, "status": "FAIL"}
        try:
            pdb = PDBFile(str(src)); ff = ForceField("amber14-all.xml", "amber14/tip3p.xml")
            system = ff.createSystem(pdb.topology, nonbondedMethod=PME, nonbondedCutoff=1*unit.nanometer, constraints=HBonds)
            integrator = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1/unit.picosecond, 1*unit.femtosecond)
            integrator.setRandomNumberSeed(seed)
            sim = Simulation(pdb.topology, system, integrator); sim.context.setPositions(pdb.positions)
            sim.minimizeEnergy(maxIterations=100); start = time.perf_counter(); sim.step(200)
            energy = float(sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole))
            rec.update(status="PASS" if math.isfinite(energy) else "FAIL", final_energy_kj_mol=energy, wall_time_s=round(time.perf_counter()-start, 3))
            if math.isfinite(energy): values.append(energy)
        except Exception as exc: rec["error"] = f"{type(exc).__name__}: {exc}"
        (OUT / f"{name}.replica{replica}.json").write_text(json.dumps(rec, indent=2) + "\n")
    mean = sum(values)/len(values) if values else None
    sd = (sum((v-mean)**2 for v in values)/(len(values)-1))**0.5 if len(values) > 1 else None
    all_results.append({"system": name, "replicas": len(values), "expected_replicas": 3, "mean_energy_kj_mol": mean, "sd_energy_kj_mol": sd, "uncertainty_status": "PASS" if len(values) == 3 else "FAIL"})
(OUT / "summary.json").write_text(json.dumps({"systems": all_results, "steps_per_replica": 200, "interpretation": "bounded replica uncertainty; not paper reproduction"}, indent=2) + "\n")
print(json.dumps(all_results, indent=2))
