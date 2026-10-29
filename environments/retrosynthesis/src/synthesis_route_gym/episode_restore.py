"""Fail-closed validation of durable host episode state."""
import hashlib
import json
import math
from .schemas import RouteCandidate, Task


def _require(condition, reason):
    if not condition:
        raise ValueError('Invalid episode checkpoint: ' + reason)


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_checkpoint(state, *, expected_task=None, now):
    _require(isinstance(state, dict) and state.get('checkpoint_version') in {1, 2, 3}, 'version')
    required = {'task', 'seed', 'routes', 'submitted_route_ids', 'usage', 'terminated', 'truncated',
                'checkpoint_version', 'task_sha256', 'started_at', 'saved_at', 'deadline_at',
                'events', 'receipts', 'pending_action', 'cancel_reason'}
    if state['checkpoint_version'] in {2, 3}:
        required |= {'scientific_usage','scientific_limits','capability_fingerprint','retrieved_source_ids','source_access_mode'}
        _validate_science(state)
    if 'application_fingerprint' in state:
        import re
        _require(isinstance(state['application_fingerprint'],str) and re.fullmatch('[a-f0-9]{64}',state['application_fingerprint']), 'application configuration')
        required |= {'application_fingerprint'}
    _require(set(state) == required, 'fields')
    task = Task.model_validate(state['task'])
    task_hash = hashlib.sha256(task.model_dump_json().encode()).hexdigest()
    _require(state['task_sha256'] == task_hash, 'task identity hash')
    if expected_task is not None:
        expected = Task.model_validate(expected_task.model_dump() if isinstance(expected_task, Task) else expected_task)
        _require(expected == task, 'task differs from requested task')
    _require(all(_number(state[k]) for k in ('started_at', 'saved_at')), 'timestamps')
    _require(state['saved_at'] >= state['started_at'] and now >= state['saved_at'], 'clock moved backwards')
    if task.budget.regime == 'unbudgeted':
        _require(state['checkpoint_version'] == 3 and state['deadline_at'] is None, 'unbudgeted deadline version')
    else:
        _require(state['checkpoint_version'] in {1, 2}, 'budgeted version')
        _require(_number(state['deadline_at']) and state['deadline_at'] == state['started_at'] + task.budget.max_wall_seconds, 'deadline')
    _require(type(state['seed']) is int, 'seed')
    _require(type(state['terminated']) is bool and type(state['truncated']) is bool, 'closed flags')
    _require(state['cancel_reason'] is None or isinstance(state['cancel_reason'], str), 'cancel reason')
    usage = state['usage']
    _require(isinstance(usage, dict) and set(usage) == {'actions', 'expansions', 'wall_seconds'}, 'usage fields')
    _require(all(type(usage[k]) is int and usage[k] >= 0 for k in ('actions', 'expansions')), 'usage counts')
    _require(usage['expansions'] <= usage['actions'] and
             (task.budget.max_actions is None or usage['actions'] <= task.budget.max_actions), 'action allowance')
    _require(task.budget.max_expansions is None or usage['expansions'] <= task.budget.max_expansions, 'expansion allowance')
    _require(_number(usage['wall_seconds']) and usage['wall_seconds'] >= 0, 'elapsed time')
    _require(isinstance(state['routes'], list), 'routes')
    routes = [RouteCandidate.model_validate(r) for r in state['routes']]
    ids = [r.route_id for r in routes]
    _require(len(set(ids)) == len(ids), 'duplicate route IDs')
    submitted = state['submitted_route_ids']
    _require(isinstance(submitted, list) and all(isinstance(v, str) for v in submitted), 'submission IDs')
    _require(len(set(submitted)) == len(submitted) and set(submitted) <= set(ids), 'unknown submitted routes')
    _require(len(submitted) <= task.budget.top_k, 'submission allowance')
    _validate_events(state)
    if state['checkpoint_version'] in {2, 3}:
        _validate_science_history(state)
    return task


