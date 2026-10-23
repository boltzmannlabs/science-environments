#!/usr/bin/env python3
"""Freeze the four requested GPU reference artifacts and provenance."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    refs = []
    paths = [ROOT/"reports/benchmark_engine/GEO-001-water.json", ROOT/"reports/benchmark_engine/GEO-002-methane.json", ROOT/"reports/benchmark_engine/GEO-003-ethanol.json", ROOT/"reports/references/benzene_gpu.json"]
    for path in paths:
        data = json.loads(path.read_text())
        refs.append({"case": data["case"], "input": data["input"], "artifact": str(path.relative_to(ROOT)), "artifact_sha256": digest(path), "backend": data.get("backend", "GPU4PySCF+SciPy-BFGS"), "method": data.get("method", "B3LYP"), "basis": data.get("basis", "6-31G*"), "converged": data.get("converged"), "energy_hartree": data.get("energy_hartree"), "max_gradient_hartree_per_bohr": data.get("max_gradient_hartree_per_bohr"), "runtime_seconds": data.get("runtime_seconds")})
    out = ROOT/"reports/references"; out.mkdir(exist_ok=True)
    (out/"manifest.json").write_text(json.dumps({"schema_version":"1.0","backend":"GPU4PySCF+SciPy-BFGS","method":"B3LYP","basis":"6-31G*","references":refs}, indent=2) + "\n")
    print(json.dumps({"references":len(refs),"all_converged":all(x["converged"] for x in refs)}))

if __name__ == "__main__": main()
