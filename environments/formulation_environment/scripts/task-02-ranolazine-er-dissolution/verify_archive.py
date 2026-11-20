#!/usr/bin/env python3
"""Task-02-only entry point; reuse the shared registry runner."""
from pathlib import Path
import argparse
import runpy
import sys

ENV = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sys.argv = [str(ENV / "scripts/shared/run_task.py"), "--task", "Task - 02", "--out", str(args.out)]
    runpy.run_path(str(ENV / "scripts/shared/run_task.py"), run_name="__main__")
