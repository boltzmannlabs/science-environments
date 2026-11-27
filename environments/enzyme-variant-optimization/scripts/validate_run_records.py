"""Validate execution identities, configuration hashes and exported evidence without scientific calls."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path


def validate_artifact_names(root: Path, metadata: dict) -> int:
    extensions = {'.csv', '.tsv', '.fasta', '.fa', '.pdb', '.cif', '.npz', '.png', '.jpg', '.jpeg', '.svg'}
    checked = 0
    for item in metadata.get('artifacts', []):
        path = root / item['path']
        if path.suffix.lower() not in extensions:
            continue
        fields = item.get('filename_components')
        if not fields or not item.get('original_filename') or not item.get('original_relative_path'):
            raise ValueError(f'Missing scientific artifact naming provenance: {path}')
        timestamp = fields['timestamp_utc']
        if timestamp is not None and not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z', timestamp):
            raise ValueError(f'Invalid recorded artifact timestamp: {path}')
        expected = '_'.join([fields['artifact_id'], fields['tool_name'], timestamp or 'unreported',
                             fields['run_reference'], fields['model_identifier'], fields['parameters']]) + path.suffix
        if path.name != expected:
            raise ValueError(f'Artifact components/order differ from metadata: {path}')
        if not item.get('source_job_id'):
            suffix = hashlib.sha256(item['original_relative_path'].encode()).hexdigest()[:8]
            if fields['artifact_id'] != 'sha256-' + item['sha256'] + '-' + suffix:
                raise ValueError(f'Export checksum identity does not match bytes/path: {path}')
        if fields['parameters'] == 'metadata':
            reference = item.get('parameters_reference')
            if not reference or not (root / reference.split('#', 1)[0]).is_file():
                raise ValueError(f'Missing recorded parameter reference: {path}')
        checked += 1
    return checked


def validate_configuration_layout(env: Path) -> dict:
    import yaml
    from jsonschema import Draft202012Validator

    root = env / 'config'
    environment = yaml.safe_load((root / 'environment.yaml').read_text())
    schema = json.loads((root / 'schemas/environment.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(environment)
    for name in ('schemas', 'shared', 'tasks'):
        if not (root / name).is_dir() or not any((root / name).iterdir()):
            raise ValueError(f'Missing populated config directory: {name}')
    for key in ('task_catalog', 'configuration_catalog', 'run_registry',
                'results_index', 'specification', 'configuration_schema', 'launch_schema'):
        if not (root / environment[key]).is_file():
            raise ValueError(f'Broken environment configuration reference: {key}')
    for relative in environment['shared_settings'].values():
        yaml.safe_load((root / relative).read_text())
    task_schema = json.loads((root / environment['configuration_schema']).read_text())
    launch_schema = json.loads((root / environment['launch_schema']).read_text())
    for item in (task_schema, launch_schema):
        Draft202012Validator.check_schema(item)
    configs = list((root / 'tasks').glob('task_*/*.json'))
    for path in configs:
        config = json.loads(path.read_text())
        Draft202012Validator(task_schema).validate(config)
        if config['task_id'] != path.parent.name:
            raise ValueError(f'Configuration/task directory mismatch: {path}')
        if 'shared_policy_ref' in config:
            policy = yaml.safe_load((path.parent / config['shared_policy_ref']).read_text())
            if config['llm'] != policy['llm'] or config['goal'] != policy['goal']:
                raise ValueError(f'Shared settings differ from recorded task settings: {path}')
    return {'configurations_validated': len(configs), 'configuration_layout': 'validated'}


def validate(env: Path) -> dict:
    configuration_checks = validate_configuration_layout(env)
    registry = json.loads((env / 'runs/registry.json').read_text())
    seen = set()
    numbers = set()
    artifacts = 0
    named_artifacts = 0
    for entry in registry['runs']:
        key = (entry['task_id'], entry['run_id'])
        if key in seen:
            raise ValueError(f'Duplicate task/run: {key}')
        seen.add(key)
        task, run_id = key
        if not (env / 'tasks' / task / 'task.md').is_file():
            raise ValueError(f'Missing task: {task}')
        number = entry['run_number']
        run_folder = entry['run_folder']
        if not re.fullmatch(r'run_[0-9]{3}_' + re.escape(run_id), run_folder):
            raise ValueError(f'Invalid numbered run folder: {run_folder}')
        if number < 1 or not run_folder.startswith(f'run_{number:03d}_'):
            raise ValueError(f'Run number/folder mismatch: {run_folder}')
        if (task, number) in numbers:
            raise ValueError(f'Duplicate task-local run number: {task}/{number}')
        numbers.add((task, number))
        folder = env / 'runs' / task / run_folder
        run = json.loads((folder / 'run.json').read_text())
        config_path = (folder / run['config_path']).resolve()
        config = json.loads(config_path.read_text())
        digest = hashlib.sha256(config_path.read_bytes()).hexdigest()
        result = (folder / run['result_path']).resolve()
        provenance = json.loads((result / 'provenance.json').read_text())
        named_artifacts += validate_artifact_names(result, provenance)
        for item in (run, config, provenance):
            if item['task_id'] != task:
                raise ValueError(f'Task mismatch: {folder}')
        for item in (run, provenance):
            if item['run_id'] != run_id or item['config_hash'] != digest:
                raise ValueError(f'Run/config mismatch: {folder}')
            if item['run_folder'] != run_folder or item['run_number'] != number:
                raise ValueError(f'Numbered folder metadata mismatch: {folder}')
        if result.name != run_folder:
            raise ValueError(f'Run/result folder mismatch: {folder}')
        if run.get('input_manifest'):
            manifest_path = folder / run['input_manifest']
            if not manifest_path.is_file():
                raise ValueError(f'Missing input manifest: {folder}')
            manifest = json.loads(manifest_path.read_text())
            if not manifest or (set(manifest) <= {'task_id', 'run_id', 'inputs', 'coverage'}
                                and not manifest.get('inputs')):
                raise ValueError(f'Empty input manifest should be consolidated into run.json: {folder}')
        elif not run.get('input_provenance_note'):
            raise ValueError(f'Missing input references or provenance note: {folder}')
        if run.get('launch_settings_snapshot'):
            from jsonschema import Draft202012Validator
            snapshot = folder / run['launch_settings_snapshot']
            if hashlib.sha256(snapshot.read_bytes()).hexdigest() != run['launch_settings_sha256']:
                raise ValueError(f'Launch snapshot checksum mismatch: {folder}')
            schema = json.loads((env / 'config/schemas/launch_settings.schema.json').read_text())
            Draft202012Validator(schema).validate(json.loads(snapshot.read_text()))
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
    for record in (env / 'benchmark/evaluation').glob('*/comparisons/provenance.json'):
        provenance = json.loads(record.read_text())
        named_artifacts += validate_artifact_names(record.parent, provenance)
        for item in provenance.get('artifacts', []):
            path = record.parent / item['path']
            if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError(f'Benchmark artifact checksum mismatch: {path}')
    return {**configuration_checks, 'runs': len(seen), 'tasks': len({t for t, _ in seen}),
            'artifacts_verified': artifacts,
            'normalized_artifact_names_validated': named_artifacts,
            'scope': 'Metadata, paths, hashes and declared naming/fallback rules; not scientific qualification or maintainer approval.'}


if __name__ == '__main__':
    print(json.dumps(validate(Path(__file__).resolve().parents[1]), indent=2))
