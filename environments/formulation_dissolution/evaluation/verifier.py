"""Independent episode verification before finalization/reporting."""
from environment.observations import Observation
from tools.mixture_validator import validate


def verify_published(result, csv_path, source_rows=None):
    """Independently audit fold isolation and reported per-profile MAE/RMSE."""
    import csv
    import math
    from collections import defaultdict
    from statistics import mean
    rows=defaultdict(list)
    with open(csv_path,newline='') as stream:
        for row in csv.DictReader(stream):
            rows[row['profile_id']].append(row)
    errors=[]
    if set(rows)!={score['profile_id'] for score in result.get('scores',[])}:
        errors.append('profile set mismatch')
    for score in result.get('scores',[]):
        pid=score['profile_id'];points=rows[pid]
        if pid in score['train_profile_ids']: errors.append('train/test profile leakage: '+pid)
        if len(score['train_profile_ids'])!=5 or len(set(score['train_profile_ids']))!=5:
            errors.append('invalid training example count: '+pid)
        if len(points)!=7 or any(float(p['time_min'])<=0 for p in points): errors.append('time support mismatch: '+pid)
        if not points: continue
        if source_rows is not None:
            for p in points:
                train=[r['release_value'] for r in source_rows if r['profile_id'] in score['train_profile_ids']
                       and r['derived_time_min']==float(p['time_min'])]
                if len(train)!=5 or not math.isclose(float(p['prediction_release_percent']),mean(train),abs_tol=1e-9):
                    errors.append('prediction does not match training-only mean: '+pid)
                    break
        diff=[float(p['observed_release_percent'])-float(p['prediction_release_percent']) for p in points]
        if not math.isclose(score['mae_pp'],mean(abs(d) for d in diff),abs_tol=1e-9):
            errors.append('MAE mismatch: '+pid)
        if not math.isclose(score['rmse_pp'],math.sqrt(mean(d*d for d in diff)),abs_tol=1e-9):
            errors.append('RMSE mismatch: '+pid)
    if result.get('specification_attainment')!='not_evaluated' or result.get('ajanta_lot_improvement')!='not_evaluated':
        errors.append('unsupported product claim')
    acid=result.get('verified_primary_acid_track',{})
    if acid.get('status')=='evaluated_descriptive_only' and source_rows is not None:
        for fold in acid['folds']:
            pid=fold['profile_id'];train=fold['train_profile_ids']
            if pid in train or len(train)!=2 or len(set(train))!=2: errors.append('acid fold leakage: '+pid)
            pts=[r for r in source_rows if r['profile_id']==pid and r['release_value'] is not None]
            if len(pts)!=7: errors.append('acid time support mismatch: '+pid);continue
            diff=[]
            for pt in pts:
                values=[r['release_value'] for r in source_rows if r['profile_id'] in train and
                        r['derived_time_min']==pt['derived_time_min']]
                if len(values)!=2:errors.append('acid training time mismatch: '+pid);continue
                diff.append(pt['release_value']-mean(values))
            if len(diff)==7 and (not math.isclose(fold['mae_pp'],mean(abs(d) for d in diff),abs_tol=1e-9) or
                                 not math.isclose(fold['rmse_pp'],math.sqrt(mean(d*d for d in diff)),abs_tol=1e-9)):
                errors.append('acid score mismatch: '+pid)
    return errors


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
