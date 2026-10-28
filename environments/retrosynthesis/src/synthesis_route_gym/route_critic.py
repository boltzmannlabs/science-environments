"""Pure, bounded Route Critic contracts for the isolated main-profile runtime.

Chemistry and source retrieval belong to the host. These contracts preserve its
public packet and restrict advice to observed identities. A model concern never
acquires deterministic rejection authority merely through confident wording.
"""
import hashlib
import json
from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator
from .condition_scientist import RuntimeResources, RESOURCE_KEYS

MAX_PACKET_BYTES = 100000
MAX_BYTES = 120000
ID = Annotated[str, Field(strict=True, min_length=1, max_length=240)]
Text = Annotated[str, Field(strict=True, min_length=1, max_length=2000)]
Molecule = Annotated[str, Field(strict=True, min_length=1, max_length=10000)]
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Nonnegative = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
Positive = Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]
Count = Annotated[int, Field(strict=True, ge=0, le=1000000)]
Flag = Annotated[bool, Field(strict=True)]
Digest = Annotated[str, Field(strict=True, pattern=r'^[a-f0-9]{64}$')]
Category = Literal['route_structure', 'constraint_violation', 'unsupported_transformation',
    'missing_materials', 'stereochemistry', 'quantity_conflict', 'incomplete_conditions',
    'model_domain_mismatch']
Severity = Literal['error', 'review', 'info']
Claim = Literal['literature_exact', 'literature_analogue', 'measured', 'proxy', 'predicted', 'unresolved']


class _Record(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, validate_default=True)

    @field_validator('*')
    @classmethod
    def nonblank(cls, value):
        if isinstance(value, str) and not value.strip():
            raise ValueError('Text must not be blank')
        return value


class Material(_Record):
    smiles: Molecule
    amount_mmol: Positive | None


class Step(_Record):
    step_id: ID
    product: Molecule
    reactants: Annotated[tuple[Material, ...], Field(min_length=1, max_length=100)]
    reagents: Annotated[tuple[Material, ...], Field(max_length=100)]
    product_amount_mmol: Positive | None
    source_tool: ID
    source_version: ID
    proposal_score: Number | None
    predicted_yield: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)] | None
    conditions: Annotated[tuple[Text, ...], Field(max_length=100)]
    condition_inputs: dict[ID, Molecule] | None
    evidence_ids: Annotated[tuple[ID, ...], Field(max_length=100)]
    required_equipment: Annotated[tuple[Text, ...], Field(max_length=100)]
    operations: Annotated[tuple[Text, ...], Field(max_length=100)]
    conditions_complete: Flag


class Route(_Record):
    route_id: ID
    target: Molecule
    steps: Annotated[tuple[Step, ...], Field(max_length=12)]
    parent_route_id: ID | None


class Constraints(_Record):
    max_steps: Annotated[int, Field(strict=True, ge=0, le=100)]
    forbidden_smiles: tuple[Molecule, ...]
    forbidden_smarts: tuple[Molecule, ...]
    available_equipment: tuple[Text, ...]
    forbidden_operations: tuple[Text, ...]
    require_complete_conditions: Flag


class TaskSummary(_Record):
    task_id: ID
    target: Molecule
    target_amount_mmol: Positive | None
    constraints: Constraints


class InventoryItem(_Record):
    smiles: Molecule
    available_mmol: Nonnegative | None
    price_per_mmol: Nonnegative | None
    currency: Annotated[str, Field(strict=True, pattern=r'^[A-Z]{3}$')] | None
    source: str | None
    quoted_at: str | None


class InventoryMatch(_Record):
    smiles: Molecule
    item: InventoryItem | None

    @model_validator(mode='after')
    def identity(self):
        if self.item is not None and self.item.smiles != self.smiles:
            raise ValueError('Inventory lookup identity differs')
        return self


class HostFinding(_Record):
    code: Text
    severity: Literal['error', 'unknown', 'info']
    message: Text
    step_id: ID | None


class Cost(_Record):
    total: Nonnegative | None
    known_subtotal: Nonnegative
    currency: Annotated[str, Field(strict=True, pattern=r'^[A-Z]{3}$')] | None
    missing_materials: tuple[Molecule, ...]
    scope: Literal['starting_materials_and_reagents']


