"""Claim-to-evidence auditor: lack of evidence causes abstention."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditRequest:
    claims: tuple[dict, ...]
    sources: dict

    def __post_init__(self):
        if not isinstance(self.claims, tuple) or not isinstance(self.sources, dict):
            raise ValueError('invalid audit input')


@dataclass
class AuditDecision:
    decision: str
    reasons: list[str]


def audit(request: AuditRequest) -> AuditDecision:
    if not isinstance(request, AuditRequest):
        raise TypeError('AuditRequest required')
    if not request.claims:
        return AuditDecision('abstain', ['no claims with independently checkable evidence'])
    errors = []
    for claim in request.claims:
        sid = claim.get('source_id')
        label = claim.get('label')
        if not sid or sid not in request.sources:
            errors.append('missing verified source')
        elif not request.sources[sid].get('citation') or not request.sources[sid].get('document_id') or not request.sources[sid].get('verified_by'):
            errors.append('source citation/verification incomplete')
        if label not in {'measured','literature_reported','predicted','derived','assumed','unknown'}:
            errors.append('invalid evidence label')
        if label == 'measured' and (not sid or not request.sources.get(sid, {}).get('authorized_measurement')):
            errors.append('unauthorized measurement claim')
        if label == 'predicted' and not claim.get('model_version'):
            errors.append('missing model version')
        if isinstance(claim.get('value'), (float, int)) and not claim.get('unit'):
            errors.append('missing unit')
        if not claim.get('text'):
            errors.append('missing claim text')
    return AuditDecision('revise' if errors else 'accept', sorted(set(errors)))
