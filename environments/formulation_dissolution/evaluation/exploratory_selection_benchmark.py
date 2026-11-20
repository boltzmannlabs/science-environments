"""Assumption-conditional selection and negative-control benchmark.

No Ajanta product inference: research 500 mg formulations only, all generated
profiles synthetic-origin predictions; F8 author endpoint is context only.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from evaluation.exploratory_scenarios import draw_scenarios, evaluate


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(config_path, scenario_path, output_path):
    config_path=Path(config_path); scenario_path=Path(scenario_path)
    cfg=json.loads(config_path.read_text()); scenario=json.loads(scenario_path.read_text())
    if scenario.get('config')!=cfg or scenario.get('status')!='exploratory_assumption_conditional_NOT_product_prediction':
        raise ValueError('invalid scenario identity or config')
    ranked=scenario['all_scenario_rankings']; top=ranked[0]
    if len(ranked)!=117 or top['id']!='grid_C84_B42_H8.5':
        raise ValueError('unexpected scenario grid or winner')
    f8=next(x for x in ranked if x['compritol_mg']==105 and x['carbopol_934_mg']==35 and x['hardness_kg_per_cm2']==8.5)
    f1=next(x for x in ranked if x['compritol_mg']==70 and x['carbopol_934_mg']==14 and x['hardness_kg_per_cm2']==8.5)
    paper_f8=next(x for x in scenario['published_recipe_scenario_comparators'] if x['research_label']=='F8')
    draws=list(draw_scenarios(cfg))
    def score(entry, samples):
        return evaluate(entry['compritol_mg'],entry['carbopol_934_mg'],entry['hardness_kg_per_cm2'],cfg,samples)
    selected=score(top,draws); comparator=score(f8,draws); f1_initial=score(f1,draws)
    if not math.isclose(selected['score_arbitrary_unitless'],top['score'],abs_tol=1e-12):
        raise ValueError('selected score not reproducible')
    zero=copy.deepcopy(draws)
    for item in zero:
        for key in ('compritol_log_rate_per_35mg','carbopol_log_rate_per_56mg','hardness_log_rate_per_kg_cm2'):
            item[key]=0.0
    zero_top=score(top,zero);zero_f8=score(f8,zero);zero_f1=score(f1,zero)
    for t in cfg['bounded_exploratory_space_assumed_not_approved']['time_h']:
        for model in ('first_order','weibull','pooled_model_and_assumption_range'):
            for q in ('p05','p50','p95'):
                if not math.isclose(zero_top['profiles_percent'][model][str(t)][q],zero_f8['profiles_percent'][model][str(t)][q],abs_tol=1e-12):
                    raise ValueError('zero-effect negative control failed')
    if zero_top['scenario_pass_fraction']!=zero_f8['scenario_pass_fraction']:
        raise ValueError('negative control scenario pass mismatch')
    if zero_f1['scenario_pass_fraction']!=zero_top['scenario_pass_fraction'] or zero_f1['score_arbitrary_unitless']<=zero_top['score_arbitrary_unitless']:
        raise ValueError('zero-effect F1 score preference did not expose weight dependence')
    # Mirrored sign-conditioned tests: these are deliberately artificial mechanisms.
    conditional={}
    for direction in ('positive_effects','negative_effects'):
        variants=copy.deepcopy(draws)
        for item in variants:
            for key in ('compritol_log_rate_per_35mg','carbopol_log_rate_per_56mg'):
                item[key]=abs(item[key])*(1 if direction=='positive_effects' else -1)
        a=score(top,variants);b=score(f8,variants);c=score(f1,variants)
        conditional[direction]={'selected_toy_score':a['score_arbitrary_unitless'],
            'F8_toy_score':b['score_arbitrary_unitless'],
            'selected_joint_toy_goal_fraction':a['scenario_pass_fraction'],
            'F8_joint_toy_goal_fraction':b['scenario_pass_fraction'],
            'F1_toy_score':c['score_arbitrary_unitless'],
            'selected_ranks_above_F8_under_same_assumptions':a['score_arbitrary_unitless']>b['score_arbitrary_unitless'],
            'selected_ranks_above_F1_under_same_assumptions':a['score_arbitrary_unitless']>c['score_arbitrary_unitless']}
    def summarized(x):
        p=x['profiles_percent']['pooled_model_and_assumption_range']
        return {'toy_score':x['score_arbitrary_unitless'],'joint_toy_goal_fraction':x['scenario_pass_fraction'],
                'median_release_percent_at_2h':p['2']['p50'],'median_release_percent_at_24h':p['24']['p50'],
                'scenario_p05_p95_at_2h':[p['2']['p05'],p['2']['p95']],
                'scenario_p05_p95_at_24h':[p['24']['p05'],p['24']['p95']]}
    result={'status':'exploratory_assumption_conditional_NOT_product_prediction',
        'study_scope':'literature research prototype 500 mg; not Ajanta recalled 1000 mg lot',
        'selection_rule':'rank by pre-existing arbitrary toy score among 117 assumed grid points',
        'selected_id':top['id'],'selected_mixture_mg':scenario['top_three_distinct_illustrative_compositions'][0]['mixture_mg'],
        'selected_hardness_kg_per_cm2_ASSUMED':top['hardness_kg_per_cm2'],
        'benchmark_comparator':'research F8 composition, rerun at same assumed hardness 8.5 kg/cm2',
        'comparator_id':f8['id'],'selected':summarized(selected),'F8_same_assumed_hardness':summarized(comparator),
        'F1_lowest_polymer_same_assumed_hardness':summarized(f1_initial),
        'scenario_score_difference_unitless':selected['score_arbitrary_unitless']-comparator['score_arbitrary_unitless'],
        'zero_effect_negative_control':{'profiles_identical':True,'joint_goal_fraction_identical':True,
             'selected':summarized(zero_top),'F8_same_assumed_hardness':summarized(zero_f8),
             'F1_lowest_polymer_same_assumed_hardness':summarized(zero_f1),
             'interpretation':'with rate effects removed, curve-based preference disappears; score can still differ via polymer-mass preference'},
        'sign_conditioned_assumption_sensitivity':conditional,
        'published_F8_author_endpoint':{'time_h':24,'percent_released':99.5,'evidence_label':'literature_reported',
            'observed_units_and_variability':'unavailable',
            'paper_hardness_kg_per_cm2':paper_f8['hardness_kg_per_cm2_literature_reported'],
            'scenario_median_percent_at_paper_hardness':scenario['literature_endpoint_sanity_check']['simulated_24h_median_percent_by_model'],
            'warning':'endpoint belongs to F8, not the selected formulation; one point cannot validate a simulation'},
        'input_sha256':_sha(scenario_path),'assumption_config_sha256':_sha(config_path),
        'model_version':scenario['model_library'],'pdf_integrity_checked_this_run':scenario['pdf_integrity_checked'],
        'scenario_count_per_candidate':len(draws),'source_evidence_label':'literature_reported',
        'generated_evidence_label':'predicted_scenario_only','data_origin':'synthetic',
        'ajanta_specification_attainment':'not_evaluated','validated_improvement':'not_established',
        'limits':['toy 2h/24h windows are unapproved assumptions','polymer and hardness rate effects are invented uniform priors',
                  'not a prospective experiment or measured release result','different research dosage/strength and unknown Ajanta approved method',
                  'F8 endpoint already inspected; not a held-out validation set']}
    output_path=Path(output_path);output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True)
    p.add_argument('--scenario',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=run(a.config,a.scenario,a.out)
    print(json.dumps({'status':r['status'],'selected_id':r['selected_id'],
                      'selected':r['selected'],'F8_same_assumed_hardness':r['F8_same_assumed_hardness'],
                      'zero_effect_negative_control':r['zero_effect_negative_control'],
                      'sign_conditioned_assumption_sensitivity':r['sign_conditioned_assumption_sensitivity'],
                      'out':str(a.out)},indent=2))

if __name__=='__main__':main()
