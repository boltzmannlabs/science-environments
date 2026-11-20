"""Independent hard-constraint and manufacturability critique."""
from dataclasses import dataclass
from tools.mixture_validator import validate, Check


@dataclass(frozen=True)
class CriticRequest:
    candidate: dict
    approved_bounds: dict | None = None
    process_limits: dict | None = None

    def __post_init__(self):
        if not isinstance(self.candidate, dict):
            raise ValueError('candidate must be dict')


def critique(request: CriticRequest) -> Check:
    if not isinstance(request, CriticRequest):
        raise TypeError('CriticRequest required')
    return validate(request.candidate, request.approved_bounds, request.process_limits)
