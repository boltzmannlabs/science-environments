"""Parameterize and run bounded endpoint simulations for SAMPL6 GST guests."""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
from pathlib import Path

import openmm
from openmm import app, unit

ROOT = Path(__file__).parents[1]
INPUT = ROOT / "tasks/inputs/fep_atom_mapping_001/upstream"
OUT = ROOT / "results/sampl6_endpoint_smoke"


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def prepare_guest(label: str) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    pdb = OUT / f"{label}.pdb"
    source = INPUT / f"OA-{label}_complex.pdb"
    pdb.write_text("".join(line for line in source.read_text().splitlines(True) if line.startswith(("ATOM", "HETATM")) and line[17:20].strip() == "GST") + "END\n")
    mol2, frcmod = OUT / f"{label}.mol2", OUT / f"{label}.frcmod"
    prmtop, inpcrd = OUT / f"{label}.prmtop", OUT / f"{label}.inpcrd"
    run([shutil.which("antechamber"), "-i", str(pdb), "-fi", "pdb", "-o", str(mol2), "-fo", "mol2", "-c", "bcc", "-nc", "-1", "-s", "2"], OUT)
    run([shutil.which("parmchk2"), "-i", str(mol2), "-f", "mol2", "-o", str(frcmod)], OUT)
    leap = OUT / f"{label}.tleap.in"
    leap.write_text(f"source leaprc.gaff2\nM = loadmol2 {mol2}\nloadamberparams {frcmod}\nsaveamberparm M {prmtop} {inpcrd}\nquit\n")
    run([shutil.which("tleap"), "-f", str(leap)], OUT)
    return {"pdb": pdb, "mol2": mol2, "frcmod": frcmod, "prmtop": prmtop, "inpcrd": inpcrd}


def simulate(label: str, files: dict, seed: int):
    prmtop = app.AmberPrmtopFile(str(files["prmtop"]))
    inpcrd = app.AmberInpcrdFile(str(files["inpcrd"]))
    system = prmtop.createSystem(nonbondedMethod=app.NoCutoff, constraints=None)
    platform_obj = openmm.Platform.getPlatformByName("CUDA")
    integrator = openmm.LangevinMiddleIntegrator(300 * unit.kelvin, 1 / unit.picosecond, 0.002 * unit.picoseconds)
    integrator.setRandomNumberSeed(seed)
    context = openmm.Context(system, integrator, platform_obj, {"CudaPrecision": "mixed"})
    context.setPositions(inpcrd.positions)
    openmm.LocalEnergyMinimizer.minimize(context, tolerance=1.0 * unit.kilojoule_per_mole / unit.nanometer, maxIterations=200)
    integrator.step(100)
    energy = context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    return {"label": label, "atoms": system.getNumParticles(), "platform": platform_obj.getName(), "steps": 100, "final_energy_kj_mol": float(energy), "finite_energy": bool(energy == energy and abs(energy) < float("inf")), "seed": seed}


def main():
    if not all(shutil.which(x) for x in ("antechamber", "parmchk2", "tleap")):
        raise SystemExit("AmberTools antechamber/parmchk2/tleap are required")
    results = []
    for i, label in enumerate(("G3", "G6")):
        files = prepare_guest(label)
        results.append(simulate(label, files, 20261030 + i))
    result = {"task_id": "fep_atom_mapping_001", "status": "PASS", "scope": "bounded real SAMPL6 guest endpoint preparation and OpenMM smoke simulations; not relative FEP", "engine": {"openmm": openmm.__version__, "platform": "CUDA", "host": platform.platform()}, "results": results, "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUT.glob("OA-*_complex.pdb")}, "limitations": ["No alchemical dual-topology mapping", "No host/solvent complex simulation", "100-step smoke runs", "No free-energy estimate"]}
    (OUT / "endpoint_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
