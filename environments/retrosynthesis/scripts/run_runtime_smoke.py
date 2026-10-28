#!/usr/bin/env python3
"""Reproduce local Step 3 runtime checks with injected backends and no inference."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from synthesis_route_gym.agent_runner import AgentBudget, BudgetExhausted, SharedLedger, run_agent_scientist
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.episode_store import EpisodeStore
from synthesis_route_gym.observation import task_prompt
from synthesis_route_gym.planning import environment_tool_schemas
from synthesis_route_gym.schemas import InventoryItem, Task


def _write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def _fixture():
    return Task(task_id='runtime-fixture', target='CCO', inventory=(InventoryItem(smiles='CCO'),))


def _reply(kwargs, request, tokens=3):
    return {'model': kwargs['profile'].model, 'provider': kwargs['profile'].provider,
            'completed': True, 'final_response': 'Deterministic runtime fixture; no chemistry claim.',
            'messages': [], 'usage': {'total_tokens': tokens},
            'token_confirmations': {request: tokens}}


class _Interrupted(BaseException):
    """Simulated process interruption; deliberately bypass ordinary stage handling."""


def _recovery(output, home):
    env_store = EpisodeStore(output / 'environment')
    env = SynthesisRouteEnv(_fixture(), store=env_store)
    first_action = env.dispatch('inspect', {}, action_id='fixture-inspect')
    runtime_store, revision = EpisodeStore(output / 'runtime'), [None]
    roles, settlements = [], []

    def checkpoint(state):
        revision[0] = (runtime_store.initialize(state) if revision[0] is None
                       else runtime_store.commit(state, expected_revision=revision[0]))

    class Backend:
        def __init__(self, interrupt=False):
            self.interrupt = interrupt

        def run(self, **kwargs):
            roles.append(kwargs['role'])
            request = kwargs['ledger'].claim_model_call(estimated_input_tokens=50)
            saved, _ = runtime_store.load()
            assert saved['ledger']['counts']['model_calls'] == len(roles)
            if self.interrupt and kwargs['role'] == 'condition_optimisation_scientist':
                raise _Interrupted()
            before = kwargs['ledger'].snapshot()
            kwargs['ledger'].settle_request(request, 3)
            after = kwargs['ledger'].snapshot()
            settlements.append({'reserved_before': before['reserved_tokens'],
                                'reserved_after': after['reserved_tokens']})
            if kwargs['role'] == 'main':
                kwargs['executor']('submit', {'route_ids': []})
            return _reply(kwargs, request)

    options = {'tool_schemas': environment_tool_schemas(), 'profile_home': home,
               'mode': 'specialists', 'budget': AgentBudget(max_model_calls=8),
               'checkpoint': checkpoint}
    prompt = task_prompt(env)
    try:
        run_agent_scientist(prompt, env.dispatch, backend=Backend(interrupt=True), **options)
    except _Interrupted:
        pass
    else:
        raise AssertionError('The simulated interruption did not occur')
    saved, _ = runtime_store.load()
    before = saved['ledger']['counts']
    recovered = SynthesisRouteEnv.resume(env_store, expected_task=_fixture())
    assert recovered.dispatch('inspect', {}, action_id='fixture-inspect') == first_action
    duplicate_no_charge = recovered.inspect()['usage']['actions'] == 1
    result = run_agent_scientist(prompt, recovered.dispatch, backend=Backend(), resume_state=saved, **options)
    final_saved, _ = runtime_store.load()
    assert final_saved['ledger']['deadline_unix'] == saved['ledger']['deadline_unix']
    assert result['ledger']['actual_tokens'] == 12
    assert result['ledger']['reserved_tokens'] == 50
    assert result['completed'] and result['submission_status'] == 'submitted'
    _write(output / 'runtime-result.json', result)
    _write(output / 'environment-result.json', recovered.export())
    return ({'model_calls_before_resume': before['model_calls'],
             'model_calls_after_resume': result['ledger']['model_calls'],
             'actual_tokens_after_resume': result['ledger']['actual_tokens'],
             'reserved_tokens_after_resume': result['ledger']['reserved_tokens'],
             'unresolved_reservation_retained': result['ledger']['reserved_tokens'] == 50,
             'deadline_preserved': True, 'submission_status': result['submission_status'],
             'submission_kind': 'explicit_empty_shortlist',
             'finished_specialist_not_repeated': roles.count('retrosynthesis_strategist') == 1,
             'role_execution_order': roles},
            {'reserved_tokens_after_response': settlements[0]['reserved_after'],
             'reserved_tokens_before_response': settlements[0]['reserved_before']},
            {'duplicate_action_no_new_charge': duplicate_no_charge})


def _finalization(home):
    limits = AgentBudget(max_model_calls=4, max_tool_calls=2, max_total_tokens=100,
                         finalization_token_fraction=0.3)
    ledger = SharedLedger(limits)
    ledger.set_stage('retrosynthesis_strategist')
    try:
        ledger.claim_model_call(estimated_input_tokens=71)
    except BudgetExhausted:
        rejected = True
    else:
        raise AssertionError('Optional work entered protected allowance')
    env = SynthesisRouteEnv(_fixture())

    class Backend:
        def run(self, **kwargs):
            request = kwargs['ledger'].claim_model_call(estimated_input_tokens=30)
            kwargs['ledger'].settle_request(request, 1)
            if kwargs['role'] == 'main':
                assert kwargs['ledger'].finalization_due()
                kwargs['executor']('submit', {'route_ids': []})
            return _reply(kwargs, request, tokens=1)

    result = run_agent_scientist(task_prompt(env), env.dispatch,
        tool_schemas=environment_tool_schemas(), profile_home=home, budget=limits,
        mode='specialists', backend=Backend())
    assert result['completed'] and result['ledger']['model_calls'] == 4
    return {'optional_work_rejected': rejected, 'main_submitted': result['submission_status'] == 'submitted',
            'model_calls': result['ledger']['model_calls'], 'model_call_cap': limits.max_model_calls,
            'charged_tokens': result['ledger']['charged_tokens'], 'no_host_submission_fallback': True}


def _cancellation(output):
    entered, release, finished = threading.Event(), threading.Event(), threading.Event()

    def blocked(*args):
        entered.set()
        try:
            if not release.wait(5):
                raise TimeoutError('Smoke callback release missing')
            return {'status': 'ok', 'predictions': []}
        finally:
            finished.set()

    env = SynthesisRouteEnv(_fixture(), expand=blocked, store=EpisodeStore(output / 'cancelled'))
    replies = []
    thread = threading.Thread(target=lambda: replies.append(
        env.dispatch('expand', {'smiles': 'CCO'}, action_id='cancelled-expansion')), daemon=True)
    thread.start()
    try:
        assert entered.wait(2), 'Scientific callback did not start'
        started = time.monotonic()
        env.cancel('Deterministic smoke cancellation')
        thread.join(1)
        elapsed = time.monotonic() - started
        assert not thread.is_alive() and elapsed < 1
        assert replies[0]['status'] == 'cancelled'
        events = env.export()['events']
    finally:
        release.set()
        assert finished.wait(2), 'Smoke callback did not clean up'
        thread.join(1)
    unchanged = env.export()['events'] == events
    assert unchanged
    return {'caller_returned_within_bound': True, 'bound_seconds': 1,
            'observed_seconds': elapsed, 'late_result_did_not_change_events': unchanged,
            'scope': 'bounded_caller_wait_and_state_fencing; callback_released_cooperatively',
            'external_job_termination_tested': False}


def measure_public_prompt(public, expected_manifest_sha256):
    """Read one smoke record and stock only; do not inspect reserved target files."""
    public = Path(public)
    manifest_bytes = (public / 'manifest.json').read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_manifest_sha256:
        raise ValueError('Public manifest hash mismatch')
    manifest = json.loads(manifest_bytes)
    if manifest.get('bundle_kind') != 'public':
        raise ValueError('Only public inputs are eligible')
    entries = sorted((e for e in manifest['tasks'] if e['partition'] == 'smoke'
                      and e['track'] == 'reference_route'), key=lambda e: e['task_id'])
    if not entries:
        raise ValueError('No public smoke task available')
    selected = None
    for entry in entries:
        if re.fullmatch(r'[A-Za-z0-9_.-]+', entry['task_id']) is None:
            raise ValueError('Invalid public task identifier')
        name = 'tasks/' + entry['task_id'] + '.json'
        raw = (public / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest['files'][name]:
            raise ValueError('Public task hash mismatch')
        candidate = json.loads(raw)
        if not candidate.get('inventory_exclusions'):
            selected = candidate
            break
    if selected is None or selected.get('partition') != 'smoke':
        raise ValueError('Full-stock smoke task required')
    stock_bytes = (public / 'inventory.json').read_bytes()
    if hashlib.sha256(stock_bytes).hexdigest() != manifest['files']['inventory.json']:
        raise ValueError('Public inventory hash mismatch')
    started = time.monotonic()
    task = Task(task_id=selected['task_id'], target=selected['target'],
                constraints=selected['constraints'], budget=selected['budget'],
                inventory=tuple(InventoryItem(smiles=s) for s in json.loads(stock_bytes)))
    env = SynthesisRouteEnv(task)
    full = len(task.model_dump_json().encode())
    compact = len(task_prompt(env).encode())
    return {'task_id': task.task_id, 'inventory_count': len(task.inventory),
            'full_task_bytes': full, 'compact_prompt_bytes': compact,
            'byte_reduction_fraction': 1 - compact / full,
            'materialization_and_measurement_seconds': time.monotonic() - started,
            'public_manifest_sha256': expected_manifest_sha256,
            'read_scope': 'public_manifest_selected_smoke_task_and_inventory_only',
            'scope': 'serialized_byte_measurement_not_provider_token_or_search_gain'}


def run_smoke(output, *, public_bundle=None, public_manifest_sha256=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='srg-runtime-profile-') as temporary:
        home = Path(temporary)
        (home / 'config.yaml').write_text('model:\n  default: smoke-double\n  provider: local-double\n')
        recovery, settlement, duplicate = _recovery(output, home)
        finalization = _finalization(home)
    cancellation = _cancellation(output)
    prompt = (measure_public_prompt(public_bundle, public_manifest_sha256)
              if public_bundle is not None else {'status': 'not_requested'})
    result = {'schema_version': 'srg03-runtime-smoke-v1', 'status': 'passed',
              'scope': 'deterministic_runtime_contracts_only',
              'live_model_calls': 0, 'scientific_model_inferences': 0,
              'backend': 'injected_test_backend', 'real_profile_modified': False,
              'scientific_improvement_claimed': False, 'hidden_evaluator_data_accessed': False,
              'runtime_recovery': recovery, 'immediate_settlement': settlement,
              'idempotency': duplicate, 'finalization': finalization,
              'cancellation': cancellation, 'public_prompt_measurement': prompt,
              'elapsed_seconds': time.monotonic() - started,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    _write(output / 'receipt.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--public-bundle', type=Path)
    parser.add_argument('--public-manifest-sha256')
    args = parser.parse_args(argv)
    if bool(args.public_bundle) != bool(args.public_manifest_sha256):
        parser.error('--public-bundle and --public-manifest-sha256 must be supplied together')
    result = run_smoke(args.output, public_bundle=args.public_bundle,
                       public_manifest_sha256=args.public_manifest_sha256)
    print(json.dumps({'status': result['status'], 'receipt': str(args.output / 'receipt.json'),
                      'scope': result['scope'], 'live_model_calls': 0}))


if __name__ == '__main__':
    main()
