"""Validate execution identities, configuration hashes and exported evidence without scientific calls."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime


def resolve_reference(base: Path, relative: str, boundary: Path) -> Path:
    """All references are relative to their declaring file's directory, never cwd."""
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ':' in relative:
        raise ValueError(f'Expected a relative local reference: {relative!r}')
    path = (base / relative).resolve()
    if not path.is_relative_to(boundary.resolve()):
        raise ValueError(f'Reference escapes its package: {relative}')
    return path


def validate_artifact_names(root: Path, metadata: dict) -> int:
    extensions = {'.csv', '.tsv', '.fasta', '.fa', '.pdb', '.cif', '.npz', '.png', '.jpg', '.jpeg', '.svg'}
    checked = 0
    for item in metadata.get('artifacts', []):
        path = resolve_reference(root, item['path'], root)
        if path.suffix.lower() not in extensions:
            continue
        fields = item.get('filename_components')
        if not fields or not item.get('original_filename') or not item.get('original_relative_path'):
            raise ValueError(f'Missing scientific artifact naming provenance: {path}')
        expected_fields = {'artifact_id', 'tool_name', 'timestamp_utc', 'run_reference', 'model_identifier', 'parameters'}
        if set(fields) != expected_fields:
            raise ValueError(f'Incomplete or unknown filename components: {path}')
        missing = item.get('missing_source_fields')
        expected_missing = {key for key in ('tool_name', 'timestamp_utc', 'model_identifier', 'parameters')
                            if fields[key] is None or fields[key] == 'unreported'}
        if not isinstance(missing, list) or len(missing) != len(set(missing)) or set(missing) != expected_missing:
            raise ValueError(f'Missing-source declarations differ from filename components: {path}')
        for key in expected_fields - {'timestamp_utc'}:
            if not isinstance(fields[key], str) or not re.fullmatch(r'[a-z0-9.+-]+', fields[key]):
                raise ValueError(f'Invalid filename component {key}: {path}')
        if fields['run_reference'] != metadata['run_id'].rsplit('_', 1)[-1]:
            raise ValueError(f'Artifact belongs to another run: {path}')
        original = resolve_reference(root, item['original_relative_path'], root)
        if original.name != item['original_filename']:
            raise ValueError(f'Original filename/path disagree: {path}')
        timestamp = fields['timestamp_utc']
        if timestamp is not None and not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z', timestamp):
            raise ValueError(f'Invalid recorded artifact timestamp: {path}')
        if timestamp is not None:
            datetime.strptime(timestamp, '%Y%m%dT%H%M%SZ')
        expected = '_'.join([fields['artifact_id'], fields['tool_name'], timestamp or 'unreported',
                             fields['run_reference'], fields['model_identifier'], fields['parameters']]) + path.suffix
        if path.name != expected:
            raise ValueError(f'Artifact components/order differ from metadata: {path}')
        suffix = hashlib.sha256(item['original_relative_path'].encode()).hexdigest()[:8]
        if item.get('source_job_id'):
            source_id = re.sub(r'[^a-z0-9.+-]+', '-', item['source_job_id'].lower()).strip('-')
            if fields['artifact_id'] != source_id + '-' + suffix:
                raise ValueError(f'Native job identity does not match filename: {path}')
        else:
            if fields['artifact_id'] != 'sha256-' + item['sha256'] + '-' + suffix:
                raise ValueError(f'Export checksum identity does not match bytes/path: {path}')
        if fields['parameters'] not in ('metadata', 'unreported'):
            raise ValueError(f'Unknown parameter provenance convention: {path}')
        if fields['parameters'] == 'unreported' and item.get('parameters_reference'):
            raise ValueError(f'Parameters declared missing but a source is claimed: {path}')
        if fields['parameters'] == 'metadata':
            reference = item.get('parameters_reference')
            if not reference or not (root / reference.split('#', 1)[0]).is_file():
                raise ValueError(f'Missing recorded parameter reference: {path}')
            target, fragment = reference.split('#', 1)
            env = next((p for p in (root, *root.parents) if (p / 'config/environment.yaml').is_file()), root)
            ledger_path = resolve_reference(root, target, env)
            ledger = json.loads(ledger_path.read_text())
            entries = ledger if isinstance(ledger, list) else next((ledger[k] for k in ('jobs', 'submissions', 'entries') if isinstance(ledger.get(k), list)), [])
            if not re.fullmatch(r'entry-[0-9]+', fragment):
                raise ValueError(f'Invalid parameter entry reference: {path}')
            index = int(fragment.removeprefix('entry-'))
            if index >= len(entries) or not isinstance(entries[index].get('payload', entries[index].get('inputparams')), dict):
                raise ValueError(f'Parameter entry has no recorded payload: {path}')
            entry = entries[index]
            job_id = next((entry[k] for k in ('doc_id', 'docId', 'docid', 'job_id', '_id') if entry.get(k)), None)
            if job_id != item.get('source_job_id'):
                raise ValueError(f'Parameter reference points to a different native job: {path}')
        checked += 1
    return checked


