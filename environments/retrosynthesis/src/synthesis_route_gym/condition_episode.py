"""Durable condition decisions exposing only admitted measured observations.

The host owns the immutable study. Policies receive public views and registered
observations, never the source optimum or unqueried outcomes.
"""
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import re
from threading import RLock
import time
from urllib.parse import urlsplit
from uuid import uuid4
from .chemistry import canonical_smiles
from .episode_store import EpisodeStore
from .portfolio_conditions import ConditionRecord, FiniteConditionStudy

SCHEMA = 'srg-condition-episode-v1'
EVIDENCE = 'measured_dataset_replay'
PREDICTION_FIELDS = frozenset({'candidate_id', 'prediction_id', 'status', 'value',
                             'unit', 'domain', 'uncertainty', 'model_version'})
OUTCOME_FIELDS = frozenset({'yield', 'yield_percent', 'outcome', 'outcomes', 'label',
                           'labels', 'score', 'best', 'optimum', 'value'})


def _copy(value):
    return json.loads(json.dumps(value, allow_nan=False))


def _hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _text(value, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError('Expected bounded nonblank text')
    return value


def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,199}', value):
        raise ValueError('Expected bounded identifier')
    return value


def _integer(value, minimum=0, maximum=100000):
    if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
        raise ValueError('Invalid bounded integer')
    return value


def _number(value, minimum=0, maximum=100):
    if type(value) not in (int, float) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError('Invalid finite number')
    return float(value)


def _validated_record(row):
    if not isinstance(row, ConditionRecord):
        raise ValueError('Invalid condition record')
    if not isinstance(row.conditions, (tuple, list)) or not 1 <= len(row.conditions) <= 32:
        raise ValueError('Expected bounded condition factors')
    pairs = []
    for pair in row.conditions:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError('Invalid condition factor')
        key, value = _text(pair[0], 100), _text(pair[1])
        if key.strip().casefold() in OUTCOME_FIELDS:
            raise ValueError('Outcomes cannot be condition inputs')
        pairs.append((key, value))
    if len({key for key, _ in pairs}) != len(pairs):
        raise ValueError('Duplicate condition factor')
    return ConditionRecord(_identifier(row.candidate_id), tuple(pairs), _number(row.yield_percent))


def _validated_study(study):
    if not isinstance(study, FiniteConditionStudy):
        raise ValueError('Expected host-owned finite measured study')
    budget = None if study.budget is None else _integer(study.budget, 1)
    url = urlsplit(_text(study.source_url))
    if url.scheme not in {'https', 'http'} or not url.netloc or url.username or url.password:
        raise ValueError('Study requires public source URL')
    _text(study.source_locator)
    if not isinstance(study.dataset_sha256, str) or not re.fullmatch('[a-f0-9]{64}', study.dataset_sha256):
        raise ValueError('Study requires dataset digest')
    if not isinstance(study._records, (tuple, list)) or not 1 <= len(study._records) <= 100:
        raise ValueError('Study requires 1..100 registered candidates')
    records = tuple(_validated_record(row) for row in study._records)
    ids = tuple(row.candidate_id for row in records)
    settings = tuple(tuple(sorted(row.conditions)) for row in records)
    if len(set(ids)) != len(ids) or len(set(settings)) != len(settings):
        raise ValueError('Duplicate candidate or settings require explicit replicate aggregation')
    factors = {key for key, _ in records[0].conditions}
    if any({key for key, _ in row.conditions} != factors for row in records):
        raise ValueError('Candidate condition factors differ')
    if (not isinstance(study.observed_ids, (tuple, list))
            or any(not isinstance(key, str) for key in study.observed_ids)):
        raise ValueError('Invalid initial observation identities')
    observed = tuple(study.observed_ids)
    if len(set(observed)) != len(observed) or set(observed) - set(ids) or (budget is not None and len(observed) > budget):
        raise ValueError('Invalid initial observation identities')
    return FiniteConditionStudy(records, observed, budget, study.source_url,
                                study.source_locator, study.dataset_sha256,
                                canonical_smiles(study.substrate))


