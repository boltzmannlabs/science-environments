"""Independent episode verification before finalization/reporting."""
from environment.observations import Observation
from tools.mixture_validator import validate


def verify(state) -> list[str]:
    errors = []
    for cid, item in state.candidates.items():
        check = validate(item['candidate'], state.constraints.get('bounds'), state.constraints.get('process_limits'))
        if item['status'] == 'valid' and not check.valid:
            errors.append('invalid candidate: ' + cid)
    for key, raw in state.predictions.items():
        try:
            obs = Observation.from_dict(raw)
            if obs.result_type != 'predicted' or not obs.provenance.get('tool') or not obs.provenance.get('version'):
                errors.append('prediction provenance/label: ' + key)
        except (ValueError, TypeError, KeyError):
            errors.append('malformed prediction: ' + key)
    for eid, item in state.experiments.items():
        if item['status'] == 'completed':
            if not item.get('approval_id') or not item.get('values'):
                errors.append('missing measurement approval/values: ' + eid)
            for value in item.get('values', []):
                if value.get('label') != 'measured' or not state.sources.get(value.get('source_id'), {}).get('authorized_measurement'):
                    errors.append('unsupported measurement: ' + eid)
    for claim in state.evidence:
        sid = claim.get('source_id')
        if claim.get('label') in ('measured','literature_reported') and sid not in state.sources:
            errors.append('unsupported evidence source')
        if claim.get('label') == 'predicted' and not claim.get('model_version'):
            errors.append('unversioned prediction')
    if any(cid not in state.candidates or state.candidates[cid]['status'] != 'valid' for cid in state.ranking):
        errors.append('ranking references invalid candidate')
    return errors
