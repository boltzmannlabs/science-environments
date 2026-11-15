#!/usr/bin/env python3
"""Run scientific-contract tests, link/privacy checks and optional real-run comparison."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import datetime
import hashlib
import io
import json
import platform
import re
import sys
import unittest
import zipfile

ENV = Path(__file__).resolve().parents[1]
REPO = ENV.parents[1]


def public_files():
    for p in ENV.rglob('*'):
        if p.is_file() and not any(x in p.parts for x in ['.runs', '.cache', '.venv', '__pycache__', '.pytest_cache']):
            yield p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, help='Actually executed fresh run to compare against curated v2')
    args = parser.parse_args()
    log = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ENV / 'tests'))
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    failures = []
    if not result.wasSuccessful():
        failures.append('scientific_contract_tests_failed')
    docs = list(ENV.rglob('*.md')) + list((REPO / 'research/clarithromycin-ir-formulation').glob('*.md'))
    checked_links = 0
    for file in docs:
        if any(x in file.parts for x in ['.runs', '.venv', '.cache']):
            continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', file.read_text()):
            url = urlsplit(target)
            if url.scheme or not url.path:
                continue
            dest = (file.parent / unquote(url.path)).resolve()
            checked_links += 1
            if not dest.exists():
                failures.append('broken_link:' + str(file.relative_to(REPO)) + ':' + target)
    patterns = [
        re.compile(r'/(?:home|Users)/[A-Za-z0-9_.-]+'),
        re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'),
        re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),
        re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    ]
    scanned = 0
    for file in public_files():
        if file.suffix == '.docx':
            with zipfile.ZipFile(file) as z:
                content = '\n'.join(z.read(n).decode('utf-8', errors='replace') for n in z.namelist() if n.endswith('.xml'))
        else:
            try:
                content = file.read_text()
            except UnicodeDecodeError:
                continue
        scanned += 1
        if any(p.search(content) for p in patterns):
            failures.append('private_path_or_credential_pattern:' + str(file.relative_to(ENV)))
    sources = json.loads((ENV / 'results/Task - 01/publication_sources.json').read_text())['artifacts']
    for artifact in sources:
        path = ENV / artifact['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact['sha256']:
            failures.append('publication_source_hash_mismatch:' + artifact['path'])
    comparison = None
    if args.run:
        import pandas as pd
        run = args.run.resolve()
        expected = json.loads((ENV / 'benchmark/Task - 01/expected_metrics.json').read_text())
        actual = json.loads((run / 'model_comparison.json').read_text())
        if len(actual) != len(expected['metrics']):
            failures.append('offline_replay_metric_count')
        keyed = {(r['model'], r['split']): r for r in actual}
        for row in expected['metrics']:
            observed = keyed.get((row['model'], row['split']))
            if observed is None:
                failures.append('offline_replay_missing_configuration')
                continue
            for metric in ['RMSE_pp', 'MAE_pp', 'MAPE_percent']:
                if abs(row[metric] - observed[metric]) > expected['tolerance_absolute']:
                    failures.append('offline_replay_metric_difference:' + row['model'] + ':' + row['split'] + ':' + metric)
        pool = json.loads((run / 'expanded_candidates.json').read_text())
        if len(pool) != 28:
            failures.append('offline_replay_recipe_count')
        if not (run / 'run_receipt.json').exists():
            failures.append('offline_replay_missing_actual_runner_receipt')
        comparison = {'status': 'PASSED' if not any(f.startswith('offline_replay') for f in failures) else 'FAILED', 'metric_rows_compared': len(actual), 'tolerance_absolute': expected['tolerance_absolute'], 'valid_recipe_records': len(pool), 'scope': 'real_portable_runner_execution_compared_to_curated_computations_not_lab_replication'}
    receipt = {
        'task_id': 'Task - 01',
        'validated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python': platform.python_version(),
        'unit_tests_run': result.testsRun,
        'unit_tests_failures': len(result.failures),
        'unit_tests_errors': len(result.errors),
        'unit_tests_skipped': len(result.skipped),
        'new_markdown_relative_links_checked': checked_links,
        'public_text_and_docx_files_scanned': scanned,
        'copied_source_artifact_hashes_checked': len(sources),
        'offline_replay': comparison,
        'failures': failures,
        'passed': not failures,
        'scope': 'new_formulation_environment_and_linked_research_only; existing_unrelated_environment_suites_not_rerun',
        'candidate_lab_validation': 'NOT_RUN',
        'scientific_review': 'PENDING',
        'visual_Word_review': 'NOT_PERFORMED',
    }
    out = ENV / 'results/Task - 01'
    # Log tests actually executed, not a fabricated success transcript.
    (out / 'repository_tests.txt').write_text(log.getvalue())
    (out / 'repository_validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(log.getvalue())
    print(json.dumps(receipt, indent=2))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
