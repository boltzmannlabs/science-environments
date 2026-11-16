"""Independent mechanical audit of ASSUMED scenario output, not lab validation."""
import argparse
import json
import math
from pathlib import Path


def verify_scenario(result:dict,config:dict)->list[str]:
    issues=[]
    if result.get('status')!='exploratory_assumption_conditional_NOT_product_prediction' or result.get('product')!='research_prototype_NOT_Glenmark':
        issues.append('scope_or_evidence_label')
    if result.get('calibrated_uncertainty','wrong') is not None or result.get('experimental_validation','wrong') is not None:
        issues.append('unearned_validation')
    if result.get('source')!=config['source'] or result.get('config')!=config:
        issues.append('config_or_source_mismatch')
    rows=result.get('all_scenario_rankings',[])
    if len(rows)!=result.get('grid_size') or len({r['id'] for r in rows})!=len(rows) or rows!=sorted(rows,key=lambda x:(-x['score'],x['polymer_total_mg'],x['id'])):
        issues.append('search_grid_or_order')
    sizes=result.get('scenario_count_per_candidate')
    if sizes!=2*config['sampling_and_search']['samples_per_model']:
        issues.append('scenario_count')
    for detail in result.get('top_three_distinct_illustrative_compositions',[]):
        pieces=detail['mixture_mg']
        if not math.isclose(sum(pieces.values()),695) or pieces['ranolazine']!=500 or not math.isclose(sum(detail['mixture_percent_ww'].values()),100):
            issues.append('mixture_balance')
        if not any(row['id']==detail['id'] and math.isclose(row['score'],detail['score'],abs_tol=1e-12) for row in rows):
            issues.append('candidate_grid_mismatch')
        score=detail['simulated']; w=config['sampling_and_search']['score_weights_assumed']
        expected=w['joint_scenario_fraction']*score['scenario_pass_fraction']+w['clipped_margin']*score['mean_clipped_margin']+w['lower_polymer_mass_proxy']*(1-(score['polymer_total_mg']-84)/91)
        if not math.isclose(expected,detail['score'],abs_tol=1e-12):
            issues.append('score_arithmetic')
        times=config['bounded_exploratory_space_assumed_not_approved']['time_h']
        for model,p in score['profiles_percent'].items():
            for t in times:
                point=p[str(t)]
                if not 0<=point['p05']<=point['p50']<=point['p95']<=100:
                    issues.append('release_bounds_or_quantiles')
            for t,u in zip(times[:-1],times[1:]):
                if p[str(t)]['p50']>p[str(u)]['p50']:
                    issues.append('nonmonotonic_median')
    if len(result.get('top_three_distinct_illustrative_compositions',[]))!=3:
        issues.append('candidate_count')
    return sorted(set(issues))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    issues=verify_scenario(json.loads(a.result.read_text()),json.loads(a.config.read_text()))
    summary={'status':'mechanically_consistent_NOT_experimentally_validated' if not issues else 'audit_failed',
             'issues':issues,'validation_scope':'source/config labels, mass, arithmetic, interval ordering, ranking; NOT dissolution accuracy'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))
    if issues:raise SystemExit(1)


if __name__=='__main__':main()
