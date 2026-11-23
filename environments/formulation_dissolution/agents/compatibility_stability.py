"""Evidence-bounded compatibility/stability triage."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CompatibilityRequest:
    material_ids: tuple[str, ...]
    evidence: tuple[dict, ...] = ()

    def __post_init__(self):
        if not self.material_ids or not all(isinstance(x, str) and x for x in self.material_ids):
            raise ValueError('material identities required')


@dataclass
class CompatibilityResult:
    status: str
    findings: list[dict]
    missing_data: list[str]


def assess(request: CompatibilityRequest) -> CompatibilityResult:
    """Return only supplied, source-linked findings; do not invent interactions."""
    if not isinstance(request, CompatibilityRequest):
        raise TypeError('CompatibilityRequest required')
    findings = [e for e in request.evidence if e.get('source_id') and e.get('label') in {'measured','literature_reported','predicted'} and set(e.get('materials', ())) <= set(request.material_ids)]
    return CompatibilityResult('success' if findings else 'insufficient_data', findings, [] if findings else ['source-linked compatibility/stability evidence'])
