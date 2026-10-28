"""Pure condition-advice contracts for the isolated main-profile LLM runtime.

Only host-normalized observations enter this module. A plan names existing
candidates and evidence; it cannot create experimental outcomes or conditions.
No chemistry package or evaluator is imported into the LLM process.
"""
import hashlib
import json
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer, model_validator

MAX_BYTES = 100000
ID = Annotated[str, Field(strict=True, min_length=1, max_length=240)]
Text = Annotated[str, Field(strict=True, min_length=1, max_length=2000)]
Count = Annotated[int, Field(strict=True, ge=0, le=1000000)]
Number = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
Percent = Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
Digest = Annotated[str, Field(strict=True, pattern=r'^[a-f0-9]{64}$')]
RESOURCE_KEYS = ('remaining_model_calls', 'remaining_tool_calls', 'remaining_tokens', 'remaining_seconds')
IDENTITY_KEYS = ('study_id', 'substrate', 'target', 'domain_status', 'measurement', 'candidates', 'predictions')
OUTCOME_WORDS = ('yield', 'outcome', 'label', 'optimum', 'response', 'score', 'measurement')


class _Record(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    @field_validator('*')
    @classmethod
    def nonblank(cls, value):
        if isinstance(value, str) and not value.strip():
            raise ValueError('Text must not be blank')
        return value


class Candidate(_Record):
    candidate_id: ID
    conditions: Annotated[dict[ID, Text], Field(min_length=1, max_length=32)]

    @field_validator('conditions')
    @classmethod
    def inputs_only(cls, value):
        if any(not key.strip() or not item.strip() or any(word in key.casefold() for word in OUTCOME_WORDS)
               for key, item in value.items()):
            raise ValueError('Conditions must contain input factors only')
        return value


class Observation(_Record):
    candidate_id: ID
    value: Percent
    source_record_id: ID
    evidence_kind: Literal['measured_dataset_replay']


class Prediction(_Record):
    candidate_id: ID
    prediction_id: ID
    status: Literal['scored', 'abstained']
    value: Percent | None
    unit: Literal['percent']
    domain: Text
    uncertainty: Text
    model_version: Text

    @model_validator(mode='after')
    def scored_value(self):
        if (self.status == 'scored') != (self.value is not None):
            raise ValueError('Prediction status and value differ')
        return self


class Measurement(_Record):
    name: Literal['yield']
    unit: Literal['percent']
    evidence_kind: Literal['measured_dataset_replay']


class RegimeResources(_Record):
    """Null means unlimited only in an explicitly identified unbudgeted contract."""
    regime: Literal['budgeted', 'unbudgeted'] = 'budgeted'
    nullable_keys: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode='after')
    def explicit_limits(self):
        unlimited = self.regime == 'unbudgeted'
        if any((getattr(self, key) is None) != unlimited for key in self.nullable_keys):
            raise ValueError('Resource limits must match the explicit budget regime')
        return self

    @model_serializer(mode='wrap')
    def preserve_finite_contract(self, handler):
        values = handler(self)
        return {key: value for key, value in values.items()
                if key != 'regime' or self.regime != 'budgeted'}


class Resources(RegimeResources):
    nullable_keys = ('remaining_observations', 'remaining_actions', 'remaining_seconds')
    initial_observations: Count
    new_observations_used: Count
    remaining_observations: Count | None
    remaining_actions: Count | None
    remaining_seconds: Number | None
    remaining_candidates: Count | None = None

    @model_serializer(mode='wrap')
    def resource_shape(self, handler):
        values = handler(self)
        return {key:value for key,value in values.items()
                if (key != 'regime' or self.regime != 'budgeted')
                and (key != 'remaining_candidates' or value is not None)}


class Usage(_Record):
    actions: Count
    observation_calls: Count
    wall_seconds: Number


