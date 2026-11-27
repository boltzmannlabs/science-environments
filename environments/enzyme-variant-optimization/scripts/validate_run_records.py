"""Validate execution identities, configuration hashes and exported evidence without scientific calls."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def validate(env: Path) -> dict:
    registry = json.loads((env / 'runs/registry.json').read_text())
    seen = set()
    artifacts = 0
    for entry in registry['runs']:
        key = (entry['task_id'], entry['run_id'])
        if key in seen:
            raise ValueError(f'Duplicate task/run: {key}')
        seen.add(key)
        task, run_id = key
        if not (env / 'tasks' / task / 'task.md').is_file():
            raise ValueError(f'Missing task: {task}')
        folder = env / 'runs' / task / run_id
        run = json.loads((folder / 'run.json').read_text())
        config_path = (folder / run['config_path']).resolve()
        config = json.loads(config_path.read_text())
        digest = hashlib.sha256(config_path.read_bytes()).hexdigest()
        result = (folder / run['result_path']).resolve()
        provenance = json.loads((result / 'provenance.json').read_text())
        for item in (run, config, provenance):
            if item['task_id'] != task:
                raise ValueError(f'Task mismatch: {folder}')
        for item in (run, provenance):
            if item['run_id'] != run_id or item['config_hash'] != digest:
                raise ValueError(f'Run/config mismatch: {folder}')
        if run['status'] != provenance['execution_status']:
            raise ValueError(f'Status mismatch: {folder}')
        if not (folder / run['input_manifest']).is_file():
            raise ValueError(f'Missing input manifest: {folder}')
        if (result / provenance['run_record']).resolve() != folder / 'run.json':
            raise ValueError(f'Broken run backlink: {result}')
        listed = set()
        for artifact in provenance['artifacts']:
            path = (result / artifact['path']).resolve()
            if not path.is_relative_to(result.resolve()):
                raise ValueError(f'Artifact outside result directory: {path}')
            if hashlib.sha256(path.read_bytes()).hexdigest() != artifact['sha256']:
                raise ValueError(f'Artifact checksum mismatch: {path}')
            listed.add(artifact['path'])
            artifacts += 1
        actual = {str(p.relative_to(result)) for p in result.rglob('*')
                  if p.is_file() and p.name != 'provenance.json'}
        if actual != listed:
            raise ValueError(f'Artifact inventory mismatch: {result}')
    return {'runs': len(seen), 'tasks': len({t for t, _ in seen}),
            'artifacts_verified': artifacts,
            'scope': 'Metadata, identities, paths and hashes; not scientific qualification or full filename-format approval.'}


if __name__ == '__main__':
    print(json.dumps(validate(Path(__file__).resolve().parents[1]), indent=2))