def _validate_events(state):
    events, receipts, pending = state['events'], state['receipts'], state['pending_action']
    _require(isinstance(events, list) and isinstance(receipts, dict), 'event collections')
    _require(len(events) + int(pending is not None) == state['usage']['actions'], 'lost action accounting')
    previous, ids = '', set()
    for index, event in enumerate(events):
        _require(isinstance(event, dict), 'event')
        original = {k: v for k, v in event.items() if k not in {'sha256', 'previous_sha256'}}
        digest = hashlib.sha256((previous + json.dumps(original, sort_keys=True)).encode()).hexdigest()
        _require(event.get('index') == index and event.get('previous_sha256') == previous
                 and event.get('sha256') == digest, 'event hash chain')
        previous = digest
        action_id = event.get('action_id')
        _require(isinstance(action_id, str) and action_id not in ids and action_id in receipts, 'action receipt')
        _require(event['usage']['actions'] == index + 1, 'event action count')
        receipt = receipts[action_id]
        _require(isinstance(receipt, dict) and set(receipt) == {'payload_sha256', 'response'}, 'receipt shape')
        payload = {'action': event['action'], 'arguments': event['arguments']}
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        _require(receipt['payload_sha256'] in {None, fingerprint}, 'receipt payload fingerprint')
        response = receipt['response']
        _require(isinstance(response, dict) and response.get('status') == event['status']
                 and response.get('result') == event['result'], 'receipt result')
        ids.add(action_id)
    _require(set(receipts) == ids, 'orphan receipts')
    if pending is not None:
        _require(isinstance(pending, dict) and set(pending) == ({'action', 'arguments', 'action_id', 'payload_sha256'} | ({'scientific_usage'} if state['checkpoint_version'] in {2, 3} else set())), 'pending action')
        _require(isinstance(pending['action_id'], str) and pending['action_id'] not in ids, 'pending identity')


def _validate_science(state):
    from .scientific_execution import ACCOUNTED_SCIENTIFIC_ACTIONS, ScientificLimits
    import re
    _require(state.get('source_access_mode') in {'closed_information','evidence_retrieval'}, 'source access mode')
    usage = state.get('scientific_usage')
    _require(isinstance(usage,dict) and set(usage) <= ACCOUNTED_SCIENTIFIC_ACTIONS, 'scientific usage fields')
    _require(all(type(v) is int and v >= 0 for v in usage.values()), 'scientific usage counts')
    _require(sum(usage.values()) <= state['usage']['actions'], 'scientific action accounting')
    ScientificLimits(**state['scientific_limits'])
    _require(isinstance(state.get('capability_fingerprint'),str) and
             re.fullmatch(r'[a-f0-9]{64}',state['capability_fingerprint']), 'scientific binding')
    ids = state['retrieved_source_ids']
    _require(isinstance(ids,list) and all(isinstance(v,str) for v in ids) and len(ids)==len(set(ids)), 'retrieved source identities')


def _validate_science_history(state):
    from .tool_registry import ALIASES
    from .scientific_execution import ACCOUNTED_SCIENTIFIC_ACTIONS, ACCOUNTING_ALIASES
    previous, retrieved = {}, []
    rows = list(state['events']) + ([state['pending_action']] if state['pending_action'] else [])
    for row in rows:
        current = row.get('scientific_usage')
        _require(isinstance(current,dict) and set(current) <= ACCOUNTED_SCIENTIFIC_ACTIONS,
                 'scientific history counts')
        _require(all(type(v) is int and v >= 0 for v in current.values()), 'scientific history values')
        action = row.get('action')
        action = ALIASES.get(action, action) if isinstance(action,str) else '__invalid__'
        action = ACCOUNTING_ALIASES.get(action,action)
        expected = dict(previous)
        if action in ACCOUNTED_SCIENTIFIC_ACTIONS:
            expected[action] = expected.get(action,0)+1
        if action == 'rank_routes':
            delta = current.get('predict_conditions',0)-previous.get('predict_conditions',0)
            _require(delta in {0,1}, 'scientific ranking calls')
            if delta:
                expected['predict_conditions'] = previous.get('predict_conditions',0)+1
        _require(current == expected, 'scientific counter differs from action history')
        previous = current
        if action == 'retrieve_sources' and row.get('status') == 'ok':
            retrieved += [record['record_id'] for record in row['result']['data']['records']]
    _require(state['scientific_usage'] == previous, 'scientific usage rollback')
    _require(state['retrieved_source_ids'] == list(dict.fromkeys(retrieved)), 'scientific retrieved source history')
