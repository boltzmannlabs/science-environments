#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "inputs/paper_source/cdk2_cs3"
OUT = ROOT / "evaluation/paper_source_validation.json"
def main() -> None:
    expected = json.loads((ROOT / "evaluation/paper_source_provenance.json").read_text())
    checks = {}
    for name, spec in expected["files"].items():
        path = SRC / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        checks[name] = {"present": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0, "sha256": digest, "hash_matches": path.is_file() and digest == spec["sha256"]}
    gro = SRC / "em.gro"; gmx = shutil.which("gmx"); log = ROOT / "execution/gmx_check_paper_source.log"
    if gmx and gro.is_file():
        run = subprocess.run([gmx, "check", "-f", str(gro)], text=True, capture_output=True)
        log.write_text(run.stdout + run.stderr); gmx_status = "PASS" if run.returncode == 0 else "FAIL"
    else: gmx_status = "REVIEW"
    result = {"source": expected["source"], "directory": expected["selected_directory"], "file_checks": checks, "gmx_check": gmx_status, "status": "PASS" if all(x["hash_matches"] for x in checks.values()) and gmx_status == "PASS" else "REVIEW", "scientific_scope": "source input integrity and coordinate readability; topology and production dynamics remain unqualified"}
    OUT.write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
