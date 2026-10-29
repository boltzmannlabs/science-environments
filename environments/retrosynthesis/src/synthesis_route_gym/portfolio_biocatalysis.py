"""Route-bound curated biocatalysis retrieval without inferred enzyme activity.

Inputs are host-supplied public records, not agent-authored evidence. Exact
identity checks cover encoded participants only, never an executable process.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

from .evidence_contracts import SourceRecord
from .schemas import Identifier, ReactionStep, Record, Smiles, Task

Text = Annotated[str, Field(strict=True, min_length=1, max_length=2000)]
Participants = Annotated[tuple[Smiles, ...], Field(min_length=1, max_length=100)]


class BioSourceRecord(Record):
    """Frozen public source claim. Quantitative activity/yield is unsupported."""

    record_id: Identifier
    reactants: Participants
    products: Participants
    enzyme_name: Text
    enzyme_class: Annotated[str, Field(pattern=r'^\d+\.\d+\.\d+\.\d+$')] | None = None
    cofactors: Annotated[tuple[Smiles, ...], Field(max_length=100)] = ()
    conditions: Annotated[tuple[Text, ...], Field(max_length=50)] = ()
    source_url: Text
    source_locator: Text
    evidence_kind: Literal['curated_database', 'literature_report']
    notes: Annotated[str, Field(strict=True, max_length=4000)] = ''
    enzyme_availability: Literal['unknown', 'available', 'unavailable'] = 'unknown'
    enzyme_availability_source: Text | None = None
    enzyme_availability_locator: Text | None = None

    @field_validator('enzyme_name', 'source_locator', 'enzyme_availability_locator')
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError('Source text must not be blank')
        return value

    @field_validator('source_url', 'enzyme_availability_source')
    @classmethod
    def source_http(cls, value):
        return SourceRecord.http_source(value) if value is not None else None

    @field_validator('conditions')
    @classmethod
    def nonblank_conditions(cls, values):
        if any(not value.strip() for value in values):
            raise ValueError('Source conditions must not be blank')
        return values

    @model_validator(mode='after')
    def availability_provenance(self):
        sourced = bool(self.enzyme_availability_source and self.enzyme_availability_locator)
        any_source = bool(self.enzyme_availability_source or self.enzyme_availability_locator)
        if ((self.enzyme_availability != 'unknown' and not sourced)
                or (self.enzyme_availability == 'unknown' and any_source)):
            raise ValueError('Known enzyme availability needs a complete sourced declaration')
        return self


def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _components(values):
    return sorted(component for value in values for component in value.split('.'))


def _record(value):
    raw = value.model_dump(mode='json') if isinstance(value, BioSourceRecord) else value
    return BioSourceRecord.model_validate(raw)


def _identity_record(record):
    raw = record.model_dump(mode='json')
    return {**raw, **{key: _components(raw[key]) for key in ('reactants', 'products', 'cofactors')}}


def bio_record_digest(record):
    """Canonical source identity, preserving participant multiplicity."""
    return _digest(_identity_record(_record(record)))


def _conditions(source, query):
    if not source:
        return 'unknown'
    if not query:
        return 'query_conditions_unknown'
    return ('same_declared_conditions' if Counter(source) == Counter(query)
            else 'different_declared_conditions')


def _match(source, reactants, products, generator):
    source_reactants = Counter(_components(source.reactants))
    source_products = Counter(_components(source.products))
    same_reactants = Counter(reactants) == source_reactants
    same_products = Counter(products) == source_products
    has_exact_product = bool(Counter(products) & source_products)
    subset = not (Counter(products) - source_products)
    query_fps = [generator.GetFingerprint(Chem.MolFromSmiles(p)) for p in products]
    source_fps = [generator.GetFingerprint(Chem.MolFromSmiles(p)) for p in source_products]
    similarity = max(DataStructs.TanimotoSimilarity(q, p) for q in query_fps for p in source_fps)
    if same_reactants and same_products:
        kind = 'exact_reaction'
    elif same_reactants and subset:
        kind = 'exact_substrates_product_projection'
    elif has_exact_product:
        kind = 'product_only'
    else:
        kind = 'product_similarity_analogue'
    return kind, same_reactants, same_products, similarity, source_products


def _candidate(source, task, step, reactants, products, generator):
    kind, same_reactants, same_products, similarity, source_products = _match(
        source, reactants, products, generator)
    stock = {component for item in task.inventory if item.available_mmol != 0
             for component in item.smiles.split('.')}
    source_reactants = _components(source.reactants)
    cofactors = _components(source.cofactors)
    query_materials = Counter(_components([m.smiles for m in step.reactants + step.reagents]))
    cofactors_declared = not (Counter(cofactors) - query_materials)
    missing_reactants = sorted(set(source_reactants) - stock)
    missing_cofactors = sorted(set(cofactors) - stock)
    return {
        **source.model_dump(mode='json'), 'record_sha256': bio_record_digest(source),
        'match_kind': kind, 'reactant_multiset_match': same_reactants,
        'complete_product_multiset_match': same_products,
        'supports_complete_query_reaction': kind == 'exact_reaction' and cofactors_declared,
        'product_similarity': similarity,
        'product_similarity_scope': 'maximum_pairwise_component_fingerprint_similarity_not_activity',
        'unrepresented_source_products': sorted((source_products - Counter(products)).elements()),
        'cofactors_declared_in_query': cofactors_declared,
        'cofactor_requirements_status': 'source_recorded' if cofactors else 'not_reported',
        'missing_reactants': missing_reactants, 'missing_cofactors': missing_cofactors,
        'inventory_complete': not missing_reactants and not missing_cofactors,
        'inventory_scope': 'identity_membership_only_not_quantity_or_suitability',
        'enzyme_availability_scope': 'host_supplied_sourced_declaration_not_verified_stock',
        'conditions_status': _conditions(source.conditions, step.conditions),
        'experimental_yield': None, 'measured_activity': None,
        'claims_activity': False, 'claims_experimental_validation': False,
        'evidence_authority': 'public_source_claim',
    }


def _validated_inputs(task, step, records, threshold):
    if type(threshold) not in {int, float} or not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError('Analogue threshold must be finite and between zero and one')
    if not isinstance(records, (list, tuple)) or len(records) > 100:
        raise ValueError('Expected at most 100 already-accessible source records')
    raw = [v.model_dump(mode='json') if isinstance(v, BioSourceRecord) else v for v in records]
    try:
        encoded = json.dumps(raw, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError('Biocatalytic catalog must contain bounded JSON records') from error
    if len(encoded) > 1_000_000:
        raise ValueError('Biocatalytic catalog exceeds bounded representation')
    sources = tuple(_record(row) for row in raw)
    if len({row.record_id for row in sources}) != len(sources):
        raise ValueError('Biocatalytic record IDs must be unique')
    task = Task.model_validate(task.model_dump(mode='json') if isinstance(task, Task) else task)
    step = ReactionStep.model_validate(step.model_dump(mode='json') if isinstance(step, ReactionStep) else step)
    return task, step, sources


def build_biocatalysis_report(task, step, *, records=(), analogue_threshold=0.5):
    """Review a stored step against public records already retrieved by the host.

    This pure function has no fetch, file, model, observation, or mutation side
    effects. The calling environment enforces source access and action budgets.
    """
    task, step, sources = _validated_inputs(task, step, records, analogue_threshold)
    reactants = _components([material.smiles for material in step.reactants])
    products = _components([step.product])
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=True)
    candidates = [_candidate(row, task, step, reactants, products, generator) for row in sources]
    selected = [row for row in candidates if row['match_kind'] != 'product_similarity_analogue'
                or row['product_similarity'] >= analogue_threshold]
    order = {'exact_reaction': 0, 'exact_substrates_product_projection': 1,
             'product_only': 2, 'product_similarity_analogue': 3}
    selected = sorted(selected, key=lambda row: (order[row['match_kind']], not row['inventory_complete'],
                                                -row['product_similarity'], row['record_id']))
    return {
        'schema_version': 'srg-biocatalysis-report-v1', 'application': 'biocatalytic_synthesis',
        'task_id': task.task_id, 'step_id': step.step_id,
        'step_sha256': _digest(step.model_dump(mode='json')),
        'catalog_sha256': _digest(sorted(bio_record_digest(row) for row in sources)),
        'query': {'reactants': reactants, 'products': products},
        'analogue_threshold': analogue_threshold, 'candidates': selected,
        'source_record_count': len(sources), 'scientific_validation': 'unvalidated',
        'claims_experimental_validation': False,
        'limitations': [
            'Exact matches establish encoded reaction identity only, not a feasible process.',
            'A projected major product omits source coproducts and is not a complete exact reaction.',
            'Product-only or fingerprint analogue matches do not establish substrate activity.',
            'Unknown enzyme preparation, quantities, cofactors or conditions remain unresolved.',
            'Source and stock declarations require independent verification; no activity or yield is inferred.',
        ],
    }
