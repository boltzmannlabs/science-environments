#!/usr/bin/env python3
"""Run the preserved regression suite against this layout from a temporary directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEST_SOURCE_COMMIT = '7c81252d67857d1025103a1042d09f58e2671812'
TEST_PREFIX = 'environments/Denovo-Enzyme-Design/tests/'


def git(*args: str) -> str:
    result = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('The pinned test source must be present in local Git history. '
                           'Use a checkout containing commit ' + TEST_SOURCE_COMMIT + '.\n' + result.stderr)
    return result.stdout


def adapt_locations(text: str, filename: str) -> str:
    replacements = {
        'runtime/controller.py': 'scripts/run.py',
        'runtime/': 'src/',
        " / 'runtime'": " / 'src'",
        'tasks/request.example.json': 'config/request.example.json',
        'tasks/homodimer.request.example.json': 'config/homodimer.request.example.json',
        'tests/validate_spec.py': 'scripts/validate_environment.py',
        'Path(__file__).resolve().parents[1]': "Path(os.environ['DENOVO_ENV_ROOT'])",
    }
    for before, after in replacements.items():
        text = text.replace(before, after)
    if '\nimport os\n' not in text:
        text = text.replace('from pathlib import Path\n', 'from pathlib import Path\nimport os\n', 1)
    if filename == 'test_controller.py':
        text = text.replace("sys.path.insert(0, str(ENVIRONMENT / 'src'))",
                            "sys.path.insert(0, str(ENVIRONMENT / 'src'))\n"
                            "sys.path.insert(0, str(ENVIRONMENT / 'scripts'))")
        text = text.replace('from controller import ', 'from run import ')
        text = text.replace('import controller as controller_module', 'import run as controller_module')
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Optional JSON report outside the environment')
    args = parser.parse_args()
    if args.report is not None:
        args.report = args.report.resolve()
        if args.report == ROOT or ROOT in args.report.parents:
            parser.error('--report must be outside the environment')
    sys.dont_write_bytecode = True
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['DENOVO_ENV_ROOT'] = str(ROOT)
    paths = [p for p in git('ls-tree', '-r', '--full-tree', '--name-only', TEST_SOURCE_COMMIT, '--', TEST_PREFIX).splitlines()
             if Path(p).name.startswith('test_') and p.endswith('.py')]
    if not paths:
        raise RuntimeError('No regression tests found in the pinned source commit.')
    provenance = {}
    with tempfile.TemporaryDirectory(prefix='denovo_regressions_') as directory:
        target = Path(directory)
        for path in paths:
            source = git('show', f'{TEST_SOURCE_COMMIT}:{path}')
            provenance[path] = hashlib.sha256(source.encode()).hexdigest()
            (target / Path(path).name).write_text(adapt_locations(source, Path(path).name))
        suite = unittest.defaultTestLoader.discover(str(target), pattern='test_*.py')
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        'scope': 'Existing location-adapted software regressions; no scientific execution',
        'source_commit': TEST_SOURCE_COMMIT,
        'source_file_sha256': provenance,
        'tests_run': result.testsRun,
        'tests_passed': result.testsRun - len(result.skipped) - len(result.failures) - len(result.errors)
                        - len(result.expectedFailures) - len(result.unexpectedSuccesses),
        'skipped': [{'test': str(t), 'reason': reason} for t, reason in result.skipped],
        'failures': [{'test': str(t), 'traceback': trace} for t, trace in result.failures],
        'errors': [{'test': str(t), 'traceback': trace} for t, trace in result.errors],
        'successful': result.wasSuccessful(),
        'scientific_jobs': 0,
    }
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
