"""Strict host-only configuration for local scientific tools and replay inputs.

No imported code, providers, filesystem references or remote fetch instructions
are accepted inside this file. Inline replay outcomes remain host-private.
"""
from pathlib import Path
import json
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from .evidence_contracts import Digest, HostAttestation, SourceRecord
from .evidence_corpus import FrozenEvidenceCorpus
from .portfolio_conditions import ConditionRecord, FiniteConditionStudy
from .schemas import Identifier, Record, Smiles
from .scientific_execution import ScientificLimits
from .application_contracts import ApplicationConfig

MAX_CONFIG_BYTES = 20_000_000
Text = Annotated[str, Field(strict=True, min_length=1, max_length=2000)]
Count = Annotated[int, Field(strict=True, ge=0, le=100000)]
PositiveCount = Annotated[int, Field(strict=True, ge=1, le=100000)]
Percent = Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
OUTCOME_FIELDS = frozenset({'yield', 'yield_percent', 'outcome', 'outcomes', 'label', 'labels',
    'score', 'best', 'optimum', 'dataset_optimum_yield_percent', 'simple_regret_percent'})


def _nonblank(value):
    if not value.strip():
        raise ValueError('Expected nonblank text')
    return value


class ReplayRow(Record):
    candidate_id: Identifier
    conditions: dict[Text, Text]
    yield_percent: Percent

    @field_validator('conditions')
    @classmethod
    def condition_inputs_only(cls, values):
        if not 1 <= len(values) <= 100:
            raise ValueError('Expected 1..100 condition factors')
        for key, value in values.items():
            _nonblank(key)
            _nonblank(value)
            if key.strip().casefold() in OUTCOME_FIELDS:
                raise ValueError('Outcome labels cannot be condition inputs')
        return values


class ConditionReplay(Record):
    data_role: Literal['smoke', 'development']
    rows: Annotated[tuple[ReplayRow, ...], Field(min_length=1, max_length=100000)]
    substrate: Smiles
    source_url: Text
    source_locator: Text
    dataset_sha256: Digest
    budget: PositiveCount

    _locator = field_validator('source_locator')(_nonblank)

    @field_validator('source_url')
    @classmethod
    def source_http(cls, value):
        return SourceRecord.http_source(value)

    @model_validator(mode='after')
    def independent_candidates(self):
        if len({row.candidate_id for row in self.rows}) != len(self.rows):
            raise ValueError('Replay candidate IDs must be unique')
        settings = [tuple(sorted(row.conditions.items())) for row in self.rows]
        if len(set(settings)) != len(settings):
            raise ValueError('Repeated settings require explicit upstream replicate aggregation')
        if any(set(row.conditions) != set(self.rows[0].conditions) for row in self.rows):
            raise ValueError('Replay candidates must declare the same condition factors')
        return self

    def study(self):
        rows = tuple(ConditionRecord(row.candidate_id, tuple(sorted(row.conditions.items())), row.yield_percent)
                     for row in self.rows)
        return FiniteConditionStudy(rows, (), self.budget, self.source_url,
                                    self.source_locator, self.dataset_sha256, self.substrate)


class BiocatalyticRecord(Record):
    record_id: Identifier
    enzyme_name: Text
    source_url: Text
    source_locator: Text
    reactants: Annotated[tuple[Smiles, ...], Field(min_length=1, max_length=100)]
    products: Annotated[tuple[Smiles, ...], Field(min_length=1, max_length=100)]
    cofactors: Annotated[tuple[Smiles, ...], Field(max_length=100)] = ()
    evidence_kind: Literal['curated_database', 'literature_report']

    _text = field_validator('enzyme_name', 'source_locator')(_nonblank)

    @field_validator('source_url')
    @classmethod
    def source_http(cls, value):
        return SourceRecord.http_source(value)


class AccessLimits(Record):
    retrieval_calls: Count = 0
    observation_calls: Count = 0


class ProcessBasis(Record):
    purity_basis: Text | None = None
    exclusions: Annotated[tuple[Text, ...], Field(max_length=100)] | None = None

    @field_validator('purity_basis')
    @classmethod
    def known_purity(cls, value):
        return _nonblank(value) if value is not None else None

    @field_validator('exclusions')
    @classmethod
    def nonblank_exclusions(cls, values):
        if values is not None:
            for value in values:
                _nonblank(value)
        return values


class ScienceConfig(Record):
    schema_version: Literal['srg-science-config-v1']
    source_access_mode: Literal['closed_information', 'evidence_retrieval'] = 'closed_information'
    source_records: Annotated[tuple[SourceRecord, ...], Field(max_length=100000)] = ()
    host_attestations: Annotated[tuple[HostAttestation, ...], Field(max_length=100000)] = ()
    scientific_limits: AccessLimits = AccessLimits()
    condition_replay: ConditionReplay | None = None
    biocatalytic_records: Annotated[tuple[BiocatalyticRecord, ...], Field(max_length=100000)] | None = None
    process_basis: ProcessBasis | None = None
    application_config: ApplicationConfig | None = None

    @model_validator(mode='after')
    def access_allowance(self):
        maximum = self.condition_replay.budget if self.condition_replay else 0
        if self.scientific_limits.observation_calls > maximum:
            raise ValueError('Observation allowance exceeds configured study budget')
        records = self.biocatalytic_records or ()
        if len({row.record_id for row in records}) != len(records):
            raise ValueError('Biocatalytic record IDs must be unique')
        return self


def _unique_pairs(pairs):
    keys = tuple(key for key, value in pairs)
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate scientific configuration field')
    return dict(pairs)


def _reject_constant(value):
    raise ValueError('Nonfinite scientific configuration number')


def load_science_config(path):
    """Return host objects for SynthesisRouteEnv; never return this to the model."""
    with Path(path).expanduser().open('rb') as stream:
        raw = stream.read(MAX_CONFIG_BYTES + 1)
    if len(raw) > MAX_CONFIG_BYTES:
        raise ValueError('Science configuration exceeds 20 MB')
    try:
        payload = json.loads(raw, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('Malformed scientific configuration JSON') from exc
    config = ScienceConfig.model_validate(payload)
    corpus = FrozenEvidenceCorpus(config.source_records, mode=config.source_access_mode,
                                  attestations=config.host_attestations)
    return {'evidence_corpus': corpus,
            'application_config': config.application_config.model_dump(mode='json') if config.application_config else None,
            'scientific_limits': ScientificLimits(**config.scientific_limits.model_dump()),
            'condition_study': config.condition_replay.study() if config.condition_replay else None,
            'biocatalytic_records': tuple(row.model_dump(mode='json') for row in config.biocatalytic_records)
                                    if config.biocatalytic_records is not None else None,
            'source_access_mode': config.source_access_mode,
            'process_basis': config.process_basis.model_dump(mode='json') if config.process_basis else None}
