#!/usr/bin/env python3
"""Run the FEP package and paper-task regression tests."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

root = Path(__file__).parents[1]
tests = [root / "tests"] + sorted((root / "tasks").glob("fep_paper_*/tests"))
raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", "-q", *map(str, tests)]))
