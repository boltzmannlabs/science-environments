"""Small engine adapters used by the MD packet harness.

Adapters prove that an input can be consumed by the available software stack;
they do not replace domain-specific scientific evaluators.
"""
from __future__ import annotations
import json
from pathlib import Path

def validate_fixture(path: Path) -> dict:
    ext = path.suffix.lower()
    try:
        if ext in {".pdb", ".gro"}:
            from openmm import app
            if ext == ".pdb":
                atoms = sum(1 for _ in app.PDBFile(str(path)).topology.atoms())
            else:
                gro = app.GromacsGroFile(str(path))
                atoms = len(gro.positions)
            if atoms <= 0: raise ValueError("topology contains no atoms")
            return {"engine": "OpenMM", "adapter_status": "PASS", "atoms": atoms}
        if ext == ".dcd":
            from mdtraj.formats import DCDTrajectoryFile
            with DCDTrajectoryFile(str(path)) as stream:
                xyz, *_ = stream.read()
            if len(xyz) == 0: raise ValueError("trajectory has no frames")
            return {"engine": "MDTraj-DCD", "adapter_status": "PASS", "frames": int(len(xyz)), "atoms": int(xyz.shape[1])}
        if ext in {".json"}:
            data = json.loads(path.read_text())
            return {"engine": "Python-json", "adapter_status": "PASS", "keys": sorted(data) if isinstance(data, dict) else []}
        if ext == ".parquet":
            import pandas as pd
            frame = pd.read_parquet(path)
            return {"engine": "PyArrow", "adapter_status": "PASS", "rows": int(len(frame))}
        if ext == ".csv":
            import csv
            with path.open(newline="") as fh: rows = list(csv.DictReader(fh))
            if not rows: raise ValueError("CSV has no data rows")
            return {"engine": "Python-csv", "adapter_status": "PASS", "rows": len(rows)}
        text = path.read_text(errors="strict")
        if not text.strip(): raise ValueError("fixture is empty")
        return {"engine": "text-parser", "adapter_status": "PASS", "bytes": len(text.encode())}
    except Exception as exc:
        return {"engine": "fixture-adapter", "adapter_status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
