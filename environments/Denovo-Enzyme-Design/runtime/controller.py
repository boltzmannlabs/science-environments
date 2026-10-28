#!/usr/bin/env python3
"""Resumable stage controller using an existing agent harness."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time
import uuid
import yaml

from agents import invoke
from assessment import check_assessment_models
from reporting import write_bundle
from contracts import (ROOT, STAGES, EXPECTED, GROUPS, load_json, digest, object_hash,
                       verify_artifact, verify_nested, check_generation, check_request,
                       check_candidates, qualified_ids)

DEFAULT_POLICY = {
    'active_seconds': 7200, 'cpu_core_hours': 16, 'gpu_hours': 1,
    'service_spend_usd': 0, 'call_timeout_seconds': 900,
    'max_stage_attempts': 3, 'max_repairs_per_stage': 2,
    'max_review_attempts': 2, 'poll_seconds': 5, 'max_pending_polls': 120,
    'deadline_utc': None,
}
TERMINAL = {'QUALIFIED', 'PARTIAL', 'NO_QUALIFYING_DESIGNS', 'BLOCKED',
            'NEEDS_INPUT', 'BUDGET_EXHAUSTED'}
IMPLEMENTATION_FILES = ['runtime/controller.py', 'runtime/agents.py', 'runtime/contracts.py', 'runtime/reporting.py',
                        'runtime/assessment.py', 'runtime/structure_preparation.py',
                        'config/environment.yaml', 'config/request.schema.json',
                        'config/generation.schema.json', 'config/protocol.schema.json']
USER_INPUT_ITEMS = {
    'essential_goal_or_reaction_ambiguity_unresolvable_from_evidence':
        ['reaction', 'substrate', 'product', 'stereochemistry', 'scientific_objective'],
    'required_access_or_resources_outside_existing_authorization':
        ['tool_access', 'resource_authorization'],
    'incompatible_explicit_user_requirements': ['explicit_requirements'],
}


def user_input_error(value: object) -> str | None:
    """Check escalation scope; the independent reviewer still checks its evidence."""
    if not isinstance(value, dict):
        return 'needs_input requires a structured input_request'
    reason = value.get('reason_code')
    if not isinstance(reason, str) or reason not in USER_INPUT_ITEMS:
        return 'This reason is not an allowed user question'
    if value.get('item') not in USER_INPUT_ITEMS[reason]:
        return 'Routine settings, chemistry preparation and technical repairs belong to the agent'
    for key in ('question', 'why_unresolved'):
        if not isinstance(value.get(key), str) or not value[key].strip():
            return f'input_request requires {key}'
    attempts = value.get('resolution_attempts')
    if not isinstance(attempts, list) or not attempts:
        return 'Check the request, run policy and available evidence before escalating'
    if any(not isinstance(a, dict) or any(not isinstance(a.get(k), str) or not a[k].strip()
           for k in ('source', 'finding')) for a in attempts):
        return 'Each resolution attempt requires an inspected source and its finding'
    return None


def job_identities(handles: object, *, allow_empty: bool = False) -> set[tuple[str, str]]:
    if not isinstance(handles, list) or (not handles and not allow_empty):
        raise ValueError('Remote work needs a nonempty list of original job handles')
    identities = set()
    for handle in handles:
        if not isinstance(handle, dict) or any(
                not isinstance(handle.get(k), str) or not handle[k].strip() for k in ('provider', 'id')):
            raise ValueError('Each remote job needs its actual provider and ID')
        identity = (handle['provider'], handle['id'])
        if identity in identities:
            raise ValueError('Duplicate remote job identity')
        identities.add(identity)
    return identities


def check_poll_response(handles: list, result: dict) -> None:
    expected = job_identities(handles)
    if job_identities(result.get('polled_job_handles')) != expected:
        raise ValueError('Poll receipt does not identify exactly the original jobs')
    remaining = job_identities(result.get('job_handles', []), allow_empty=True)
    if result.get('status') == 'pending':
        if remaining != expected:
            raise ValueError('Pending poll cannot replace or discard original job handles')
    elif result.get('status') in {'completed', 'failed'}:
        if remaining:
            raise ValueError('Terminal poll must not leave outstanding jobs unresolved')
    else:
        raise ValueError('Poll must report pending, completed or failed for the original jobs')


def default_policy() -> dict:
    fallback = yaml.safe_load((ROOT / 'config/environment.yaml').read_text())['autonomy']['fallback_pilot']
    budget = fallback['budget']
    return {**DEFAULT_POLICY, 'active_seconds': budget['wall_time_hours'] * 3600,
            'cpu_core_hours': budget['cpu_core_hours'], 'gpu_hours': budget['gpu_hours'],
            'service_spend_usd': fallback['additional_service_spend_usd']}


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


@contextmanager
def run_lock(root: Path):
    with (root / '.controller.lock').open('a') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Another controller already owns this run') from exc
        yield


def validate_policy(policy: dict) -> None:
    if set(policy) != set(DEFAULT_POLICY):
        raise ValueError('Unknown or missing policy field')
    for key, value in policy.items():
        if key == 'deadline_utc':
            if value is not None:
                d = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if d.tzinfo is None:
                    raise ValueError('deadline_utc must include a timezone')
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f'Invalid policy limit: {key}')
        if key not in {'gpu_hours', 'service_spend_usd', 'poll_seconds'} and value == 0:
            raise ValueError(f'Positive limit required: {key}')
        if key.startswith('max_') and not isinstance(value, int):
            raise ValueError(f'Integer limit required: {key}')


def initialize(root: Path, request: str, inputs: list[Path], agent_config: dict,
               policy: dict | None = None, condition: str = 'agent_selected') -> dict:
    if not request.strip():
        raise ValueError('A scientific request is required')
    p = {**default_policy(), **(policy or {})}
    validate_policy(p)
    if condition not in {'agent_selected', 'tools_specified'}:
        raise ValueError('Invalid tool-selection condition')
    refs = []
    for path in inputs:
        if not path.is_file():
            raise ValueError(f'Input must be a file or manifest: {path}')
        refs.append({'path': str(path.resolve()), 'sha256': digest(path)})
    root.mkdir(parents=True, exist_ok=False)
    state = {
        'format_version': 1, 'run_id': uuid.uuid4().hex, 'status': 'READY',
        'request': request, 'inputs': refs, 'condition': condition,
        'agent_config': agent_config, 'policy': p,
        'policy_sha256': object_hash(p), 'intent_sha256': object_hash([request, refs, condition]),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'stages': {s: {'status': 'queued', 'attempts': 0, 'repairs': 0,
                       'artifacts': [], 'history': []} for s in STAGES},
        'usage': {'active_seconds': 0, 'cpu_core_hours': 0, 'gpu_hours': 0,
                  'service_spend_usd': 0, 'setup_active_seconds': 0,
                  'campaign_active_seconds': 0},
        'inflight': None, 'qualified_candidates': [], 'events': 0,
        'implementation_sha256': {name: digest(ROOT / name) for name in IMPLEMENTATION_FILES},
    }
    atomic_json(root / 'state.json', state)
    return state


class Controller:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.state = load_json(self.root / 'state.json')

    def save(self):
        atomic_json(self.root / 'state.json', self.state)

    def event(self, kind: str, **details):
        self.state['events'] += 1
        row = {'n': self.state['events'], 'time': datetime.now(timezone.utc).isoformat(),
               'kind': kind, **details}
        with (self.root / 'trajectory.jsonl').open('a') as f:
            f.write(json.dumps(row, allow_nan=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
        self.save()

    def effective_limits(self) -> dict:
        p = dict(self.state['policy'])
        for key, value in self.state.get('resolved_limits', {}).items():
            p[key] = min(p[key], value)
        refs = self.artifacts()
        if 'resolved_request' in refs:
            budget = self.data('resolved_request', refs)['execution']['budget']
            p['active_seconds'] = min(p['active_seconds'], budget['wall_time_hours'] * 3600)
            p['cpu_core_hours'] = min(p['cpu_core_hours'], budget['cpu_core_hours'])
            p['gpu_hours'] = min(p['gpu_hours'], budget['gpu_hours'])
        return p

    def remaining(self) -> dict:
        p, usage = self.effective_limits(), self.state['usage']
        result = {k: max(0, p[k] - usage[k]) for k in
                  ('active_seconds', 'cpu_core_hours', 'gpu_hours', 'service_spend_usd')}
        if p['deadline_utc'] is not None:
            deadline = datetime.fromisoformat(p['deadline_utc'].replace('Z', '+00:00')).timestamp()
            result['active_seconds'] = min(result['active_seconds'], max(0, deadline - time.time()))
        return result

    def verify_run(self):
        s = self.state
        for name, expected in s['implementation_sha256'].items():
            if digest(ROOT / name) != expected:
                raise ValueError('Controller or scientific contracts changed; migration requires a new versioned run')
        if object_hash(s['policy']) != s['policy_sha256']:
            raise ValueError('Run limits changed outside the recorded run')
        if object_hash([s['request'], s['inputs'], s['condition']]) != s['intent_sha256']:
            raise ValueError('Frozen user intent or input manifest changed')
        for ref in s['inputs']:
            verify_artifact(ref, self.root)

    def artifacts(self) -> dict:
        refs = {}
        for stage in STAGES:
            item = self.state['stages'][stage]
            if item['status'] in {'accepted', 'accepted_sequence_only'}:
                for ref in item['artifacts']:
                    refs[ref['kind']] = ref
        return refs

    def data(self, kind: str, refs: dict | None = None) -> dict:
        return load_json(verify_artifact((refs or self.artifacts())[kind], self.root))

    def assessment_models(self) -> list:
        fold = self.state['stages']['fold']
        if fold['status'] != 'accepted':
            return []
        refs = {r['kind']: r for r in fold['artifacts']}
        return self.data('stage_evidence', refs).get('assessment_models', [])

    def require_assessment_models(self, candidates: list) -> list:
        fold = self.state['stages']['fold']
        if fold['status'] != 'accepted':
            raise ValueError('FOLD_EVIDENCE_REQUIRED: no accepted independent fold assessment')
        # Reuse the admission check on the current files, including on restart
        # and before final qualification; a saved status is not evidence.
        self.validate_output('fold', {'status': 'completed', 'artifacts': fold['artifacts']})
        models = self.assessment_models()
        if not {c['candidate_id'] for c in candidates}.issubset({m['candidate_id'] for m in models}):
            raise ValueError('FOLD_EVIDENCE_REQUIRED: downstream candidate lacks a reviewed assessment model')
        return models

    def finish(self, status: str, reason: str):
        self.state.update(status=status, reason=reason)
        if status in TERMINAL:
            # A stopped local controller cannot attest that a remote job stopped.
            uncertain = self.state.get('unreconciled_call') or self.state.get('inflight') or {}
            for name, item in self.state['stages'].items():
                if item['status'] == 'running':
                    item['history'].append({'event': 'controller_stopped', 'previous_status': 'running',
                                            'run_status': status, 'reason': reason})
                    item['status'] = ('awaiting_reconciliation' if item.get('job_handles')
                                      or uncertain.get('stage') == name else 'incomplete')
        summary = {
            'run_id': self.state['run_id'], 'status': status, 'reason': reason,
            'qualified_candidates': self.state['qualified_candidates'],
            'qualified_design_count': len(self.state['qualified_candidates']),
            'stages': {k: v['status'] for k, v in self.state['stages'].items()},
            'artifacts': self.artifacts(), 'usage': self.state['usage'],
            'outstanding_jobs': {s: v.get('job_handles', []) for s, v in self.state['stages'].items()
                                 if v.get('job_handles')},
            'unreconciled_call': self.state.get('unreconciled_call') or self.state.get('inflight'),
            'execution_approval_block': self.state.get('execution_approval_block'),
            'resource_scope': 'Local waited CPU plus agent-reported usage; external limits require harness enforcement.',
            'scientific_scope': 'Computational evidence only; control-flow tests do not demonstrate enzyme activity.',
        }
        if status == 'NEEDS_INPUT':
            summary['input_request'] = self.state['pending_user_input']
        atomic_json(self.root / 'report.json', summary)
        self.event('run_stopped', status=status, reason=reason)
        write_bundle(self.root, self.state, summary)
        return summary

    def stop_partial(self, reason: str):
        useful = any(s['status'] == 'accepted' for s in self.state['stages'].values())
        return self.finish('PARTIAL' if useful else 'BLOCKED', reason)

    def task(self, stage: str, mode: str = 'execute', **extra) -> dict:
        configuration = yaml.safe_load((ROOT / 'config/environment.yaml').read_text())
        return {
            'run_id': self.state['run_id'], 'run_dir': str(self.root), 'stage': stage,
            'mode': mode, 'scientific_request': self.state['request'],
            'input_files': self.state['inputs'], 'condition': self.state['condition'],
            'environment_spec': str(ROOT / 'ENVIRONMENT_SPEC.md'),
            'contracts_file': str(ROOT / 'runtime' / 'CONTRACTS.md'),
            'schemas_dir': str(ROOT / 'config'), 'accepted_artifacts': self.artifacts(),
            'assessment_models': self.assessment_models(),
            'expected_artifact_kinds': EXPECTED[stage], 'limits_remaining': self.remaining(),
            'stage_history': self.state['stages'][stage]['history'],
            'autonomy_policy': configuration['autonomy'],
            'startup_policy': configuration['startup_validation'],
            'method_validation_policy': configuration['method_validation'],
            'user_input_contract': {
                'allowed_reason_items': USER_INPUT_ITEMS,
                'required_fields': ['reason_code', 'item', 'question', 'why_unresolved', 'resolution_attempts'],
                'resolution_attempts': 'Nonempty list of inspected source/finding objects; reviewer verifies applicability',
                'routine_questions': 'Resolve omitted research settings, profile preparation, defaults, tool installation and review internally',
                'invalid_request_action': 'bounded_internal_repair',
            },
            'requirements': [
                'Work only on this assigned stage; do not start a nested controller or launch another campaign.',
                'Generation may yield a reviewed sequence-only candidate despite defective coordinates. Sequence screening and independent folding may use the unchanged FASTA without repairing those coordinates first. Every generation route requires independent assessment_models with sequence/input provenance, method controls and reviewed integrity evidence before fold acceptance. Preparation or minimization alone cannot pass fold. Never use defective generated coordinates as an accepted assessment model.',
                'Own routine parameter choices, tool discovery, internal review and bounded repair.',
                'Only the current stage prerequisites apply; do not require final qualification before generation.',
                'Read the generation/full-profile schemas and runtime response contracts.',
                'Preserve reaction, assembly, explicit length limits, catalytic groups and requested objectives.',
                'Use reusable verified runtimes; assess compatible accelerators before a CPU-only fallback.',
                'Preserve an exact prescribed-tool condition; record compatible alternatives only when permitted.',
                'Write outputs to new immutable attempt paths, never overwrite accepted artifacts or historical inputs.',
                'Before any external job, verify the existing entitlement and resource reservation.',
                'Do not launch detached local jobs. Remote jobs need durable handles and idempotency keys.',
                'Report external CPU hours, GPU device-hours and scientific service spend; unknown is not zero.',
                'Claims about catalytic performance require matched controls and valid chemistry evidence.',
                'Validate the combined startup path on the actual input before expensive inference; standalone import tests are insufficient.',
                'Distinguish technical startup failure, method-control failure, unresolved assessment and verified candidate failure. Method selection uses controls, not the highest candidate score.',
                'Report a genuine execution-tool denial or approval timeout as failure.category execution_approval with the exact tool error, blocked command and receipt when available. Do not retry it through another command or harness.',
            ], **extra,
        }

    def call(self, role: str, task: dict) -> dict:
        remaining = self.remaining()
        if remaining['active_seconds'] <= 0 or remaining['cpu_core_hours'] <= 0:
            raise TimeoutError('The recorded run budget or deadline is exhausted')
        stage = task['stage']
        call_id = uuid.uuid4().hex
        directory = self.root / 'attempts' / stage / (call_id + '-' + role)
        timeout = min(remaining['active_seconds'], self.state['policy']['call_timeout_seconds'])
        task['idempotency_key'] = self.state['run_id'] + ':' + stage + ':' + str(self.state['stages'][stage]['attempts'])
        self.state['inflight'] = {'id': call_id, 'stage': stage, 'role': role,
                                  'directory': str(directory), 'started': time.time(), 'timeout': timeout,
                                  'mode': task.get('mode'), 'receipt_path': str(directory / 'receipt.json'),
                                  'local_accounted': False}
        self.event('agent_started', stage=stage, role=role, call_id=call_id)
        receipt = invoke(self.state['agent_config'], role, task, directory, timeout)
        receipt['call_id'] = call_id
        atomic_json(directory / 'receipt.json', receipt)
        usage = self.state['usage']
        elapsed = receipt['elapsed_seconds']
        usage['active_seconds'] += elapsed
        phase = 'setup_active_seconds' if stage == 'prepare' or role == 'repair' else 'campaign_active_seconds'
        usage[phase] += elapsed
        usage['cpu_core_hours'] += receipt['cpu_seconds'] / 3600
        self.state['inflight']['local_accounted'] = True
        self.event('agent_finished', stage=stage, role=role, call_id=call_id,
                   exit_code=receipt['exit_code'], timed_out=receipt['timed_out'])
        response = receipt.get('response') or {}
        failure = response.get('failure')
        if isinstance(failure, dict) and failure.get('category') == 'execution_approval':
            try:
                self.account_external(response, call_id)
            except ValueError as exc:
                self.state['stages'][stage]['accounting_error'] = str(exc)
            if task.get('mode') != 'poll':
                self.state['stages'][stage]['job_handles'] = response.get(
                    'job_handles', self.state['stages'][stage].get('job_handles', []))
            self.ack_call()
            self.check_execution_gate(stage, response, role)
        return receipt

    def check_execution_gate(self, stage: str, response: dict, role: str = 'executor'):
        failure = response.get('failure')
        if not isinstance(failure, dict) or failure.get('category') != 'execution_approval':
            return
        self.state['execution_approval_block'] = {
            'stage': stage, 'role': role, 'failure': failure,
            'artifacts': response.get('artifacts', []),
            'deadline_utc': self.state['policy'].get('deadline_utc'),
            'recovery': 'Supported execution-gate approval is required; recheck limits without automatic renewal.'}
        self.event('execution_approval_blocked', stage=stage, role=role, failure=failure)
        raise ValueError('EXECUTION_APPROVAL_REQUIRED: preserve the denial; no automatic retry or alternate launch route')

    def ack_call(self):
        self.state['inflight'] = None
        self.save()

    def account_external(self, response: dict, receipt_id: str | None = None):
        accounted = self.state.setdefault('accounted_receipts', [])
        if receipt_id is not None and receipt_id in accounted:
            return
        usage = response.get('usage')
        if not isinstance(usage, dict):
            raise ValueError('Missing scientific resource accounting; unknown usage is not zero')
        increments = {}
        for source, target in (('external_cpu_core_hours', 'cpu_core_hours'),
                               ('gpu_hours', 'gpu_hours'), ('service_spend_usd', 'service_spend_usd')):
            value = usage.get(source)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < float('inf'):
                raise ValueError(f'Invalid or unmetered usage: {source}')
            increments[target] = value
        for target, value in increments.items():
            self.state['usage'][target] += value
        if receipt_id is not None:
            accounted.append(receipt_id)
        self.save()
        if any(self.state['usage'][k] > self.effective_limits()[k] for k in
               ('cpu_core_hours', 'gpu_hours', 'service_spend_usd')):
            raise TimeoutError('Reported work exceeded its resource allocation; further dispatch disabled')

    def validate_output(self, stage: str, response: dict) -> dict:
        if response.get('status') != 'completed':
            raise ValueError('Stage execution did not complete')
        artifacts = response.get('artifacts', [])
        refs = {r['kind']: r for r in artifacts}
        if len(refs) != len(artifacts) or not set(EXPECTED[stage]).issubset(refs):
            raise ValueError('Duplicate or missing stage output artifact kinds')
        allowed = set(EXPECTED[stage]) | {'stage_report', 'capability_registry'}
        if stage in {'chemistry', 'evaluate'}:
            allowed.add('qualified_profile')
        if not set(refs).issubset(allowed):
            raise ValueError('Stage attempted to replace a frozen or unrelated artifact kind')
        if 'qualified_profile' in refs and 'qualified_profile' in self.artifacts():
            if refs['qualified_profile']['sha256'] != self.artifacts()['qualified_profile']['sha256']:
                raise ValueError('Evaluation cannot change a previously frozen qualified profile')
        for ref in artifacts:
            verify_artifact(ref, self.root)
        merged = {**self.artifacts(), **refs}
        if stage == 'prepare':
            request = self.data('resolved_request', refs)
            check_request(request)
            generation = self.data('generation_profile', refs)
            check_generation(generation, self.root)
            if generation['request_sha256'] != object_hash(request):
                raise ValueError('Generation profile belongs to a different resolved request')
            mode = request.get('assembly', {}).get('mode', 'resolve_from_evidence')
            if mode != 'resolve_from_evidence' and mode != generation['assembly']['kind']:
                raise ValueError('Requested and prepared assembly differ')
            plan = self.data('evaluation_plan', refs)
            if (set(plan.get('required_groups', [])) != GROUPS
                    or plan.get('calibration_basis') != 'reference_controls_only'
                    or plan.get('request_sha256') != object_hash(request)):
                raise ValueError('Evaluation intent and reference-only calibration must be frozen before generation')
        if 'candidate_manifest' in refs:
            manifest = self.data('candidate_manifest', refs)
            check_candidates(manifest, self.root,
                             self.data('resolved_request', merged))
            if stage != 'generate':
                canonical = self.state['stages']['generate']['artifacts']
                origin = self.data('candidate_manifest', {r['kind']: r for r in canonical})
                prior = {c['candidate_id']: c for c in origin['candidates']}
                for candidate in manifest['candidates']:
                    old = prior.get(candidate['candidate_id'])
                    if old is None or any(candidate[k] != old[k] for k in ('revision', 'sequence', 'structure')):
                        raise ValueError('Candidate changed after generation; invalidate and regenerate its evidence')
        if 'stage_evidence' in refs:
            evidence = self.data('stage_evidence', refs)
            if evidence.get('stage') != stage or not isinstance(evidence.get('checks'), list):
                raise ValueError('Stage evidence must identify the stage and actual checks')
            if evidence.get('candidate_manifest_sha256') != refs['candidate_manifest']['sha256']:
                raise ValueError('Stage evidence is not bound to the current candidate manifest')
            verify_nested(evidence, self.root)
            if stage == 'fold':
                if not isinstance(evidence.get('assessment_models'), list) or not evidence['assessment_models']:
                    raise ValueError('FOLD_EVIDENCE_REQUIRED: every generation route needs independent assessment models; preparation alone cannot pass fold')
                check_assessment_models(evidence['assessment_models'], manifest['candidates'],
                                        self.data('generation_profile')['assembly'],
                                        merged['evaluation_plan']['sha256'], self.root)
                if evidence.get('structural_integrity_ready') is not True:
                    raise ValueError('Predicted assessment models still require independent integrity review')
            if STAGES.index(stage) > STAGES.index('fold'):
                models = self.require_assessment_models(manifest['candidates'])
                if evidence.get('assessment_models_sha256') != object_hash(models):
                    raise ValueError('Downstream evidence is not bound to the reviewed assessment models')
        if stage == 'evaluate':
            evaluation = self.data('evaluation', refs)
            if evaluation.get('evaluation_plan_sha256') != merged['evaluation_plan']['sha256']:
                raise ValueError('Final evaluation is not bound to the frozen evaluation plan')
            if not isinstance(evaluation.get('qualification_requested'), bool):
                raise ValueError('Evaluation must distinguish a partial report from final qualification')
            if evaluation['qualification_requested']:
                manifest = self.data('candidate_manifest', merged)
                models = self.require_assessment_models(manifest['candidates'])
                if evaluation.get('assessment_models_sha256') != object_hash(models):
                    raise ValueError('Qualification must use the reviewed assessment model versions')
                assessed = {m['candidate_id']: m['structure'] for m in models}
                protocol = self.data('qualified_profile', merged)
                generation = self.data('generation_profile', merged)
                if (protocol['reaction']['sha256'] != generation['reaction']['sha256']
                        or protocol['assembly']['kind'] != generation['assembly']['kind']):
                    raise ValueError('Qualified profile changed the intended reaction or assembly')
                for name in ('motif', 'motif_map'):
                    if protocol[name]['sha256'] != generation[name]['sha256']:
                        raise ValueError('Qualified profile changed the fixed catalytic identity/mapping')
                a, b = protocol['assembly'], generation['assembly']
                for name in ('subunit_count', 'unique_sequence_count', 'sequence_groups'):
                    if a[name] != b[name]:
                        raise ValueError('Qualified profile changed the chain/sequence contract')
                for name in ('reference_assembly', 'chain_map'):
                    if a[name]['sha256'] != b[name]['sha256']:
                        raise ValueError('Qualified profile changed the reference assembly mapping')
                if a['design_symmetry'] != b['design_symmetry']:
                    raise ValueError('Qualified profile changed the generation symmetry contract')
                site_map = lambda x: {s['site_id']: sorted(s['chain_ids']) for s in x['active_sites']}
                if site_map(a) != site_map(b):
                    raise ValueError('Qualified profile changed required catalytic sites')
                conditions = self.data('resolved_request', merged)['conditions']
                scope = protocol['scope']
                if (not scope['pH_range'][0] <= conditions['pH'] <= scope['pH_range'][1]
                        or not scope['temperature_C_range'][0] <= conditions['temperature_C'] <= scope['temperature_C_range'][1]
                        or conditions['expression_host'] not in scope['supported_hosts']):
                    raise ValueError('Final profile does not support the requested operating conditions')
                if evaluation.get('protocol_sha256') != merged['qualified_profile']['sha256']:
                    raise ValueError('Final evaluation is not bound to the qualified protocol')
                manifest = self.data('candidate_manifest', merged)
                passed = set(qualified_ids(evaluation, manifest, protocol, self.root))
                for candidate in manifest['candidates']:
                    if candidate['candidate_id'] not in passed:
                        continue
                    mapping = load_json(verify_artifact(candidate['assembly_map'], self.root))
                    if (mapping.get('candidate_id') != candidate['candidate_id']
                            or mapping.get('sequence_sha256') != candidate['sequence']['sha256']
                            or mapping.get('structure_sha256') != assessed[candidate['candidate_id']]['sha256']
                            or set(mapping.get('chain_ids', [])) != set(a['sequence_groups'][0]['chain_ids'])
                            or set(mapping.get('site_ids', [])) != set(site_map(a))):
                        raise ValueError('Qualified candidate lacks a current sequence/structure/site assembly map')
            elif not evaluation.get('unresolved'):
                raise ValueError('A partial evaluation must list its missing evidence')
        return refs

    def track_candidates(self, response: dict):
        refs = {r['kind']: r for r in response.get('artifacts', [])}
        manifest = self.data('candidate_manifest', refs)
        limits = self.data('resolved_request')['execution']
        seen = self.state.setdefault('candidate_history', {})
        for c in manifest['candidates']:
            key = c['candidate_id']
            signature = object_hash([c['sequence'], c['structure']])
            old = seen.get(key)
            if old is None:
                seen[key] = {'revision': c['revision'], 'signature': signature, 'refinements': 0}
            elif signature != old['signature']:
                if c['revision'] <= old['revision']:
                    raise ValueError('A changed candidate needs a new revision')
                old.update(revision=c['revision'], signature=signature, refinements=old['refinements'] + 1)
            if seen[key]['refinements'] > limits['max_refinements_per_lineage']:
                raise TimeoutError('Cumulative candidate refinement limit exceeded')
        self.save()
        if len(seen) > limits['max_generated']:
            raise TimeoutError('Cumulative distinct-candidate generation limit exceeded')

    def invalidate(self, stage: str, reason: str):
        for name in STAGES[STAGES.index(stage):]:
            item = self.state['stages'][name]
            item['history'].append({'event': 'invalidated', 'reason': reason,
                                    'previous_artifacts': item['artifacts']})
            item.update(status='queued', artifacts=[], response=None, job_handles=[], pending_since=None)
        self.state['qualified_candidates'] = []
        self.event('evidence_invalidated', stage=stage, reason=reason)

    def check_accepted(self) -> tuple[str, str] | None:
        self.verify_run()
        for stage in STAGES:
            item = self.state['stages'][stage]
            if item['status'] not in {'accepted', 'accepted_sequence_only'}:
                continue
            try:
                for ref in item['artifacts']:
                    path = verify_artifact(ref, self.root)
                    if path.suffix == '.json':
                        verify_nested(load_json(path), self.root)
                if stage == 'fold':
                    self.validate_output('fold', {'status': 'completed', 'artifacts': item['artifacts']})
            except (ValueError, OSError, KeyError, TypeError) as exc:
                return stage, str(exc)
        return None

    def review(self, stage: str, response: dict, errors: list[str]) -> dict:
        fingerprint = object_hash(response)
        for attempt in range(self.state['policy']['max_review_attempts']):
            receipt = self.call('reviewer', self.task(
                stage, 'review', output=response, output_sha256=fingerprint,
                contract_errors=errors, review_attempt=attempt + 1,
                response_contract={'decision': 'accept|accept_sequence_only|retry|repair|reject|blocked|needs_input',
                                   'reason': 'Evidence-grounded explanation', 'reviewed_sha256': fingerprint,
                                   'input_request': 'Required for needs_input; follow task.user_input_contract',
                                   'repair_from': 'Optional current or earlier stage ID'},
                review_instruction='Read-only review. Request repair for calculations; never edit artifacts.'))
            decision = receipt.get('response') or {}
            self.ack_call()
            if (receipt['exit_code'] == 0 and decision.get('reviewed_sha256') == fingerprint
                    and decision.get('decision') in {'accept', 'accept_sequence_only', 'retry', 'repair', 'reject', 'blocked', 'needs_input'}
                    and isinstance(decision.get('reason'), str) and decision['reason'].strip()):
                if decision['decision'] in {'accept', 'accept_sequence_only'} and errors:
                    decision = {**decision, 'decision': 'repair',
                                'reason': 'Reviewer cannot override contract failures: ' + '; '.join(errors)}
                if decision['decision'] == 'needs_input':
                    error = user_input_error(decision.get('input_request'))
                    if error:
                        self.event('user_question_redirected', stage=stage, reason=error,
                                   original_decision=decision)
                        decision = {**decision, 'decision': 'repair', 'repair_from': stage,
                                    'reason': 'Resolve internally under the existing autonomy policy: ' + error}
                self.event('review_decision', stage=stage, decision=decision)
                return decision
            self.event('invalid_review', stage=stage, error=receipt.get('error'))
        return {'decision': 'blocked', 'reason': 'Independent reviewer failed its response contract'}

    def repair(self, stage: str, decision: dict, response: dict) -> bool:
        item = self.state['stages'][stage]
        recovered = item.pop('pending_repair_receipt', None)
        if not recovered and item['repairs'] >= self.state['policy']['max_repairs_per_stage']:
            return False
        if not recovered:
            item['repairs'] += 1
        item['pending_repair_decision'] = decision
        item['failed_response'] = response
        self.state['status'] = 'RECOVERING'
        self.save()
        receipt = recovered or self.call('repair', self.task(
            stage, 'repair', failed_output=response, decision=decision,
            response_contract={'status': 'repaired|blocked', 'summary': 'Diagnosis and applied change',
                               'artifacts': 'Hashed repair evidence', 'usage': 'Measured scientific usage'}))
        result = receipt.get('response') or {}
        item['history'].append({'event': 'repair', 'result': result, 'receipt_error': receipt.get('error')})
        try:
            self.account_external(result, receipt.get('call_id'))
        except ValueError as exc:
            item['accounting_error'] = str(exc)
        self.ack_call()
        item.pop('pending_repair_decision', None)
        if receipt['exit_code'] != 0 or result.get('status') != 'repaired':
            self.save()
            return False
        verify_nested(result.get('artifacts', []), self.root)
        if item.get('accounting_error'):
            if not isinstance(result.get('recovered_usage'), dict):
                self.save()
                return False
            self.account_external({'usage': result['recovered_usage']}, 'recovered:' + str(receipt.get('call_id')))
            item.pop('accounting_error', None)
        target = decision.get('repair_from', stage)
        if target not in STAGES or STAGES.index(target) > STAGES.index(stage):
            raise ValueError('A repair must identify the current or an earlier affected stage')
        self.invalidate(target, decision['reason'])
        self.state['status'] = 'RUNNING'
        self.save()
        return True

    def reconcile(self) -> bool:
        interrupted = self.state['inflight']
        if not interrupted:
            return True
        stage = interrupted['stage']
        item = self.state['stages'][stage]
        saved_path = Path(interrupted.get('receipt_path', ''))
        saved = load_json(saved_path) if saved_path.is_file() else None
        if not interrupted.get('local_accounted'):
            elapsed = saved['elapsed_seconds'] if saved else max(0, time.time() - interrupted['started'])
            self.state['usage']['active_seconds'] += elapsed
            if saved:
                self.state['usage']['cpu_core_hours'] += saved['cpu_seconds'] / 3600
        if saved and saved['exit_code'] == 0 and saved.get('response'):
            result = saved['response']
            failure = result.get('failure')
            if isinstance(failure, dict) and failure.get('category') == 'execution_approval':
                try:
                    self.account_external(result, saved.get('call_id', interrupted['id']))
                except ValueError as exc:
                    item['accounting_error'] = str(exc)
                if interrupted.get('mode') != 'poll':
                    item['job_handles'] = result.get('job_handles', item.get('job_handles', []))
                self.ack_call()
                self.check_execution_gate(stage, result, interrupted['role'])
            if interrupted['role'] == 'executor':
                result = saved['response']
                if interrupted.get('mode') == 'poll':
                    try:
                        self.account_external(result, saved.get('call_id', interrupted['id']))
                        check_poll_response(item.get('job_handles'), result)
                    except ValueError as exc:
                        item['poll_identity_error'] = str(exc)
                        self.event('poll_receipt_rejected', stage=stage, error=str(exc))
                        self.ack_call()
                        return False
                item['response'] = result
                item['pending_since'] = interrupted['started'] + saved['elapsed_seconds'] if result.get('status') == 'pending' else None
                item['job_handles'] = result.get('job_handles', [])
                try:
                    self.account_external(result, saved.get('call_id', interrupted['id']))
                except ValueError as exc:
                    item['accounting_error'] = str(exc)
                self.event('completed_executor_receipt_recovered', stage=stage, call_id=interrupted['id'])
                self.ack_call()
                return True
            if interrupted['role'] == 'repair' and interrupted.get('mode') == 'repair':
                item['pending_repair_receipt'] = saved
                self.ack_call()
                return True
        if interrupted.get('mode') == 'poll' and item.get('job_handles'):
            self.ack_call()
            return True
        self.state['inflight'] = None
        self.state['unreconciled_call'] = interrupted
        self.event('interrupted_call', previous=interrupted)
        if interrupted['role'] == 'reviewer' and item.get('response'):
            self.state.pop('unreconciled_call', None)
            self.save()
            return True
        receipt = self.call('repair', self.task(
            stage, 'reconcile', interrupted_call=interrupted,
            response_contract={'status': 'reconciled', 'safe_to_retry': True,
                               'job_handles': [], 'artifacts': 'Required reconciliation evidence',
                               'usage': 'Recovered scientific usage; never invent zero',
                               'completed_response': 'Optional recovered executor response'},
            recovery_instruction='Inspect receipts and job state. Do not submit another scientific job.'))
        result = receipt.get('response') or {}
        if (receipt['exit_code'] != 0 or result.get('status') != 'reconciled'
                or result.get('safe_to_retry') is not True or result.get('job_handles') != []
                or not result.get('artifacts')):
            self.state['unreconciled_call'] = interrupted
            self.save()
            return False
        verify_nested(result['artifacts'], self.root)
        self.account_external(result, receipt.get('call_id'))
        item['response'] = result.get('completed_response')
        item['history'].append({'event': 'reconciled', 'evidence': result['artifacts']})
        self.state.pop('unreconciled_call', None)
        self.ack_call()
        return True

    def run(self, max_stages: int | None = None) -> dict:
        with run_lock(self.root):
            self.state = load_json(self.root / 'state.json')
            try:
                self.verify_run()
                if self.state['status'] in TERMINAL:
                    changed = self.check_accepted()
                    if changed:
                        self.invalidate(*changed)
                        return self.finish('BLOCKED', 'Previously reported evidence changed; qualification invalidated')
                    summary = load_json(self.root / 'report.json')
                    write_bundle(self.root, self.state, summary)
                    return summary
                if not self.reconcile():
                    return self.stop_partial('An interrupted job cannot yet be safely reconciled')
                return self._drive(max_stages)
            except TimeoutError as exc:
                return self.finish('BUDGET_EXHAUSTED', str(exc))
            except (ValueError, KeyError, TypeError, OSError) as exc:
                return self.stop_partial(f'Controller contract/access error: {exc}')

    def _drive(self, max_stages: int | None) -> dict:
        self.state['status'] = 'RUNNING'
        completed = 0
        while True:
            if self.remaining()['active_seconds'] <= 0 or self.remaining()['cpu_core_hours'] <= 0:
                raise TimeoutError('The recorded run budget or deadline is exhausted')
            changed = self.check_accepted()
            if changed:
                self.invalidate(*changed)
            stage = next((s for s in STAGES if self.state['stages'][s]['status'] not in {'accepted', 'accepted_sequence_only'}), None)
            if stage is None:
                return self.finalize()
            item = self.state['stages'][stage]
            if item.get('pending_repair_receipt'):
                if self.repair(stage, item['pending_repair_decision'], item.get('failed_response', {})):
                    continue
                return self.stop_partial('Recovered repair did not resolve the stage failure')
            response = item.get('response')
            if response is None:
                if item['attempts'] >= self.state['policy']['max_stage_attempts']:
                    return self.stop_partial(f'{stage}: bounded attempts exhausted; see retained failures')
                item['attempts'] += 1
                item['status'] = 'running'
                self.save()
                receipt = self.call('executor', self.task(stage,
                    response_contract={'status': 'completed|failed|pending|blocked|needs_input',
                        'artifacts': 'Array of kind/path/sha256 objects',
                        'job_handles': 'Durable provider/id objects for pending jobs',
                        'usage': {'external_cpu_core_hours': 'number', 'gpu_hours': 'number',
                                  'service_spend_usd': 'number'},
                        'input_request': 'Required for needs_input; follow task.user_input_contract',
                        'failure': 'category and message when incomplete'}))
                response = receipt.get('response') or {'status': 'failed',
                    'failure': {'category': 'execution', 'message': receipt.get('error') or 'Missing response'}}
                if receipt['exit_code'] != 0:
                    if not self.reconcile():
                        return self.stop_partial('Executor transport failed; job effects remain unreconciled')
                    continue
                item['response'] = response
                item['pending_since'] = time.time() if response.get('status') == 'pending' else None
                item['job_handles'] = response.get('job_handles', [])
                item['history'].append({'event': 'execution', 'response': response})
                self.save()
                try:
                    self.account_external(response, receipt.get('call_id'))
                except ValueError as exc:
                    item['accounting_error'] = str(exc)
                    self.save()
                self.ack_call()
            self.check_execution_gate(stage, response)
            if response.get('status') == 'pending':
                if not self.poll(stage, response):
                    return self.stop_partial(f'{stage}: pending job cannot be reconciled within policy')
                continue
            errors = []
            if item.get('accounting_error'):
                errors.append(item['accounting_error'])
            try:
                self.validate_output(stage, response)
                if stage == 'generate':
                    self.track_candidates(response)
            except TimeoutError:
                raise
            except Exception as exc:
                errors.append(str(exc))
            decision = self.review(stage, response, errors)
            action = decision['decision']
            if action == 'blocked' and response.get('failure', {}).get('category') in {
                    'execution', 'technical', 'capability', 'input_format',
                    'preparation', 'chemistry_profile', 'routine_setting'}:
                action = 'repair'
                decision = {**decision, 'decision': 'repair'}
            if action in {'accept', 'accept_sequence_only'}:
                try:
                    self.validate_output(stage, response)
                    if action == 'accept' and stage == 'generate':
                        refs = {r['kind']: r for r in response['artifacts']}
                        if 'stage_report' in refs and self.data('stage_report', refs).get('geometry_status') in {'failed', 'unresolved'}:
                            raise ValueError('Documented geometry defect requires sequence-only scope, never full structural acceptance')
                    if action == 'accept_sequence_only':
                        if stage != 'generate':
                            raise ValueError('Sequence-only acceptance is restricted to generation')
                        refs = {r['kind']: r for r in response['artifacts']}
                        if 'stage_report' not in refs:
                            raise ValueError('Sequence-only generation requires a hashed defect report')
                        report = self.data('stage_report', refs)
                        candidates = self.data('candidate_manifest', refs)['candidates']
                        if (report.get('sequence_only_eligible') is not True
                                or report.get('geometry_status') not in {'failed', 'unresolved'}
                                or not candidates or any(c['status'] not in {'exploratory', 'unresolved'} for c in candidates)):
                            raise ValueError('Sequence-only scope and physical defect must be explicit')
                    changed = self.check_accepted()
                    if changed:
                        self.invalidate(*changed)
                        continue
                except Exception as exc:
                    action = 'repair'
                    decision = {'decision': 'repair', 'reason': f'Artifacts changed during review: {exc}'}
                else:
                    item.update(status=('accepted_sequence_only' if action == 'accept_sequence_only' else 'accepted'),
                                artifacts=response['artifacts'], response=None)
                    if stage == 'prepare':
                        limits = self.effective_limits()
                        self.state['resolved_limits'] = {key: limits[key] for key in
                            ('active_seconds', 'cpu_core_hours', 'gpu_hours')}
                    self.event('stage_accepted', stage=stage)
                    completed += 1
                    if max_stages is not None and completed >= max_stages:
                        return self.finish('READY', 'Checkpoint requested after completed stages; same run budget retained')
                    continue
            item['response'] = None
            self.save()
            if action == 'retry' and not item.get('accounting_error'):
                continue
            if action == 'retry':
                action = 'repair'
                decision = {**decision, 'decision': 'repair', 'reason': item['accounting_error']}
            if action == 'repair' and self.repair(stage, decision, response):
                continue
            if action == 'needs_input':
                self.state['pending_user_input'] = decision['input_request']
                return self.finish('NEEDS_INPUT', decision['reason'])
            if action == 'reject':
                if not errors and 'candidate_manifest' in {r['kind'] for r in response.get('artifacts', [])}:
                    candidates = self.data('candidate_manifest', {r['kind']: r for r in response['artifacts']})['candidates']
                    if candidates and all(c['status'] == 'rejected' for c in candidates):
                        return self.finish('NO_QUALIFYING_DESIGNS', decision['reason'])
                return self.stop_partial('No audited all-candidate scientific rejection: ' + decision['reason'])
            return self.stop_partial(decision['reason'])

    def poll(self, stage: str, response: dict) -> bool:
        item = self.state['stages'][stage]
        handles = response.get('job_handles')
        try:
            job_identities(handles)
        except ValueError as exc:
            item['poll_identity_error'] = str(exc)
            return False
        item['job_handles'] = handles
        item['polls'] = item.get('polls', 0) + 1
        if item['polls'] > self.state['policy']['max_pending_polls']:
            self.save()
            return False
        since = item.get('pending_since') or time.time()
        delay = min(self.state['policy']['poll_seconds'], self.remaining()['active_seconds'])
        time.sleep(delay)
        waited = max(0, time.time() - since)
        self.state['usage']['active_seconds'] += waited
        self.state['usage']['campaign_active_seconds'] += waited
        item['pending_since'] = None
        self.save()
        receipt = self.call('executor', self.task(stage, 'poll', job_handles=handles,
            response_contract={'status': 'pending|completed|failed', 'artifacts': 'Stage outputs',
                               'polled_job_handles': 'Required exact original provider/id pairs, including on completion',
                               'job_handles': 'All original jobs while any remain pending; empty only after all are terminal',
                               'usage': 'Incremental measured usage since previous response'},
            polling_instruction='Poll existing jobs only; never submit a replacement while their state is unknown.'))
        result = receipt.get('response')
        if receipt['exit_code'] != 0 or result is None:
            item['response'] = response
            item['pending_since'] = time.time()
            item['history'].append({'event': 'poll_failed', 'error': receipt.get('error')})
            self.ack_call()
            return True
        self.account_external(result, receipt.get('call_id'))
        try:
            check_poll_response(handles, result)
        except ValueError as exc:
            item['poll_identity_error'] = str(exc)
            item['history'].append({'event': 'poll_receipt_rejected', 'error': str(exc)})
            self.ack_call()
            return False
        item['response'] = result
        item['job_handles'] = result.get('job_handles', []) if result.get('status') == 'pending' else []
        item['pending_since'] = time.time() if result.get('status') == 'pending' else None
        item['history'].append({'event': 'poll', 'response': result})
        self.ack_call()
        return True

    def finalize(self) -> dict:
        refs = self.artifacts()
        evaluation = self.data('evaluation', refs)
        if not evaluation['qualification_requested']:
            return self.finish('PARTIAL', '; '.join(evaluation['unresolved']))
        manifest = self.data('candidate_manifest', refs)
        ids = qualified_ids(evaluation, manifest, self.data('qualified_profile', refs), self.root)
        wanted = self.data('resolved_request', refs)['execution']['final_count']
        ids = ids[:wanted]
        self.state['qualified_candidates'] = ids
        required = {r['rule_id'] for r in self.data('qualified_profile', refs)['rules'] if r['required']}
        evaluated = {row['candidate_id']: row for row in evaluation.get('candidates', [])}
        unresolved = False
        for c in manifest['candidates']:
            if c['status'] == 'rejected':
                continue
            rows = {r['rule_id']: r for r in evaluated.get(c['candidate_id'], {}).get('rules', [])}
            if not required.issubset(rows) or any(rows[r].get('status') not in {'PASS', 'FAIL'} for r in required if r in rows):
                unresolved = True
        status = 'QUALIFIED' if len(ids) == wanted else 'PARTIAL' if ids or unresolved else 'NO_QUALIFYING_DESIGNS'
        return self.finish(status, f'{len(ids)} candidates satisfy every required computational evidence rule')


def doctor(root: Path) -> dict:
    c = Controller(root)
    c.verify_run()
    cfg = c.state['agent_config']
    binary = cfg.get('executable', 'sci') if cfg.get('backend', 'sci') == 'sci' else cfg['argv'][0]
    found = shutil.which(binary)
    return {'harness_executable': found, 'controller_ready': found is not None,
            'remaining': c.remaining(), 'condition': c.state['condition'],
            'scientific_methods_qualified': 'not_assessed',
            'scope': 'Offline wiring check only; model access and scientific adapters are not exercised'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'run', 'status', 'doctor'):
        sub = subs.add_parser(name)
        sub.add_argument('--run-dir', type=Path, required=True)
        if name == 'init':
            sub.add_argument('--request', required=True)
            sub.add_argument('--input', type=Path, action='append', default=[])
            sub.add_argument('--agent-config', type=Path)
            sub.add_argument('--policy', type=Path)
            sub.add_argument('--condition', choices=('agent_selected', 'tools_specified'), default='agent_selected')
        if name == 'run':
            sub.add_argument('--max-stages', type=int)
    args = parser.parse_args()
    try:
        if args.command == 'init':
            result = initialize(args.run_dir, args.request, args.input,
                                load_json(args.agent_config) if args.agent_config else {'backend': 'sci'},
                                load_json(args.policy) if args.policy else None, args.condition)
            result = {'run_id': result['run_id'], 'status': result['status'],
                      'next': f'Run this CLI with run --run-dir {args.run_dir}'}
        elif args.command == 'run':
            if args.max_stages is not None and args.max_stages < 1:
                raise ValueError('--max-stages must be positive')
            result = Controller(args.run_dir).run(args.max_stages)
        elif args.command == 'doctor':
            result = doctor(args.run_dir)
        else:
            c = Controller(args.run_dir)
            result = {'status': c.state['status'], 'remaining': c.remaining(),
                      'stages': {k: v['status'] for k, v in c.state['stages'].items()},
                      'inflight': c.state['inflight'], 'qualified_candidates': c.state['qualified_candidates']}
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except Exception as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
