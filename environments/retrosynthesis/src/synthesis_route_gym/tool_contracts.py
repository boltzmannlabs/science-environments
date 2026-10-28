"""Versioned public scientific schemas; scores and source claims are not proof."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, AfterValidator, model_validator
from .chemistry import canonical_smiles
from .evidence_contracts import SourceProjection

CONTRACT_VERSION = 'srg-scientific-tool-v1'
Text = Annotated[str, Field(min_length=1, max_length=2000, strict=True)]
ID = Annotated[str, Field(min_length=1, max_length=200, strict=True)]
SMILES = Annotated[str, Field(min_length=1, max_length=10000, strict=True), AfterValidator(canonical_smiles)]
Digest = Annotated[str, Field(pattern=r'^[a-f0-9]{64}$', strict=True)]
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Percent = Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
Positive = Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]
Nonnegative = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]

class Contract(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid', validate_default=True)

class ExpandRequest(Contract):
    smiles: SMILES
    top_k: Annotated[int, Field(strict=True, ge=1, le=100)] = 10

class ConditionCandidate(Contract):
    id: ID
    aryl_halide: SMILES = Field(alias='aryl halide')
    ligand: SMILES
    additive: SMILES
    base: SMILES

class ConditionRequest(Contract):
    candidates: Annotated[tuple[ConditionCandidate, ...], Field(min_length=1, max_length=1000)]
    @model_validator(mode='after')
    def unique(self):
        if len({c.id for c in self.candidates}) != len(self.candidates):
            raise ValueError('Duplicate condition identifiers')
        return self

class CNConditionCandidate(Contract):
    id: ID
    aryl: SMILES
    amine: SMILES
    catalyst: SMILES
    base: SMILES
    solvent: SMILES
    product: SMILES

class CNConditionRequest(Contract):
    candidates: Annotated[tuple[CNConditionCandidate, ...], Field(min_length=1, max_length=1000)]
    @model_validator(mode='after')
    def unique(self):
        if len({c.id for c in self.candidates}) != len(self.candidates):
            raise ValueError('Duplicate C-N condition identifiers')
        return self

class ReactionYieldCandidate(Contract):
    id: ID
    reactants: Annotated[tuple[SMILES, ...], Field(min_length=1, max_length=100)]
    reagents: Annotated[tuple[SMILES, ...], Field(max_length=100)] = ()
    product: SMILES

class ReactionYieldRequest(Contract):
    candidates: Annotated[tuple[ReactionYieldCandidate, ...], Field(min_length=1, max_length=100)]
    @model_validator(mode='after')
    def unique(self):
        if len({c.id for c in self.candidates}) != len(self.candidates):
            raise ValueError('Duplicate reaction yield identifiers')
        return self

class SourceRequest(Contract):
    product: SMILES | None = None
    reactants: Annotated[tuple[SMILES, ...], Field(min_length=1, max_length=100)] | None = None
    query: Annotated[str, Field(min_length=1, max_length=300, strict=True)] | None = None
    limit: Annotated[int, Field(strict=True, ge=1, le=20)] = 10

class ForwardRequest(Contract):
    reactants: Annotated[tuple[SMILES, ...], Field(min_length=1, max_length=100)]
    product: SMILES
    top_k: Annotated[int, Field(strict=True, ge=1, le=100)] = 10

class ImpurityRequest(ForwardRequest):
    top_k: Annotated[int, Field(strict=True, ge=1, le=10)] = 5

class ObservationRequest(Contract):
    candidate_id: ID

class ProcessRequest(Contract):
    route_ids: Annotated[tuple[ID, ...], Field(min_length=1, max_length=100)]
    target_amount_mmol: Positive | None = None
    @model_validator(mode='after')
    def unique(self):
        if len(set(self.route_ids)) != len(self.route_ids):
            raise ValueError('Duplicate route identifiers')
        return self

class BioRequest(Contract):
    target_smiles: SMILES
    limit: Annotated[int, Field(strict=True, ge=1, le=20)] = 10

class PredictionSource(Contract):
    tool: ID
    version: ID

class ExpansionPrediction(Contract):
    reactants: Annotated[tuple[SMILES, ...], Field(min_length=1, max_length=100)]
    product: SMILES
    score: Number | None = None
    source: PredictionSource
    evidence_status: Literal['predicted'] = 'predicted'

class ExpansionResult(Contract):
    predictions: Annotated[tuple[ExpansionPrediction, ...], Field(max_length=100)]

class ConditionPrediction(Contract):
    id: ID
    predicted_yield_percent: Percent
    lower_yield_percent: Percent | None = None
    upper_yield_percent: Percent | None = None
    interval_kind: Text = 'uncalibrated_or_unspecified'
    domain: Text = 'host_declared_domain_not_general_feasibility'
    unseen_components: Annotated[tuple[Text, ...], Field(max_length=10)] = ()
    model_version: ID
    evidence_status: Literal['predicted'] = 'predicted'
    @model_validator(mode='after')
    def ordered(self):
        if self.lower_yield_percent is not None and self.upper_yield_percent is not None and self.lower_yield_percent > self.upper_yield_percent:
            raise ValueError('Reversed uncertainty band')
        return self

class ConditionResult(Contract):
    predictions: Annotated[tuple[ConditionPrediction, ...], Field(max_length=1000)]

class CNConditionPrediction(Contract):
    id: ID
    status: Literal['scored','abstained']
    hit_score: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)] | None
    raw_hit_score: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)] | None = None
    reason: Text | None = None
    model_version: ID
    domain: Text
    calibration_kind: Literal['uncalibrated_forest_score','heldout_isotonic_not_transfer_guarantee']
    evidence_status: Literal['predicted'] = 'predicted'
    endpoint_scope: Literal['source_screen_hit_not_synthesis_feasibility'] = 'source_screen_hit_not_synthesis_feasibility'
    @model_validator(mode='after')
    def consistent_status(self):
        if self.status == 'scored' and (self.hit_score is None or self.reason is not None):
            raise ValueError('Scored C-N prediction requires a score and no abstention reason')
        if self.status == 'abstained' and (self.hit_score is not None or self.raw_hit_score is not None
                or self.reason is None or not self.reason.strip()):
            raise ValueError('C-N abstention requires null scores and explicit reason')
        return self

class CNConditionResult(Contract):
    predictions: Annotated[tuple[CNConditionPrediction, ...], Field(max_length=1000)]

class ReactionYieldPrediction(Contract):
    id: ID
    status: Literal['scored','abstained']
    predicted_yield_percent: Percent | None
    raw_yield_percent: Number | None
    reason: Text | None = None
    model_version: ID
    domain: Text
    uncertainty_kind: Literal['not_calibrated'] = 'not_calibrated'
    evidence_status: Literal['predicted'] = 'predicted'
    endpoint_scope: Literal['model_yield_not_experimental_feasibility'] = 'model_yield_not_experimental_feasibility'
    @model_validator(mode='after')
    def consistent_status(self):
        if self.status == 'scored' and (self.predicted_yield_percent is None
                or self.raw_yield_percent is None or self.reason is not None):
            raise ValueError('Scored yield requires bounded prediction, finite raw value and no reason')
        if self.status == 'abstained' and (self.predicted_yield_percent is not None
                or self.reason is None or not self.reason.strip()):
            raise ValueError('Yield abstention requires a null prediction and explicit reason')
        return self

class ReactionYieldResult(Contract):
    predictions: Annotated[tuple[ReactionYieldPrediction, ...], Field(max_length=100)]

class ForwardPrediction(Contract):
    product: SMILES
    score: Number | None = None
    evidence_status: Literal['predicted'] = 'predicted'

class ForwardResult(Contract):
    predictions: Annotated[tuple[ForwardPrediction, ...], Field(max_length=100)]
    target_in_predictions: bool
    atom_balance_status: Literal['unknown_coproducts_not_provided'] = 'unknown_coproducts_not_provided'
    scope: Literal['model_consistency_not_experimental_feasibility'] = 'model_consistency_not_experimental_feasibility'

class ImpurityResult(Contract):
    predicted_smiles: Annotated[tuple[SMILES, ...], Field(max_length=10)]
    evidence_kind: Literal['predicted_impurity_hypotheses'] = 'predicted_impurity_hypotheses'
    concentration: None = None
    measured_impurities: None = None
    metrics: None = None

class ObservationResult(Contract):
    candidate_id: ID
    conditions: dict[ID, Text]
    yield_percent: Percent
    source_record_id: ID
    dataset_sha256: Digest
    evidence_kind: Literal['measured_dataset_replay'] = 'measured_dataset_replay'
    new_experiment_performed: Literal[False] = False
    @model_validator(mode='after')
    def bounded(self):
        if not 1 <= len(self.conditions) <= 100:
            raise ValueError('Observation requires bounded conditions')
        return self

class ProcessRow(Contract):
    route_id: ID
    steps: Annotated[int, Field(strict=True, ge=0, le=100)]
    material_cost: Nonnegative | None = None
    cost_currency: Annotated[str, Field(pattern=r'^[A-Z]{3}$')] | None = None
    scale_mmol: Positive | None = None
    cost_basis: Text | None = None
    cost_source_id: Text | None = None
    quoted_at: Text | None = None
    target: SMILES | None = None
    price_status: Literal['unknown', 'supplied_estimate', 'unverified_estimate', 'source_quote'] = 'unknown'
    inventory_sha256: Digest | None = None
    purity_basis: Text | None = None
    exclusions: tuple[Text, ...] = ()
    comparison_eligible: bool = False
    cost_status: Literal['unknown', 'supplied_estimate'] = 'unknown'

class ProcessResult(Contract):
    routes: Annotated[tuple[ProcessRow, ...], Field(min_length=1, max_length=100)]
    pareto_route_ids: tuple[ID, ...]
    dominated_route_ids: tuple[ID, ...]
    unranked_route_ids: tuple[ID, ...]
    common_basis_known: bool
    comparison_status: Literal['comparable_supplied_estimates', 'insufficient_common_basis']
    claims_manufacturing_savings: Literal[False] = False

class RetrievalResult(Contract):
    records: Annotated[tuple[SourceProjection, ...], Field(max_length=20)]
    corpus_sha256: Digest
    access_mode: Literal['evidence_retrieval']
    review_scope: Literal['retrieved_claims_not_verified'] = 'retrieved_claims_not_verified'

class BioCandidate(Contract):
    record_id: ID
    enzyme_name: Text
    source_url: Text
    source_locator: Text
    reactants: Annotated[tuple[SMILES, ...], Field(min_length=1, max_length=100)]
    products: Annotated[tuple[SMILES, ...], Field(min_length=1, max_length=100)]
    cofactors: tuple[Text, ...] = ()
    match_kind: Literal['exact_product', 'analogue']
    missing_reactants: tuple[SMILES, ...] = ()
    enzyme_availability: Literal['unknown'] = 'unknown'
    conditions_status: Literal['unknown'] = 'unknown'
    experimental_yield: None = None
    claims_activity: Literal[False] = False
    review_status: Literal['requires_independent_review'] = 'requires_independent_review'

class BioResult(Contract):
    candidates: Annotated[tuple[BioCandidate, ...], Field(max_length=20)]
    claims_experimental_validation: Literal[False] = False

INPUT_MODELS = {'expand':ExpandRequest, 'predict_conditions':ConditionRequest,
    'score_cn_conditions':CNConditionRequest,
    'predict_reaction_yield':ReactionYieldRequest,
    'retrieve_sources':SourceRequest, 'forward_check':ForwardRequest,
    'observe_condition':ObservationRequest, 'predict_impurities':ImpurityRequest,
    'compare_process':ProcessRequest, 'retrieve_biocatalysis':BioRequest}
OUTPUT_MODELS = {'expand':ExpansionResult, 'predict_conditions':ConditionResult,
    'score_cn_conditions':CNConditionResult,
    'predict_reaction_yield':ReactionYieldResult,
    'retrieve_sources':RetrievalResult, 'forward_check':ForwardResult,
    'observe_condition':ObservationResult, 'predict_impurities':ImpurityResult,
    'compare_process':ProcessResult, 'retrieve_biocatalysis':BioResult}

class ToolError(Contract):
    code: Annotated[str, Field(pattern=r'^[a-z][a-z0-9_]{0,79}$')]
    message: Annotated[str, Field(min_length=1, max_length=500)]

class ToolUsage(Contract):
    backend_calls: Annotated[int, Field(strict=True, ge=0, le=1)]
    request_units: Literal[1] = 1
    elapsed_seconds: Nonnegative
    condition_observations: Annotated[int, Field(strict=True, ge=0, le=1)] = 0

class BindingIdentity(Contract):
    version: ID
    configuration_version: ID
    model_version: ID
    artifact_sha256: Digest | None
    authority: Literal['prediction','source_retrieval','measured_replay','estimate']
    timeout_seconds: Positive

class ToolProvenance(Contract):
    registry_fingerprint: Digest
    stock_sha256: Digest | None
    evidence_sha256: Digest | None
    binding: BindingIdentity | None
    version_status: Literal['host_declared_artifact_digest','declared_not_artifact_verified']

class ToolEnvelope(Contract):
    schema_version: Literal['srg-scientific-tool-v1'] = CONTRACT_VERSION
    capability: ID
    status: Literal['ok','error','unavailable']
    data: dict | None
    error: ToolError | None
    provenance: ToolProvenance
    usage: ToolUsage
    evidence_kind: ID

    @model_validator(mode='after')
    def consistent_status(self):
        if (self.status == 'ok') != (self.data is not None and self.error is None):
            raise ValueError('Scientific result status/data mismatch')
        if self.status != 'ok' and (self.data is not None or self.error is None):
            raise ValueError('Scientific failure requires an error and no data')
        return self


def envelope_schema(name):
    """Merge payload definitions into the common envelope without dangling refs."""
    base=ToolEnvelope.model_json_schema()
    payload=OUTPUT_MODELS[name].model_json_schema()
    defs={**base.get('$defs',{}), **payload.get('$defs',{})}
    data={key:value for key,value in payload.items() if key!='$defs'}
    return {**base,'$defs':defs,'properties':{**base['properties'],
        'data':{'anyOf':[data,{'type':'null'}]}}}