class Submission(_Record):
    status: Literal['not_submitted', 'selected', 'abstained']
    candidate_id: ID | None

    @model_validator(mode='after')
    def selected_identity(self):
        if (self.status == 'selected') != (self.candidate_id is not None):
            raise ValueError('Submission status and identity differ')
        return self


class PublicView(_Record):
    schema_version: Literal['srg-condition-view-v1']
    study_id: ID
    revision: Count
    substrate: Text
    target: Text | None
    domain_status: ID
    measurement: Measurement
    candidates: Annotated[tuple[Candidate, ...], Field(min_length=1, max_length=100)]
    observations: Annotated[tuple[Observation, ...], Field(max_length=100)]
    predictions: Annotated[tuple[Prediction, ...], Field(max_length=100)]
    unavailable_candidate_ids: Annotated[tuple[ID, ...], Field(max_length=100)] = ()
    resources: Resources
    submission: Submission
    terminated: Annotated[bool, Field(strict=True)]
    truncated: Annotated[bool, Field(strict=True)]
    usage: Usage

    @model_validator(mode='after')
    def linked_identities(self):
        candidates = [row.candidate_id for row in self.candidates]
        observed = [row.candidate_id for row in self.observations]
        predicted = [row.candidate_id for row in self.predictions]
        collections = (candidates, observed, predicted, self.unavailable_candidate_ids,
                       [row.source_record_id for row in self.observations],
                       [row.prediction_id for row in self.predictions])
        if any(len(set(values)) != len(values) for values in collections):
            raise ValueError('Duplicate public condition identities')
        if (set(observed) | set(predicted) | set(self.unavailable_candidate_ids)) - set(candidates):
            raise ValueError('Evidence refers to an unknown candidate')
        if set(self.unavailable_candidate_ids) & set(observed):
            raise ValueError('Unknown and observed measurements cannot overlap')
        if self.submission.candidate_id is not None and self.submission.candidate_id not in observed:
            raise ValueError('Condition submission lacks an observed measurement')
        initial, queried = self.resources.initial_observations, self.resources.new_observations_used
        if not initial <= len(observed) <= initial + queried:
            raise ValueError('Observation counts differ from resources')
        if queried != self.usage.observation_calls:
            raise ValueError('Observation accounting differs')
        remaining = self.resources.remaining_candidates
        if remaining is not None and remaining != len(set(candidates)-set(observed)-set(self.unavailable_candidate_ids)):
            raise ValueError('Remaining candidate count differs from authorized pool')
        return self


class RuntimeResources(RegimeResources):
    nullable_keys = RESOURCE_KEYS
    remaining_model_calls: Count | None
    remaining_tool_calls: Count | None
    remaining_tokens: Annotated[int, Field(strict=True, ge=0)] | None
    remaining_seconds: Number | None


class ConditionPlan(_Record):
    schema_version: Literal['srg-condition-plan-v1']
    context_sha256: Digest
    decision: Literal['observe', 'abstain']
    next_candidate_id: ID | None
    cited_observation_ids: Annotated[tuple[ID, ...], Field(max_length=20)]
    cited_prediction_ids: Annotated[tuple[ID, ...], Field(max_length=20)]
    rationale: Annotated[str, Field(strict=True, min_length=1, max_length=1200)]
    evidence_status: Literal['agent_proposal']

    @model_validator(mode='after')
    def decision_identity(self):
        if (self.decision == 'observe') != (self.next_candidate_id is not None):
            raise ValueError('Observation decision and candidate differ')
        for values in (self.cited_observation_ids, self.cited_prediction_ids):
            if len(set(values)) != len(values):
                raise ValueError('Duplicate evidence citations')
        return self


def _encoded(value):
    try:
        raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError('Expected finite JSON contract') from error
    if len(raw) > MAX_BYTES:
        raise ValueError('Condition contract exceeds bounded context')
    return raw


def _copy(value):
    return json.loads(_encoded(value))


