"""Pre-specified improvements and evaluation; no new laboratory observations."""
from pathlib import Path
import json,hashlib,itertools,math,copy
from decimal import Decimal as D
import numpy as np,pandas as pd
from scipy.optimize import least_squares
from scipy.special import expit
from scipy.spatial.distance import pdist


def run_task01(input_dir: Path, output_dir: Path):
    """Run Task - 01 offline; write computed diagnostics, never lab results.

    Inputs are published comparator means and design-only formulations.
    Held-out timepoints do not establish external formulation/batch validity.
    """
    BASE=Path(input_dir).resolve()
    ROOT=Path(output_dir).resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    profiles=json.loads((BASE/'literature_profiles.json').read_text())
    original=json.loads((BASE/'candidates.json').read_text())
    # Freeze choices before running evaluation. No data cleaning changes are selected by error.
    CONFIGS=['mean_baseline','linear_interpolation_baseline','first_order_free','Weibull_free','logistic_free','first_order_cap100','Weibull_cap100','logistic_cap100','first_order_fixed100','Weibull_fixed100','origin_logistic_cap100']
    plan={'status':'COMPUTATIONAL_EVALUATION_AND_EXPERIMENTAL_DESIGN_ONLY','primary_metric':'RMSE on held-out published mean timepoints, percentage points','secondary_metrics':['heldout_MAE','heldout_MAPE','forward_30min_RMSE','in_sample_RMSE','fitted_asymptote_gt100','estimated_release_at_t0'],'configurations':CONFIGS,'splits':['in_sample_all5','leave_one_timepoint_out_each_of5','forward_train5_10_15_20_predict30'],'deduplication':'same source formulation identity plus identical times/means: keep first provenance, record aliases','no_claims':['external_formulation_validation','batch_holdout_validation','candidate_recipe_prediction','calibrated_prediction_intervals','experimental_improvement'],'weighting':'unweighted; source SD is not a substitute for available raw unit observations and covariance','bounds':'free asymptotes 1..150; capped 1..100; fixed100; all rate/shape constraints recorded in code','optimization':'deterministic three-start bounded least_squares, best finite converged SSR; tol1e-9 max_nfev2000','model_selection':'no candidate chosen as efficacy-best; lowest observed diagnostic error is exploratory, requires external confirmation','new_early_samples_min':[1,2,3],'new_sample_schedule_min':[1,2,3,5,10,15,20,30,45,60]}
    (ROOT/'evaluation_plan.json').write_text(json.dumps(plan,indent=2))
    unique=[];seen={};aliases=[]
    for p in profiles:
     key=(p['source'],p['source_formulation_id'],tuple(p['time_min']),tuple(p['reported_mean_percent']))
     if key in seen:aliases.append({'kept':seen[key],'excluded_duplicate':p['id'],'reason':'same published reference profile; not independent evidence'})
     else:seen[key]=p['id'];unique.append(p)
    assert len(unique)==15 and len(aliases)==1
    (ROOT/'duplicate_reference_audit.json').write_text(json.dumps(aliases,indent=2))

    def specification(name):
     capped=name.endswith('cap100');fixed=name.endswith('fixed100');amax=100 if capped else 150
     if name.startswith('first_order'):
      if fixed:return lambda t,z:100*(-np.expm1(-z[0]*t)),[1e-5],[5],[[.1],[.2],[.4]]
      return lambda t,z:z[0]*(-np.expm1(-z[1]*t)),[1,1e-5],[amax,5],[[min(99,amax),.2],[min(90,amax),.1],[min(105,amax-1e-5),.4]]
     if name.startswith('Weibull'):
      if fixed:return lambda t,z:100*(-np.expm1(-(t/z[0])**z[1])),[.05,.05],[200,5],[[4,.7],[6,1],[10,1.5]]
      return lambda t,z:z[0]*(-np.expm1(-(t/z[1])**z[2])),[1,.05,.05],[amax,200,5],[[min(99,amax),4,.7],[min(90,amax),6,1],[min(105,amax-1e-5),10,1.5]]
     if name=='origin_logistic_cap100':
      def fn(t,z):
       s0=expit(-z[1]*z[2]);return z[0]*(expit(z[1]*(t-z[2]))-s0)/max(1-s0,1e-12)
      return fn,[1,.001,-30],[100,5,40],[[99,.2,0],[99,.1,5],[90,.4,3]]
     if name.startswith('logistic'):
      return lambda t,z:z[0]*expit(z[1]*(t-z[2])),[1,.001,-30],[amax,5,40],[[min(99,amax),.2,1],[min(90,amax),.1,5],[min(105,amax-1e-5),.4,3]]
     raise ValueError(name)

    def fit_predict(name,t,y,target):
     if name=='mean_baseline':return np.full(len(target),np.mean(y)),{'fit':'mean_only','parameter_count':1,'asymptote':None,'t0':None,'parameters':[float(np.mean(y))]}
     if name=='linear_interpolation_baseline':return np.interp(target,t,y),{'fit':'piecewise_linear_nearest_endpoint_extrapolation','parameter_count':None,'asymptote':None,'t0':None,'parameters':None}
     fn,lo,hi,starts=specification(name);best=None;attempts=[]
     for seed in starts:
      r=least_squares(lambda z:fn(t,z)-y,seed,bounds=(lo,hi),ftol=1e-9,xtol=1e-9,gtol=1e-9,max_nfev=2000)
      ss=float(np.sum((fn(t,r.x)-y)**2));attempts.append({'success':bool(r.success),'ss':ss,'nfev':r.nfev})
      if r.success and np.isfinite(ss) and (best is None or ss<best[0]):best=(ss,r.x,r)
     if best is None:raise RuntimeError('No successful optimizer start '+name)
     ss,z,r=best;pred=fn(np.array(target),z)
     asym=100 if name.endswith('fixed100') else float(z[0])
     return pred,{'parameters':z.tolist(),'parameter_count':len(z),'asymptote':asym,'t0':float(fn(np.array([0.]),z)[0]),'training_SS':ss,'starts':attempts,'successful':True}

    errors=[];allfit=[]
    for pi,p in enumerate(unique):
     t=np.array(p['time_min']);y=np.array(p['reported_mean_percent'])
     for name in CONFIGS:
      splits=[('in_sample_all5',np.arange(5),np.arange(5))]
      splits += [('LOTO',np.delete(np.arange(5),j),np.array([j])) for j in range(5)]
      splits += [('forward30',np.arange(4),np.array([4]))]
      for split,train,test in splits:
       pred,info=fit_predict(name,t[train],y[train],t[test]);allfit.append({'profile_id':p['id'],'model':name,'split':split,'train_times_min':t[train].tolist(),'test_times_min':t[test].tolist(),**info})
       for j,value in zip(test,pred):
        error=float(value-y[j]);errors.append({'profile_id':p['id'],'model':name,'split':split,'time_min':float(t[j]),'literature_percent':float(y[j]),'fitted_or_heldout_percent':float(value),'signed_error_pp':error,'absolute_error_pp':abs(error),'relative_error_percent':100*error/y[j],'asymptote_percent':info['asymptote'],'estimated_t0_percent':info['t0'],'scope':'same_published_curve_timepoint_diagnostic_not_new_formulation_prediction'})
     print('Evaluated',pi+1,'/',len(unique),p['id'],flush=True)
    frame=pd.DataFrame(errors);frame.to_csv(ROOT/'all_evaluation_predictions.csv',index=False)
    (ROOT/'all_fit_parameters.json').write_text(json.dumps(allfit,indent=2))
    summary=[]
    for (model,split),g in frame.groupby(['model','split'],sort=False):
     summary.append({'model':model,'split':split,'profile_count':g.profile_id.nunique(),'test_points':len(g),'RMSE_pp':float(np.sqrt(np.mean(g.signed_error_pp**2))),'MAE_pp':float(g.absolute_error_pp.mean()),'MAPE_percent':float(np.mean(abs(g.relative_error_percent))),'mean_bias_pp':float(g.signed_error_pp.mean()),'max_absolute_error_pp':float(g.absolute_error_pp.max())})
    summarydf=pd.DataFrame(summary);summarydf.to_csv(ROOT/'model_comparison.csv',index=False)
    (ROOT/'model_comparison.json').write_text(json.dumps(summary,indent=2))
    per=[]
    for (model,split,pid),g in frame.groupby(['model','split','profile_id']):per.append({'model':model,'split':split,'profile_id':pid,'RMSE_pp':float(np.sqrt(np.mean(g.signed_error_pp**2))),'MAE_pp':float(g.absolute_error_pp.mean())})
    pd.DataFrame(per).to_csv(ROOT/'per_profile_metrics.csv',index=False)
    # No claim that reducing plateau is bound to improve error; measure paired outcomes.
    changes=[]
    for family in ['first_order','Weibull','logistic']:
     for split in ['in_sample_all5','LOTO','forward30']:
      before=next(x for x in summary if x['model']==family+'_free' and x['split']==split);after=next(x for x in summary if x['model']==family+'_cap100' and x['split']==split)
      a=[x for x in per if x['model']==family+'_free' and x['split']==split];b={x['profile_id']:x for x in per if x['model']==family+'_cap100' and x['split']==split}
      changes.append({'family':family,'split':split,'free_RMSE_pp':before['RMSE_pp'],'cap100_RMSE_pp':after['RMSE_pp'],'RMSE_reduction_percent':100*(before['RMSE_pp']-after['RMSE_pp'])/before['RMSE_pp'],'profiles_improved':sum(b[x['profile_id']]['RMSE_pp']<x['RMSE_pp']-1e-8 for x in a),'profiles_worsened':sum(b[x['profile_id']]['RMSE_pp']>x['RMSE_pp']+1e-8 for x in a),'note':'Positive reduction indicates better diagnostic error; no new experimental evidence.'})
    (ROOT/'before_after_comparison.json').write_text(json.dumps(changes,indent=2));pd.DataFrame(changes).to_csv(ROOT/'before_after_comparison.csv',index=False)
    # Expand the matched CP x PVP design to a complete 3x3 grid; no endpoint response.
    NAMES=[x['name'] for x in original[0]['ingredients']]
    BOUNDS=dict(zip(NAMES[1:],[(15,32.5),(2,6),(1.5,4.5),(.25,1.25),(.25,1.25),(1,3),(.5,1.5),(.5,2)]))
    base=next(r for r in original if r['formulation_id']=='F02');grid=[];new=[]
    for cp,pvp in itertools.product([25,35,45],[16,24,32]):
     r=copy.deepcopy(base);mg={x['name']:D(str(x['mg'])) for x in r['ingredients']}
     mg['Crospovidone']=D(cp);mg['Povidone K30']=D(pvp)
     mg['Microcrystalline Cellulose']=D(800)-sum(v for n,v in mg.items() if n!='Microcrystalline Cellulose')
     match=next((a for a in original if all(D(str(x['mg']))==mg[x['name']] for x in a['ingredients'])),None)
     if match:r=copy.deepcopy(match)
     else:
      r['formulation_id']=f'I{len(new)+1:02d}';r['namespace']='clarithromycin_improvements_v2';r['origin']='new_matched_factorial_corner'
      for x in r['ingredients']:x['mg']=float(mg[x['name']]);x['w_w_percent']=float(mg[x['name']]/8)
      r['selection_order']=None;r.pop('selection_rationale',None);new.append(r)
     r['rank']=None;r['rank_basis']='experimental_design_only_no_efficacy_rank';r['dissolution']['status']='NOT_PREDICTED'
     assert sum(mg.values())==800 and mg['Clarithromycin']==500
     assert all(D(str(lo))<=mg[n]/8<=D(str(hi)) for n,(lo,hi) in BOUNDS.items())
     assert len(mg)==9 and min(mg.values())>=0
     r['factor_codes']={'CP':(cp-35)/10,'PVP':(pvp-24)/8};grid.append(r)
    assert len(grid)==9 and len(new)==4
    merged=copy.deepcopy(original)+new
    vectors=np.array([[x['mg'] for x in r['ingredients'][1:]] for r in merged]);assert pdist(vectors,metric='chebyshev').min()>=1
    (ROOT/'expanded_candidates.json').write_text(json.dumps(merged,indent=2));(ROOT/'factorial_design.json').write_text(json.dumps(grid,indent=2))
    rows=[]
    for r in merged:
     row={'id':r['formulation_id'],'status':'DESIGN_ONLY','in_3x3_factorial':r['formulation_id'] in {g['formulation_id'] for g in grid}}
     for x in r['ingredients']:row[x['name']+' mg']=x['mg'];row[x['name']+' %']=x['w_w_percent']
     row.update({'core_mg':r['core_mg'],'coat_mg':r['coat_mg'],'total_mg':sum(x['mg'] for x in r['ingredients']),'total_percent':sum(x['w_w_percent'] for x in r['ingredients'])});rows.append(row)
    pd.DataFrame(rows).to_csv(ROOT/'expanded_candidates.csv',index=False)
    def features(r):
     x=r['factor_codes']['CP'];z=r['factor_codes']['PVP'];return [1,x,z,x*z,x*x,z*z]
    X=np.array([features(r) for r in grid]);assert np.linalg.matrix_rank(X)==6
    # One pilot batch per factorial design plus two additional center batches.
    batches=[{'batch_id':'V2-'+r['formulation_id']+'-B01','formulation_id':r['formulation_id'],'status':'PLANNED_NOT_RUN'} for r in grid]
    batches += [{'batch_id':'V2-F02-B02','formulation_id':'F02','status':'PLANNED_NOT_RUN'},{'batch_id':'V2-F02-B03','formulation_id':'F02','status':'PLANNED_NOT_RUN'}]
    Xrep=np.vstack([X,features(next(r for r in grid if r['formulation_id']=='F02')),features(next(r for r in grid if r['formulation_id']=='F02'))])
    doe={'old_selected_unique_designs':3,'old_main_effect_rank':3,'old_main_effect_residual_df':0,'new_factorial_unique_designs':len(grid),'new_factorial_quadratic_columns':['intercept','CP','PVP','CP*PVP','CP^2','PVP^2'],'new_factorial_matrix_rank':int(np.linalg.matrix_rank(X)),'new_unique_design_lack_of_fit_df':len(grid)-int(np.linalg.matrix_rank(X)),'planned_batches_with_center_repeats':len(batches),'planned_quadratic_total_residual_df':len(batches)-int(np.linalg.matrix_rank(Xrep)),'planned_pure_error_df':len(batches)-len(grid),'new_unique_recipes_added':len(new),'total_valid_recipe_pool':len(merged),'limitation':'Algebraic estimability, not a fitted response model. Only center batch replication initially; no other factors/scale effects estimated.'}
    (ROOT/'design_improvement.json').write_text(json.dumps(doe,indent=2));(ROOT/'planned_batches.json').write_text(json.dumps(batches,indent=2))
    # Prospective protocol: no official QC method or new observations are invented.
    protocol={'status':'DRAFT_REQUIRES_SCIENTIFIC_APPROVAL_NOT_VALIDATED','route':'PVP_K30_wet_granulation_as_original_stratum','primary_development_comparator':{'basis':'R1_literature_method_only','apparatus':'USP_II_paddle','rpm':50,'volume_mL':900,'pH':5.0,'medium':'acetate buffer; exact preparation and suitability require approval','temperature_C':37,'temperature_tolerance_C':.5},'challenge_media':['citrate_at_matched_pH_and_justified_ionic_strength_TBD','non_carboxylate_buffer_at_matched_pH_and_justified_ionic_strength_TBD'],'times_min':plan['new_sample_schedule_min'],'exploratory_units_per_batch_per_medium':6,'official_release_Q_and_time':None,'reference_product_and_batch':None,'prerequisites':{'reference_profile':'MISSING','API_form_XRPD_PSD_KF_assay':'MISSING','excipient_grade_supplier_lot':'MISSING','sink_conditions_solution_stability_filter_recovery':'NOT_VERIFIED','stability_indicating_assay_specificity':'NOT_VERIFIED','sampling_volume_replacement_corrections':'TO_DEFINE','processing_parameters_and_granulation_exposure':'TO_DEFINE','jurisdiction_TiO2_assessment':'REQUIRED','coating_acceptability':'NOT_VERIFIED'},'mechanism_gate':'Never infer KP mechanism without eligible early observations; no library all-point fallback accepted for mechanism','stability':'Independent packaged accelerated/long-term experiments required; no shelf-life inference','normalization':'Preserve measured percent-label-claim; investigate assay and analytical corrections; do not clip values or retrospectively renormalize to final sample.'}
    (ROOT/'experimental_protocol_draft.json').write_text(json.dumps(protocol,indent=2))
    blank=[]
    for b in batches:
     for medium in ['ACETATE_PRIMARY_DRAFT','CITRATE_CHALLENGE_TBD','NONCARBOXYLATE_CHALLENGE_TBD']:
      for unit in range(1,7):
       for t in plan['new_sample_schedule_min']:blank.append({**b,'medium_id':medium,'unit_id':f'U{unit:02d}','time_min':t,'measured_intact_API_percent':None,'measured_degradants_percent':None,'actual_pH':None,'method_version':None,'API_lot':None,'API_form':None,'assay_potency_basis':None,'sampling_correction':None})
    pd.DataFrame(blank).to_csv(ROOT/'planned_measurement_template.csv',index=False)
    # Verify exports independently, preserving original source hashes.
    back=pd.read_csv(ROOT/'expanded_candidates.csv');assert len(back)==28 and np.allclose(back.total_mg,800) and np.allclose(back.total_percent,100)
    assert len(allfit)==len(unique)*len(CONFIGS)*7
    checks={'source_profiles':len(profiles),'deduplicated_profiles':len(unique),'duplicate_reference_records_excluded':len(aliases),'configurations':len(CONFIGS),'profile_model_split_evaluations':len(allfit),'prediction_rows':len(frame),'heldout_points_per_configuration_LOTO':len(unique)*5,'forward30_points_per_configuration':len(unique),'new_valid_factorial_corners':len(new),'valid_total_recipes':len(merged),'planned_batches':len(batches),'planned_units':len(batches)*3*6,'planned_blank_measurement_rows':len(blank),'candidate_measured_or_predicted_endpoint_values':0,'calibrated_prediction_intervals':None,'benchmark_candidates_source_sha256':hashlib.sha256((BASE/'candidates.json').read_bytes()).hexdigest(),'literature_profiles_source_sha256':hashlib.sha256((BASE/'literature_profiles.json').read_bytes()).hexdigest(),'scope':'Heldout timepoints within a single literature study, not heldout formulations/batches or independent external validation.'}
    (ROOT/'verification.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(checks,indent=2));print(summarydf.to_string(index=False));print('BOUNDING_BEFORE_AFTER',json.dumps(changes,indent=2));print('DESIGN',json.dumps(doe,indent=2))

    return checks
