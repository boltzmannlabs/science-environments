#!/usr/bin/env python3
"""Run Task-01 through the shared registry runner."""
from pathlib import Path
import argparse
import runpy
import sys

ENV = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    runner = ENV / 'scripts/shared/run_task.py'
    sys.argv = [str(runner), '--task', 'Task - 01', '--out', str(args.out)]
    runpy.run_path(str(runner), run_name='__main__')
