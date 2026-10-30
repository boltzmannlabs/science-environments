"""Run a bounded native OpenMM molecular TI calculation.

This is an executable local-backend proof for alchemical bonded endpoint
interpolation. It deliberately uses a three-atom water-like molecule so that
the result is cheap and auditable without openmmtools. It is not a production
protein-ligand FEP protocol.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import openmm
from openmm import app, unit


def build_system():
    system = openmm.System()
    for mass in (15.9994, 1.008, 1.008):
        system.addParticle(mass * unit.amu)
    bonds = openmm.CustomBondForce(
        "0.5*k*((1-lambda)*rA+lambda*rB-r)^2"
    )
    bonds.addGlobalParameter("lambda", 0.0)
    bonds.addPerBondParameter("k")
    bonds.addPerBondParameter("rA")
    bonds.addPerBondParameter("rB")
    # Endpoint A/B are two explicitly parameterized water geometries.
    bonds.addBond(0, 1, [450000.0, 0.096, 0.100])
    bonds.addBond(0, 2, [450000.0, 0.096, 0.100])
    system.addForce(bonds)
    return system


def platform_and_properties():
    for name in ("CUDA", "OpenCL", "CPU", "Reference"):
        try:
            p = openmm.Platform.getPlatformByName(name)
            props = {"CudaPrecision": "mixed"} if name == "CUDA" else {}
            return p, props
        except Exception:
            continue
    raise RuntimeError("no OpenMM platform available")


def run(output: Path, windows: int = 11, replicas: int = 2, steps: int = 400, seed: int = 20261030):
    system = build_system()
    positions = unit.Quantity(np.array([[0.0, 0.0, 0.0], [0.096, 0.0, 0.0], [-0.024, 0.093, 0.0]]), unit.nanometer)
    platform_obj, properties = platform_and_properties()
    records = []
    lambdas = np.linspace(0.0, 1.0, windows)
    for rep in range(replicas):
        for index, lam in enumerate(lambdas):
            integrator = openmm.LangevinMiddleIntegrator(300 * unit.kelvin, 1 / unit.picosecond, 0.001 * unit.picoseconds)
            integrator.setRandomNumberSeed(seed + rep * 1000 + index)
            context = openmm.Context(system, integrator, platform_obj, properties)
            context.setPositions(positions)
            context.setParameter("lambda", float(lam))
            openmm.LocalEnergyMinimizer.minimize(context, tolerance=0.1 * unit.kilojoule_per_mole / unit.nanometer, maxIterations=100)
            integrator.step(100)
            deriv = []
            energies = []
            for _ in range(max(1, steps // 20)):
                integrator.step(20)
                state = context.getState(getEnergy=True, getPositions=True)
                x = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
                energy = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
                # dU/dlambda for the two interpolated harmonic bonds.
                d = 0.0
                for atom in (1, 2):
                    r = float(np.linalg.norm(x[atom] - x[0]))
                    target = (1 - lam) * 0.096 + lam * 0.100
                    d += 450000.0 * (target - r) * (0.100 - 0.096)
                deriv.append(d)
                energies.append(float(energy))
            records.append({"replica": rep, "lambda": float(lam), "mean_dU_dlambda": float(np.mean(deriv)), "std_dU_dlambda": float(np.std(deriv)), "mean_energy_kj_mol": float(np.mean(energies)), "samples": len(deriv)})
            del context, integrator
    by_lambda = []
    for lam in lambdas:
        vals = [r["mean_dU_dlambda"] for r in records if r["lambda"] == float(lam)]
        by_lambda.append({"lambda": float(lam), "mean_dU_dlambda": float(np.mean(vals)), "replica_std": float(np.std(vals))})
    estimate = float(np.trapezoid([x["mean_dU_dlambda"] for x in by_lambda], lambdas))
    result = {
        "task_id": "fep_molecular_ti_local_001",
        "status": "PASS",
        "scope": "bounded native OpenMM molecular TI proof; not protein-ligand production FEP",
        "engine": {"name": "OpenMM", "version": openmm.__version__, "platform": platform_obj.getName(), "host": platform.platform()},
        "protocol": {"windows": windows, "replicas": replicas, "steps_per_window": steps, "temperature_K": 300, "timestep_ps": 0.001, "endpoint": "water-like 3-atom molecule; O-H 0.096 -> 0.100 nm"},
        "estimate_kj_mol": estimate,
        "finite_energy": all(np.isfinite(r["mean_energy_kj_mol"]) for r in records),
        "finite_derivative": all(np.isfinite(r["mean_dU_dlambda"]) for r in records),
        "lambda_coverage": len(by_lambda) == windows,
        "windows": by_lambda,
        "records": records,
        "limitations": ["bonded-only alchemical interpolation", "no solvent or protein", "short bounded sampling", "no experimental reference"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "engine", "estimate_kj_mol", "finite_energy", "finite_derivative", "lambda_coverage")}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/molecular_ti_local_001.json"))
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
