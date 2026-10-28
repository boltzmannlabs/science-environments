"""Versioned local candidate handoffs and evidence-limited, call-free feedback."""
import hashlib
import json
import math
from typing import Annotated, Literal
from pydantic import Field, field_validator, model_validator
from .schemas import Record, Identifier, Smiles, InventoryItem, Constraints, Budget, Task, RouteCandidate
from .validation import assess_route

Text = Annotated[str, Field(strict=True, min_length=1, max_length=200)]
Digest = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]


def plain(value):
    if hasattr(value, 'model_dump'):
        value = value.model_dump(mode='json')
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    require(len(encoded.encode()) <= 20_000_000, 'Handoff input exceeds size limit')
    return json.loads(encoded)


def digest(value):
    return hashlib.sha256(json.dumps(plain(value), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


class SmallMoleculeHandoff(Record):
    schema_version: Literal['srg-small-molecule-handoff-v1'] = 'srg-small-molecule-handoff-v1'
    candidate_id: Identifier
    smiles: Smiles
    source_job_id: Identifier
    source_tool: Text
    source_tool_version: Text | None = None
    upstream_payload_sha256: Digest | None = None
    target_amount_mmol: Annotated[float, Field(strict=True, gt=0, le=1e12, allow_inf_nan=False)] | None = None
    inventory: Annotated[tuple[InventoryItem, ...], Field(max_length=100000)]
    constraints: Constraints = Field(default_factory=Constraints)
    budget: Budget = Field(default_factory=Budget)
    seed: Annotated[int, Field(strict=True, ge=0, le=2**32-1)] = 0

    @field_validator('source_tool', 'source_tool_version')
    @classmethod
    def nonblank(cls, value):
        require(value is None or bool(value.strip()), 'Source tool metadata must not be blank')
        return value

    @model_validator(mode='after')
    def unique_inventory(self):
        require(len({x.smiles for x in self.inventory}) == len(self.inventory), 'Inventory identities must be unique')
        return self


def build_handoff_task(handoff):
    row = SmallMoleculeHandoff.model_validate(plain(handoff))
    return Task(task_id=row.candidate_id, target=row.smiles, inventory=row.inventory,
                target_amount_mmol=row.target_amount_mmol, constraints=row.constraints, budget=row.budget)


def build_handoff_manifest(handoff):
    row = SmallMoleculeHandoff.model_validate(plain(handoff))
    task = build_handoff_task(row)
    return {'schema_version': 'srg-small-molecule-manifest-v1', 'handoff': plain(row),
            'task': plain(task), 'handoff_sha256': digest(row),
            'task_sha256': hashlib.sha256(task.model_dump_json().encode()).hexdigest(),
            'provenance_status': 'caller_supplied_unverified'}


def _episode(manifest, episode):
    expected = build_handoff_manifest(manifest['handoff'])
    require(manifest == expected, 'Handoff manifest mismatch')
    task = build_handoff_task(manifest['handoff'])
    require(episode.get('task') == manifest['task'] and episode.get('task_sha256') == manifest['task_sha256'], 'Episode task mismatch')
    require(type(episode.get('seed')) is int and episode['seed'] == manifest['handoff']['seed'], 'Episode seed mismatch')
    require(all(type(episode.get(k)) is bool for k in ('terminated', 'truncated')), 'Invalid episode status')
    routes = [RouteCandidate.model_validate(r) for r in episode.get('routes', [])]
    require((task.budget.max_actions is None or len(routes) <= task.budget.max_actions) and len({r.route_id for r in routes}) == len(routes), 'Invalid route identities')
    require([plain(r) for r in routes] == episode.get('routes'), 'Noncanonical episode routes')
    events, head = _event_chain(episode, routes)
    require(len(episode['submitted_route_ids']) <= task.budget.top_k, 'Submission exceeds top-k')
    return task, routes, events, head


def _event_chain(episode, routes):
    events = episode.get('events')
    require(isinstance(events, list) and len(events) <= 100000, 'Invalid event list')
    head, ids, proposed, submissions = '', set(), [], []
    for i, event in enumerate(events):
        require(isinstance(event, dict) and event.get('index') == i, 'Invalid event index')
        body = {k:v for k,v in event.items() if k not in {'sha256', 'previous_sha256'}}
        checksum = hashlib.sha256((head + json.dumps(body, sort_keys=True)).encode()).hexdigest()
        require(event.get('previous_sha256') == head and event.get('sha256') == checksum, 'Event hash chain mismatch')
        identity = event.get('action_id')
        require(isinstance(identity, str) and identity not in ids, 'Invalid action identity')
        ids.add(identity)
        require(event.get('usage', {}).get('actions') == i+1, 'Invalid action accounting')
        if event.get('status') == 'ok' and event.get('action') == 'propose_route':
            proposed.append(plain(RouteCandidate.model_validate(event['arguments']['route'])))
        if event.get('status') == 'ok' and event.get('action') == 'submit':
            submissions.append(event['arguments']['route_ids'])
        head = checksum
    require(proposed == [plain(r) for r in routes], 'Registered routes differ from committed proposals')
    submitted = episode.get('submitted_route_ids')
    require(isinstance(submitted, list) and all(isinstance(x, str) for x in submitted), 'Invalid submission')
    require(len(submitted) == len(set(submitted)) and set(submitted) <= {r.route_id for r in routes}, 'Invalid submitted routes')
    require(len(submissions) <= 1 and bool(submissions) == episode['terminated'], 'Submission state mismatch')
    require(submitted == (submissions[0] if submissions else []), 'Submission differs from committed event')
    usage = episode.get('usage', {})
    require(usage.get('actions') == len(events), 'Snapshot contains uncommitted action')
    require(type(usage.get('expansions')) is int and 0 <= usage['expansions'] <= len(events), 'Invalid expansion accounting')
    require(isinstance(usage.get('wall_seconds'), (int,float)) and math.isfinite(usage['wall_seconds']) and usage['wall_seconds'] >= 0, 'Invalid elapsed time')
    return events, head


def _assessment_rows(task, routes, episode):
    supplied = episode.get('assessments', [])
    require(isinstance(supplied, list) and len(supplied) == len(routes), 'Missing route assessments')
    rows = []
    for route, recorded in zip(routes, supplied):
        calculated = plain(assess_route(task, route))
        ignored = {'evidence_status', 'conditions_evidence', 'weak_steps'}
        require({k:v for k,v in recorded.items() if k not in ignored} == {k:v for k,v in calculated.items() if k not in ignored}, 'Assessment differs from task and route')
        require(set(recorded['evidence_status']) == {s.step_id for s in route.steps}, 'Evidence step identities mismatch')
        require(set(recorded['conditions_evidence']) == {s.step_id for s in route.steps}, 'Condition step identities mismatch')
        require(set(recorded['evidence_status'].values()) <= {'literature_exact','literature_analogue','measured','proxy','predicted','unresolved'} and set(recorded['conditions_evidence'].values()) <= {'unknown','same','different'}, 'Invalid evidence statuses')
        gaps = [s.step_id for s in route.steps if recorded['evidence_status'][s.step_id] not in {'literature_exact','measured'} or recorded['conditions_evidence'][s.step_id] != 'same']
        eligible = calculated['graph_valid'] and calculated['inventory_complete'] and calculated['constraint_compliant'] and calculated['quantity_status'] != 'insufficient'
        rows.append({'route_id': route.route_id, 'route_sha256': digest(route), 'deterministically_eligible': eligible,
                     'assessment': recorded, 'source_support_gaps': gaps,
                     'evidence_authority': 'recorded_host_assessment_not_independent_review', 'claims_feasible_synthesis': False})
    return rows


def _process_estimates(task, routes, events, submitted, task_sha256):
    latest, references = {}, {r.route_id:digest(r) for r in routes}
    for event in events:
        outer = event.get('result', {})
        if event.get('status') != 'ok' or event.get('action') != 'application_report' or outer.get('application') != 'process_route_selection':
            continue
        require(outer.get('task_sha256') == task_sha256, 'Process report task mismatch')
        for ref in outer.get('route_references', []):
            require(references.get(ref.get('route_id')) == ref.get('route_sha256'), 'Process route reference mismatch')
        report = outer.get('result', {})
        require(report.get('schema_version') == 'srg-process-report-v1', 'Unknown process report')
        for row in report.get('routes', []):
            require(references.get(row.get('route_id')) == row.get('route_sha256') and row.get('target') == task.target and row.get('scale_mmol') == task.target_amount_mmol, 'Process estimate route or scale mismatch')
            latest[row['route_id']] = (row, report, event)
    results = []
    for rid in submitted:
        base = {'route_id':rid, 'material_cost':None, 'status':'unavailable', 'reason':'no_matching_recorded_process_report'}
        if rid in latest:
            row, report, event = latest[rid]
            if row.get('comparison_eligible'):
                cost = row.get('material_cost')
                require(type(cost) in (int,float) and math.isfinite(cost) and cost >= 0, 'Invalid recorded material cost')
                base = {'route_id':rid, 'material_cost':cost, 'status':'available_declared_estimate',
                        'currency':row.get('currency'), 'scale_mmol':row['scale_mmol'],
                        'price_evidence_kind':row.get('price_evidence_kind'), 'basis':report.get('basis'),
                        'cost_lines':row.get('cost_lines'), 'event_sha256':event['sha256'],
                        'claims_process_savings':False}
            else:
                base = {**base, 'reason':'recorded_process_estimate_ineligible', 'ineligible_reasons':row.get('ineligible_reasons', [])}
        results.append(base)
    return results


def _resources(episode, run, agent):
    ledger = agent.get('ledger')
    if ledger is None and (run.get('runtime_checkpoint') or {}).get('ledger'):
        from .agent_accounting import SharedLedger
        ledger = SharedLedger.from_state(run['runtime_checkpoint']['ledger']).snapshot()
    require(ledger is None or isinstance(ledger, dict), 'Invalid resource ledger')
    values = {k:(ledger or {}).get(k) for k in ('model_calls','tool_calls','actual_tokens','reserved_tokens','charged_tokens','unsettled_requests')}
    require(all(v is None or type(v) is int and v >= 0 for v in values.values()), 'Invalid resource counts')
    if all(values[k] is not None for k in ('actual_tokens','reserved_tokens','charged_tokens')):
        require(values['charged_tokens'] == values['actual_tokens'] + values['reserved_tokens'], 'Token accounting mismatch')
    settled = values['actual_tokens'] if values['reserved_tokens'] == 0 and values['unsettled_requests'] == 0 else None
    return {**values, 'fully_settled_actual_tokens':settled, 'environment_usage':episode['usage'],
            'scientific_usage':episode.get('scientific_usage', {}), 'monetary_cost':None}


def _failures(agent):
    found = []
    def collect(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'provider_request_failures' and isinstance(value, list):
                    found.extend({k:r.get(k) for k in ('category','exception_type','request_id')} for r in value if isinstance(r, dict))
                elif key not in {'context','messages','history','prompt'}:
                    collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)
    collect(agent)
    return list({digest(row):row for row in found}.values())


def _runtime_errors(node):
    if isinstance(node, dict):
        own = [str(node[k]) for k in ('error_type','stop_reason') if node.get(k)]
        if node.get('error'):
            own.append('runtime_error')
        return own + [error for key,value in node.items() if key not in {'context','messages','history','prompt'} for error in _runtime_errors(value)]
    if isinstance(node, list):
        return [error for value in node for error in _runtime_errors(value)]
    return []


def build_handoff_feedback(manifest, episode, *, agent_run=None, episode_id=None, commitment=None):
    manifest, episode, run = plain(manifest), plain(episode), plain(agent_run or {})
    task, routes, events, head = _episode(manifest, episode)
    require('episode' not in run or run['episode'] == episode, 'Agent run episode mismatch')
    agent = run.get('agent', {})
    require(isinstance(agent, dict), 'Invalid agent record')
    rows, failures = _assessment_rows(task, routes, episode), _failures(agent)
    submitted = episode['submitted_route_ids']
    submission = 'submitted_routes' if submitted else 'submitted_empty' if episode['terminated'] else 'not_submitted'
    errors = _runtime_errors(agent)
    stop = ' '.join(errors).lower()
    interrupted = 'interrupt' in stop or any(e['status'] == 'interrupted' for e in events)
    exhausted = ((task.budget.max_actions is not None and episode['usage']['actions'] >= task.budget.max_actions)
                 or (task.budget.max_wall_seconds is not None and episode['usage']['wall_seconds'] >= task.budget.max_wall_seconds)
                 or (task.budget.regime == 'budgeted' and 'budget' in stop))
    execution = ('completed' if episode['terminated'] else 'interrupted' if interrupted else 'budget_exhausted' if exhausted else 'cancelled' if episode['truncated'] else 'failed' if errors else 'incomplete' if agent_run is not None else 'in_progress')
    bound = plain(commitment) if commitment is not None else {'durability':'in_memory_snapshot','episode_sha256':digest(episode)}
    require(bound.get('episode_sha256') == digest(episode) and bound.get('durability') in {'in_memory_snapshot','durable_local_store'}, 'Feedback commitment mismatch')
    return {'schema_version':'srg-small-molecule-feedback-v1',
            **{k:manifest['handoff'][k] for k in ('candidate_id','source_job_id','source_tool','source_tool_version','upstream_payload_sha256','target_amount_mmol')},
            'target':task.target, 'episode_id':episode_id, 'handoff_sha256':manifest['handoff_sha256'],
            'task_sha256':manifest['task_sha256'], 'episode_sha256':digest(episode), 'event_chain_head':head,
            'agent_run_sha256':digest(run) if agent_run is not None else None, 'commitment':bound,
            'provenance_status':'caller_supplied_unverified', 'execution_status':execution, 'submission_status':submission,
            'conversation_status':'not_applicable' if run.get('method') == 'direct_tool' and agent.get('execution_kind') == 'deterministic_direct_tool' else 'unknown' if agent_run is None else 'completed' if agent.get('conversation_completed',agent.get('completed',False)) else 'incomplete',
            'submitted_route_ids':submitted, 'deterministically_eligible_route_ids':[r['route_id'] for r in rows if r['route_id'] in submitted and r['deterministically_eligible']],
            'route_assessments':rows, 'process_estimates':_process_estimates(task,routes,events,submitted,manifest['task_sha256']),
            'provider_failure_count':len(failures), 'provider_failures':failures,
            'failed_actions':[{'action_id':e['action_id'],'action':e['action'],'status':e['status']} for e in events if e['status'] != 'ok'],
            'resources':_resources(episode,run,agent), 'claims_experimental_validation':False,
            'limitations':['Deterministic eligibility is not experimental feasibility.', 'Caller provenance is unverified.', 'Missing costs and unsettled usage remain unknown.']}
