#!/usr/bin/env python3
"""Small reproducible PySCF + SciPy geometry-optimization backend.

This is a first CPU reference backend for the Tier-1 pilot. It deliberately
does not claim production-quality optimizer coverage; every setting is
recorded in the output so it can be compared with another backend later.
"""
from __future__ import annotations

import json
import platform
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pyscf import dft, gto, grad
from scipy.optimize import minimize


@dataclass(frozen=True)
class System:
    name: str
    atoms: tuple[tuple[str, tuple[float, float, float]], ...]
    charge: int = 0
    multiplicity: int = 1


def optimize(system: System, method: str = "B3LYP", basis: str = "6-31G*", maxiter: int = 40, use_gpu: bool = False) -> dict:
    spin = system.multiplicity - 1
    atom = [(element, coords) for element, coords in system.atoms]

    def make_mol(coords_bohr: np.ndarray):
        coords_ang = coords_bohr.reshape((-1, 3)) * gto.param.BOHR
        return gto.M(atom=[(e, tuple(x)) for (e, _), x in zip(atom, coords_ang)],
                     basis=basis, charge=system.charge, spin=spin, unit="Angstrom",
                     verbose=0)

    def evaluate(coords_bohr: np.ndarray):
        mol = make_mol(coords_bohr)
        mf = dft.UKS(mol) if spin else dft.RKS(mol)
        if use_gpu:
            import gpu4pyscf.dft  # registers GPU implementations
            mf = mf.to_gpu()
        mf.xc = method
        mf.conv_tol = 1e-9
        mf.max_cycle = 100
        energy = float(mf.kernel())
        if not mf.converged:
            raise RuntimeError(f"SCF did not converge for {system.name}")
        g = mf.nuc_grad_method().kernel() if use_gpu else (grad.uks.Gradients(mf).kernel() if spin else grad.rks.Gradients(mf).kernel())
        return energy, np.asarray(g, dtype=float).reshape(-1)

    initial = np.array([xyz for _, xyz in atom], dtype=float).reshape(-1) / gto.param.BOHR
    evaluations = 0
    history: list[dict] = []
    started = time.perf_counter()

    def objective(coords):
        nonlocal evaluations
        energy, gradient = evaluate(coords)
        evaluations += 1
        history.append({"evaluation": evaluations, "energy_hartree": energy,
                        "max_gradient_hartree_per_bohr": float(np.max(np.abs(gradient)))})
        return energy, gradient

    result = minimize(objective, initial, jac=True, method="BFGS",
                      options={"gtol": 1e-4, "maxiter": maxiter, "disp": False})
    final_energy, final_gradient = evaluate(result.x)
    return {
        "schema_version": "0.1", "system": system.name, "backend": "GPU4PySCF+SciPy-BFGS" if use_gpu else "PySCF+SciPy-BFGS",
        "method": method, "basis": basis, "charge": system.charge,
        "multiplicity": system.multiplicity, "initial_coordinates_angstrom": (initial.reshape(-1,3)*gto.param.BOHR).tolist(),
        "final_coordinates_angstrom": (result.x.reshape(-1,3)*gto.param.BOHR).tolist(),
        "energy_hartree": final_energy, "max_gradient_hartree_per_bohr": float(np.max(np.abs(final_gradient))),
        "rms_gradient_hartree_per_bohr": float(np.sqrt(np.mean(final_gradient**2))),
        "converged": bool(result.success and np.max(np.abs(final_gradient)) < 1e-4),
        "optimizer_success": bool(result.success), "optimizer_message": str(result.message),
        "optimizer_iterations": int(getattr(result, "nit", 0)), "scf_energy_evaluations": evaluations,
        "runtime_seconds": time.perf_counter() - started, "history": history,
        "software": {"python": platform.python_version(), "pyscf": __import__("pyscf").__version__},
    }

def single_point(system: System, method: str = "B3LYP", basis: str = "6-31G*", use_gpu: bool = False) -> dict:
    """Evaluate one energy/analytic gradient without optimizer line searches."""
    spin = system.multiplicity - 1
    mol = gto.M(atom=[(e, xyz) for e, xyz in system.atoms], basis=basis,
                charge=system.charge, spin=spin, unit="Angstrom", verbose=0)
    mf = dft.UKS(mol) if spin else dft.RKS(mol)
    if use_gpu:
        import gpu4pyscf.dft
        mf = mf.to_gpu()
    mf.xc = method; mf.conv_tol = 1e-9; mf.max_cycle = 100
    started = time.perf_counter(); energy = float(mf.kernel())
    gradient = mf.nuc_grad_method().kernel() if use_gpu else (grad.uks.Gradients(mf).kernel() if spin else grad.rks.Gradients(mf).kernel())
    gradient = np.asarray(gradient, dtype=float)
    return {"energy_hartree": energy, "max_gradient_hartree_per_bohr": float(np.max(np.abs(gradient))), "rms_gradient_hartree_per_bohr": float(np.sqrt(np.mean(gradient**2))), "scf_converged": bool(mf.converged), "runtime_seconds": time.perf_counter()-started, "backend": "GPU4PySCF-single-point" if use_gpu else "PySCF-single-point"}


SYSTEMS = (
    System("water", (("O", (0.000000, 0.000000, 0.000000)), ("H", (0.758602, 0.000000, 0.504284)), ("H", (-0.758602, 0.000000, 0.504284)))),
    System("ammonia", (("N", (0.000000, 0.000000, 0.116489)), ("H", (0.000000, 0.939731, -0.271485)), ("H", (0.812301, -0.469865, -0.271485)), ("H", (-0.812301, -0.469865, -0.271485)))),
    System("methane", (("C", (0.000000, 0.000000, 0.000000)), ("H", (0.629118, 0.629118, 0.629118)), ("H", (-0.629118, -0.629118, 0.629118)), ("H", (-0.629118, 0.629118, -0.629118)), ("H", (0.629118, -0.629118, -0.629118)))),
    System("ethane", (("C", (-0.763000, 0.000000, 0.000000)), ("C", (0.763000, 0.000000, 0.000000)), ("H", (-1.158000, 0.000000, 1.027000)), ("H", (-1.158000, 0.889000, -0.514000)), ("H", (-1.158000, -0.889000, -0.514000)), ("H", (1.158000, 0.000000, -1.027000)), ("H", (1.158000, -0.889000, 0.514000)), ("H", (1.158000, 0.889000, 0.514000)))),
)


def main() -> None:
    out = Path("reports/tier1")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for system in SYSTEMS:
        try:
            row = optimize(system)
        except Exception as exc:  # preserve failures as benchmark evidence
            row = {"schema_version": "0.1", "system": system.name, "converged": False,
                   "failure_category": "engine_failure", "error": repr(exc)}
        (out / f"{system.name}.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append({k: row.get(k) for k in ("system", "converged", "energy_hartree", "max_gradient_hartree_per_bohr", "rms_gradient_hartree_per_bohr", "optimizer_iterations", "scf_energy_evaluations", "runtime_seconds", "failure_category")})
        print(json.dumps(rows[-1]))
    (out / "summary.json").write_text(json.dumps({"backend": "PySCF+SciPy-BFGS", "systems": rows}, indent=2) + "\n")


if __name__ == "__main__":
    main()
