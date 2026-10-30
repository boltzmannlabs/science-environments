"""Six dissolution fits and a strictly synthetic grouped holdout demonstration.

Published summary curves are reconstructed, NEVER used as Ajanta lot data. The
synthetic batch fixture is generated here from declared arbitrary parameters;
its holdout metrics cannot establish ranolazine prediction performance.
"""
import argparse
import csv
import hashlib
import json
import math
import random
import warnings
from collections import defaultdict
from pathlib import Path
from statistics import mean

MODELS=('weibull','first_order','zero_order','higuchi','korsmeyer_peppas','hixson_crowell')
TIMES=(0,30,60,120,240,480,720,1440)  # minutes; SYNTHETIC fixture only
SEED=31415
FORMULATIONS={'F1':400.0,'F3':450.0,'F5':500.0,'F8':550.0}  # invented Weibull time scales in minutes
ALPHA=0.85  # invented simulation shape; not fitted to ranolazine


def clean(value):
    """Represent nonfinite failure metrics as null, never as perfect scores."""
    return float(value) if value is not None and math.isfinite(float(value)) else None


def fitted_curve(t,q,label,models=MODELS):
    """Fit OpenPKFlow v2.9.0 to one training/summary curve, retaining failures."""
    if len(t)!=len(q) or len(t)<5 or len(set(t))!=len(t) or any(b<=a for a,b in zip(t,t[1:])):
        raise ValueError('aligned unique increasing times required')
    if not all(math.isfinite(float(x)) for x in (*t,*q)):raise ValueError('nonfinite inputs')
    if any(x < 0 for x in (*t,*q)):raise ValueError('negative time or cumulative release')
    import openpkflow
    from openpkflow.dissolution.models import fit_dissolution_models
    if openpkflow.__version__!='2.9.0': raise ValueError('OpenPKFlow API pinned to 2.9.0')
    if not math.isclose(t[0],0):
        # Other published reports may begin after zero: valid but not comparable without method.
        pass
    fits={};failures=[]
    for model in models:
        if model=='korsmeyer_peppas':
            # Do not fit power-law to near-complete release. Later evaluation is extrapolation.
            available=[i for i,v in enumerate(q) if v<=60]
            if len(available)<4:
                failures.append({'model':model,'reason':'fewer_than_four_early_points_below_60_percent'})
                continue
            ts=[t[i] for i in available];ys=[q[i] for i in available]
        else:ts,ys=t,q
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            try: fitted=fit_dissolution_models(ts,ys,label,models=[model]).fits[0]
            except (ValueError,RuntimeError,FloatingPointError,OverflowError) as exc:
                failures.append({'model':model,'reason':type(exc).__name__});continue
        if not fitted.converged or not all(math.isfinite(x) for x in fitted.params.values()):
            failures.append({'model':model,'reason':'nonconverged_or_nonfinite'});continue
        fits[model]={'fit':fitted,'trained_on_percent_le_60_only':model=='korsmeyer_peppas',
            'fit_points':len(ts),'aicc_in_sample':clean(fitted.aicc),
            'params':fitted.params,'warnings':[str(x.message) for x in caught]}
    return fits,failures


def synthetic_batches():
    """Deterministic labelled simulation; split by batch BEFORE fitting."""
    rng=random.Random(SEED); batches=[]
    for label,scale in FORMULATIONS.items():
        for idx in range(6):
            batch=f'SYN_{label}_B{idx}'
            # Explicitly assumed batch effect and observation noise (not lab variability).
            time_scale=scale*math.exp(rng.gauss(0,0.08))
            vals=[0.0 if t==0 else max(0.0,min(100.0,100*(1-math.exp(-(t/time_scale)**ALPHA))+rng.gauss(0,1.2))) for t in TIMES]
            batches.append({'batch_id':batch,'formulation_id':label,'split':('train' if idx<3 else 'validation' if idx==3 else 'test'),
                            'time_min':list(TIMES),'release_percent':vals,'data_origin':'synthetic',
                            'evidence_label':'assumed_fixture_not_measured','method_id':'synthetic_fixture_only'})
    return batches


def scores(actual,pred):
    err=[p-y for y,p in zip(actual,pred,strict=True)]
    return {'mae_pp':mean(abs(x) for x in err),'rmse_pp':math.sqrt(mean(x*x for x in err)),
            'bias_pp':mean(err)}


def quantile(seq,p):
    arr=sorted(seq); pos=(len(arr)-1)*p;low=int(pos)
    return arr[low]+(arr[min(low+1,len(arr)-1)]-arr[low])*(pos-low)


