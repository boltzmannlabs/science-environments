#!/usr/bin/env python3
"""De Novo-style FEP environment entry point for the fixture audit."""
from runpy import run_path
from pathlib import Path

run_path(str(Path(__file__).with_name("run_fep_validation.py")), run_name="__main__")