def validate_usage_accounting(run: dict) -> None:
    accounting = run['usage_accounting']
    parents = accounting['parent_session_ids']
    specialists = accounting['specialist_session_ids']
    if parents != run['native_session_ids'] or len(set(parents)) != len(parents):
        raise ValueError('Parent accounting must match the deduplicated continuation lineage')
    if len(set(specialists)) != len(specialists) or set(parents) & set(specialists):
        raise ValueError('Parent and specialist accounting overlap')
    if set(accounting['excluded_associated_session_ids']) & (set(parents) | set(specialists)):
        raise ValueError('Excluded associated sessions were counted')
    fields = ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'reasoning_tokens', 'tool_call_count')
    for key, expected_count in (('parent_lineage', len(parents)), ('delegated_specialists', len(specialists)),
                                ('parent_plus_specialists', len(parents) + len(specialists))):
        total = accounting[key]
        if total['session_count'] != expected_count or any(type(total[f]) is not int or total[f] < 0 for f in fields):
            raise ValueError('Invalid session usage counts')
        if total['token_total_excluding_reasoning_subset'] != sum(total[f] for f in fields[:4]):
            raise ValueError('Token total double-counts reasoning or differs from components')
    for field in fields:
        if accounting['parent_plus_specialists'][field] != accounting['parent_lineage'][field] + accounting['delegated_specialists'][field]:
            raise ValueError('Cumulative usage differs from parent plus specialist usage')


def validate_benchmark_identity(env: Path, record: Path, provenance: dict) -> None:
    run_path = resolve_reference(record.parent, provenance['run_record'], env)
    result_path = resolve_reference(record.parent, provenance['result_record'], env)
    linked_run = json.loads(run_path.read_text())
    linked_result = json.loads(result_path.read_text())
    if (provenance.get('approach') != 'agent-alone' or provenance.get('source_kind') != 'historical_publication'
            or linked_run['approach'] != 'agent-alone' or linked_run['source_kind'] != 'historical_publication'):
        raise ValueError(f'Benchmark must use its declared historical agent-alone run: {record}')
    for linked in (linked_run, linked_result):
        if (linked['task_id'], linked['run_id']) != (provenance['task_id'], provenance['run_id']):
            raise ValueError(f'Benchmark links a different task/run: {record}')
    if run_path != resolve_reference(result_path.parent, linked_result['run_record'], env):
        raise ValueError(f'Benchmark run/result links disagree: {record}')


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
        if not resolve_reference(root, environment[key], env).is_file():
            raise ValueError(f'Broken environment configuration reference: {key}')
    for relative in environment['shared_settings'].values():
        yaml.safe_load(resolve_reference(root, relative, env).read_text())
    task_schema = json.loads(resolve_reference(root, environment['configuration_schema'], env).read_text())
    launch_schema = json.loads(resolve_reference(root, environment['launch_schema'], env).read_text())
    for item in (task_schema, launch_schema):
        Draft202012Validator.check_schema(item)
    configs = list((root / 'tasks').glob('task_*/*.json'))
    for path in configs:
        config = json.loads(path.read_text())
        Draft202012Validator(task_schema).validate(config)
        if config['task_id'] != path.parent.name:
            raise ValueError(f'Configuration/task directory mismatch: {path}')
        if 'shared_policy_ref' in config:
            policy = yaml.safe_load(resolve_reference(path.parent, config['shared_policy_ref'], env).read_text())
            if config['llm'] != policy['llm'] or config['goal'] != policy['goal']:
                raise ValueError(f'Shared settings differ from recorded task settings: {path}')
    return {'configurations_validated': len(configs), 'configuration_layout': 'validated'}


def validate(env: Path) -> dict:
    env = env.resolve()
    configuration_checks = validate_configuration_layout(env)
    registry = json.loads((env / 'runs/registry.json').read_text())
    seen = set()
    numbers = set()
    artifacts = 0
    named_artifacts = 0
    usage_owners = {}
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
        validate_usage_accounting(run)
        accounting = run['usage_accounting']
        for session_id in accounting['parent_session_ids'] + accounting['specialist_session_ids']:
            identity = (accounting['profile'], session_id)
            if identity in usage_owners:
                raise ValueError(f'Usage session attributed to multiple runs: {identity}')
            usage_owners[identity] = key
        config_path = resolve_reference(folder, run['config_path'], env)
        config = json.loads(config_path.read_text())
        digest = hashlib.sha256(config_path.read_bytes()).hexdigest()
        result = resolve_reference(folder, run['result_path'], env)
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
            manifest_path = resolve_reference(folder, run['input_manifest'], env)
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
            snapshot = resolve_reference(folder, run['launch_settings_snapshot'], env)
            if hashlib.sha256(snapshot.read_bytes()).hexdigest() != run['launch_settings_sha256']:
                raise ValueError(f'Launch snapshot checksum mismatch: {folder}')
            schema = json.loads((env / 'config/schemas/launch_settings.schema.json').read_text())
            Draft202012Validator(schema).validate(json.loads(snapshot.read_text()))
        if resolve_reference(result, provenance['run_record'], env) != folder / 'run.json':
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
        if len(listed) != len(provenance['artifacts']) or actual != listed:
            raise ValueError(f'Artifact inventory mismatch: {result}')
    for record in (env / 'benchmark/evaluation').glob('*/comparisons/provenance.json'):
        provenance = json.loads(record.read_text())
        validate_benchmark_identity(env, record, provenance)
        named_artifacts += validate_artifact_names(record.parent, provenance)
        listed = {item['path'] for item in provenance.get('artifacts', [])}
        actual = {str(p.relative_to(record.parent)) for p in record.parent.rglob('*') if p.is_file() and p.name != 'provenance.json'}
        if len(listed) != len(provenance['artifacts']) or actual != listed:
            raise ValueError(f'Benchmark artifact inventory mismatch: {record}')
        for item in provenance.get('artifacts', []):
            path = resolve_reference(record.parent, item['path'], record.parent)
            if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError(f'Benchmark artifact checksum mismatch: {path}')
    return {**configuration_checks, 'runs': len(seen), 'tasks': len({t for t, _ in seen}),
            'artifacts_verified': artifacts,
            'normalized_artifact_names_validated': named_artifacts,
            'scope': 'Metadata, paths, hashes and declared naming/fallback rules; not scientific qualification or maintainer approval.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(validate(args.environment), indent=2))