class Assessment(_Record):
    route_id: ID
    graph_valid: Flag
    inventory_complete: Flag
    quantity_status: Literal['complete', 'unknown', 'insufficient', 'not_requested']
    constraint_compliant: Flag
    acquisition_only: Flag
    evidence_status: dict[ID, Claim]
    conditions_evidence: dict[ID, Literal['unknown', 'same', 'different']]
    cost: Cost
    findings: tuple[HostFinding, ...]
    unstocked: tuple[Molecule, ...]
    weak_steps: tuple[ID, ...]
    review_status: Literal['pending']
    solved: Literal[False]


class Source(_Record):
    record_id: ID
    document_id: Text
    source_url: Text
    locator: Text
    reactants: Annotated[tuple[Molecule, ...], Field(min_length=1, max_length=100)]
    product: Molecule
    claim_kind: Claim
    conditions_scope: Literal['unknown', 'same', 'different']
    conditions: Annotated[tuple[Text, ...], Field(max_length=50)]
    retrieved_at: Text
    source_content_sha256: Digest
    visibility: Literal['public_source']
    stereochemistry_scope: Literal['as_encoded', 'not_reported']
    record_sha256: Digest
    reaction_sha256: Digest
    evidence_status: Literal['source_claim']
    verification_status: Literal['not_attested']
    atom_balance_status: Literal['unknown']

    @model_validator(mode='after')
    def public_identity(self):
        parsed = urlsplit(self.source_url)
        if (parsed.scheme not in {'http', 'https'} or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or any(char.isspace() or ord(char) < 32 for char in self.source_url)):
            raise ValueError('Source URL must be public HTTP(S) without credentials')
        parsed.port
        instant = datetime.fromisoformat(self.retrieved_at.replace('Z', '+00:00'))
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError('Source time requires a timezone')
        return self


class ToolBinding(_Record):
    version: ID
    configuration_version: ID
    model_version: ID
    artifact_sha256: Digest | None
    authority: Literal['prediction', 'source_retrieval', 'measured_replay', 'estimate']
    timeout_seconds: Positive


class ToolProvenance(_Record):
    registry_fingerprint: Digest
    stock_sha256: Digest | None
    evidence_sha256: Digest | None
    binding: ToolBinding | None
    version_status: Literal['host_declared_artifact_digest', 'declared_not_artifact_verified']


class ToolUsage(_Record):
    backend_calls: Annotated[int, Field(strict=True, ge=0, le=1)]
    request_units: Literal[1]
    elapsed_seconds: Nonnegative
    condition_observations: Annotated[int, Field(strict=True, ge=0, le=1)]


class ToolError(_Record):
    code: Text
    message: Annotated[str, Field(strict=True, min_length=1, max_length=500)]


class ToolEnvelope(_Record):
    schema_version: Literal['srg-scientific-tool-v1']
    capability: ID
    status: Literal['ok', 'error', 'unavailable']
    data: dict[str, JsonValue] | None
    error: ToolError | None
    provenance: ToolProvenance
    usage: ToolUsage
    evidence_kind: ID

    @model_validator(mode='after')
    def status_data(self):
        if (self.status == 'ok') != (self.data is not None and self.error is None):
            raise ValueError('Scientific tool status and payload differ')
        if self.status != 'ok' and (self.data is not None or self.error is None):
            raise ValueError('Failed tool result requires null data and an error')
        return self


class ToolResult(_Record):
    tool_result_id: ID
    action: Literal['expand', 'predict_conditions', 'score_cn_conditions', 'predict_reaction_yield',
        'retrieve_sources', 'forward_check', 'observe_condition', 'predict_impurities',
        'compare_process', 'retrieve_biocatalysis']
    arguments: dict[str, JsonValue]
    result: ToolEnvelope

    @model_validator(mode='after')
    def capability(self):
        if self.action != self.result.capability:
            raise ValueError('Tool action and capability differ')
        return self