def initial_state():
    return {'schema_version': 'srg-condition-observer-v1', 'view': None,
            'identity_sha256': None, 'closed': False}


def _view(value):
    raw = _copy(value)
    return PublicView.model_validate(raw).model_dump(mode='json')


def _identity(view):
    return hashlib.sha256(_encoded({key: view[key] for key in IDENTITY_KEYS})).hexdigest()


def _state(value):
    copied = _copy(value)
    if (not isinstance(copied, dict) or set(copied) != set(initial_state())
            or copied['schema_version'] != 'srg-condition-observer-v1'
            or type(copied['closed']) is not bool):
        raise ValueError('Invalid condition observer snapshot')
    current = copied['view']
    if current is None:
        if copied['identity_sha256'] is not None:
            raise ValueError('Empty observer has a study binding')
    else:
        current = _view(current)
        if copied['identity_sha256'] != _identity(current):
            raise ValueError('Condition observer study binding differs')
        copied = {**copied, 'view': current}
    return copied


def _advance(previous, current):
    if current['revision'] < previous['revision']:
        raise ValueError('Stale condition view')
    before = {row['candidate_id']: row for row in previous['observations']}
    after = {row['candidate_id']: row for row in current['observations']}
    if any(after.get(key) != row for key, row in before.items()):
        raise ValueError('Previously observed evidence changed or disappeared')
    if current['revision'] == previous['revision'] and before != after:
        raise ValueError('New evidence requires a new host revision')
    if set(previous['unavailable_candidate_ids']) - set(current['unavailable_candidate_ids']):
        raise ValueError('An unavailable measurement became queryable again')
    for key in ('initial_observations',):
        if current['resources'][key] != previous['resources'][key]:
            raise ValueError('Initial observation allowance changed')
    old, new = previous['resources'], current['resources']
    if old.get('regime', 'budgeted') != new.get('regime', 'budgeted'):
        raise ValueError('Condition budget regime changed')
    if (new['new_observations_used'] < old['new_observations_used']
            or any(old[key] is not None and new[key] > old[key]
                   for key in ('remaining_observations', 'remaining_actions'))):
        raise ValueError('Condition resources were reset')
    if new.get('regime') == 'unbudgeted':
        return
    budget = lambda view: sum(view['resources'][key] for key in ('new_observations_used', 'remaining_observations'))
    if budget(current) != budget(previous):
        raise ValueError('Condition observation allowance changed')


def observe(state, action, args, response):
    """Only successful allowlisted host views update the immutable observer."""
    saved = _state(state)
    if not isinstance(args, dict) or not isinstance(response, dict):
        raise ValueError('Host arguments and responses must be objects')
    for flag in ('terminated', 'truncated'):
        if flag in response and type(response[flag]) is not bool:
            raise ValueError('Invalid host terminal flag')
    closed = saved['closed'] or response.get('terminated', False) or response.get('truncated', False)
    saved = {**saved, 'closed': closed}
    if response.get('status') != 'ok' or action not in {'inspect', 'observe_condition', 'predict_reaction_yield', 'submit'}:
        return saved
    data = response.get('result')
    if not isinstance(data, dict):
        raise ValueError('Successful condition action requires a public view')
    current = _view(data if action == 'inspect' else data.get('view'))
    identity = _identity(current)
    if saved['identity_sha256'] is not None and identity != saved['identity_sha256']:
        raise ValueError('Condition study inputs or predictions changed')
    if saved['view'] is not None:
        _advance(saved['view'], current)
    return _copy({**saved, 'view': current, 'identity_sha256': identity,
                  'closed': closed or current['terminated'] or current['truncated']
                  or current['submission']['status'] != 'not_submitted'})


