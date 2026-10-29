"""Compatibility entry point matching the repository environment layout."""
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).parents[1]

def run(live: bool = False, strict: bool = False) -> int:
    cmd = [sys.executable, str(ROOT / "scripts/run_agent_harness.py")]
    if live: cmd.append("--live")
    if strict: cmd.append("--strict")
    return subprocess.call(cmd, cwd=ROOT)

if __name__ == "__main__":
    raise SystemExit(run(live="--live" in sys.argv, strict="--strict" in sys.argv))
