#!/usr/bin/env python3
"""Reproducible analytical thermodynamic-integration smoke benchmark.

This is an executable statistical/calculation test for the FEP evaluators.  It
is deliberately not a protein-ligand production FEP calculation.
"""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parents[1]

def run(seed: int, n_samples: int = 20000):
    rng = np.random.default_rng(seed)
    k0, k1, kbt = 1.0, 2.0, 1.0
    lambdas = np.linspace(0.0, 1.0, 11)
    means = []
    overlap = []
    for lam in lambdas:
        k = k0 + (k1-k0)*lam
        x = rng.normal(0.0, np.sqrt(kbt/k), n_samples)
        means.append(float(np.mean(0.5*(k1-k0)*x*x)))
        # Bhattacharyya coefficient for adjacent zero-mean normal ensembles.
        if lam > 0:
            kp = k0 + (k1-k0)*(lam-0.1)
            overlap.append(float(np.sqrt(2*np.sqrt(k*kp)/(k+kp))))
    estimate = float(np.trapezoid(means, lambdas))
    exact = float(0.5*kbt*np.log(k1/k0))
    return {"seed": seed, "estimate": estimate, "exact": exact,
            "absolute_error": abs(estimate-exact),
            "min_adjacent_overlap": min(overlap), "effective_samples": n_samples}

def main():
    repeats = [run(20261027), run(20261028)]
    estimate = float(np.mean([r["estimate"] for r in repeats]))
    exact = repeats[0]["exact"]
    payload = {
        "benchmark": "fep-toy-ti-v1",
        "model": "one-dimensional harmonic oscillator; numpy analytical sampler",
        "protocol": {"k0": 1.0, "k1": 2.0, "kbt": 1.0, "lambda_windows": 11,
                     "replicas": 2, "samples_per_window": 20000},
        "repeats": repeats,
        "mean_estimate": estimate,
        "exact_reference": exact,
        "absolute_error": abs(estimate-exact),
        "min_adjacent_overlap": min(r["min_adjacent_overlap"] for r in repeats),
        "status": "PASS" if abs(estimate-exact) < 0.02 and min(r["min_adjacent_overlap"] for r in repeats) > 0.5 else "REVIEW",
        "scope": "toy thermodynamic-integration smoke calculation; not protein-ligand production FEP",
        "limitations": ["No molecular topology, force field, solvent, or engine adapter", "Analytical harmonic reference only"]
    }
    out = ROOT / "results" / "toy_ti"
    out.mkdir(parents=True, exist_ok=True)
    (out / "toy_results.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
