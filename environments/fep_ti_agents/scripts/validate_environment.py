#!/usr/bin/env python3
"""Run the package contract validator from the environment root."""
from runpy import run_path
from pathlib import Path

root = Path(__file__).parents[1]
run_path(str(root / "tests" / "validate_spec.py"), run_name="__main__")
