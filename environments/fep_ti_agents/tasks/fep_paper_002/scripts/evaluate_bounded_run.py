"""Independent evaluator for the bounded OpenFE NetCDF outputs."""
from __future__ import annotations

import json
from pathlib import Path

import netCDF4
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "execution" / "openfe_bounded_run"


def evaluate(leg: str) -> dict:
    with netCDF4.Dataset(RUN / leg / "scratch" / "simulation.nc") as ds:
        energies = np.asarray(ds.variables["energies"])
        accepted = np.asarray(ds.variables["accepted"])
        proposed = np.asarray(ds.variables["proposed"])
    finite = bool(np.isfinite(energies).all())
    # The output contains two recorded iterations (equilibration and one
    # production iteration), so it cannot support a statistically meaningful
    # block estimate or replica uncertainty.
    production_samples = max(0, energies.shape[0] - 1)
    acceptance = float(accepted[-1].sum() / max(1, proposed[-1].sum()))
    adjacent_delta = np.diff(energies[-1], axis=-1)
    overlap_proxy = float(np.mean(np.exp(-np.abs(adjacent_delta))))
    return {
        "leg": leg,
        "netcdf": str((RUN / leg / "scratch" / "simulation.nc").relative_to(ROOT)),
        "iterations": int(energies.shape[0]),
        "replicas": int(energies.shape[1]),
        "lambda_windows": int(energies.shape[2]),
        "finite_energies": finite,
        "production_samples_per_window": production_samples,
        "replica_exchange_acceptance": acceptance,
        "adjacent_overlap_proxy": overlap_proxy,
        "convergence": "INSUFFICIENT_SAMPLES",
        "uncertainty": "NOT_ESTIMABLE",
        "qualification": "REVIEW",
    }


def main() -> int:
    result = {
        "status": "REVIEW",
        "legs": {leg: evaluate(leg) for leg in ("solvent", "complex")},
        "criteria": {
            "minimum_production_samples": 100,
            "required_replicas": 3,
            "required_lambda_windows": 11,
            "note": "The bounded smoke run proves execution and output generation, not convergence or a publishable free energy.",
        },
    }
    (RUN / "independent_evaluation.json").write_text(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
