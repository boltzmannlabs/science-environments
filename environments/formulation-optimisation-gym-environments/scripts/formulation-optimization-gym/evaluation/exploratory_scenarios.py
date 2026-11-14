"""Scenario-only ranolazine 500 mg research-prototype simulation.

This DOES NOT predict recalled Glenmark tablets. The paper supplies recipe
examples but NO curated numerical profiles; ALL release kinetics and scenario
probabilities are assumptions. No fitting to synthetic measurements occurs.
"""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

from tools.mixture_validator import validate


def percentile(values, q):
    values = sorted(values)
    index = q*(len(values)-1)
    lo = int(index)
    return values[lo] + (values[min(lo+1,len(values)-1)]-values[lo])*(index-lo)


def recipe(c, b, h, cfg):
    base = cfg['paper_mass_mg']
    mcc = 165 - c - b
    ingredients = [
        {'material_id':'ranolazine','amount':500,'unit':'mg'},
        {'material_id':'compritol','amount':c,'unit':'mg'},
        {'material_id':'carbopol_934','amount':b,'unit':'mg'},
        {'material_id':'avicel_PH101','amount':mcc,'unit':'mg'},
    ] + [{'material_id':key,'amount':base[key],'unit':'mg'} for key in ('povidone_K30','aerosil','titanium_dioxide')]
    candidate = {'ingredients':ingredients,'tablet_mass':base['tablet_total'],
                 'dose':500,'dose_unit':'mg','potency':1.0,'potency_unit':'fraction',
                 'api_material_id':'ranolazine','process':{'hardness_kg_per_cm2':h}}
    space = cfg['bounded_exploratory_space_assumed_not_approved']
    bounds = {i:space[i+'_mg'] for i in ('compritol','carbopol_934','avicel_PH101')}
    bounds.update({k:[v,v] for k,v in base.items() if k!='tablet_total'})
    result = validate(candidate,bounds=bounds,limits={'hardness_kg_per_cm2':space['hardness_kg_per_cm2']})
    if not result.valid:
        raise ValueError('exploratory window or mass balance failed: '+str(result.failed))
    return candidate, result.as_dict()


def draw_scenarios(cfg):
    par=cfg['release_assumptions_unfitted']
    r=random.Random(cfg['sampling_and_search']['seed'])
    for model in ('first_order','weibull'):
        for _ in range(cfg['sampling_and_search']['samples_per_model']):
            draw={k.replace('_uniform',''):r.uniform(*v) for k,v in par.items() if k.endswith('_uniform')}
            draw['model']=model
            yield draw


def curve(c,b,h,draw,times):
    # Version-locked OpenPKFlow's functional equations; never invoke fit APIs
    # on synthesized responses (that would misleadingly seem empirical).
    from openpkflow.dissolution.models import _first_order, _weibull
    import numpy as np
    c_term=(c-87.5)/35
    b_term=(b-42)/56
    z=(draw['compritol_log_rate_per_35mg']*c_term
        +draw['carbopol_log_rate_per_56mg']*b_term
        -draw['hardness_log_rate_per_kg_cm2']*(h-8.5))
    t=np.array(times,dtype=float)
    if draw['model']=='first_order':
        y=_first_order(t,draw['first_order_k1_per_h']*math.exp(z))
    else:
        y=_weibull(t,draw['weibull_alpha'],draw['weibull_beta_time_h']*math.exp(-z))
    if not np.isfinite(y).all() or (y<-1e-10).any() or (y>100+1e-10).any() or (np.diff(y)<-1e-10).any():
        raise ValueError('invalid simulated release curve')
    return [float(v) for v in y]