def _eligible(view):
    observed = {row['candidate_id'] for row in view['observations']}
    unavailable = observed | set(view['unavailable_candidate_ids'])
    return (view['domain_status'] == 'registered_measured_study'
            and not view['terminated'] and not view['truncated']
            and view['submission']['status'] == 'not_submitted'
            and view['resources']['new_observations_used'] >= 2
            and len(observed) - view['resources']['initial_observations'] >= 2
            and all(view['resources'][key] is None or view['resources'][key] > 0
                    for key in ('remaining_observations', 'remaining_actions', 'remaining_seconds'))
            and any(row['candidate_id'] not in unavailable for row in view['candidates']))


def build_context(state, resources):
    saved = _state(state)
    available = RuntimeResources.model_validate(_copy(resources)).model_dump(mode='json')
    if saved['closed'] or saved['view'] is None or not _eligible(saved['view']):
        return None
    if any(available[key] is not None and available[key] <= 0 for key in RESOURCE_KEYS):
        return None
    return _copy({'schema_version': 'srg-condition-context-v1',
                  'trigger': 'feedback_after_two_queries', 'view': saved['view'],
                  'resources': available})


def _context(value):
    context = _copy(value)
    if (not isinstance(context, dict) or set(context) != {'schema_version', 'trigger', 'view', 'resources'}
            or context['schema_version'] != 'srg-condition-context-v1'
            or context['trigger'] != 'feedback_after_two_queries'):
        raise ValueError('Invalid condition advice context')
    current = _view(context['view'])
    resources = RuntimeResources.model_validate(context['resources']).model_dump(mode='json')
    if not _eligible(current) or any(resources[key] is not None and resources[key] <= 0 for key in RESOURCE_KEYS):
        raise ValueError('Condition advice context is no longer eligible')
    return {**context, 'view': current, 'resources': resources}


def context_fingerprint(context):
    return hashlib.sha256(_encoded(_context(context))).hexdigest()


def _unique_pairs(pairs):
    if len({key for key, _ in pairs}) != len(pairs):
        raise ValueError('Duplicate advice JSON key')
    return dict(pairs)


def _reject_constant(_):
    raise ValueError('Nonfinite advice JSON number')


def parse_plan(text, context):
    """Validate model choices against exact observed identities and context."""
    if not isinstance(text, str) or len(text.encode()) > MAX_BYTES:
        raise ValueError('Advice must be bounded JSON text')
    try:
        raw = json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    except (ValueError, RecursionError) as error:
        raise ValueError('Advice must be one strict JSON object') from error
    checked = ConditionPlan.model_validate(raw).model_dump(mode='json')
    current = _context(context)
    if checked['context_sha256'] != context_fingerprint(current):
        raise ValueError('Advice context hash differs')
    view = current['view']
    known = {row['candidate_id'] for row in view['candidates']}
    observed = {row['candidate_id'] for row in view['observations']}
    unavailable = observed | set(view['unavailable_candidate_ids'])
    if checked['decision'] == 'observe' and checked['next_candidate_id'] not in known - unavailable:
        raise ValueError('Advice must select a known unobserved candidate')
    evidence = {row['source_record_id'] for row in view['observations']}
    predictions = {row['prediction_id'] for row in view['predictions']}
    if (set(checked['cited_observation_ids']) - evidence
            or set(checked['cited_prediction_ids']) - predictions):
        raise ValueError('Advice cites unavailable evidence')
    return checked


def hydrate_plan(plan, context):
    """Attach exact host conditions/evidence; never trust model-generated values."""
    checked = parse_plan(_encoded(plan).decode(), context)
    view = _context(context)['view']
    candidates = {row['candidate_id']: row for row in view['candidates']}
    observed = {row['source_record_id']: row for row in view['observations']}
    predictions = {row['prediction_id']: row for row in view['predictions']}
    selected = checked['next_candidate_id']
    return _copy({**checked,
                  'selected_conditions': candidates[selected]['conditions'] if selected is not None else None,
                  'supporting_observations': [observed[key] for key in checked['cited_observation_ids']],
                  'cited_predictions': [predictions[key] for key in checked['cited_prediction_ids']]})