def evaluate_synthetic():
    """Six train-only fits per formulation; validation intervals and frozen test."""
    from openpkflow.dissolution.similarity import f2
    batches=synthetic_batches()
    by_label=defaultdict(list)
    for row in batches:by_label[row['formulation_id']].append(row)
    fits={};failures=[]; per=[];point_rows=[]; calibration=defaultdict(list);val_scores=defaultdict(list)
    for label,items in sorted(by_label.items()):
        train=[x for x in items if x['split']=='train']; val=[x for x in items if x['split']=='validation'];test=[x for x in items if x['split']=='test']
        if len(train)!=3 or len(val)!=1 or len(test)!=2:raise ValueError('batch split broken')
        avg=[mean(row['release_percent'][i] for row in train) for i in range(len(TIMES))]
        model_fits,errors=fitted_curve(list(TIMES),avg,label)
        failures.extend([{'formulation_id':label,**e} for e in errors])
        fits[label]={name:{key:v for key,v in meta.items() if key!='fit'} for name,meta in model_fits.items()}
        for model,meta in model_fits.items():
            prediction=[float(x) for x in meta['fit'].predict(TIMES)]
            for batch in val:
                # One grouped calibration statistic per independent validation batch.
                calibration[model].append(max(abs(a-b) for a,b in zip(prediction[1:],batch['release_percent'][1:])))
                val_scores[model].append({'batch_id':batch['batch_id'],**scores(batch['release_percent'][1:],prediction[1:])})
            for batch in test:
                actual=batch['release_percent']; metric=scores(actual[1:],prediction[1:])
                # Arithmetic f2 only; never use the IR regulatory cutoff on an ER product.
                try: math_f2=f2(actual[1:],prediction[1:],method='all_points')
                except ValueError:math_f2=None
                per.append({'model':model,'formulation_id':label,'batch_id':batch['batch_id'],'train_batch_ids':[r['batch_id'] for r in train],
                    'test_data_origin':'synthetic','f2_math_only_not_regulatory':math_f2,**metric})
                for t,y,p in zip(TIMES,actual,prediction):
                    point_rows.append({'model':model,'formulation_id':label,'batch_id':batch['batch_id'],
                       'time_min':t,'actual_percent_synthetic':y,'prediction_percent':p,'residual_prediction_minus_actual_pp':p-y})
    summary={}
    for model in MODELS:
        profile=[x for x in per if x['model']==model]
        if not profile:
            summary[model]={'status':'not_evaluated','reason':'no converged train fits'};continue
        radius=quantile(calibration[model],0.9) if calibration[model] else None
        points=[x for x in point_rows if x['model']==model and x['time_min']>0]
        summary[model]={'status':'synthetic_fixture_only','eligible_test_batches':len(profile),
            'macro_mae_pp':mean(x['mae_pp'] for x in profile),'macro_rmse_pp':mean(x['rmse_pp'] for x in profile),
            'macro_bias_pp':mean(x['bias_pp'] for x in profile),
            'residual_bias_by_time_min':{str(t):mean(x['residual_prediction_minus_actual_pp'] for x in points if x['time_min']==t) for t in TIMES[1:]},
            'nominal_90pct_interval_halfwidth_pp_from_four_validation_batches':radius,
            'test_interval_coverage':mean(abs(x['residual_prediction_minus_actual_pp'])<=radius for x in points) if radius is not None else None,
            'test_interval_width_pp':2*radius if radius is not None else None,
            'interval_calibration':'not_established_four_validation_batches_only',
            'mean_f2_math_only_not_regulatory':mean(x['f2_math_only_not_regulatory'] for x in profile if x['f2_math_only_not_regulatory'] is not None) if any(x['f2_math_only_not_regulatory'] is not None for x in profile) else None,
            'f2_evaluable_batches':sum(x['f2_math_only_not_regulatory'] is not None for x in profile),
            'regulatory_f2':'not_evaluated_unapproved_method_and_insufficient_unit_variance'}
    validation_ranking=sorted((m for m in MODELS if val_scores[m]),key=lambda m:(mean(x['rmse_pp'] for x in val_scores[m]),m))
    return {'status':'synthetic_only_not_ranolazine_validation','seed':SEED,'release_generator':{'law':'Weibull','alpha_ASSUMED':ALPHA,
       'time_scale_min_by_research_recipe_ASSUMED':FORMULATIONS,'batch_lognormal_sd_ASSUMED':0.08,'point_noise_sd_pp_ASSUMED':1.2,
       'clipping_at_0_and_100_applies_ONLY_to_synthetic_generation':True},
       'method_id':'synthetic_fixture_only','time_min':list(TIMES),
       'scored_time_min':list(TIMES[1:]),'heldout_metric_excludes_shared_zero':True,
       'split_policy':'per-formulation independent batch IDs 0-2 train, 3 validation, 4-5 final test; no test-label fitting',
       'batch_counts':{'train':sum(x['split']=='train' for x in batches),'validation':sum(x['split']=='validation' for x in batches),'test':sum(x['split']=='test' for x in batches)},
       'batch_split_manifest':{split:sorted(x['batch_id'] for x in batches if x['split']==split) for split in ('train','validation','test')},
       'selected_by_synthetic_validation_macro_RMSE_NOT_product_reliability':validation_ranking[0] if validation_ranking else None,
       'validation_model_ranking':validation_ranking,
       'validation_metrics':{name:{'batch_count':len(val_scores[name]),'macro_rmse_pp':mean(x['rmse_pp'] for x in val_scores[name])} for name in MODELS if val_scores[name]},
       'models':summary,'fit_metadata_train_only':fits,'fit_failure_ledger':failures,
       'per_test_batch_scores':per,'per_test_timepoint_residuals':point_rows,
       'uncertainty_limitation':'one calibration batch per formulation, no independent calibration established',
       'mixture_model':'not_trained_no_source_verified_measured_composition_to_profile_dataset',
       'scientific_performance':'not_evaluated'}


