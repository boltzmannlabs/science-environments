"""Strict host-only joins of public condition inputs, private replay and predictions."""
import hashlib
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from .evidence_contracts import SourceRecord
from .condition_identity import condition_input_digest
from .portfolio_conditions import ConditionRecord, FiniteConditionStudy
from .science_config import OUTCOME_FIELDS
from .tool_contracts import Contract, Digest, ID, Percent, ReactionYieldCandidate, SMILES, Text

MAX_BYTES = 2_000_000
Count = Annotated[int, Field(strict=True, ge=1, le=100)]


class StudyCandidate(Contract):
    candidate_id: ID
    conditions: dict[Text, Text]
    recipe: ReactionYieldCandidate

    @model_validator(mode='after')
    def inputs_only(self):
        if self.recipe.id != self.candidate_id or not 1 <= len(self.conditions) <= 100:
            raise ValueError('Invalid candidate binding')
        if any(key.strip().casefold() in OUTCOME_FIELDS or not key.strip() or not value.strip()
               for key, value in self.conditions.items()):
            raise ValueError('Condition factors must be nonempty inputs')
        return self


class ConditionStudySpec(Contract):
    schema_version: Literal['srg-condition-study-v1']
    data_role: Literal['smoke', 'development']
    study_id: ID
    substrate: SMILES
    target: SMILES
    source_url: Text
    source_locator: Text
    dataset_sha256: Digest
    observation_budget: Count
    initial_ids: Annotated[tuple[ID, ...], Field(max_length=100)]
    candidates: Annotated[tuple[StudyCandidate, ...], Field(min_length=1, max_length=100)]
    outcomes_sha256: Digest
    group_id: ID | None = None
    product_group_id: ID | None = None
    measurement: Literal['source_reported_yield_percent'] = 'source_reported_yield_percent'
    limitations: Annotated[tuple[Text, ...], Field(max_length=30)] = ()

    @field_validator('source_url')
    @classmethod
    def public_source(cls, value):
        return SourceRecord.http_source(value)

    @model_validator(mode='after')
    def identities(self):
        ids = {row.candidate_id for row in self.candidates}
        settings = {tuple(sorted(row.conditions.items())) for row in self.candidates}
        if (len(ids) != len(self.candidates) or len(settings) != len(self.candidates)
                or len(set(self.initial_ids)) != len(self.initial_ids)
                or not set(self.initial_ids) <= ids
                or not len(self.initial_ids) <= self.observation_budget <= len(ids)):
            raise ValueError('Invalid study identities or allowance')
        if any(row.recipe.product != self.target or self.substrate not in row.recipe.reactants
               or set(row.conditions) != set(self.candidates[0].conditions) for row in self.candidates):
            raise ValueError('Candidates do not belong to the same declared study')
        return self


class ConditionOutcomes(Contract):
    schema_version: Literal['srg-condition-outcomes-v1']
    study_id: ID
    dataset_sha256: Digest
    candidate_inputs_sha256: Digest
    outcomes: dict[ID, Percent]


class ConditionPrediction(Contract):
    candidate_id: ID
    prediction_id: ID
    status: Literal['scored', 'abstained']
    value: Percent | None
    unit: Literal['percent']
    domain: Text
    uncertainty: Text
    model_version: Text

    @model_validator(mode='after')
    def value_status(self):
        if (self.status == 'scored') != (self.value is not None):
            raise ValueError('Prediction status differs from value')
        return self


class PredictionTable(Contract):
    schema_version: Literal['srg-condition-predictions-v1']
    study_id: ID
    candidate_inputs_sha256: Digest
    model_metadata: dict
    predictions: Annotated[tuple[ConditionPrediction, ...], Field(max_length=100)]


def _pairs(values):
    if len(dict(values)) != len(values):
        raise ValueError('Duplicate JSON field')
    return dict(values)


def _constant(_):
    raise ValueError('Nonfinite JSON value')


def _read(path):
    with Path(path).open('rb') as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Condition input exceeds 2 MB')
    return raw


def _decode(raw):
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)


def load_condition_inputs(study_path, outcomes_path, predictions_path=None):
    """Return host objects. Never expose this return value as a model tool result."""
    try:
        public_payload = _decode(_read(study_path))
        public = ConditionStudySpec.model_validate(public_payload)
    except (ValueError, TypeError, RecursionError):
        raise ValueError('Invalid public condition study') from None
    raw = _read(outcomes_path)
    if hashlib.sha256(raw).hexdigest() != public.outcomes_sha256:
        raise ValueError('Condition outcome commitment differs')
    ids = {row.candidate_id for row in public.candidates}
    try:
        private = ConditionOutcomes.model_validate(_decode(raw))
        if (private.study_id != public.study_id or private.dataset_sha256 != public.dataset_sha256
                or private.candidate_inputs_sha256 != condition_input_digest(public_payload)
                or set(private.outcomes) != ids):
            raise ValueError('Private study identity differs')
    except (ValueError, TypeError, RecursionError):
        raise ValueError('Invalid host condition outcomes') from None
    predictions = _load_predictions(predictions_path, public.study_id, ids,
                                    condition_input_digest(public_payload))
    records = tuple(ConditionRecord(row.candidate_id, tuple(sorted(row.conditions.items())),
                                    private.outcomes[row.candidate_id]) for row in public.candidates)
    study = FiniteConditionStudy(records, tuple(public.initial_ids), public.observation_budget,
                                 public.source_url, public.source_locator, public.dataset_sha256,
                                 public.substrate)
    return {'study': study, 'study_id': public.study_id, 'target': public.target,
            'predictions': predictions, 'public_metadata': public.model_dump(mode='json')}


def _load_predictions(path, study_id, candidate_ids, input_digest):
    if path is None:
        return ()
    try:
        table = PredictionTable.model_validate(_decode(_read(path)))
        ids = [row.candidate_id for row in table.predictions]
        if (table.study_id != study_id or table.candidate_inputs_sha256 != input_digest
                or len(set(ids)) != len(ids)
                or set(ids) != candidate_ids
                or len({row.prediction_id for row in table.predictions}) != len(ids)):
            raise ValueError('Prediction identities differ')
    except (ValueError, TypeError, RecursionError):
        raise ValueError('Invalid host condition predictions') from None
    return tuple(row.model_dump(mode='json') for row in table.predictions)