def evaluate(c,b,h,config,scenarios):
    times=config['bounded_exploratory_space_assumed_not_approved']['time_h']
    limits=config['bounded_exploratory_space_assumed_not_approved']['illustrative_targets_NOT_approved_QC']
    curves={m:[] for m in ('first_order','weibull')}
    passing=0
    margins=[]
    for draw in scenarios:
        vals=curve(c,b,h,draw,times)
        curves[draw['model']].append(vals)
        at2=vals[times.index(2)]; at24=vals[times.index(24)]
        passing+=at2<=limits['at_2h_max_percent'] and at24>=limits['at_24h_min_percent']
        # 0 if either illustrative window missed; 1 for balanced large margins
        margins.append(max(0.0,min(1.0,(limits['at_2h_max_percent']-at2)/25,
                                    (at24-limits['at_24h_min_percent'])/15)))
    all_curves=curves['first_order']+curves['weibull']
    stats=lambda profiles:{str(t):{'p05':percentile([y[i] for y in profiles],.05),
                                 'p50':percentile([y[i] for y in profiles],.50),
                                 'p95':percentile([y[i] for y in profiles],.95)} for i,t in enumerate(times)}
    polymer=c+b
    weights=config['sampling_and_search']['score_weights_assumed']
    score=(weights['joint_scenario_fraction']*passing/len(scenarios)
           +weights['clipped_margin']*sum(margins)/len(margins)
           +weights['lower_polymer_mass_proxy']*(1-(polymer-84)/91))
    return {'scenario_pass_fraction':passing/len(scenarios),'score_arbitrary_unitless':score,
            'mean_clipped_margin':sum(margins)/len(margins),
            'polymer_total_mg':polymer,
            'profiles_percent':{'pooled_model_and_assumption_range':stats(all_curves),
                                **{m:stats(y) for m,y in curves.items()}},
            'model_form_disagreement_at_24h_percent':abs(stats(curves['first_order'])['24']['p50']-stats(curves['weibull'])['24']['p50'])}


