"""Versioned immutable input contracts; unknown scientific values remain null."""

from typing import Annotated, Literal, Mapping
from types import MappingProxyType
from pydantic import BaseModel, ConfigDict, Field, AfterValidator, model_validator, field_validator, field_serializer, model_serializer
from .chemistry import canonical_smiles, validate_smarts

Smiles = Annotated[str, AfterValidator(canonical_smiles)]
Smarts = Annotated[str, AfterValidator(validate_smarts)]
Identifier = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")]
Nonnegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Fraction = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class Record(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", validate_default=True)


class MaterialUse(Record):
    smiles: Smiles
    amount_mmol: Positive | None = None


class InventoryItem(Record):
    smiles: Smiles
    available_mmol: Nonnegative | None = None
    price_per_mmol: Nonnegative | None = None
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")] | None = None
    source: str | None = None
    quoted_at: str | None = None

    @model_validator(mode="after")
    def price_has_units(self):
        if self.price_per_mmol is not None and self.currency is None:
            raise ValueError("A price requires its currency")
        return self


class EvidenceRecord(Record):
    evidence_id: Identifier
    kind: Literal["literature_exact", "literature_analogue", "measured", "proxy", "predicted", "unresolved"]
    source: Annotated[str, Field(min_length=1, max_length=2000)]
    locator: Annotated[str, Field(min_length=1, max_length=2000)]
    reactants: tuple[Smiles, ...] = ()
    product: Smiles | None = None
    verified_by: str | None = None
    conditions_scope: Literal["unknown", "same", "different"] = "unknown"
    notes: str = ""


class ReactionStep(Record):
    step_id: Identifier
    product: Smiles
    reactants: Annotated[tuple[MaterialUse, ...], Field(min_length=1, max_length=100)]
    reagents: Annotated[tuple[MaterialUse, ...], Field(max_length=100)] = ()
    product_amount_mmol: Positive | None = None
    source_tool: Annotated[str, Field(min_length=1, max_length=200)]
    source_version: Annotated[str, Field(min_length=1, max_length=200)]
    proposal_score: Annotated[float, Field(allow_inf_nan=False)] | None = None
    predicted_yield: Fraction | None = None
    conditions: tuple[str, ...] = ()
    condition_inputs: Mapping[str, Smiles] | None = None
    evidence_ids: tuple[Identifier, ...] = ()
    required_equipment: tuple[str, ...] = ()
    operations: tuple[str, ...] = ()
    conditions_complete: bool = False

    @field_validator("condition_inputs")
    @classmethod
    def freeze_condition_inputs(cls, value):
        return None if value is None else MappingProxyType(dict(value))

    @field_serializer("condition_inputs")
    def serialize_condition_inputs(self, value):
        return None if value is None else dict(value)


class RouteCandidate(Record):
    route_id: Identifier
    target: Smiles
    steps: Annotated[tuple[ReactionStep, ...], Field(max_length=100)]
    parent_route_id: Identifier | None = None


class Constraints(Record):
    max_steps: Annotated[int, Field(ge=0, le=100)] = 8
    forbidden_smiles: tuple[Smiles, ...] = ()
    forbidden_smarts: tuple[Smarts, ...] = ()
    available_equipment: tuple[str, ...] = ()
    forbidden_operations: tuple[str, ...] = ()
    require_complete_conditions: bool = False


class Budget(Record):
    max_actions: Annotated[int, Field(ge=1, le=100000, strict=True)] | None = 200
    max_expansions: Annotated[int, Field(ge=1, le=100000, strict=True)] | None = 1000
    max_wall_seconds: Annotated[float, Field(gt=0, allow_inf_nan=False, strict=True)] | None = 1800
    max_llm_tokens: Annotated[int, Field(ge=1, strict=True)] | None = 100000
    top_k: Annotated[int, Field(ge=1, le=100, strict=True)] = 10
    regime: Literal["budgeted", "unbudgeted"] = "budgeted"

    @model_validator(mode="after")
    def explicit_resource_regime(self):
        limits = (self.max_actions, self.max_expansions, self.max_wall_seconds, self.max_llm_tokens)
        if self.regime == "unbudgeted" and any(value is not None for value in limits):
            raise ValueError("Unbudgeted aggregate limits must all be null")
        if self.regime == "budgeted" and any(value is None for value in limits):
            raise ValueError("Budgeted aggregate limits must all be finite")
        return self

    @model_serializer(mode="wrap")
    def legacy_budget_identity(self, handler):
        values = handler(self)
        # Historical task digests include exact budget keys and field order.
        return {key: value for key, value in values.items()
                if key != "regime" or self.regime != "budgeted"}

    @classmethod
    def unbudgeted(cls, *, top_k=10):
        return cls(regime="unbudgeted", max_actions=None, max_expansions=None,
                   max_wall_seconds=None, max_llm_tokens=None, top_k=top_k)


class Task(Record):
    schema_version: Literal["1.0"] = "1.0"
    task_id: Identifier
    target: Smiles
    inventory: Annotated[tuple[InventoryItem, ...], Field(max_length=100000)]
    target_amount_mmol: Positive | None = None
    constraints: Constraints = Field(default_factory=Constraints)
    budget: Budget = Field(default_factory=Budget)
    evidence: tuple[EvidenceRecord, ...] = ()

    @model_validator(mode="after")
    def unique_keys(self):
        for values in ([item.smiles for item in self.inventory],
                       [item.evidence_id for item in self.evidence]):
            if len(values) != len(set(values)):
                raise ValueError("Inventory identities and evidence IDs must be unique")
        return self


class Finding(Record):
    code: str
    severity: Literal["error", "unknown", "info"]
    message: str
    step_id: str | None = None


class CostEstimate(Record):
    total: Nonnegative | None = None
    known_subtotal: Nonnegative = 0
    currency: str | None = None
    missing_materials: tuple[str, ...] = ()
    scope: Literal["starting_materials_and_reagents"] = "starting_materials_and_reagents"


class RouteAssessment(Record):
    route_id: str
    graph_valid: bool
    inventory_complete: bool
    quantity_status: Literal["complete", "unknown", "insufficient", "not_requested"]
    constraint_compliant: bool
    acquisition_only: bool
    evidence_status: Mapping[str, str]
    conditions_evidence: Mapping[str, str]
    cost: CostEstimate
    findings: tuple[Finding, ...]
    unstocked: tuple[str, ...]
    weak_steps: tuple[str, ...]
    review_status: Literal["pending"] = "pending"
    solved: Literal[False] = False

    @field_validator("evidence_status", "conditions_evidence")
    @classmethod
    def freeze_status(cls, value):
        return MappingProxyType(dict(value))

    @field_serializer("evidence_status", "conditions_evidence")
    def serialize_status(self, value):
        return dict(value)
