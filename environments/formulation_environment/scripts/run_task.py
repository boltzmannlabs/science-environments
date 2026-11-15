#!/usr/bin/env python3
"""Registry-dispatched offline task runner. Refuse to overwrite prior runs."""
from pathlib import Path
import argparse
import contextlib
import json
import sys

ENV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENV / 'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', default='Task - 01', help='Exact registered task ID')
    parser.add_argument('--out', type=Path, required=True, help='New output directory')
    args = parser.parse_args()
    registry = json.loads((ENV / 'config/tasks.json').read_text())
    task = registry['tasks'].get(args.task)
    if task is None:
        parser.error('Unknown task; registered tasks: ' + ', '.join(registry['tasks']))
    output = args.out.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Output directory is not empty; use a new run directory.')
    output.mkdir(parents=True, exist_ok=True)
    inputs = ENV / task['benchmark_dir'] / 'inputs'
    if task['entrypoint'] != 'formulation_environment.task01:run_task01':
        parser.error('Unsupported entrypoint; extend the explicit dispatch when adding tasks.')
    from formulation_environment.task01 import run_task01
    with (output / 'execution.log').open('w') as log, contextlib.redirect_stdout(log):
        result = run_task01(inputs, output)
    receipt = {
        'task_id': args.task,
        'title': task['title'],
        'implementation': task['entrypoint'],
        'status': 'COMPUTATIONAL_RUN_COMPLETE',
        'candidate_lab_observations': 0,
        'candidate_recipe_predictions': 0,
        'scope': result['scope'],
        'verification_artifact': 'verification.json',
    }
    (output / 'run_receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