def run(cfg, *, pdf_path=None):
    import openpkflow
    if openpkflow.__version__ != '2.9.0':
        raise ValueError('openpkflow private model equations are pinned to 2.9.0')
    source=cfg['source']
    if pdf_path is not None and hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest()!=source['pdf_sha256']:
        raise ValueError('literature PDF SHA-256 does not match indexed source')
    study=cfg['literature_formulations_mg']
    for name, parts in study.items():
        recipe(parts['compritol'],parts['carbopol_934'],8.5,cfg)
        if 165-parts['compritol']-parts['carbopol_934']!=parts['avicel_PH101']:
            raise ValueError('paper recipe transcription failed '+name)
    draws=list(draw_scenarios(cfg))
    s=cfg['sampling_and_search']
    grid=[]
    for c in s['compritol_grid_mg']:
        for b in s['carbopol_grid_mg']:
            mcc=165-c-b
            if not cfg['bounded_exploratory_space_assumed_not_approved']['avicel_PH101_mg'][0]<=mcc<=cfg['bounded_exploratory_space_assumed_not_approved']['avicel_PH101_mg'][1]:
                continue
            for h in s['hardness_grid_kg_per_cm2']:
                r,_=recipe(c,b,h,cfg)
                score=evaluate(c,b,h,cfg,draws)
                grid.append({'id':f'grid_C{c}_B{b}_H{h}','compritol_mg':c,'carbopol_934_mg':b,
                             'avicel_PH101_mg':mcc,'hardness_kg_per_cm2':h,'score':score['score_arbitrary_unitless'],
                             'scenario_pass_fraction':score['scenario_pass_fraction'],
                             'polymer_total_mg':c+b, 'minimum_24h_p05':score['profiles_percent']['pooled_model_and_assumption_range']['24']['p05'],
                             'maximum_2h_p95':score['profiles_percent']['pooled_model_and_assumption_range']['2']['p95']})
    grid.sort(key=lambda x:(-x['score'],x['polymer_total_mg'],x['id']))
    # Non-dominated on assumed score, polymer use, and worst-quantile endpoints.
    def dominates(a,b):
        keys=('scenario_pass_fraction','minimum_24h_p05')
        return (all(a[k]>=b[k] for k in keys) and a['polymer_total_mg']<=b['polymer_total_mg']
                and a['maximum_2h_p95']<=b['maximum_2h_p95']
                and (any(a[k]>b[k] for k in keys) or a['polymer_total_mg']<b['polymer_total_mg'] or a['maximum_2h_p95']<b['maximum_2h_p95']))
    pareto={r['id'] for r in grid if not any(dominates(other,r) for other in grid if other is not r)}
    picked=[]
    for entry in grid:
        if (entry['compritol_mg'],entry['carbopol_934_mg']) in [(x['compritol_mg'],x['carbopol_934_mg']) for x in picked]:
            continue
        picked.append(entry)
        if len(picked)==3:break
    def detail(entry):
        c,b,h=entry['compritol_mg'],entry['carbopol_934_mg'],entry['hardness_kg_per_cm2']
        r,v=recipe(c,b,h,cfg)
        return {**entry,'in_exploratory_window_only':v, 'mixture_mg':{p['material_id']:p['amount'] for p in r['ingredients']},
                'mixture_percent_ww':{p['material_id']:100*p['amount']/r['tablet_mass'] for p in r['ingredients']},
                'simulated':evaluate(c,b,h,cfg,draws),'on_assumed_pareto_front':entry['id'] in pareto}
    published=[]
    for name,parts in study.items():
        c,b=parts['compritol'],parts['carbopol_934']
        measured_paper_h=cfg['literature_hardness_kg_per_cm2'][name]
        published.append({'research_label':name,'composition_mg':parts,
                          'hardness_kg_per_cm2_literature_reported':measured_paper_h,
                          'simulated':evaluate(c,b,measured_paper_h,cfg,draws)})
    claim=cfg['literature_endpoint_claim_not_training_data']
    comparison=next(x for x in published if x['research_label']==claim['formulation'])
    endpoint=str(claim['time_h'])
    literature_comparison={'claim':claim,'simulated_24h_median_percent_by_model':{},
                           'absolute_difference_from_claim_percent_by_model':{},
                           'interpretation':'unfitted scenario mismatch; one uncurated summary point cannot establish model fit'}
    for model in ('first_order','weibull'):
        val=comparison['simulated']['profiles_percent'][model][endpoint]['p50']
        literature_comparison['simulated_24h_median_percent_by_model'][model]=val
        literature_comparison['absolute_difference_from_claim_percent_by_model'][model]=abs(val-claim['percent_released'])
    # One-at-a-time effects at fixed assumed median kinetics. No scientific
    # sensitivity may be inferred when slope signs are not identified.
    mid={'model':'weibull','weibull_beta_time_h':9.25,'weibull_alpha':.9,
         'compritol_log_rate_per_35mg':.6,'carbopol_log_rate_per_56mg':.6,
         'hardness_log_rate_per_kg_cm2':.1}
    def effect(key,from_val,to_val,sign):
        mid['compritol_log_rate_per_35mg']=sign*.6
        mid['carbopol_log_rate_per_56mg']=sign*.6
        point={'c':87.5,'b':42,'h':8.5}
        point[key]=from_val; a=curve(**point,draw=mid,times=[2,24])
        point[key]=to_val; z=curve(**point,draw=mid,times=[2,24])
        return {'delta_release_2h_percent':z[0]-a[0],'delta_release_24h_percent':z[1]-a[1]}
    sensitivity={
        'compritol_70_to_105mg_at_assumed_positive_slope':effect('c',70,105,1),
        'compritol_70_to_105mg_at_assumed_negative_slope':effect('c',70,105,-1),
        'carbopol_14_to_70mg_at_assumed_positive_slope':effect('b',14,70,1),
        'carbopol_14_to_70mg_at_assumed_negative_slope':effect('b',14,70,-1),
        'hardness_7p5_to_9p5_kg_cm2':effect('h',7.5,9.5,1)}
    return {'status':'exploratory_assumption_conditional_NOT_product_prediction','product':'research_prototype_NOT_Glenmark',
        'source':source,'model_library':'openpkflow 2.9.0 _first_order and _weibull (private, version pinned)',
        'pdf_integrity_checked':pdf_path is not None,'config':cfg,
        'scenario_count_per_candidate':len(draws),'grid_size':len(grid),
        'all_scenario_rankings':grid,'pareto_front_count':len(pareto),
        'top_three_distinct_illustrative_compositions':[detail(x) for x in picked],
        'published_recipe_scenario_comparators':published,'literature_endpoint_sanity_check':literature_comparison,
        'sensitivity':sensitivity,
        'calibrated_uncertainty':None,'experimental_validation':None,
        'limitations':['NO actual recalled-batch formula or cause','NO curated measured numerical training/validation profiles',
                       'P05/P95 are Monte Carlo quantiles of invented prior ranges, not confidence or predictive intervals',
                       'No QC acceptance criteria: goals, costs, dose potency, and coefficients are assumed',
                       'Paper ingredients Compritol and Carbopol differ from current Glenmark label: no substitution authorized',
                       'Hardness is a literature tablet attribute, not a transferable process setting',
                       'Sign of polymer-release relationship unverified; ranking reverses under other assumptions',
                       'Physical experiments and product changes require approval']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--pdf',type=Path)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    cfg=json.loads(args.config.read_text())
    obj=run(cfg,pdf_path=args.pdf)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':obj['status'],'grid_size':obj['grid_size'],
        'models':['first_order','weibull'],'top_ids':[x['id'] for x in obj['top_three_distinct_illustrative_compositions']],
        'out':str(args.out)}))


if __name__=='__main__': main()
