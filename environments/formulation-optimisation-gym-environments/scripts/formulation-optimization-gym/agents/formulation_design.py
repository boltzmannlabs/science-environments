"""Bounded, typed formulation design specialist (no inferred original formula)."""
from dataclasses import dataclass
from tools.mixture_validator import validate


@dataclass(frozen=True)
class DesignRequest:
    inventory: dict
    candidate: dict
    verified_bounds: dict | None = None

    def __post_init__(self):
        if not isinstance(self.inventory, dict) or not isinstance(self.candidate, dict):
            raise ValueError('invalid design request')


@dataclass
class DesignResult:
    status: str
    candidate: dict | None
    gaps: list[str]


def propose(request: DesignRequest) -> DesignResult:
    """Only validate user-supplied candidate against registered inventory."""
    if not isinstance(request, DesignRequest):
        raise TypeError('DesignRequest required')
    parts = request.candidate.get('ingredients', [])
    if not parts or any(not isinstance(p, dict) or p.get('material_id') not in request.inventory for p in parts):
        return DesignResult('insufficient_data', None, ['verified candidate ingredients/inventory'])
    checks = validate(request.candidate, request.verified_bounds)
    return DesignResult('valid' if checks.valid else 'invalid', request.candidate if checks.valid else None, checks.failed + checks.not_evaluated)
