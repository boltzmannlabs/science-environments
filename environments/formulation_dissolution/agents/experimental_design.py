"""Approval-gated discriminating experiment proposals, never execution."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentRequest:
    hypothesis: str
    factors: tuple[str, ...]
    responses: tuple[str, ...]
    controls: tuple[str, ...]
    replicates: int
    rationale: str
    cost: float | None = None

    def __post_init__(self):
        if not self.hypothesis or not self.factors or not self.responses or not self.controls or isinstance(self.replicates, bool) or self.replicates < 1 or not self.rationale or self.cost is not None and self.cost < 0:
            raise ValueError('incomplete experiment design')


@dataclass
class ExperimentProposal:
    status: str
    request: ExperimentRequest
    approval_required: bool = True


def design(request: ExperimentRequest, *, remaining_cost: float | None = None) -> ExperimentProposal:
    if not isinstance(request, ExperimentRequest):
        raise TypeError('ExperimentRequest required')
    if remaining_cost is not None and (request.cost is None or request.cost > remaining_cost):
        return ExperimentProposal('budget_exhausted', request)
    return ExperimentProposal('proposed', request)
