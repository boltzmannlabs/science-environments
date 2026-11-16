"""Rebuild benchmark reports from tracked data; no scientific or network calls."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "src/benchmark_reports.py"), run_name="__main__")