class Fact(_Record):
    fact_id: ID
    route_id: ID
    step_id: ID | None
    category: Category
    severity: Severity
    authority: Literal['deterministic', 'source_consistency', 'uncertainty']
    source_record_ids: Annotated[tuple[ID, ...], Field(max_length=60)]
    code: Text
    message: Text

    @model_validator(mode='after')
    def authority_boundary(self):
        if self.severity == 'error' and self.authority != 'deterministic':
            raise ValueError('Only deterministic host facts may have error authority')
        _unique(self.source_record_ids)
        return self


class RecheckArguments(_Record):
    route_id: ID


class Recheck(_Record):
    recheck_id: ID
    action: Literal['validate']
    arguments: RecheckArguments


class ReviewPacket(_Record):
    schema_version: Literal['srg-route-review-v1']
    task_sha256: Digest
    task: TaskSummary
    routes: Annotated[tuple[Route, ...], Field(min_length=1, max_length=3)]
    assessments: Annotated[tuple[Assessment, ...], Field(min_length=1, max_length=3)]
    inventory: Annotated[tuple[InventoryMatch, ...], Field(max_length=1000)]
    sources: Annotated[tuple[Source, ...], Field(max_length=60)]
    tool_results: Annotated[tuple[ToolResult, ...], Field(max_length=12)]
    facts: Annotated[tuple[Fact, ...], Field(max_length=300)]
    recheck_menu: Annotated[tuple[Recheck, ...], Field(max_length=3)]

    @model_validator(mode='after')
    def links(self):
        route_ids = {row.route_id for row in self.routes}
        collections = ([row.route_id for row in self.routes], [row.route_id for row in self.assessments],
            [row.smiles for row in self.inventory], [row.record_id for row in self.sources],
            [row.tool_result_id for row in self.tool_results], [row.fact_id for row in self.facts],
            [row.recheck_id for row in self.recheck_menu])
        for values in collections:
            _unique(values)
        if {row.route_id for row in self.assessments} != route_ids:
            raise ValueError('Route assessments differ from shortlist identities')
        steps = {row.route_id: {step.step_id for step in row.steps} for row in self.routes}
        for row in self.routes:
            _unique([step.step_id for step in row.steps])
        sources = {row.record_id for row in self.sources}
        for fact in self.facts:
            if (fact.route_id not in route_ids or fact.step_id is not None and fact.step_id not in steps[fact.route_id]
                    or set(fact.source_record_ids) - sources):
                raise ValueError('Host fact refers to an unavailable route, step or source')
        if any(row.arguments.route_id not in route_ids for row in self.recheck_menu):
            raise ValueError('Recheck menu refers to an unavailable route')
        return self


class Resources(RuntimeResources):
    """Shared explicit-regime contract; finite serialized contexts are unchanged."""


class CriticFinding(_Record):
    route_id: ID
    step_id: ID | None
    category: Category
    severity: Severity
    supporting_fact_ids: Annotated[tuple[ID, ...], Field(max_length=12)]
    source_record_ids: Annotated[tuple[ID, ...], Field(max_length=12)]
    requested_revision: Literal['revise_route', 'recheck', 'retain_uncertainty', 'none']
    rationale: Annotated[str, Field(strict=True, min_length=1, max_length=600)]

    @model_validator(mode='after')
    def unique_citations(self):
        _unique(self.supporting_fact_ids)
        _unique(self.source_record_ids)
        return self


class CriticReport(_Record):
    schema_version: Literal['srg-route-critic-report-v1']
    context_sha256: Digest
    findings: Annotated[tuple[CriticFinding, ...], Field(max_length=8)]
    recommended_recheck_id: ID | None
    evidence_status: Literal['agent_proposal']

    @model_validator(mode='after')
    def distinct_findings(self):
        _unique([(row.route_id, row.step_id, row.category) for row in self.findings])
        return self


def _unique(values):
    if len(set(values)) != len(values):
        raise ValueError('Duplicate contract identity or citation')


def _encoded(value, maximum=MAX_BYTES):
    try:
        raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError('Expected finite JSON contract') from error
    if len(raw) > maximum:
        raise ValueError('Route critic contract exceeds bounded context')
    return raw


def _packet(value):
    raw = json.loads(_encoded(value, MAX_PACKET_BYTES))
    return ReviewPacket.model_validate(raw).model_dump(mode='json')


