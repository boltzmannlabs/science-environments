"""Source-only release checks do not depend on the local research archive."""
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    'test_application_examples.py',
    'test_orchestration_pilot.py',
    'test_strategist_benchmark.py',
    'test_srg12_native_unbudgeted.py',
)


def test_source_only_checkout_collects_and_runs_core_checks(tmp_path):
    for name in ('src', 'tests'):
        shutil.copytree(ROOT / name, tmp_path / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(ROOT / 'pyproject.toml', tmp_path / 'pyproject.toml')
    environment = dict(os.environ)
    environment.pop('SRG_SCIENTIST_SOURCE', None)
    environment['PYTHONPATH'] = str(tmp_path / 'src')
    environment['PYTEST_ADDOPTS'] = ''
    command = [sys.executable, '-m', 'pytest', '--no-cov', '-q', '-rs',
               *(str(tmp_path / 'tests' / name) for name in MODULES),
               str(tmp_path / 'tests/test_portfolio.py') +
               '::test_five_portfolio_examples_execute_end_to_end']
    result = subprocess.run(command, cwd=tmp_path, env=environment,
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'passed' in result.stdout  # Core accounting/evaluation checks still run.
    assert 'archiv' in result.stdout.lower()
    assert 'SRG_SCIENTIST_SOURCE' in result.stdout
