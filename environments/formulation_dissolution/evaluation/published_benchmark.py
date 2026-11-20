"""Descriptive benchmark of published ranolazine summary curves, not Ajanta QC.

Leave-one-formulation-out uses only other published examples in the same
pH 6.8 method. The within-curve kinetic fit is reconstructed separately.
Neither is validated formulation optimization or individual-vessel prediction.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

GROUP='patent_201741007784_ph68'


def metrics(actual, predicted):
    """MAE/RMSE in percentage points, conditional on aligned original times."""
    if len(actual)!=len(predicted) or not actual: raise ValueError('aligned nonempty points required')
    err=[a-p for a,p in zip(actual,predicted)]
    return {'mae_pp':mean(abs(e) for e in err),'rmse_pp':math.sqrt(mean(e*e for e in err))}


def _profiles(rows):
    grouped={}
    for r in rows:
        if r['method_id']!=GROUP or r['release_value'] is None:continue
        grouped.setdefault(r['profile_id'],{})[r['derived_time_min']]=r['release_value']
    return grouped


def acid_reference_track(rows, source_check):
    """Separate, source-verified, same-paper HCl SR summary comparison."""
    if not source_check or source_check.get('status')!='table_4_transcription_sequence_verified':
        return {'status':'not_evaluated','reason':'primary Table 4 sequence not verified'}
    ids=('US6525057_SR_A','US6525057_SR_B','US6525057_SR_C')
    pool={pid:{r['derived_time_min']:r['release_value'] for r in rows
               if r['profile_id']==pid and r['release_value'] is not None} for pid in ids}
    if len({tuple(sorted(curve)) for curve in pool.values()})!=1:
        raise ValueError('acid profiles do not share a measured time grid')
    folds=[]
    for pid in ids:
        times=sorted(pool[pid]); others=[pool[p] for p in ids if p!=pid]
        folds.append({'profile_id':pid,'train_profile_ids':[p for p in ids if p!=pid],
            **metrics([pool[pid][t] for t in times],[mean(p[t] for p in others) for t in times])})
    return {'status':'evaluated_descriptive_only','method_id':'patent_US6525057_hcl',
        'source_id':'US6525057B2','source_sha256':source_check['sha256'],
        'n_summary_formulations':len(ids),'n_individual_vessels':None,
        'macro_profile_mae_pp':mean(x['mae_pp'] for x in folds),
        'macro_profile_rmse_pp':mean(x['rmse_pp'] for x in folds),
        'folds':folds,'limitations':['patent formulation doses, speed, temperature and individual variability not established',
            'same-study related examples; not Ajanta product performance','US6525057_IR excluded (different dosage form)']}


def first_order_fit(points):
    """Observed-curve reconstruction; a fitted parameter cannot be used as blind prediction."""
    grid=[0]+[0.00001*(1.04**i) for i in range(200)]
    times=sorted(t for t in points if t>0)
    k=min(grid,key=lambda rate:sum((points[t]-100*(-math.expm1(-rate*t)))**2 for t in times))
    return k,{t:0 if t==0 else 100*(-math.expm1(-k*t)) for t in points}


def run(input_path, out):
    """Write frozen input hash, observations, predictions and method-stratified scores."""
    path=Path(input_path); raw=path.read_bytes(); rows=json.loads(raw)
    pool=_profiles(rows)
    example_ids=sorted(pid for pid in pool if pid.startswith('201741007784_Example_'))
    reference=pool['201741007784_Ranexa_1g']
    if len(example_ids)!=6 or len(pool)!=7 or any(set(pool[pid])!=set(reference) for pid in example_ids):
        raise ValueError('expected six complete examples and one separate reference on same time grid')
    scores=[]; observations=[]; fitting=[]
    for pid in example_ids:
        others=[pool[other] for other in example_ids if other!=pid]
        actual=pool[pid];times=sorted(t for t in actual if t>0)
        predicted=[mean(p[t] for p in others) for t in times]
        row={'profile_id':pid,'source_id':'201741007784','method_id':GROUP,'model':'leave_one_example_out_mean',
             'train_profile_ids':[p for p in example_ids if p!=pid],**metrics([actual[t] for t in times],predicted)}
        scores.append(row)
        k,fit=first_order_fit(actual)
        fitting.append({'profile_id':pid,'model':'first_order_fit_to_same_observed_curve',
                        'fit_rate_per_min':k,**metrics([actual[t] for t in times],[fit[t] for t in times]),
                        'evidence_label':'derived_reconstruction_not_blind_prediction'})
        for t,p in zip(times,predicted):
            observations.append({'profile_id':pid,'method_id':GROUP,'time_min':t,'observed_release_percent':actual[t],
                 'prediction_release_percent':p,'evidence_label_observed':'literature_reported',
                 'evidence_label_prediction':'derived_heldout_summary_mean','source_id':'201741007784',
                 'source_locator':next(r['source_locator'] for r in rows if r['profile_id']==pid)})
    # Contextual reference error: Ranexa withheld and not part of example train/test ranking.
    times=sorted(t for t in reference if t>0);context_pred=[mean(pool[p][t] for p in example_ids) for t in times]
    reference_context={'profile_id':'201741007784_Ranexa_1g','comparison':'contextual_reference_vs_example_mean_NOT_QC',
         **metrics([reference[t] for t in times],context_pred)}
    root=Path(out);root.mkdir(parents=True,exist_ok=True)
    with (root/'published_profile_predictions.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,observations[0].keys());w.writeheader();w.writerows(observations)
    with (root/'published_profile_scores.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,scores[0].keys());w.writeheader();w.writerows(scores)
    source_path=Path('data/raw/US6525057B2_source_check.json')
    source_check=json.loads(source_path.read_text()) if source_path.is_file() else None
    scenario_path=path.parent/'prior_scenario_reference.json'
    scenario_check={'status':'not_evaluated','reason':'previous scenario artifact unavailable'}
    if scenario_path.is_file():
        scenario=json.loads(scenario_path.read_text())
        if scenario.get('status')=='exploratory_assumption_conditional_NOT_product_prediction':
            check=scenario['artifact']['literature_endpoint_sanity_check']
            endpoint=next(r['release_value'] for r in rows if r['profile_id']=='zenodo_F8_endpoint' and r['time_value']==24)
            scenario_check={'status':'exploratory_mismatch_only','source_id':'zenodo_1170150','endpoint_percent':endpoint,
                'simulated_median_percent_by_model':check['simulated_24h_median_percent_by_model'],
                'absolute_difference_pp_by_model':{key:abs(endpoint-value) for key,value in check['simulated_24h_median_percent_by_model'].items()},
                'scenario_sha256':scenario['sha256'],'uncertainty_calibration':'not_established',
                'warning':'previously inspected 500 mg endpoint; not independent test or Ajanta 1000 mg prediction'}
    result={'status':'evaluated_descriptive_only','track':'published_summary_curves','source':'201741007784 transcribed tables in supplied specification',
            'input_path':str(path),'input_sha256':hashlib.sha256(raw).hexdigest(),
            'train_test':'leave one complete example out; no row-level time split; same patent source shared across train/test',
            'sample_size_formulations':len(example_ids),'sample_size_individual_vessels':None,
            'macro_profile_mae_pp':mean(s['mae_pp'] for s in scores),'macro_profile_rmse_pp':mean(s['rmse_pp'] for s in scores),
            'reference_context':reference_context,'scores':scores,'reconstruction_only':fitting,
            'verified_primary_acid_track':acid_reference_track(rows,source_check),
            'prior_500mg_scenario_sanity_check':scenario_check,
            'arms':{'A':'leave_one_example_out_mean','B':'unavailable_no_approved_model','C':'local_specialist_audit_no_numeric_predictor','D':'not_trained'},
            'specification_attainment':'not_evaluated','ajanta_lot_improvement':'not_evaluated',
            'limitations':['source tables for 201741007784 inaccessible via QuickCompany (403); numbers transcribed from supplied specification, not independently rechecked',
                'patent examples share source and likely formulation lineage: results are not independent-source generalization',
                'raw vessel units and variability unavailable; example dose/composition linkage not independently verified',
                'reference manufacturer is not recalled Ajanta product; pH 6.8 method is not Ajanta approved method',
                'kinetic fitting to evaluated curve is reconstruction only; not included in predictive leaderboard'],
            'artifacts':[str(root/'published_profile_predictions.csv'),str(root/'published_profile_scores.csv'),str(root/'published_benchmark.json')]}
    from evaluation.verifier import verify_published
    result['verifier_findings']=verify_published(result,root/'published_profile_predictions.csv',rows)
    if result['verifier_findings']: result['status']='verification_failed'
    (root/'published_benchmark.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    return result