def build_context(packet, resources):
    """Construct a detached context from a host packet; no query or authority added."""
    checked = _packet(packet)
    available = Resources.model_validate(json.loads(_encoded(resources))).model_dump(mode='json')
    if any(available[key] is not None and available[key] <= 0 for key in RESOURCE_KEYS):
        return None
    return json.loads(_encoded({'schema_version':'srg-route-critic-context-v1',
                               'packet':checked, 'resources':available}))


def _context(value):
    current = json.loads(_encoded(value))
    if (not isinstance(current, dict) or set(current) != {'schema_version', 'packet', 'resources'}
            or current['schema_version'] != 'srg-route-critic-context-v1'):
        raise ValueError('Invalid Route Critic context')
    checked = build_context(current['packet'], current['resources'])
    if checked is None:
        raise ValueError('Route Critic context has exhausted resources')
    return checked


def context_fingerprint(context):
    return hashlib.sha256(_encoded(_context(context))).hexdigest()


def _pairs(pairs):
    _unique([key for key, _ in pairs])
    return dict(pairs)


def _constant(_):
    raise ValueError('Nonfinite JSON number')


def _validate_finding(finding, packet):
    routes = {row['route_id']:row for row in packet['routes']}
    facts = {row['fact_id']:row for row in packet['facts']}
    rid, sid = finding['route_id'], finding['step_id']
    if rid not in routes or sid is not None and sid not in {s['step_id'] for s in routes[rid]['steps']}:
        raise ValueError('Critic finding refers to unavailable route or step')
    cited = []
    for key in finding['supporting_fact_ids']:
        fact = facts.get(key)
        if fact is None or (fact['route_id'], fact['step_id']) != (rid, sid):
            raise ValueError('Critic fact citation differs from route and step')
        cited.append(fact)
    allowed = {key for fact in packet['facts'] if (fact['route_id'], fact['step_id']) == (rid, sid)
               for key in fact['source_record_ids']}
    if sid is not None:
        allowed.update(key for step in routes[rid]['steps'] if step['step_id'] == sid for key in step['evidence_ids'])
    available = {row['record_id'] for row in packet['sources']}
    if set(finding['source_record_ids']) - (allowed & available):
        raise ValueError('Critic source citation is unavailable or unrelated to this route and step')
    if finding['severity'] == 'error' and not any(fact['severity'] == 'error'
            and fact['authority'] == 'deterministic' and fact['category'] == finding['category'] for fact in cited):
        raise ValueError('Critic error requires a matching deterministic host error fact')


def parse_report(text, context):
    """Accept strict JSON advice referencing only the exact host context."""
    if not isinstance(text, str) or len(text.encode()) > MAX_BYTES:
        raise ValueError('Critic report must be bounded JSON text')
    try:
        raw = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except (ValueError, RecursionError) as error:
        raise ValueError('Critic report must be one strict JSON object') from error
    checked = CriticReport.model_validate(raw).model_dump(mode='json')
    current = _context(context)
    if checked['context_sha256'] != context_fingerprint(current):
        raise ValueError('Critic context hash differs')
    packet = current['packet']
    for finding in checked['findings']:
        _validate_finding(finding, packet)
    if (checked['recommended_recheck_id'] is not None and
            checked['recommended_recheck_id'] not in {r['recheck_id'] for r in packet['recheck_menu']}):
        raise ValueError('Critic recheck is absent from the host action menu')
    return checked


def hydrate_report(report, context):
    """Attach exact host records and recheck arguments, not invented model data."""
    checked = parse_report(_encoded(report).decode(), context)
    packet = _context(context)['packet']
    facts = {row['fact_id']:row for row in packet['facts']}
    sources = {row['record_id']:row for row in packet['sources']}
    rechecks = {row['recheck_id']:row for row in packet['recheck_menu']}
    findings = [{**row, 'supporting_facts':[facts[key] for key in row['supporting_fact_ids']],
                 'source_records':[sources[key] for key in row['source_record_ids']]} for row in checked['findings']]
    return json.loads(_encoded({**checked, 'findings':findings,
        'recommended_recheck':rechecks.get(checked['recommended_recheck_id'])}))
