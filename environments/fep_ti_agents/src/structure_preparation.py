"""Independent checks for prepared endpoint artifacts."""
from __future__ import annotations
from pathlib import Path

REQUIRED_SUFFIXES = (".mol2", ".frcmod", ".prmtop", ".inpcrd")

def endpoint_status(directory: str | Path, endpoint: str) -> dict:
    root = Path(directory)
    files = {suffix: root / f"{endpoint}{suffix}" for suffix in REQUIRED_SUFFIXES}
    checks = {suffix: path.is_file() and path.stat().st_size > 0 for suffix, path in files.items()}
    return {"endpoint": endpoint, "checks": checks, "status": "PASS" if all(checks.values()) else "REVIEW"}
