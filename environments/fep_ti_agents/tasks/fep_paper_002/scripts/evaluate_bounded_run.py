"""Independent evaluator for the bounded OpenFE NetCDF outputs."""
from __future__ import annotations

import json
import argparse
from pathlib import Path

import netCDF4
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "execution" / "openfe_bounded_run"
RUN = DEFAULT_RUN


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--minimum-samples", type=int, default=100)
    args = parser.parse_args()
    global RUN
    # Accept paths relative to either the repository working directory or the
    # task directory.  This keeps the evaluator usable from the repository
    # root without accidentally creating ROOT/ROOT/... paths.
    if args.run.is_absolute():
        RUN = args.run
    elif (Path.cwd() / args.run).exists():
        RUN = (Path.cwd() / args.run).resolve()
    else:
        RUN = (ROOT / args.run).resolve()
    result = {
        "status": "REVIEW",
        "legs": {leg: evaluate(leg) for leg in ("solvent", "complex")},
        "criteria": {
            "minimum_production_samples": args.minimum_samples,
            "required_replicas": 3,
            "required_lambda_windows": 11,
            "note": "Independent evaluator distinguishes execution from convergence and publication-level qualification.",
        },
    }
    (RUN / "independent_evaluation.json").write_text(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