def evaluate_literature(path):
    """Fit existing source-labelled published summaries; never holdout predictions."""
    rows=json.loads(Path(path).read_text());grouped=defaultdict(list)
    for row in rows:
        if row.get('evidence_label')=='literature_reported' and row.get('data_origin')=='experimental' and row.get('method_id') and row.get('release_value') is not None:
            if row['profile_id']=='US6525057_IR':continue  # IR not part of ER comparison
            grouped[row['profile_id']].append(row)
    entries=[];excluded=[]
    for pid,profile in sorted(grouped.items()):
        profile.sort(key=lambda r:r['derived_time_min'])
        t=[x['derived_time_min'] for x in profile];q=[x['release_value'] for x in profile]
        if len(t)<5:excluded.append({'profile_id':pid,'reason':'insufficient_timepoints'});continue
        fits,failures=fitted_curve(t,q,pid)
        method=profile[0]['method_id']
        for name,meta in fits.items():
            pred=[float(x) for x in meta['fit'].predict(t)]
            entries.append({'profile_id':pid,'method_id':method,'source_id':profile[0]['source_id'],
                'model':name,'model_params':meta['params'],'trained_points':meta['fit_points'],
                'fit_to_same_curve':True,'kp_extrapolation_warning':meta['trained_on_percent_le_60_only'],
                'aicc_fitted_segment':meta['aicc_in_sample'],**scores(q,pred),
                'profile_has_over_100_percent':any(x>100 for x in q),'raw_unit_variability':'unavailable'})
        excluded.extend({'profile_id':pid,**e} for e in failures)
    by_method=defaultdict(list)
    for item in entries:by_method[item['method_id']].append(item)
    method_summaries={}
    for method,items in by_method.items():
        forms={}
        for model in MODELS:
            subset=[x for x in items if x['model']==model]
            if subset:
                forms[model]={'converged_profiles':len(subset),'in_sample_macro_mae_pp':mean(x['mae_pp'] for x in subset),
                    'in_sample_macro_rmse_pp':mean(x['rmse_pp'] for x in subset),
                    'warning':'power-law fitted only <=60%; full-curve extrapolation, AICc not comparable' if model=='korsmeyer_peppas' else None}
        best=[]
        for pid in sorted({x['profile_id'] for x in items}):
            comparable=[x for x in items if x['profile_id']==pid and x['model']!='korsmeyer_peppas' and x['aicc_fitted_segment'] is not None]
            if comparable:best.append({'profile_id':pid,'lowest_full_curve_AICc_model':min(comparable,key=lambda x:x['aicc_fitted_segment'])['model']})
        method_summaries[method]={'model_in_sample_summary':forms,'best_full_curve_AICc_per_profile':best,
           'interpretation':'same-curve fit quality only; not predictive holdout or mechanism proof'}
    return {'status':'published_summary_reconstruction_ONLY','source_path':str(path),
       'source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
       'source_groups':{'patent_201741007784_ph68':'pH6.8 100rpm reference and examples; transcription not independently checked',
                        'patent_US6525057_hcl':'0.1M HCl, speed/strengths unknown; primary patent Table 4 verified'},
       'fits':entries,'exclusion_failure_ledger':excluded,'method_stratified_in_sample':method_summaries,
       'predictive_holdout_performance':'not_evaluated',
       'note':'AICc of KP fit to early segment not comparable with full-curve AICc; do not pool pH6.8 and HCl model ranks'}


