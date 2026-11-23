"""Independent six-model artifact auditor: software integrity, NOT science validation."""
import argparse
import json
import math
from pathlib import Path
from statistics import mean


def verify(result,fixture):
    errors=[]; syn=result['synthetic']; splits=syn['batch_split_manifest']
    sets={key:set(value) for key,value in splits.items()}
    if any(sets[a]&sets[b] for a,b in (('train','validation'),('train','test'),('validation','test'))):
        errors.append('batch_id_split_overlap')
    observed={b['batch_id']:b for b in fixture}
    if set(observed)!=set.union(*sets.values()) or len(observed)!=len(fixture):errors.append('batch_inventory_mismatch')
    for split,ids in sets.items():
        if any(observed[bid]['split']!=split for bid in ids):errors.append('split_labels_mismatch')
    if any(x['data_origin']!='synthetic' or x['evidence_label']!='assumed_fixture_not_measured' for x in fixture):
        errors.append('fixture_evidence_mislabel')
    if result['approved_ajanta_lot_QC']!='not_evaluated' or result['mixture_model']['status']!='not_trained':
        errors.append('unsupported_product_or_mixture_claim')
    for r in syn['per_test_batch_scores']:
        if r['batch_id'] not in sets['test'] or set(r['train_batch_ids'])-sets['train'] or r['batch_id'] in r['train_batch_ids']:
            errors.append('train_test_leakage')
        if r['test_data_origin']!='synthetic':errors.append('test_label_mismatch')
        points=[p for p in syn['per_test_timepoint_residuals'] if p['model']==r['model'] and p['batch_id']==r['batch_id']]
        if len(points)!=len(syn['time_min']):errors.append('missing_test_timepoints');continue
        diff=[p['prediction_percent']-p['actual_percent_synthetic'] for p in points if p['time_min']>0]
        check={'mae_pp':mean(abs(d) for d in diff),'rmse_pp':math.sqrt(mean(d*d for d in diff)),'bias_pp':mean(diff)}
        if any(not math.isclose(check[k],r[k],abs_tol=1e-9) for k in check):errors.append('per_batch_score_mismatch')
    published=result['published']
    if published['predictive_holdout_performance']!='not_evaluated' or any(not x['fit_to_same_curve'] for x in published['fits']):
        errors.append('published_fits_mislabelled')
    if any(x['profile_id']=='US6525057_IR' for x in published['fits']):errors.append('ir_in_er_comparison')
    if result['PTCalc']['status']!='tool_unavailable' or result['mechanistic_model']['status']!='not_evaluated':
        errors.append('unsupported_mechanistic_tool_claim')
    return sorted(set(errors))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--fixture',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=json.loads(args.result.read_text());fixture=json.loads(args.fixture.read_text())
    errors=verify(result,fixture)
    audit={'status':'mechanically_consistent_NOT_scientifically_validated' if not errors else 'audit_failed',
           'findings':errors,'scope':'batch leakage, score arithmetic, labels, tool abstention; no experimental validation'}
    args.out.write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
