"""Pure route-step joins for finite condition replay; no observation is purchased here.

The host supplies already admitted observations. Public views never derive a
hidden optimum or reveal an unqueried record. Recipe matches describe recorded
inputs; they do not transfer a measured candidate endpoint onto an agent route.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from types import MappingProxyType
from typing import Annotated, Literal, Mapping

from pydantic import Field, field_serializer, field_validator, model_validator
from rdkit import rdBase

from .chemistry import canonical_smiles
from .evidence_contracts import SourceRecord
from .portfolio_conditions import ConditionRecord, FiniteConditionStudy
from .schemas import ReactionStep
from .tool_contracts import Contract, Digest, ID, ObservationResult, SMILES, Text

MAX_PUBLIC_BYTES = 256000
OUTCOME_FIELDS = frozenset({'yield', 'yield_percent', 'outcome', 'outcomes', 'label', 'labels',
    'score', 'best', 'optimum', 'value', 'dataset_optimum_yield_percent', 'simple_regret_percent'})
RECIPE_FIELDS = ('reactants', 'reagents', 'product', 'product_amount_mmol', 'conditions',
                 'condition_inputs', 'required_equipment', 'operations', 'conditions_complete')


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ValueError('Expected bounded nonblank text')
    return value


def _bounded(value):
    if len(json.dumps(value, allow_nan=False).encode()) > MAX_PUBLIC_BYTES:
        raise ValueError('Condition application public context exceeds bounded size')
    return value


def _chemical_factor(value):
    # Operating parameters can be explicit text, not molecular identities.
    with rdBase.BlockLogs():
        try:
            return canonical_smiles(value)
        except ValueError:
            return None


def _same_factor(expected, supplied):
    if expected == supplied:
        return True
    chemical = _chemical_factor(expected)
    return chemical is not None and chemical == _chemical_factor(supplied)


def _validate_factor_recipe(factors, recipe):
    inputs = recipe.condition_inputs or {}
    materials = {use.smiles for use in recipe.reactants + recipe.reagents}
    for key, value in factors.items():
        tags = [condition.split('=', 1)[1] for condition in recipe.conditions
                if '=' in condition and condition.split('=', 1)[0].strip() == key]
        if len(tags) > 1 or (tags and not _same_factor(value, tags[0])):
            raise ValueError('Condition factor has contradictory or ambiguous recipe tags')
        if key in inputs:
            if not _same_factor(value, inputs[key]):
                raise ValueError('Condition factor contradicts explicit recipe inputs')
        elif not tags:
            raise ValueError('Condition factor requires explicit recipe input or name=value tag')
        chemical = _chemical_factor(value)
        if chemical is not None and chemical not in materials:
            raise ValueError('Condition factor chemical is absent from declared recipe materials')


class RouteConditionCandidate(Contract):
    candidate_id: ID
    conditions: Mapping[Text, Text]
    recipe: ReactionStep

    @field_validator('conditions')
    @classmethod
    def inputs_only(cls, values):
        if not 1 <= len(values) <= 100:
            raise ValueError('Expected bounded condition factors')
        for key, value in values.items():
            _text(key); _text(value)
            if key.strip().casefold() in OUTCOME_FIELDS:
                raise ValueError('Outcomes cannot be condition factors')
        return MappingProxyType(dict(values))

    @field_serializer('conditions')
    def serialize_conditions(self, values):
        return dict(values)

    @model_validator(mode='after')
    def recipe_identity(self):
        if self.candidate_id != self.recipe.step_id:
            raise ValueError('Candidate and recipe IDs differ')
        _bounded(self.recipe.model_dump(mode='json'))
        _validate_factor_recipe(self.conditions, self.recipe)
        return self


class RouteConditionBinding(Contract):
    schema_version: Literal['srg-route-condition-binding-v1']
    study_id: ID
    dataset_sha256: Digest
    source_url: Text
    source_locator: Text
    reactants: Annotated[tuple[SMILES, ...], Field(min_length=1, max_length=100)]
    product: SMILES
    candidates: Annotated[tuple[RouteConditionCandidate, ...], Field(min_length=1, max_length=100)]

    @field_validator('source_url')
    @classmethod
    def source_http(cls, value):
        return SourceRecord.http_source(value)

    _locator = field_validator('source_locator')(_text)

    @model_validator(mode='after')
    def chemical_identity(self):
        ids = [row.candidate_id for row in self.candidates]
        if len(set(ids)) != len(ids):
            raise ValueError('Duplicate condition candidate IDs')
        for row in self.candidates:
            if (Counter(use.smiles for use in row.recipe.reactants) != Counter(self.reactants)
                    or row.recipe.product != self.product):
                raise ValueError('Candidate recipe reaction differs from study binding')
        _bounded(self.model_dump(mode='json'))
        return self


def _study_public(study):
    """Validate input metadata without inspecting unqueried numerical outcomes."""
    if not isinstance(study, FiniteConditionStudy):
        raise ValueError('Expected host finite condition study')
    if ((study.budget is not None and (type(study.budget) is not int or not 1 <= study.budget <= 100000))
            or not isinstance(study._records, (tuple, list)) or not 1 <= len(study._records) <= 100):
        raise ValueError('Invalid bounded condition study')
    _text(study.source_locator)
    SourceRecord.http_source(_text(study.source_url))
    canonical_smiles(study.substrate)
    records = []
    for row in study._records:
        if not isinstance(row, ConditionRecord) or not isinstance(row.conditions, (tuple, list)):
            raise ValueError('Invalid condition record')
        pairs = list(row.conditions)
        if (not 1 <= len(pairs) <= 100 or any(not isinstance(pair, (tuple, list)) or len(pair) != 2 for pair in pairs)):
            raise ValueError('Invalid condition factors')
        _text(row.candidate_id)
        for key, value in pairs:
            _text(key); _text(value)
            if key.strip().casefold() in OUTCOME_FIELDS:
                raise ValueError('Outcome cannot be a condition input')
        values = dict(pairs)
        if len(values) != len(pairs):
            raise ValueError('Duplicate condition factors')
        records.append({'candidate_id': row.candidate_id, 'conditions': values})
    ids = [row['candidate_id'] for row in records]
    settings = [tuple(sorted(row['conditions'].items())) for row in records]
    if len(set(ids)) != len(ids) or len(set(settings)) != len(settings):
        raise ValueError('Duplicate study candidates or settings')
    if any(set(row['conditions']) != set(records[0]['conditions']) for row in records):
        raise ValueError('Condition study factors differ')
    if (not isinstance(study.observed_ids, (tuple, list))
            or any(not isinstance(key, str) for key in study.observed_ids) or len(set(study.observed_ids)) != len(study.observed_ids)
            or not set(study.observed_ids) <= set(ids)
            or (study.budget is not None and len(study.observed_ids) > study.budget)):
        raise ValueError('Invalid initial observation identities')
    return records


def validate_binding(study, binding):
    """Return only public chemistry/source metadata; private outcomes stay private."""
    public = _study_public(study)
    bound = RouteConditionBinding.model_validate(binding)
    if (bound.dataset_sha256 != study.dataset_sha256 or bound.source_url != study.source_url
            or bound.source_locator != study.source_locator or canonical_smiles(study.substrate) not in bound.reactants):
        raise ValueError('Condition source or substrate identity differs from host study')
    candidates = {row.candidate_id: dict(row.conditions) for row in bound.candidates}
    if candidates != {row['candidate_id']: row['conditions'] for row in public}:
        raise ValueError('Condition candidates differ from host study')
    payload = {**bound.model_dump(mode='json'), 'study_observation_allowance': study.budget}
    return {**payload, 'binding_sha256': _hash(payload)}


def condition_recipe_digest(step):
    """Fingerprint operating inputs, excluding IDs, source claims and model scores."""
    step = ReactionStep.model_validate(step).model_dump(mode='json')
    recipe = {key: step[key] for key in RECIPE_FIELDS}
    recipe = {**recipe, **{key: sorted(recipe[key], key=lambda row: (row['smiles'], row['amount_mmol'] or 0))
                          for key in ('reactants', 'reagents')}}
    return _hash(_bounded(recipe))


def validate_step_binding(step, study, binding):
    step = ReactionStep.model_validate(step)
    public = validate_binding(study, binding)
    if (Counter(use.smiles for use in step.reactants) != Counter(public['reactants'])
            or step.product != public['product']):
        raise ValueError('Stored step reaction differs from condition study')
    return public


def _observations(study, public, observations, recipe_digest):
    if not isinstance(observations, (list, tuple)) or len(observations) > 100:
        raise ValueError('Expected bounded host observation sequence')
    if study.budget is not None and len(observations) > study.budget:
        raise ValueError('Observed candidate count exceeds declared study allowance')
    records = {row.candidate_id: row for row in study._records}
    candidates = {row['candidate_id']: row for row in public['candidates']}
    result = []
    for raw in observations:
        observed = ObservationResult.model_validate(raw)
        key = observed.candidate_id
        if key not in records:
            raise ValueError('Observation names unknown study candidate')
        expected_id = f'study:{study.dataset_sha256}:{_hash(key)[:20]}'
        if (observed.dataset_sha256 != study.dataset_sha256 or observed.source_record_id != expected_id
                or observed.conditions != dict(records[key].conditions)
                or type(records[key].yield_percent) not in (int, float)
                or observed.yield_percent != records[key].yield_percent):
            raise ValueError('Observation does not match source-bound candidate')
        candidate = candidates[key]
        result.append({**observed.model_dump(mode='json'), 'recipe': candidate['recipe'],
                       'recipe_matches_current_step': condition_recipe_digest(candidate['recipe']) == recipe_digest})
    if len({row['candidate_id'] for row in result}) != len(result):
        raise ValueError('Duplicate observations cannot create extra measurements')
    return result


def condition_catalog(step, study, binding, *, observations=()):
    public = validate_step_binding(step, study, binding)
    digest = condition_recipe_digest(step)
    observed = _observations(study, public, observations, digest)
    candidates = [{**row, 'recipe_sha256': condition_recipe_digest(row['recipe']),
                   'recipe_matches_current_step': condition_recipe_digest(row['recipe']) == digest}
                  for row in public['candidates']]
    return _bounded({**public, 'schema_version': 'srg-route-condition-catalog-v1',
        'current_recipe_sha256': digest, 'candidates': candidates, 'observations': observed,
        'observation_count': len(observed), 'claims_experimental_validation': False,
        'evidence_scope': 'Host-registered retrospective condition alternatives; no new experiment.',
        'limitations': ['Only supplied admitted observations are displayed; other outcomes remain private.',
            'Recipe identity is not proof of procedure completeness, scale transfer or reaction feasibility.',
            'Observation allowance is declared study scope; host separately accounts for failed or pending requests.']})


def build_condition_report(step, study, binding, *, observations=(), selected_candidate_id=None):
    catalog = condition_catalog(step, study, binding, observations=observations)
    indexed = {row['candidate_id']: row for row in catalog['observations']}
    if selected_candidate_id is not None and (not isinstance(selected_candidate_id, str) or selected_candidate_id not in indexed):
        raise ValueError('Selected condition must be an already observed candidate')
    best = min(indexed, key=lambda key: (-indexed[key]['yield_percent'], key)) if indexed else None
    return _bounded({**catalog, 'schema_version': 'srg-condition-application-report-v1',
        'selected_candidate_id': selected_candidate_id, 'selected_observation': indexed.get(selected_candidate_id),
        'best_observed_candidate_id': best, 'route_step_yield_percent': None,
        'evidence_status': 'measured_dataset_replay' if indexed else 'registered_unobserved_alternatives',
        'limitations': [*catalog['limitations'],
            'Candidate measurements are not grafted onto the current route step, even when declared inputs match.',
            'Best observed candidate is computed only over revealed observations, never the hidden study optimum.']})
