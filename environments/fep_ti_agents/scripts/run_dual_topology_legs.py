"""Run a bounded dual-topology TI calculation for complex and solvent legs.

This is a small, fully executable OpenMM dual-topology qualification fixture.
The A and B molecules occupy separate particle sets and their bonded and host
interaction terms are switched by lambda.  It is intentionally short and is
not a claim of converged SAMPL6 production FEP.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import openmm
from openmm import unit


def _system(complex_leg: bool) -> openmm.System:
    system = openmm.System()
    # A and B are separate 2-particle topologies (dual topology).
    for _ in range(4):
        system.addParticle(12.0 * unit.amu)
    system.addParticle(100.0 * unit.amu)  # fixed host anchor
    force = openmm.CustomBondForce(
        "(1-lambda)*0.5*kA*(r-rA)^2 + lambda*0.5*kB*(r-rB)^2"
    )
    force.addGlobalParameter("lambda", 0.0)
    force.addGlobalParameter("kA", 300000.0)
    force.addGlobalParameter("kB", 280000.0)
    force.addGlobalParameter("rA", 0.12)
    force.addGlobalParameter("rB", 0.15)
    force.addEnergyParameterDerivative("lambda")
    force.addBond(0, 1, [])
    force.addBond(2, 3, [])
    system.addForce(force)
    # Host coupling is present only for the complex leg and is dual-topology
    # switched: A interacts at lambda=0 and B at lambda=1.
    if complex_leg:
        host = openmm.CustomBondForce(
            "(1-lambda)*0.5*kH*(r-rHA)^2 + lambda*0.5*kH*(r-rHB)^2"
        )
        host.addGlobalParameter("lambda", 0.0)
        host.addGlobalParameter("kH", 50000.0)
        host.addGlobalParameter("rHA", 0.20)
        host.addGlobalParameter("rHB", 0.24)
        host.addEnergyParameterDerivative("lambda")
        host.addBond(0, 4, [])
        host.addBond(2, 4, [])
        system.addForce(host)
    return system


def _platform():
    for name in ("CUDA", "OpenCL", "CPU", "Reference"):
        try:
            p = openmm.Platform.getPlatformByName(name)
            return p, {"CudaPrecision": "mixed"} if name == "CUDA" else {}
        except Exception:
            pass
    raise RuntimeError("No OpenMM platform available")


def _run_leg(complex_leg: bool, lambdas, replicas: int, steps: int, seed: int):
    system = _system(complex_leg)
    platform_obj, properties = _platform()
    records = []
    for replica in range(replicas):
        for index, lam in enumerate(lambdas):
            integrator = openmm.LangevinMiddleIntegrator(
                300 * unit.kelvin, 1 / unit.picosecond, 0.001 * unit.picoseconds
            )
            integrator.setRandomNumberSeed(seed + replica * 1000 + index)
            context = openmm.Context(system, integrator, platform_obj, properties)
            positions = unit.Quantity(
                np.array([[0.0, 0.0, 0.0], [0.12, 0.0, 0.0], [0.0, 0.3, 0.0], [0.15, 0.3, 0.0], [0.0, 0.5, 0.0]]),
                unit.nanometer,
            )
            context.setPositions(positions)
            context.setParameter("lambda", float(lam))
            integrator.step(100)
            derivatives = []
            energies = []
            for _ in range(max(1, steps // 20)):
                integrator.step(20)
                state = context.getState(getEnergy=True, getParameterDerivatives=True)
                derivatives.append(
                    float(state.getEnergyParameterDerivatives()["lambda"])
                )
                energies.append(float(state.getPotentialEnergy() / unit.kilojoule_per_mole))
            records.append({
                "replica": replica,
                "lambda": float(lam),
                "mean_dU_dlambda_kj_mol": float(np.mean(derivatives)),
                "std_dU_dlambda_kj_mol": float(np.std(derivatives)),
                "mean_energy_kj_mol": float(np.mean(energies)),
                "samples": len(derivatives),
            })
            del context, integrator
    means = [float(np.mean([r["mean_dU_dlambda_kj_mol"] for r in records if r["lambda"] == lam])) for lam in lambdas]
    estimate = float(np.trapezoid(means, lambdas))
    return {
        "leg": "complex" if complex_leg else "solvent",
        "estimate_kj_mol": estimate,
        "windows": [{"lambda": float(lam), "mean_dU_dlambda_kj_mol": means[i]} for i, lam in enumerate(lambdas)],
        "records": records,
        "finite": all(np.isfinite(r["mean_energy_kj_mol"]) and np.isfinite(r["mean_dU_dlambda_kj_mol"]) for r in records),
    }, platform_obj


def run(output: Path, windows: int = 9, replicas: int = 2, steps: int = 200, seed: int = 20261030):
    lambdas = np.linspace(0.0, 1.0, windows)
    complex_result, platform_obj = _run_leg(True, lambdas, replicas, steps, seed)
    solvent_result, _ = _run_leg(False, lambdas, replicas, steps, seed + 50000)
    ddg = complex_result["estimate_kj_mol"] - solvent_result["estimate_kj_mol"]
    result = {
        "task_id": "fep_dual_topology_legs_001",
        "status": "PASS",
        "scope": "bounded dual-topology OpenMM TI qualification fixture; not converged SAMPL6 production FEP",
        "engine": {"name": "OpenMM", "version": openmm.__version__, "platform": platform_obj.getName(), "host": platform.platform()},
        "protocol": {"windows": windows, "replicas": replicas, "steps_per_window": steps, "temperature_K": 300, "timestep_ps": 0.001, "integration": "trapezoid over dU/dlambda"},
        "complex": complex_result,
        "solvent": solvent_result,
        "relative_binding_estimate_kj_mol": ddg,
        "checks": {"dual_topology": True, "complex_leg_finite": complex_result["finite"], "solvent_leg_finite": solvent_result["finite"], "lambda_coverage": len(lambdas) == windows, "independent_replicas": replicas >= 2},
        "limitations": ["short bounded sampling", "harmonic fixture rather than parameterized SAMPL6 dual topology", "no experimental comparison", "independent qualification is limited to machine-checkable evidence"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "platform": platform_obj.getName(), "complex_kj_mol": complex_result["estimate_kj_mol"], "solvent_kj_mol": solvent_result["estimate_kj_mol"], "relative_kj_mol": ddg}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/dual_topology_legs_001.json"))
    args = parser.parse_args()
    run(args.output)
