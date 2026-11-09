#!/usr/bin/env python3
"""Run focused publication-replication setup checks.

This is intentionally conservative: it validates exact local inputs and
reported/variant configuration metadata, but never fabricates a paper outcome.
"""
from __future__ import annotations
import argparse, hashlib, json, platform, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_case(case: dict, config: str) -> dict:
    selected = case["reported"] if config == "published" else case["variant"]
    input_path = ROOT / case["input"]
    errors = []
    if not input_path.exists():
        errors.append(f"missing input: {case['input']}")
    elif input_path.stat().st_size == 0:
        errors.append("input is empty")
    if not case.get("paper", {}).get("doi"):
        errors.append("missing DOI")
    if not selected:
        errors.append(f"missing {config} configuration")
    status = "FAIL" if errors else "REVIEW"
    return {
        "id": case["id"], "module": case["module"], "system": case["system"],
        "configuration": config, "paper": case["paper"], "parameters": selected,
        "input": case["input"],
        "input_sha256": sha256(input_path) if input_path.exists() else None,
        "status": status, "errors": errors,
        "qualification_note": case["acceptance"],
        "host": platform.platform(),
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=["published", "variant"], action="append", default=None)
    args = ap.parse_args()
    configs = args.config or ["published", "variant"]
    manifest = json.loads((HERE / "manifest.json").read_text())
    records = [check_case(case, config) for config in configs for case in manifest["cases"]]
    out_dir = HERE / "results"; out_dir.mkdir(exist_ok=True)
    payload = {"benchmark": manifest["benchmark"], "records": records,
               "scope": "publication setup replication and controlled variants; not outcome qualification"}
    (out_dir / "latest.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    return 1 if any(r["status"] == "FAIL" for r in records) else 0

if __name__ == "__main__":
    raise SystemExit(main())
