"""The Step 3 receipt is a local runtime test, never a chemistry result."""
import hashlib
import importlib.util
import json
from pathlib import Path
import socket

import pytest


def script():
    path = Path(__file__).parents[1] / 'scripts' / 'run_runtime_smoke.py'
    spec = importlib.util.spec_from_file_location('runtime_smoke', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_smoke_reproduces_durable_runtime_contracts_without_network(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Smoke must never open a network connection')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    output = tmp_path / 'smoke'
    result = script().run_smoke(output)
    assert result['scope'] == 'deterministic_runtime_contracts_only'
    assert result['live_model_calls'] == result['scientific_model_inferences'] == 0
    assert result['runtime_recovery']['model_calls_before_resume'] == 2
    assert result['runtime_recovery']['model_calls_after_resume'] == 5
    assert result['runtime_recovery']['unresolved_reservation_retained']
    assert result['runtime_recovery']['submission_status'] == 'submitted'
    assert result['runtime_recovery']['finished_specialist_not_repeated']
    assert result['immediate_settlement']['reserved_tokens_after_response'] == 0
    assert result['finalization']['optional_work_rejected']
    assert result['finalization']['main_submitted']
    assert result['idempotency']['duplicate_action_no_new_charge']
    assert result['cancellation']['caller_returned_within_bound']
    assert result['cancellation']['late_result_did_not_change_events']
    assert json.loads((output / 'receipt.json').read_text()) == result
    with pytest.raises(FileExistsError):
        script().run_smoke(output)


def test_prompt_measurement_reads_only_selected_public_smoke_record(tmp_path):
    public = tmp_path / 'public'
    (public / 'tasks').mkdir(parents=True)
    stock = json.dumps(['CCO', 'O']).encode()
    task = json.dumps({'task_id': 'smoke-one', 'partition': 'smoke',
                       'track': 'reference_route', 'target': 'CCO',
                       'inventory_exclusions': [], 'constraints': {}, 'budget': {}}).encode()
    (public / 'inventory.json').write_bytes(stock)
    (public / 'tasks' / 'smoke-one.json').write_bytes(task)
    (public / 'tasks' / 'reserved-final.json').write_text('MUST NOT BE READ')
    manifest = {'bundle_kind': 'public', 'tasks': [
        {'task_id': 'reserved-final', 'partition': 'final', 'track': 'reference_route'},
        {'task_id': 'smoke-one', 'partition': 'smoke', 'track': 'reference_route'}],
        'files': {'inventory.json': hashlib.sha256(stock).hexdigest(),
                  'tasks/smoke-one.json': hashlib.sha256(task).hexdigest()}}
    raw = json.dumps(manifest).encode()
    (public / 'manifest.json').write_bytes(raw)
    result = script().measure_public_prompt(public, hashlib.sha256(raw).hexdigest())
    assert result['task_id'] == 'smoke-one'
    assert result['inventory_count'] == 2
    assert result['read_scope'] == 'public_manifest_selected_smoke_task_and_inventory_only'
    assert result['full_task_bytes'] > 0 and result['compact_prompt_bytes'] > 0
    with pytest.raises(ValueError, match='hash'):
        script().measure_public_prompt(public, '0' * 64)
