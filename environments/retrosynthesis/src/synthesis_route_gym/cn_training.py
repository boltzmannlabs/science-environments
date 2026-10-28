"""Frozen, bounded C–N screen-hit experiment; never promotes production defaults."""
from __future__ import annotations

import hashlib
from collections import Counter
import importlib.metadata
import json
import platform
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.isotonic import IsotonicRegression

from .cn_model import CNConditionModel, CN_ROLES, ENDPOINT, cn_features, export_classifier

SEED = 20261027
VERSION = 'srg06-cn-training-v1'


def _json(value):
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n'


def _hash(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _write(path, value):
    content = _json(value)
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(content)
    return hashlib.sha256(content.encode()).hexdigest()


def candidate_panel():
    common = {'n_estimators':128, 'max_depth':18, 'random_state':SEED, 'n_jobs':2}
    means = ({'name':'global_mean', 'kind':'global', 'arm':'baseline', 'config':{}},
             {'name':'condition_mean_shrink5', 'kind':'condition', 'arm':'baseline', 'config':{'shrinkage':5}})
    forests = [('legacy_et_leaf2','baseline','extra_trees',1.0,2),
               ('legacy_et_leaf8','baseline','extra_trees',1.0,8),
               ('rf_leaf2','candidate','random_forest',0.5,2),
               ('rf_leaf8','candidate','random_forest',0.5,8),
               ('et_leaf4','candidate','extra_trees',0.5,4)]
    return means + tuple({'name':name, 'kind':'forest', 'arm':arm, 'algorithm':algorithm,
        'config':{**common, 'max_features':features, 'min_samples_leaf':leaf}}
        for name,arm,algorithm,features,leaf in forests)


def _public(rows):
    return tuple({'id':r['record_id'], **{key:r[key] for key in CN_ROLES}} for r in rows)


def _scores_valid(rows, scores):
    if not rows or len(rows) != len(scores) or len({r['record_id'] for r in rows}) != len(rows):
        raise ValueError('Rows must be nonempty with unique IDs and one score per row')
    if any(s is not None and (isinstance(s, bool) or not np.isfinite(s) or not 0 <= s <= 1) for s in scores):
        raise ValueError('Scores must be finite probabilities or None')


def make_choices(rows, scores, raw_scores=None):
    """Public decisions only: calibrated score, raw score, then stable record ID."""
    _scores_valid(rows, scores)
    raw_scores = scores if raw_scores is None else raw_scores
    _scores_valid(rows, raw_scores)
    if any((s is None) != (raw is None) for s,raw in zip(scores,raw_scores)):
        raise ValueError('Raw and calibrated coverage must agree')
    pools = {}
    for row,score,raw in zip(rows,scores,raw_scores):
        key = (row['group_id'],row['product'])
        pools.setdefault(key, [])
        if score is not None:
            pools[key].append((-float(score),-float(raw),row['record_id']))
    return [{'group_id':group,'product':product,
             'ordered_record_ids':[item[2] for item in sorted(items)]}
            for (group,product),items in sorted(pools.items())]


def _reliability(rows, scores):
    pairs = [(float(score),row['label']) for row,score in zip(rows,scores) if score is not None]
    bins = []
    for i in range(10):
        selected = [(s,y) for s,y in pairs if min(int(s*10),9) == i]
        bins.append({'lower':i/10, 'upper':(i+1)/10, 'count':len(selected),
            'mean_probability':float(np.mean([s for s,_ in selected])) if selected else None,
            'observed_hit_rate':float(np.mean([y for _,y in selected])) if selected else None})
    return {'brier':float(np.mean([(s-y)**2 for s,y in pairs])) if pairs else None,
            'reliability_bins':bins, 'probability_metric_scope':'scored_candidates_only',
            'scored_candidate_count':len(pairs), 'abstained_candidate_count':len(rows)-len(pairs)}


def score_choices(rows, choices, scores, raw_scores=None):
    """Evaluate product pools first, then equally weight scaffold groups."""
    if any(type(r.get('label')) is not int or r['label'] not in (0,1) for r in rows):
        raise ValueError('Evaluation requires binary integer labels')
    if choices != make_choices(rows,scores,raw_scores):
        raise ValueError('Choices do not match frozen public scores')
    by_id = {r['record_id']:r for r in rows}
    per_product = []
    for choice in choices:
        pool = [r for r in rows if (r['group_id'],r['product']) == (choice['group_id'],choice['product'])]
        oracle = max(r['label'] for r in pool)
        ordered = choice['ordered_record_ids']
        per_product.append({**choice, 'oracle_hit':oracle, 'missing_choice':not ordered,
            **{f'top_{k}_regret':float(oracle-max(by_id[i]['label'] for i in ordered[:k])) if ordered else 1.0
               for k in (1,5)}})
    groups = sorted({r['group_id'] for r in rows})
    per_group = [{'group_id':group, 'product_count':sum(p['group_id']==group for p in per_product),
        **{f'top_{k}_regret':float(np.mean([p[f'top_{k}_regret'] for p in per_product if p['group_id']==group]))
           for k in (1,5)}} for group in groups]
    return {'candidate_count':len(rows), 'group_count':len(groups), 'product_count':len(per_product),
        'missing_choice_count':sum(p['missing_choice'] for p in per_product),
        **{f'top_{k}_group_macro_regret':float(np.mean([g[f'top_{k}_regret'] for g in per_group])) for k in (1,5)},
        **_reliability(rows,scores), 'per_group':per_group, 'per_product':per_product}


def bootstrap_difference(baseline, candidate):
    old = {r['group_id']:r['top_1_regret'] for r in baseline['per_group']}
    new = {r['group_id']:r['top_1_regret'] for r in candidate['per_group']}
    if not old or old.keys() != new.keys():
        raise ValueError('Paired bootstrap requires identical nonempty groups')
    differences = np.array([old[group]-new[group] for group in sorted(old)])
    rng = np.random.default_rng(SEED)
    samples = np.concatenate([rng.choice(differences,size=(1000,len(differences)),replace=True).mean(axis=1) for _ in range(10)])
    return {'mean_regret_reduction':float(differences.mean()), 'lower_95':float(np.quantile(samples,.025)),
        'upper_95':float(np.quantile(samples,.975)), 'replicates':10000, 'seed':SEED,
        'scope':'descriptive_scaffold_group_bootstrap_one_source',
        'per_group_difference':[{'group_id':g,'regret_reduction':float(old[g]-new[g])} for g in sorted(old)]}


def _metadata(rows, name, split_hash, source):
    return {'model_version':VERSION+'-'+name, 'training_component_smiles':{
        key:sorted({row[key] for row in rows}) for key in CN_ROLES},
        'substrate_similarity_threshold':0.2, 'endpoint':ENDPOINT,
        'source':source, 'training_row_count':len(rows), 'training_data_sha256':_hash(rows),
        'split_sha256':split_hash, 'selected_config':name,
        'evaluation_scope':'source_scoped_development_holdout', 'calibration_scope':'isolated_calibration_partition'}


def _fit(spec, rows, metadata):
    labels = [r['label'] for r in rows]
    if set(labels) != {0,1}:
        raise ValueError('Training requires both binary classes')
    if spec['kind'] == 'forest':
        cls = RandomForestClassifier if spec['algorithm']=='random_forest' else ExtraTreesClassifier
        estimator = cls(**spec['config']).fit(cn_features(_public(rows)),labels)
        return {'kind':'forest', 'name':spec['name'], 'model':export_classifier(estimator,metadata)}
    mean = float(np.mean(labels))
    keys = sorted({tuple(row[k] for k in ('catalyst','base','solvent')) for row in rows})
    conditions = [{'key':list(key), 'score':(sum(r['label'] for r in rows if tuple(r[k] for k in ('catalyst','base','solvent'))==key)+5*mean)/
        (sum(tuple(r[k] for k in ('catalyst','base','solvent'))==key for r in rows)+5)} for key in keys]
    return {'kind':spec['kind'], 'name':spec['name'], 'global_mean':mean, 'conditions':conditions,
            'metadata':metadata, 'calibration':None}


def _predict(artifact, rows):
    if artifact['kind'] == 'forest':
        model = CNConditionModel(artifact['model'])
        public = _public(rows)
        return [p for start in range(0,len(public),1000) for p in model.predict(public[start:start+1000])]
    conditions = {tuple(r['key']):r['score'] for r in artifact['conditions']}
    result = []
    for row in rows:
        raw = conditions.get(tuple(row[k] for k in ('catalyst','base','solvent')),artifact['global_mean']) if artifact['kind']=='condition' else artifact['global_mean']
        calibration = artifact['calibration']
        score = float(np.interp(raw,calibration['x'],calibration['y'])) if calibration else raw
        result.append({'id':row['record_id'], 'status':'scored', 'hit_score':score, 'raw_hit_score':raw,
                       'reason':None, 'evidence_status':'predicted'})
    return result


def _calibrate(artifact, rows):
    before = _predict(artifact,rows)
    pairs = [(p['raw_hit_score'],r['label']) for r,p in zip(rows,before) if p['status']=='scored']
    if not pairs:
        return artifact, {'status':'unavailable_no_scored_candidates', 'before':_reliability(rows,[p['hit_score'] for p in before]), 'after':None}
    x,y = zip(*pairs)
    fitted = IsotonicRegression(out_of_bounds='clip',y_min=0,y_max=1).fit(x,y)
    xx,yy = fitted.X_thresholds_.tolist(),fitted.y_thresholds_.tolist()
    if len(xx)==1:
        xx,yy = [0.0,1.0],[yy[0],yy[0]]
    calibration = {'kind':'isotonic','x':xx,'y':yy}
    updated = {**artifact, 'model':{**artifact['model'],'calibration':calibration}} if artifact['kind']=='forest' else {**artifact,'calibration':calibration}
    after = _predict(updated,rows)
    return updated, {'status':'fitted_constant' if len(set(y))==1 or len(set(x))==1 else 'fitted',
        'fitted_candidate_count':len(pairs), 'label_class_count':len(set(y)),
        'before':_reliability(rows,[p['hit_score'] for p in before]),
        'after':_reliability(rows,[p['hit_score'] for p in after]),
        'metric_scope':'calibration_fit_diagnostics_not_independent_evaluation'}


def _validate_split(rows, split):
    if set(split) != {'train','development','calibration','assessment'} or not all(split.values()):
        raise ValueError('All four nonempty partitions are required')
    indices = [i for items in split.values() for i in items]
    if any(type(i) is not int for i in indices) or sorted(indices) != list(range(len(rows))):
        raise ValueError('Partitions must cover each record exactly once')
    if len({r['record_id'] for r in rows}) != len(rows):
        raise ValueError('Record IDs must be unique')
    for key in ('group_id','product'):
        membership = {}
        for name,items in split.items():
            for i in items:
                value = rows[i][key]
                if value in membership and membership[value] != name:
                    raise ValueError('Group/product crosses partition boundaries')
                membership[value] = name


def _code_hashes():
    directory = Path(__file__).parent
    paths = [directory/name for name in ('cn_training.py','cn_model.py','cn_data.py')]
    paths.append(directory.parent.parent/'scripts'/'train_cn_condition_model.py')
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def _decision(artifact, public_rows):
    predictions = _predict(artifact,public_rows)
    if any('raw_hit_score' not in p or (p['status']=='scored' and p['raw_hit_score'] is None) for p in predictions):
        raise ValueError('Prediction contract requires raw_hit_score for every scored candidate')
    scores = [p['hit_score'] for p in predictions]
    raw = [p['raw_hit_score'] for p in predictions]
    return {'predictions':predictions, 'choices':make_choices(public_rows,scores,raw)}


def _coverage_diagnostics(rows, predictions, training):
    known = {key:{r[key] for r in training} for key in CN_ROLES}
    return {'candidate_count':len(rows),
        'scored_candidate_count':sum(p['status']=='scored' for p in predictions),
        'abstention_reason_counts':dict(sorted(Counter(str(p['reason']) for p in predictions if p['status']=='abstained').items())),
        'novel_component_candidate_counts':{key:sum(r[key] not in known[key] for r in rows) for key in CN_ROLES},
        'reference':'train_plus_development_components',
        'note':'Novelty is input-only; unseen products do not themselves trigger abstention.'}


def _assessment_probability_diagnostics(rows, predictions):
    raw = _reliability(rows,[p['raw_hit_score'] for p in predictions])
    calibrated = _reliability(rows,[p['hit_score'] for p in predictions])
    change = calibrated['brier']-raw['brier'] if raw['brier'] is not None else None
    return {'raw':raw, 'calibrated':calibrated, 'calibration_brier_change':change,
            'calibration_harmed_assessment_brier':bool(change > 0) if change is not None else None,
            'retuning_permitted':False}


def _evaluate(rows, decision):
    return score_choices(rows,decision['choices'],[p['hit_score'] for p in decision['predictions']],
                         [p['raw_hit_score'] for p in decision['predictions']])


def _selection_key(trial):
    metrics = trial['metrics']
    return (metrics['top_1_group_macro_regret'],metrics['top_5_group_macro_regret'],
            metrics['brier'] if metrics['brier'] is not None else float('inf'),trial['name'])


def _recipe(panel,memberships,split_hash,source_metadata,code_hashes):
    return {'version':VERSION, 'endpoint':ENDPOINT, 'seed':SEED, 'panel':panel,
        'split_record_ids':memberships, 'split_sha256':split_hash, 'source':source_metadata,
        'source_code_sha256':code_hashes, 'final_run_authorized':False,
        'selection_order':['group_macro_top1_binary_simple_regret','group_macro_top5_binary_simple_regret','scored_candidate_brier','configuration_name'],
        'choice_order':['calibrated_probability_descending','raw_probability_descending','record_id_ascending'],
        'missing_choice_regret':1, 'condition_mean_shrinkage':5,
        'eligibility':'Same source/structural candidate pools; forests retain domain abstention; means retain global fallback',
        'calibration':'Isolated isotonic after train+development refit; never selects configuration',
        'gate':{'minimum_regret_reduction':0.05,'bootstrap_lower_95_strictly_positive':True,'permits_production_promotion':False},
        'versions':{'python':platform.python_version(),**{name:importlib.metadata.version(name) for name in ('numpy','scikit-learn','rdkit')}}}


def _select(panel,subsets,split_hash,source_metadata):
    trials = []
    for spec in panel:
        tick = time.monotonic()
        fitted = _fit(spec,subsets['train'],_metadata(subsets['train'],spec['name'],split_hash,source_metadata))
        decision = _decision(fitted,subsets['development'])
        trials.append({'name':spec['name'],'arm':spec['arm'],'configuration':spec,
            'metrics':_evaluate(subsets['development'],decision),'runtime_seconds':time.monotonic()-tick})
    winners = {arm:min((t for t in trials if t['arm']==arm),key=_selection_key)['name'] for arm in ('baseline','candidate')}
    return trials,winners


def _refit(panel,winners,training,calibration_rows,split_hash,source_metadata):
    models,calibration = {},{}
    for arm,name in winners.items():
        spec = next(s for s in panel if s['name']==name)
        fitted = _fit(spec,training,_metadata(training,name,split_hash,source_metadata))
        models[arm],calibration[arm] = _calibrate(fitted,calibration_rows)
    return models,calibration


def run_cn_experiment(records, output_dir, *, split, source_metadata):
    """Execute a predeclared internal experiment. Explicit splits support synthetic tests.

    Production callers must use train_cn_model, which enforces the source scaffold split.
    Assessment labels are consumed only after model/decision files are committed.
    """
    rows = tuple(dict(r) for r in records)
    _validate_split(rows,split)
    output = Path(output_dir)
    output.mkdir(parents=True,exist_ok=False)
    started = time.monotonic()
    panel = candidate_panel()
    memberships = {name:[rows[i]['record_id'] for i in indices] for name,indices in split.items()}
    split_hash = _hash(memberships)
    code_hashes = _code_hashes()
    recipe = _recipe(panel,memberships,split_hash,source_metadata,code_hashes)
    _write(output/'recipe.json',recipe)
    subsets = {name:tuple(rows[i] for i in indices) for name,indices in split.items()}
    trials,winners = _select(panel,subsets,split_hash,source_metadata)
    _write(output/'development-selection.json',{'trials':trials,'selected':winners})
    training = subsets['train'] + subsets['development']
    models,calibration = _refit(panel,winners,training,subsets['calibration'],split_hash,source_metadata)
    model_hashes = {'candidate':_write(output/'candidate-model.json',models['candidate']['model']),
                    'baseline':_write(output/'baseline-model.json',models['baseline'])}
    public = tuple({key:r[key] for key in ('record_id','group_id',*CN_ROLES)} for r in subsets['assessment'])
    decisions = {arm:_decision(model,public) for arm,model in models.items()}
    decision_hash = _write(output/'assessment-decisions.json',{'public_candidates':public,'model_sha256':model_hashes,**decisions})
    metrics = {arm:_evaluate(subsets['assessment'],decision) for arm,decision in decisions.items()}
    difference = bootstrap_difference(metrics['baseline'],metrics['candidate'])
    passed = difference['mean_regret_reduction'] >= .05 and difference['lower_95'] > 0
    report = {'scope':'source_scoped_development_holdout','endpoint':ENDPOINT,'final_run_authorized':False,
        'existing_default_modified':False,'candidate_selected':winners['candidate'],'baseline_selected':winners['baseline'],
        'development_trials':trials,'assessment':metrics,'calibration':calibration,'paired_comparison':difference,
        'development_candidate_gate_passed':bool(passed),'disposition':'experimental_candidate_only' if passed else 'retain_existing_default_negative_or_inconclusive_result',
        'training_record_ids':[r['record_id'] for r in training],
        'calibration_record_ids':memberships['calibration'],'assessment_record_ids':memberships['assessment'],
        'assessment_probability_diagnostics':{arm:_assessment_probability_diagnostics(subsets['assessment'],decision['predictions']) for arm,decision in decisions.items()},
        'coverage_diagnostics':{arm:_coverage_diagnostics(public,decision['predictions'],training) for arm,decision in decisions.items()},
        'assessment_decisions_sha256':decision_hash,'model_sha256':model_hashes,'source':source_metadata,
        'limitations':['One publication only; scaffold bootstrap is descriptive, not source-transfer evidence.',
                      'CAD screen-hit endpoint is not isolated yield or general reaction feasibility.',
                      'No sealed final/Q1 promotion or physical experimental validation.'],
        'runtime_seconds':time.monotonic()-started}
    if _code_hashes() != code_hashes:
        _write(output/'invalidated.json',{'reason':'source_code_changed_during_experiment'})
        raise RuntimeError('Source code changed during experiment; result invalidated')
    _write(output/'evaluation.json',report)
    return report


def train_cn_model(dataset, output_dir, *, expected_sha256):
    """Production entry: verified source loader and mandatory scaffold allocation."""
    from .cn_data import load_cn_records, frozen_split
    records,audit = load_cn_records(dataset,expected_sha256)
    return run_cn_experiment(records,output_dir,split=frozen_split(records),source_metadata=audit)