def _validated_predictions(rows, ids):
    if not isinstance(rows, (tuple, list)) or len(rows) > 100:
        raise ValueError('Expected bounded registered predictions')
    result = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != PREDICTION_FIELDS:
            raise ValueError('Invalid prediction fields')
        _identifier(row['prediction_id'])
        if not isinstance(row['candidate_id'], str) or row['candidate_id'] not in ids or row['unit'] != 'percent':
            raise ValueError('Prediction identity or unit differs')
        for key in ('domain', 'uncertainty', 'model_version'):
            _text(row[key])
        if row['status'] == 'scored':
            _number(row['value'])
        elif row['status'] != 'abstained' or row['value'] is not None:
            raise ValueError('Invalid prediction value or status')
        result.append(_copy(row))
    if (len({r['candidate_id'] for r in result}) != len(result)
            or len({r['prediction_id'] for r in result}) != len(result)):
        raise ValueError('Duplicate prediction identity')
    return tuple(result)


class ConditionEpisode:
    """Persistent measured replay, unique observation reservations and safe views.

    New observations are reserved before source lookup. Unknown interrupted
    requests remain charged and cannot be queried again. Repeated known values
    cost an action only. Exact action-ID replay returns the original response.
    """

    def __init__(self, study, *, study_id, predictions=(), target=None, max_actions=80,
                 wall_seconds=600, store=None, clock=time.monotonic, wall_clock=time.time, regime='budgeted'):
        self._configure(study, study_id, predictions, target, max_actions, wall_seconds,
                        store, clock, wall_clock, regime)
        started = float(wall_clock())
        self._state = {'schema_version': self._schema, 'binding': self._binding, 'revision': 0,
                       'started_wall': started, 'deadline': None if self.wall_seconds is None else started + self.wall_seconds,
                       'elapsed_seconds': 0.0, 'saved_at_wall': started,
                       'actions': 0, 'observations': [self._reveal(key) for key in self._study.observed_ids],
                       'reserved_candidate_ids': [], 'pending': None, 'cache': {}, 'events': [],
                       'submission': {'status': 'not_submitted', 'candidate_id': None},
                       'terminated': False, 'truncated': False, 'stop_reason': None}
        self._store_revision = self._store.initialize(self._state) if self._store else None

    def _configure(self, study, study_id, predictions, target, max_actions, wall_seconds, store, clock, wall_clock, regime):
        self._study = _validated_study(study)
        if regime not in {'budgeted', 'unbudgeted'}:
            raise ValueError('Unknown condition resource regime')
        ceilings = (max_actions, wall_seconds, self._study.budget)
        if (regime == 'unbudgeted' and any(value is not None for value in ceilings)
                or regime == 'budgeted' and any(value is None for value in ceilings)):
            raise ValueError('Condition resource ceilings must match explicit regime')
        self.regime = regime
        self._schema = 'srg-condition-episode-v2' if regime == 'unbudgeted' else SCHEMA
        self.study_id = _identifier(study_id)
        self.target = canonical_smiles(target) if target is not None else None
        self.max_actions = None if max_actions is None else _integer(max_actions, 1)
        self.wall_seconds = None if wall_seconds is None else _number(wall_seconds, minimum=0.000001, maximum=31536000)
        self._clock, self._wall_clock, self._monotonic_start = clock, wall_clock, float(clock())
        self._elapsed_floor, self._lock = 0.0, RLock()
        self._records = {row.candidate_id: row for row in self._study._records}
        self._predictions = _validated_predictions(predictions, set(self._records))
        self._candidates = [{'candidate_id': row.candidate_id, 'conditions': dict(row.conditions)}
                            for row in self._study._records]
        if len(json.dumps([self._candidates, self._predictions]).encode()) > 64000:
            raise ValueError('Public candidate/prediction context exceeds 64 KB')
        self._store = store if isinstance(store, EpisodeStore) or store is None else EpisodeStore(store)
        self._binding = _hash({'study': asdict(self._study), 'study_id': self.study_id,
                              'predictions': self._predictions, 'target': self.target,
                              'max_actions': self.max_actions, 'wall_seconds': self.wall_seconds,
                              **({'regime': regime} if regime == 'unbudgeted' else {}),
                              'implementation': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})

    @property
    def binding_fingerprint(self):
        return self._binding

    @classmethod
    def resume(cls, store, study, *, study_id, predictions=(), target=None, max_actions=80,
               wall_seconds=600, clock=time.monotonic, wall_clock=time.time, regime='budgeted'):
        env = cls.__new__(cls)
        env._configure(study, study_id, predictions, target, max_actions, wall_seconds, store, clock, wall_clock, regime)
        state, revision = env._store.load()
        if state.get('schema_version') != env._schema or state.get('binding') != env._binding:
            raise ValueError('Condition episode resume binding differs')
        try:
            env._validate_restored(state)
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError('Malformed condition episode checkpoint') from exc
        env._state, env._store_revision = _copy(state), revision
        now = float(wall_clock())
        env._elapsed_floor = max(state['elapsed_seconds'],
            state['elapsed_seconds'] + max(0.0, now - state['saved_at_wall']),
            max(0.0, now - state['started_wall']))
        if state['pending'] is not None:
            env._finish('interrupted', {'reason': 'Interrupted action consumed; unknown measurement is not replayed.'})
        return env

    def _validate_restored(self, state):
        required = {'schema_version', 'binding', 'revision', 'started_wall', 'deadline', 'actions',
                    'observations', 'reserved_candidate_ids', 'pending', 'cache', 'events',
                    'submission', 'terminated', 'truncated', 'stop_reason',
                    'elapsed_seconds', 'saved_at_wall'}
        if set(state) != required:
            raise ValueError('Invalid condition checkpoint fields')
        _integer(state['revision'], maximum=None if self.max_actions is None else 2 * self.max_actions + 1)
        _integer(state['actions'], maximum=self.max_actions)
        _number(state['started_wall'], maximum=1e15)
        if self.wall_seconds is not None:
            _number(state['deadline'], maximum=1e15)
        _number(state['saved_at_wall'], maximum=1e15)
        _number(state['elapsed_seconds'], maximum=1e15)
        expected_deadline = None if self.wall_seconds is None else state['started_wall'] + self.wall_seconds
        if state['deadline'] != expected_deadline:
            raise ValueError('Invalid persisted deadline')
        reserved = state['reserved_candidate_ids']
        if (not isinstance(reserved, list) or len(set(reserved)) != len(reserved)
                or set(reserved) - set(self._records) or set(reserved) & set(self._study.observed_ids)
                or (self._study.budget is not None and len(reserved) + len(self._study.observed_ids) > self._study.budget)):
            raise ValueError('Invalid observation reservations')
        keys = [row['candidate_id'] for row in state['observations']]
        if (len(set(keys)) != len(keys) or set(self._study.observed_ids) - set(keys)
                or set(keys) - (set(reserved) | set(self._study.observed_ids))
                or any(row != self._reveal(row['candidate_id']) for row in state['observations'])):
            raise ValueError('Invalid persisted observations')
        if (type(state['terminated']) is not bool or type(state['truncated']) is not bool
                or not isinstance(state['cache'], dict) or not isinstance(state['events'], list)
                or len(state['events']) > state['actions']):
            raise ValueError('Invalid persisted episode progress')
        submission = state['submission']
        if (set(submission) != {'status', 'candidate_id'}
                or submission['status'] not in {'not_submitted', 'selected', 'abstained'}
                or (submission['status'] == 'selected' and submission['candidate_id'] not in keys)
                or (submission['status'] != 'selected' and submission['candidate_id'] is not None)
                or state['terminated'] != (submission['status'] != 'not_submitted')):
            raise ValueError('Invalid persisted submission')
        self._validate_journal(state)

    def _validate_journal(self, state):
        pending, events, cache = state['pending'], state['events'], state['cache']
        if len(events) + int(pending is not None) != state['actions']:
            raise ValueError('Persisted action count differs from journal')
        event_ids = [row['action_id'] for row in events]
        if len(set(event_ids)) != len(event_ids) or set(cache) != set(event_ids):
            raise ValueError('Persisted action cache differs from journal')
        observed = [self._reveal(key) for key in self._study.observed_ids]
        reserved = []
        for event in events:
            entry = cache[event['action_id']]
            request = {'name': event['name'], 'arguments': event['arguments']}
            if (set(entry) != {'request', 'response'} or entry['request'] != request
                    or entry['response'] != event['response']):
                raise ValueError('Persisted action response differs from journal')
            candidate = event['candidate_id']
            if candidate is not None:
                if (event['name'] != 'observe_condition' or candidate not in self._records
                        or event['arguments'].get('candidate_id') != candidate):
                    raise ValueError('Invalid persisted observation admission')
                reserved.append(candidate)
                if event['status'] == 'ok':
                    observed.append(self._reveal(candidate))
            result = event['response']['result']
            view = result if event['name'] == 'inspect' and event['status'] == 'ok' else result['view']
            if (view['observations'] != observed or view['candidates'] != self._candidates
                    or view['predictions'] != list(self._predictions) or view['study_id'] != self.study_id):
                raise ValueError('Persisted public view differs from admitted observations')
        if pending is not None:
            if (not isinstance(pending, dict) or set(pending) != {'action_id', 'request', 'candidate_id'}
                    or set(pending['request']) != {'name', 'arguments'}
                    or pending['action_id'] in cache):
                raise ValueError('Invalid pending action')
            _identifier(pending['action_id'])
            if pending['candidate_id'] is not None:
                if (pending['request']['name'] != 'observe_condition'
                        or pending['request']['arguments'].get('candidate_id') != pending['candidate_id']):
                    raise ValueError('Invalid pending observation admission')
                reserved.append(pending['candidate_id'])
        if reserved != state['reserved_candidate_ids'] or observed != state['observations']:
            raise ValueError('Persisted observation progress differs from journal')

    def _elapsed(self, state=None):
        state = self._state if state is None else state
        return max(state['elapsed_seconds'],
                   self._elapsed_floor + max(0.0, float(self._clock()) - self._monotonic_start),
                   max(0.0, float(self._wall_clock()) - state['started_wall']))

    def _usage(self, state=None):
        state = self._state if state is None else state
        return {'actions': state['actions'], 'observation_calls': len(state['reserved_candidate_ids']),
                'wall_seconds': self._elapsed(state)}

    def _remaining(self, state):
        allowance = len(self._records) if self._study.budget is None else min(self._study.budget, len(self._records))
        return max(0, allowance
                   - len(self._study.observed_ids) - len(state['reserved_candidate_ids']))

    def _wall_exhausted(self):
        return self.wall_seconds is not None and self._elapsed() >= self.wall_seconds

    def _resources(self, state):
        return {'initial_observations': len(self._study.observed_ids),
                'new_observations_used': len(state['reserved_candidate_ids']),
                'remaining_observations': None if self._study.budget is None else self._remaining(state),
                'remaining_actions': None if self.max_actions is None else max(0, self.max_actions - state['actions']),
                'remaining_seconds': None if self.wall_seconds is None else max(0.0, self.wall_seconds - self._elapsed(state)),
                **({'regime': 'unbudgeted', 'remaining_candidates': self._remaining(state)}
                   if self.regime == 'unbudgeted' else {})}

    def _view(self, state):
        return {'schema_version': 'srg-condition-view-v1', 'study_id': self.study_id,
                'revision': state['revision'], 'substrate': self._study.substrate, 'target': self.target,
                'domain_status': 'registered_measured_study',
                'measurement': {'name': 'yield', 'unit': 'percent', 'evidence_kind': EVIDENCE},
                'candidates': self._candidates, 'observations': state['observations'],
                'unavailable_candidate_ids': [key for key in state['reserved_candidate_ids']
                    if key not in {row['candidate_id'] for row in state['observations']}],
                'predictions': list(self._predictions),
                'resources': self._resources(state),
                'submission': state['submission'], 'terminated': state['terminated'],
                'truncated': state['truncated'], 'usage': self._usage(state)}

    def public_view(self):
        with self._lock:
            return _copy(self._view(self._state))

    def export(self):
        with self._lock:
            return _copy({**self._view(self._state), 'events': self._state['events'],
                          'stop_reason': self._state['stop_reason']})

    def _save(self, state):
        updated = {**state, 'revision': self._state['revision'] + 1,
                   'elapsed_seconds': self._elapsed(), 'saved_at_wall': float(self._wall_clock())}
        if self._store:
            self._store_revision = self._store.commit(updated, expected_revision=self._store_revision)
        self._state = updated

    def _reveal(self, candidate_id):
        row = self._records[candidate_id]
        return {'candidate_id': candidate_id, 'value': row.yield_percent,
                'source_record_id': f'study:{self._study.dataset_sha256}:{_hash(candidate_id)[:20]}',
                'evidence_kind': EVIDENCE}

    def _envelope(self, status, result, state=None):
        state = self._state if state is None else state
        return _copy({'status': status, 'result': result, 'terminated': state['terminated'],
                      'truncated': state['truncated'], 'usage': self._usage(state)})

    def cancel(self, reason='host_cancelled'):
        _text(reason, 200)
        with self._lock:
            if not self._state['terminated'] and not self._state['truncated']:
                self._save({**self._state, 'truncated': True, 'stop_reason': reason})

    def _validate_action(self, name, args):
        if not isinstance(args, dict):
            raise ValueError('Action arguments must be an object')
        fields = {'inspect': set(), 'observe_condition': {'candidate_id'},
                  'predict_reaction_yield': {'candidate_ids'}, 'submit': {'candidate_id'}}
        if name not in fields or set(args) != fields[name]:
            raise ValueError('Unsupported condition action or fields')
        if name in {'observe_condition', 'submit'}:
            key = args['candidate_id']
            if name == 'submit' and key is None:
                return
            if not isinstance(key, str) or key not in self._records:
                raise ValueError('Unknown registered condition candidate')
        if name == 'predict_reaction_yield':
            keys = args['candidate_ids']
            if (not isinstance(keys, list) or not 1 <= len(keys) <= 64
                    or any(not isinstance(key, str) or key not in self._records for key in keys)
                    or len(set(keys)) != len(keys)):
                raise ValueError('Expected 1..64 unique registered prediction candidates')

    def dispatch(self, name, args, action_id=None):
        ident = _identifier(action_id) if action_id is not None else uuid4().hex
        try:
            request = _copy({'name': name, 'arguments': args})
            if len(json.dumps(request).encode()) > 64000:
                raise ValueError('Action request exceeds size limit')
        except (ValueError, TypeError, RecursionError):
            raise ValueError('Action request must be bounded JSON') from None
        with self._lock:
            cached = self._state['cache'].get(ident)
            if cached is not None:
                if cached['request'] == request:
                    return _copy(cached['response'])
                return self._envelope('error', {'reason': 'Action identity already used for another request'})
            if self._state['pending'] is not None:
                return self._envelope('error', {'reason': 'Pending action requires host recovery'})
            if self._state['terminated'] or self._state['truncated']:
                return self._envelope('error', {'reason': 'Condition episode is closed'})
            if self._wall_exhausted() or (self.max_actions is not None and self._state['actions'] >= self.max_actions):
                self.cancel('episode_deadline_expired' if self._wall_exhausted() else 'action_budget_exhausted')
                return self._envelope('error', {'reason': 'Condition episode resource limit reached'})
            return self._admit(ident, request)

    def _admit(self, ident, request):
        name, args = request['name'], request['arguments']
        error, candidate = None, None
        try:
            self._validate_action(name, args)
            if name == 'observe_condition':
                known = {r['candidate_id'] for r in self._state['observations']}
                if args['candidate_id'] not in known:
                    if args['candidate_id'] in self._state['reserved_candidate_ids']:
                        raise ValueError('Prior unknown observation remains consumed')
                    if self._remaining(self._state) == 0:
                        raise ValueError('Observation allowance exhausted')
                    candidate = args['candidate_id']
        except (ValueError, TypeError, KeyError):
            error = 'Invalid condition action or exhausted observation allowance'
        pending = {'action_id': ident, 'request': request, 'candidate_id': candidate}
        reserved = self._state['reserved_candidate_ids'] + ([candidate] if candidate else [])
        self._save({**self._state, 'actions': self._state['actions'] + 1,
                    'reserved_candidate_ids': reserved, 'pending': pending})
        if error:
            return self._finish('error', {'reason': error})
        try:
            status, payload, updates = self._execute(name, args)
        except Exception:
            return self._finish('error', {'reason': 'Condition action failed; reserved observation remains charged'})
        return self._finish(status, payload, updates)

    def _execute(self, name, args):
        if name == 'inspect':
            return 'ok', {}, {}
        if name == 'predict_reaction_yield':
            indexed = {row['candidate_id']: row for row in self._predictions}
            if any(key not in indexed for key in args['candidate_ids']):
                return 'unavailable', {'reason': 'No registered model prediction for requested candidate'}, {}
            return 'ok', {'predictions': [indexed[key] for key in args['candidate_ids']]}, {}
        known = {row['candidate_id']: row for row in self._state['observations']}
        key = args['candidate_id']
        if name == 'submit':
            if key is not None and key not in known:
                return 'error', {'reason': 'Only observed conditions may be submitted'}, {}
            submission = {'status': 'abstained' if key is None else 'selected', 'candidate_id': key}
            return 'ok', {'submission': submission}, {'submission': submission, 'terminated': True,
                                                     'stop_reason': 'agent_submitted'}
        if key in known:
            return 'ok', {'observation': known[key], 'already_observed': True}, {}
        observation = self._reveal(key)
        if self._wall_exhausted():
            return 'error', {'reason': 'Observation completed after deadline; discarded'}, {
                'truncated': True, 'stop_reason': 'episode_deadline_expired'}
        return 'ok', {'observation': observation, 'already_observed': False}, {
            'observations': [*self._state['observations'], observation],
            **({'stop_reason': 'candidate_space_exhausted'}
               if self.regime == 'unbudgeted' and self._remaining(self._state) == 0 else {})}

    def _finish(self, status, payload, updates=None):
        pending = self._state['pending']
        updated = {**self._state, **(updates or {}), 'pending': None,
                   'revision': self._state['revision'] + 1}
        view = self._view(updated)
        result = view if pending['request']['name'] == 'inspect' and status == 'ok' else {**payload, 'view': view}
        response = self._envelope(status, result, updated)
        event = {'action_id': pending['action_id'], **pending['request'], 'status': status,
                 'candidate_id': pending['candidate_id'], 'response': response}
        cache = {**self._state['cache'], pending['action_id']: {'request': pending['request'], 'response': response}}
        self._save({**updated, 'events': [*self._state['events'], event], 'cache': cache})
        return _copy(response)
