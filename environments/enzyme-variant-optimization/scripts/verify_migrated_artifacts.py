"""Verify published original Git blobs and current exported artifacts with SHA-256."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess


def verify(env: Path, report: Path | None = None) -> dict:
    env = env.resolve()
    repo = Path(subprocess.check_output(['git', '-C', str(env), 'rev-parse', '--show-toplevel'], text=True).strip())
    prefix = str(env.relative_to(repo)) + '/'
    records = sorted((env / 'results').rglob('provenance.json')) + sorted((env / 'benchmark/evaluation').rglob('provenance.json'))
    if not records:
        raise ValueError('No migrated artifact provenance records found')
    count = preserved = transformed = scientific = 0
    originals = {}
    rows = []
    for record in records:
        metadata = json.loads(record.read_text())
        for artifact in metadata['artifacts']:
            evidence = artifact['migration_evidence']
            original_path = evidence['original_path']
            if not original_path.startswith(prefix) or '..' in Path(original_path).parts:
                raise ValueError(f'Original path outside environment: {original_path}')
            commit = evidence['source_git_commit']
            if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
                raise ValueError('Source must be an immutable full Git commit ID')
            key = (commit, original_path)
            if key not in originals:
                try:
                    data = subprocess.check_output(['git', '-C', str(repo), 'show', f'{commit}:{original_path}'], stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as exc:
                    raise ValueError(f'Original Git blob unavailable: {commit}:{original_path}; fetch the PR history before verification') from exc
                originals[key] = hashlib.sha256(data).hexdigest()
            original = originals[key]
            current_path = (record.parent / artifact['path']).resolve()
            if not current_path.is_relative_to(record.parent.resolve()):
                raise ValueError(f'Current path escapes package: {current_path}')
            current = hashlib.sha256(current_path.read_bytes()).hexdigest()
            if original != evidence['original_sha256'] or current != artifact['sha256']:
                raise ValueError(f'Original/current checksum mismatch: {current_path}')
            same = original == current
            if same != evidence['content_preserved']:
                raise ValueError(f'Incorrect content-preserved declaration: {current_path}')
            expected_kind = 'byte_preserving_move_or_rename' if same else 'documentation_or_metadata_update'
            if evidence['change_kind'] != expected_kind:
                raise ValueError(f'Incorrect migration change kind: {current_path}')
            if artifact.get('filename_components'):
                if not same:
                    raise ValueError(f'Scientific data changed during migration: {current_path}')
                scientific += 1
            rows.append({'source_git_commit': commit, 'original_path': original_path, 'current_path': str(current_path.relative_to(repo)), 'original_sha256': original, 'current_sha256': current, 'content_preserved': same})
            count += 1
            preserved += same
            transformed += not same
    if report is not None:
        with report.open('x', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    return {'artifact_packages': len(records), 'original_and_current_checksums_verified': count,
            'byte_preserved': preserved, 'document_or_metadata_updates': transformed,
            'scientific_artifacts_byte_preserved': scientific,
            'evidence': 'Each provenance artifact records its original Git commit/path/SHA256 and current path/SHA256.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path, help='Optional new CSV file with original/current paths and hashes; existing files are never overwritten.')
    args = parser.parse_args()
    print(json.dumps(verify(args.environment, args.report), indent=2))
