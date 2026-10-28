"""Route-bound impurity hypotheses and host-supplied assay annotations.

The caller must supply canonical recorded tools and host-owned annotations.
Neither a URL nor a digest establishes independent verification. Assay-level
identity metrics never establish concentration or general reaction feasibility.
"""
from __future__ import annotations

import hashlib
import json
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from .chemistry import reaction_identity
from .evidence_contracts import Digest, SourceRecord
from .schemas import Identifier, ReactionStep, Record, Smiles
from .tool_contracts import ImpurityRequest, ImpurityResult, ToolEnvelope

Text = Annotated[str, Field(strict=True, min_length=1, max_length=2000)]
MAX_BYTES = 1_000_000


def _text(value):
    if not value.strip() or any(ord(char) < 32 for char in value):
        raise ValueError('Expected nonblank text without control characters')
    return value


def _plain(value):
    if hasattr(value, 'model_dump'):
        value = value.model_dump(mode='json')
    try:
        encoded = json.dumps(value, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError('Expected finite JSON data') from error
    if len(encoded.encode()) > MAX_BYTES:
        raise ValueError('Impurity report input exceeds bounded size')
    return json.loads(encoded)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def impurity_recipe_digest(step: ReactionStep | dict) -> str:
    """Bind declared recipe, amounts and operation scope; not proposal identities."""
    record = ReactionStep.model_validate(_plain(step))
    def materials(rows):
        values = [row.model_dump(mode='json') for row in rows]
        return sorted(values, key=lambda row: (row['smiles'], row['amount_mmol'] is None, row['amount_mmol'] or 0))
    recipe = {'reactants': materials(record.reactants), 'reagents': materials(record.reagents),
              'product': record.product, 'product_amount_mmol': record.product_amount_mmol,
              'conditions': list(record.conditions),
              'condition_inputs': None if record.condition_inputs is None else dict(record.condition_inputs),
              'required_equipment': sorted(record.required_equipment), 'operations': list(record.operations),
              'conditions_complete': record.conditions_complete}
    return _digest(recipe)


class ImpurityQuantity(Record):
    """A stated measured quantity or assay limit; chromatogram area is excluded."""
    value: Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
    unit: Literal['mass_fraction', 'mass_percent', 'mol_fraction', 'mol_percent',
                  'mg_per_g', 'mg_per_L', 'mmol_per_L']
    basis: Text
    _basis = field_validator('basis')(_text)

    @model_validator(mode='after')
    def physical_fraction(self):
        ceiling = {'mass_fraction': 1, 'mol_fraction': 1, 'mass_percent': 100,
                   'mol_percent': 100, 'mg_per_g': 1000}.get(self.unit)
        if ceiling is not None and self.value > ceiling:
            raise ValueError('Measured fraction exceeds unit range')
        return self


class MeasuredImpurity(Record):
    smiles: Smiles
    concentration: ImpurityQuantity | None = None


class ImpurityAnnotation(Record):
    """Host configuration only: one reaction, declared recipe and assay scope."""
    annotation_id: Identifier
    reactants: Annotated[tuple[Smiles, ...], Field(min_length=1, max_length=100)]
    product: Smiles
    recipe_sha256: Digest
    source_url: Text
    source_locator: Text
    source_content_sha256: Digest
    assay_method: Text
    assay_scope: Text
    annotation_coverage: Literal['partial', 'complete_within_assay_scope'] = 'partial'
    detection_limit: ImpurityQuantity | None = None
    quantitation_limit: ImpurityQuantity | None = None
    reporting_limit: ImpurityQuantity | None = None
    impurities: Annotated[tuple[MeasuredImpurity, ...], Field(max_length=100)]

    _strings = field_validator('source_locator', 'assay_method', 'assay_scope')(_text)
    @field_validator('source_url')
    @classmethod
    def valid_url(cls, value):
        return SourceRecord.http_source(value)

    @model_validator(mode='after')
    def assay_consistency(self):
        identities = [row.smiles for row in self.impurities]
        if len(set(identities)) != len(identities) or self.product in identities:
            raise ValueError('Measured impurity identities must be unique and exclude the main product')
        detection, quantitation = self.detection_limit, self.quantitation_limit
        if detection and quantitation and _same_units(detection, quantitation) and detection.value > quantitation.value:
            raise ValueError('Detection limit exceeds quantitation limit')
        reporting = self.reporting_limit
        if quantitation and reporting and (not _same_units(quantitation, reporting)
                                            or quantitation.value > reporting.value):
            raise ValueError('Quantitation and reporting limits require matching units and ordered levels')
        for row in self.impurities:
            value = row.concentration
            if value is not None and (quantitation is None or not _same_units(value, quantitation)
                                      or value.value < quantitation.value):
                raise ValueError('Concentration requires a matching quantitation limit and a quantifiable value')
            if (value is not None and reporting is not None
                    and self.annotation_coverage == 'complete_within_assay_scope'
                    and (not _same_units(value, reporting) or value.value < reporting.value)):
                raise ValueError('Complete assay contains a concentration outside its reporting scope')
        return self


class ImpurityPredictionRecord(Record):
    action: Literal['predict_impurities']
    arguments: ImpurityRequest
    result: ToolEnvelope


def _same_units(first, second):
    return (first.unit, first.basis) == (second.unit, second.basis)


def _prediction(step, raw):
    if raw is None:
        return None, 'not_run', None
    record = ImpurityPredictionRecord.model_validate(_plain(raw))
    args, result = record.arguments, record.result
    if reaction_identity(args.reactants, args.product) != reaction_identity([r.smiles for r in step.reactants], step.product):
        raise ValueError('Prediction reaction differs from the stored step')
    if result.capability != 'predict_impurities' or result.evidence_kind != 'predicted_impurity_hypotheses':
        raise ValueError('Prediction capability or evidence authority differs')
    if result.status != 'ok':
        return None, result.status, record.model_dump(mode='json')
    binding = result.provenance.binding
    if binding is None or binding.authority != 'prediction':
        raise ValueError('Successful prediction requires its host prediction binding')
    payload = ImpurityResult.model_validate(result.data)
    values = list(dict.fromkeys(payload.predicted_smiles))
    if step.product in values or len(values) > args.top_k:
        raise ValueError('Prediction includes major product or exceeds requested bound')
    return values, 'ok', record.model_dump(mode='json')


def _metric_limitations(step, annotation):
    return [reason for condition, reason in (
        (annotation.annotation_coverage != 'complete_within_assay_scope', 'incomplete_annotation_coverage'),
        (annotation.reporting_limit is None, 'reporting_limit_unknown'),
        (not step.conditions_complete, 'route_recipe_incomplete')) if condition]


def _metrics(predictions, annotation, limitations):
    if predictions is None:
        return None
    known = {row.smiles for row in annotation.impurities}
    predicted = set(predictions)
    matched = len(known & predicted)
    known_recall = matched / len(known) if known else None
    complete = not limitations
    precision = matched / len(predicted) if complete and predicted else None
    recall = known_recall if complete else None
    f1 = (2 * precision * recall / (precision + recall) if precision + recall else 0.0
          ) if precision is not None and recall is not None else None
    return {'scope': 'supplied_assay_identity_annotations_above_reporting_limit' if complete
            else 'known_positive_annotations_only', 'true_positives': matched,
            'known_annotations': len(known), 'predicted_count': len(predicted),
            'known_annotation_recall': known_recall, 'precision': precision, 'recall': recall, 'f1': f1,
            'false_positives': len(predicted - known) if complete else None,
            'false_negatives': len(known - predicted) if complete else None,
            'unlabeled_predictions': None if complete else len(predicted - known)}


def build_impurity_report(step, *, prediction=None, annotations=()):
    """Assess a single stored step against individually matched host assays.

    No source files or outcome databases are opened. The host owns access to
    annotation records; never expose this function as agent-supplied truth.
    Incomplete annotations yield known-positive recall only. Even complete-scope
    scores are conditional on supplied assay annotations, not chemical truth.
    """
    record = ReactionStep.model_validate(_plain(step))
    recipe_hash = impurity_recipe_digest(record)
    predictions, status, trace = _prediction(record, prediction)
    if not isinstance(annotations, (tuple, list)) or len(annotations) > 100:
        raise ValueError('Expected at most 100 host annotations')
    checked = tuple(ImpurityAnnotation.model_validate(_plain(row)) for row in annotations)
    if len({row.annotation_id for row in checked}) != len(checked):
        raise ValueError('Host annotation IDs must be unique')
    matches, excluded = [], []
    identity = reaction_identity([r.smiles for r in record.reactants], record.product)
    for annotation in checked:
        reason = ('reaction_mismatch' if reaction_identity(annotation.reactants, annotation.product) != identity
                  else 'recipe_mismatch' if annotation.recipe_sha256 != recipe_hash else None)
        if reason:
            excluded = [*excluded, {'annotation_id': annotation.annotation_id, 'reason': reason}]
            continue
        limitations = _metric_limitations(record, annotation)
        matches = [*matches, {**annotation.model_dump(mode='json'),
            'evidence_status': 'host_supplied_measurement_claim', 'verification_status': 'not_independently_verified',
            'metric_limitations': limitations, 'metrics': _metrics(predictions, annotation, limitations)}]
    report = {'schema_version': 'srg-impurity-report-v1', 'application': 'impurity_analysis',
        'step_id': record.step_id, 'recipe_sha256': recipe_hash,
        'reaction': {'reactants': [r.smiles for r in record.reactants], 'product': record.product},
        'prediction_status': status, 'prediction_trace': trace, 'predicted_impurities': predictions,
        'prediction_evidence_kind': 'predicted_impurity_hypotheses', 'predicted_concentrations': None,
        'prediction_condition_scope': 'reaction_identity_only',
        'annotation_results': matches, 'excluded_annotations': excluded,
        'evaluation_status': 'matched_host_annotation_claims' if matches else 'no_matched_measurement_annotations',
        'measured_impurities': None, 'metrics': None, 'claims_experimental_validation': False,
        'limitations': ['Predictions remain hypotheses; the existing T5 backend uses proxy multi-product training labels.',
            'The recorded predictor receives reactants and major product only, not conditions, reagents or scale.',
            'Measurements and metrics are reported separately per supplied assay; no incompatible assay pooling.',
            'Partial annotations do not establish negative labels for unlisted impurity identities.',
            'Complete-scope metrics are conditional identity scores above a supplied reporting limit, not a global impurity inventory.',
            'Conditions and amounts are declared recipe fields; hashes and source URLs do not authenticate experimental results.',
            'No predicted concentration or general chemical-feasibility claim is made.']}
    return _plain(report)
