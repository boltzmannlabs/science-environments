#!/usr/bin/env python3
"""Run the frozen Tier-1 pilot with GPU4PySCF."""
from __future__ import annotations
import json
from pathlib import Path
from .pyscf_scipy import SYSTEMS, optimize

def main() -> None:
    out = Path("reports/tier1_gpu")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for system in SYSTEMS:
        try:
            row = optimize(system, use_gpu=True)
        except Exception as exc:
            row = {"schema_version":"0.1", "system":system.name, "backend":"GPU4PySCF+SciPy-BFGS", "converged":False, "failure_category":"engine_failure", "error":repr(exc)}
        (out / f"{system.name}.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append({k: row.get(k) for k in ("system","backend","converged","energy_hartree","max_gradient_hartree_per_bohr","rms_gradient_hartree_per_bohr","optimizer_iterations","scf_energy_evaluations","runtime_seconds","failure_category")})
        print(json.dumps(rows[-1]))
    (out / "summary.json").write_text(json.dumps({"backend":"GPU4PySCF+SciPy-BFGS","systems":rows}, indent=2) + "\n")

if __name__ == "__main__": main()
