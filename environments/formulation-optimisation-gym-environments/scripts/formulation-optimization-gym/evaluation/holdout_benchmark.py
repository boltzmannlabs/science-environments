"""Leakage-aware deterministic split and measured-only benchmark."""
import hashlib
from models.mixture_predictor import MixturePredictor
from models.uncertainty import calibration


def split(rows: list[dict], *, seed: str = 'frozen-v1', holdout_fraction: float = 0.25):
    if not 0 < holdout_fraction < 1:
        raise ValueError('fraction outside (0,1)')
    groups = {}
    for row in rows:
        if row.get('label') != 'measured' or not row.get('source_id') or not row.get('group_id'):
            raise ValueError('measured, source-linked group_id required')
        groups.setdefault(row['group_id'], []).append(row)
    ordered = sorted(groups, key=lambda g: hashlib.sha256((seed + ':' + g).encode()).hexdigest())
    n = max(1, round(len(ordered)*holdout_fraction))
    test = set(ordered[:n])
    return ([r for g in ordered if g not in test for r in groups[g]], [r for g in ordered if g in test for r in groups[g]])


def benchmark(rows: list[dict], materials: tuple[str,...], unit: str, *, seed: str = 'frozen-v1') -> dict:
    if len(rows) < 4 or len({r.get('group_id') for r in rows}) < 3:
        return {'status':'not_evaluated','reason':'insufficient independent measured formulation groups; acquire/curate dataset','arms':{'A':'not_evaluated','B':'not_evaluated','C':'not_evaluated','D':'not_evaluated'}}
    train, test = split(rows, seed=seed)
    if not train or not test:
        return {'status':'not_evaluated','reason':'empty train/holdout after grouped split'}
    model = MixturePredictor(materials, unit).fit(train)
    predictions = [model.predict(row['composition'])['value'] for row in test]
    scores = calibration(predictions, [r['target'] for r in test])
    return {'status':'evaluated','split_seed':seed,'train_count':len(train),'holdout_count':len(test),'model_version':model.version,'point_metrics':scores,'other_arms':'not_evaluated; matched authorized specialist/direct-tool runs required','limitations':['nearest-neighbour baseline only; calibration may not be established','group_id must merge all replicates and related formulations; externally verify grouping']}