def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader()
        for r in rows:writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()})


def plots(out,synthetic):
    """Save labelled synthetic test overlay and time-stratified signed residuals."""
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    points=synthetic['per_test_timepoint_residuals']
    fig,ax=plt.subplots(figsize=(8,5))
    for model in MODELS:
        subset=[r for r in points if r['model']==model]
        if subset:
            ax.plot(TIMES[1:],[mean(r['residual_prediction_minus_actual_pp'] for r in subset if r['time_min']==t) for t in TIMES[1:]],label=model)
    ax.axhline(0,color='black',linewidth=0.7)
    ax.set(xlabel='Synthetic fixture time (min)',ylabel='Mean prediction minus synthetic test (percentage points)',
           title='SYNTHETIC ONLY: signed held-out-batch residuals')
    ax.legend(fontsize=7);fig.tight_layout();fig.savefig(out/'synthetic_test_residuals.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    example=[r for r in points if r['formulation_id']=='F8' and r['batch_id']=='SYN_F8_B4']
    actual=[next(r for r in example if r['model']=='weibull' and r['time_min']==t)['actual_percent_synthetic'] for t in TIMES]
    ax.plot(TIMES,actual,'ko-',label='synthetic held-out batch F8/B4')
    for model in MODELS:
        subset=[r for r in example if r['model']==model]
        if subset:
            ax.plot(TIMES,[next(r for r in subset if r['time_min']==t)['prediction_percent'] for t in TIMES],label=model)
    ax.set(xlabel='Synthetic fixture time (min)',ylabel='Release (%)',
           title='SYNTHETIC ONLY: excluded batch vs training-only fits')
    ax.legend(fontsize=7);fig.tight_layout();fig.savefig(out/'synthetic_test_overlay.png');plt.close(fig)


def main():
    p=argparse.ArgumentParser();p.add_argument('--literature',type=Path,default=Path('data/processed/literature_profiles.json'))
    p.add_argument('--out',type=Path,default=Path('data/processed/six_model_pipeline'))
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    published=evaluate_literature(a.literature);synthetic=evaluate_synthetic()
    records={'status':'software_demo_and_published_reconstruction_not_product_validation',
       'published':published,'synthetic':synthetic,
       'mechanistic_model':{'status':'not_evaluated','reason':'no source-verified product solubility, particle-size distribution, solid-state, matrix transport, method and raw unit profiles'},
       'PTCalc':{'status':'tool_unavailable','reason':'no installed/documented PTCalc contract or approved adapter in current session'},
       'mixture_model':{'status':'not_trained','reason':'no eligible measured ranolazine tablet profiles with linked formula and method'},
       'approved_ajanta_lot_QC':'not_evaluated'}
    (a.out/'six_model_results.json').write_text(json.dumps(records,indent=2,allow_nan=False))
    write_csv(a.out/'published_in_sample_fits.csv',published['fits'])
    write_csv(a.out/'synthetic_test_batch_scores.csv',synthetic['per_test_batch_scores'])
    write_csv(a.out/'synthetic_test_timepoint_residuals.csv',synthetic['per_test_timepoint_residuals'])
    (a.out/'synthetic_batch_fixture.json').write_text(json.dumps(synthetic_batches(),indent=2))
    (a.out/'synthetic_split_manifest.json').write_text(json.dumps(synthetic['batch_split_manifest'],indent=2))
    plots(a.out,synthetic)
    print(json.dumps({'status':records['status'],'published_fit_count':len(published['fits']),
        'synthetic_batch_counts':synthetic['batch_counts'],
        'synthetic_models':{k:{m:v.get(m) for m in ('status','macro_mae_pp','macro_rmse_pp','macro_bias_pp','test_interval_coverage','f2_evaluable_batches')} for k,v in synthetic['models'].items()},
        'mechanistic':records['mechanistic_model']['status'],'PTCalc':records['PTCalc']['status'],
        'out':str(a.out/'six_model_results.json')},indent=2))

if __name__=='__main__':main()
