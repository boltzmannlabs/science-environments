#!/usr/bin/env python3
"""Run the retained AbFlow DockQ implementation on task-004 complexes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

DOCKQ = Path("/home/boltzmann10/Dileep_kumar/Rabies/design_setup/tool_repos/AbFlow/DockQ/DockQ.py")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def score(model: Path, native: Path) -> dict[str, object]:
    cmd = [
        "python3", str(DOCKQ), str(model), str(native),
        "-model_chain1", "B", "C", "-model_chain2", "A",
        "-native_chain1", "B", "C", "-native_chain2", "A",
        "-short", "-no_needle",
    ]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    line = completed.stdout.strip().splitlines()[-1]
    match = re.search(
        r"DockQ\s+(?P<dockq>[0-9.]+)\s+Fnat\s+(?P<fnat>[0-9.]+)\s+"
        r"iRMS\s+(?P<irms>[0-9.]+)\s+LRMS\s+(?P<lrms>[0-9.]+)\s+"
        r"Fnonnat\s+(?P<fnonnat>[0-9.]+)",
        line,
    )
    if not match:
        raise RuntimeError(f"Could not parse DockQ output: {line}")
    out: dict[str, object] = {k: float(v) for k, v in match.groupdict().items()}
    out["model"] = str(model)
    out["native"] = str(native)
    out["command"] = cmd
    out["stdout"] = completed.stdout.strip()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True, type=Path)
    ap.add_argument("--model", action="append", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    payload = {
        "tool": "AbFlow retained DockQ.py",
        "tool_path": str(DOCKQ),
        "tool_sha256": sha256(DOCKQ),
        "biopython_runtime": __import__("Bio").__version__,
        "protocol": {
            "model_chain1": ["B", "C"],
            "model_chain2": ["A"],
            "native_chain1": ["B", "C"],
            "native_chain2": ["A"],
            "flags": ["-short", "-no_needle"],
            "meaning": "antibody chains B/C versus LCAT antigen chain A; deposited 5BV7 reference",
        },
        "results": [score(model, args.native) for model in args.model],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
