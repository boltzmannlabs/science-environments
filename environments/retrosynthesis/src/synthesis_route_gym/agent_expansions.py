"""Metered one-step agent hypotheses for normal SynthChem route search.

Only a host-labelled precursor hypothesis is returned. No model-authored source,
score or evidence assertion can enter the shared proposal pool.
"""

from typing import Literal

from pydantic import Field, model_validator

from .chemistry import canonical_smiles
from .planning import _step
from .schemas import Record, RouteCandidate
from .validation import assess_route

SOURCE = {"tool": "submitted_hypothesis", "version": "host-registered-v1"}
MAX_BATCH = 20
MAX_EPISODE_PROPOSALS = 1000


class AgentCandidate(Record):
    reactants: tuple[str, ...] = Field(min_length=1, max_length=10)
    status: Literal["hypothesis"]
    rationale: str = Field(default="", max_length=500)
    product: str | None = None

    @model_validator(mode="after")
    def bound_structures(self):
        if any(not isinstance(value, str) or not 1 <= len(value) <= 512
               for value in self.reactants):
            raise ValueError("Precursor structures must be bounded strings")
        if self.product is not None and (not isinstance(self.product, str)
                                         or not 1 <= len(self.product) <= 512):
            raise ValueError("Product structure must be a bounded string")
        return self


class AgentBatch(Record):
    product: str = Field(min_length=1, max_length=512)
    candidates: tuple[AgentCandidate, ...] = Field(min_length=1, max_length=MAX_BATCH)


def _successful_count(events):
    return sum(len(event["result"]["predictions"])
               for event in events if event["action"] == "propose_expansion"
               and event["status"] == "ok")


def validate_agent_expansions(task, arguments, events):
    """Return canonical, host-labelled predictions or reject the whole batch."""
    batch = AgentBatch.model_validate(arguments)
    if _successful_count(events) + len(batch.candidates) > MAX_EPISODE_PROPOSALS:
        raise ValueError("Agent proposal allowance exhausted")
    product = canonical_smiles(batch.product)
    checked_task = task.model_copy(update={"target": product})
    rows, seen = [], set()
    for candidate in batch.candidates:
        if candidate.product is not None and canonical_smiles(candidate.product) != product:
            raise ValueError("Agent proposal changed product identity")
        reactants = tuple(canonical_smiles(value) for value in candidate.reactants)
        if product in reactants:
            raise ValueError("Product cannot be its own precursor")
        key = tuple(sorted(reactants))
        if key in seen:
            raise ValueError("Duplicate agent proposal")
        seen.add(key)
        prediction = {"product": product, "reactants": list(reactants),
                      "source": SOURCE.copy()}
        step = _step(prediction)
        assessment = assess_route(checked_task, RouteCandidate(
            route_id="agent-hypothesis", target=product, steps=(step,)))
        if not assessment.graph_valid or not assessment.constraint_compliant:
            raise ValueError("Agent precursor hypothesis violates structural or task constraints")
        rows.append(prediction)
    return {"product": product, "predictions": rows,
            "evidence_status": "agent_hypothesis_unverified"}
