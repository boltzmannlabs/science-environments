"""Read-only scientific artifact QA and comparison; never loads/reruns a model."""
import argparse
import csv
import datetime
import hashlib
import json
import math
import pathlib
import re
import numpy as np
from scipy.special import logsumexp
from scipy.stats import pearsonr, spearmanr

ARM=pathlib.Path(__file__).resolve().parents[1]
AA='ACDEFGHIKLMNPQRSTVWY'

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def require(ok,message):
    if not ok: raise ValueError(message)

def readcsv(path):
    with pathlib.Path(path).open(newline='') as f: return list(csv.DictReader(f))

def metrics(a,b):
    a=np.asarray(a,dtype=float); b=np.asarray(b,dtype=float)
    return {'n':len(a),'mean_absolute_error':float(np.mean(abs(a-b))),'root_mean_squared_error':float(np.sqrt(np.mean((a-b)**2))),'Pearson_r':float(pearsonr(a,b).statistic),'Spearman_rho':float(spearmanr(a,b).statistic),'strict_threshold_minus_1_5_agreement_count':int(np.sum((a < -1.5)==(b < -1.5))),'maximum_absolute_error':float(np.max(abs(a-b)))}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run-id',required=True); args=parser.parse_args()
    run=ARM/'runs'/args.run_id
    manifest=json.loads((ARM/'INPUT_MANIFEST.json').read_text())
    job=json.loads((run/'job.json').read_text())
    require(job['status']=='completed_full_ESM_inference','Producer has not finished all requested full scans')
    require(job['input_manifest_sha256']==sha(ARM/'INPUT_MANIFEST.json'),'Manifest changed after producer started')
    require(job['run_plan_sha256']==sha(ARM/'RUN_PLAN.json'),'Plan changed after producer started')
    require(job['model_identity']['parameters']==651043254,'Unexpected loaded parameter count')
    require(job['model_identity']['device']=='cpu','Unexpected model device')
    require(job['model_identity']['parameter_dtype']=='torch.float32','Unexpected inference precision')
    require(job['model_identity']['torch_threads']<=4,'Too many CPU threads')
    require(job['model_identity']['address_space_soft_hard_bytes']==[12*1024**3]*2,'Address-space cap not maintained')
    vocabulary=job['model_identity']['alphabet']
    report={'schema':'paper-artifact-QA.v1','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_id':args.run_id,'new_model_inference_jobs':0,'overall_full_paper_workflow_complete':False,'Pythia_status':'both_blocked_not_started','cases':{},'reference_score_comparison':{},'artifacts':[],'reference_internal_discrepancies':[]}
    all_comparisons=[]
    for name,reference_table in [('cellulase_M2','Table_S3.csv'),('beta_glucanase_M5','Table_S7.csv')]:
        seq=manifest['sequences'][name]['sequence']; path=run/name
        raw=[json.loads(line) for line in (path/'raw_masked_logits.jsonl').read_text().splitlines()]
        require(len(raw)==len(seq),'Raw forward-pass count incorrect')
        require([r['position'] for r in raw]==list(range(1,len(seq)+1)),'Raw positions missing/duplicated/reordered')
        raw_scores={}
        for r in raw:
            pos=r['position']; wt=seq[pos-1]
            require(r['wild_type']==wt,'Raw wild-type residue mismatch')
            require(r['sequence_sha256']==manifest['sequences'][name]['sequence_sha256'],'Raw background digest mismatch')
            require(r['mask_count']==1 and r['input_tokens']==len(seq)+2,'Incorrect masking or sequence length')
            logits=np.asarray(r['logits'],dtype=np.float64)
            require(logits.shape==(len(vocabulary),) and np.isfinite(logits).all(),'Raw logits invalid')
            lp=logits-logsumexp(logits)
            require(abs(float(np.exp(lp).sum())-1)<1e-12,'Log probabilities do not normalize')
            for mt in AA: raw_scores[(pos,mt)]=float(lp[vocabulary.index(wt)]-lp[vocabulary.index(mt)])
        rows=readcsv(path/'all_substitutions.csv')
        full=readcsv(path/'all_scores_including_identity.csv')
        ranked=readcsv(path/'ranked_substitutions.csv')
        threshold=readcsv(path/'thresholded_substitutions.csv')
        best=readcsv(path/'best_per_position.csv')
        threshold_best=readcsv(path/'thresholded_best_per_position.csv')
        expected={(i,mt) for i,wt in enumerate(seq,1) for mt in AA if mt!=wt}
        actual={(int(r['position']),r['mutant']) for r in rows}
        require(len(rows)==len(expected) and actual==expected,'Nonidentity substitution grid incomplete or duplicated')
        require(len(full)==len(seq)*20 and {(int(r['position']),r['mutant']) for r in full}=={(i,mt) for i in range(1,len(seq)+1) for mt in AA},'Full grid/identity controls incomplete')
        for r in full:
            pos=int(r['position']); mt=r['mutant']; value=float(r['negative_log_likelihood_ratio'])
            require(r['wild_type']==seq[pos-1] and r['mutation']==f'{seq[pos-1]}{pos}{mt}','Tabulated mutation identity mismatch')
            require(math.isfinite(value) and abs(value-raw_scores[pos,mt])<1e-10,'Score does not match independently recomputed raw-logit ratio')
            require(abs(float(r['mutant_minus_wt_logit'])+value)<1e-10,'Retained signs disagree')
            require((r['below_minus_1_5']=='True')==(value < -1.5),'Threshold flag incorrect')
            if mt==seq[pos-1]: require(value==0,'Identity control is not zero')
        key=lambda r:(float(r['negative_log_likelihood_ratio']),int(r['position']),r['mutant'])
        require(ranked==sorted(rows,key=key),'Global ranking incorrect')
        require(threshold==[r for r in ranked if float(r['negative_log_likelihood_ratio']) < -1.5],'Thresholded table incorrect')
        exp_best=[min([r for r in rows if int(r['position'])==pos],key=key) for pos in range(1,len(seq)+1)]
        require(sorted(best,key=key)==sorted(exp_best,key=key) and len(best)==len(seq),'Best-per-position table incorrect')
        require(sorted(threshold_best,key=key)==sorted([r for r in exp_best if float(r['negative_log_likelihood_ratio']) < -1.5],key=key),'Thresholded best-per-position table incorrect')
        observed_job=job['cases'][name]
        require(observed_job['coverage']['nonidentity_substitutions']==len(rows),'Producer summary disagrees with actual coverage')
        by_mut={r['mutation']:r for r in rows}
        ref=readcsv(ARM/'paper_reference'/reference_table)
        ref_scores=[]; predicted=[]; case_comparisons=[]
        reference_wt_tm=float(ref[0]['Tm (℃)'])
        for r in ref:
            label=r['Mutation']; match=re.fullmatch(r'M[25]\+([A-Z]\d+[A-Z])',label)
            if not match: continue
            mutation=match.group(1)
            require(mutation in by_mut,'Reference mutation absent from exact-background full table: '+mutation)
            q=by_mut[mutation]
            p=float(q['negative_log_likelihood_ratio']); rscore=float(r['ESM-2 scores'])
            ref_scores.append(rscore); predicted.append(p)
            item={'background':name,'mutation':mutation,'reference_source':reference_table,'paper_ESM_score':rscore,'new_negative_LLR_score':p,'new_positive_LLR_diagnostic':-p,'new_rank_among_all_substitutions':next(i for i,row in enumerate(ranked,1) if row['mutation']==mutation),'new_best_at_position':mutation in {x['mutation'] for x in best},'paper_below_minus_1_5':rscore < -1.5,'new_below_minus_1_5':p < -1.5,'paper_relative_activity_percent':r['Relative activity (%)'],'paper_Tm_C':r['Tm (℃)'],'paper_reported_delta_Tm_C':r['∆Tm (℃)'],'reference_measurements_not_new_experiments':True}
            case_comparisons.append(item); all_comparisons.append(item)
            actual_delta=float(r['Tm (℃)'])-reference_wt_tm
            if abs(actual_delta-float(r['∆Tm (℃)']))>0.051:
                report['reference_internal_discrepancies'].append({'table':reference_table,'mutation':mutation,'paper_Tm_C':float(r['Tm (℃)']),'paper_WT_Tm_C':reference_wt_tm,'paper_reported_delta_Tm_C':float(r['∆Tm (℃)']),'computed_Tm_minus_paper_WT_Tm_C':actual_delta,'action':'retained published values unchanged; no correction of primary source'})
        report['cases'][name]={'length':len(seq),'raw_masked_forward_passes':len(raw),'expected_nonidentity_substitutions':len(expected),'verified_nonidentity_substitutions':len(rows),'identity_controls':len(seq),'coverage_fraction':len(rows)/len(expected),'thresholded_substitutions':len(threshold),'thresholded_best_positions':len(threshold_best),'all_invariants_passed':True,'top_five_best_per_position':[{'mutation':r['mutation'],'negative_log_likelihood_ratio':float(r['negative_log_likelihood_ratio'])} for r in best[:5]],'reference_score_rows':len(case_comparisons)}
        report['reference_score_comparison'][name]={'scope':'Agreement with published selected-mutant model scores, not biological accuracy or independent validation','predeclared_negative_LLR':metrics(predicted,ref_scores),'positive_LLR_sign_diagnostic_only':metrics([-p for p in predicted],ref_scores)}
        for p in sorted(path.iterdir()):
            report['artifacts'].append({'path':str(p.relative_to(ARM)),'bytes':p.stat().st_size,'sha256':sha(p)})
    report['totals']={'masked_forward_passes':sum(x['raw_masked_forward_passes'] for x in report['cases'].values()),'nonidentity_substitutions':sum(x['verified_nonidentity_substitutions'] for x in report['cases'].values()),'identity_controls':sum(x['identity_controls'] for x in report['cases'].values()),'reference_score_rows':len(all_comparisons),'full_ESM_scans_completed':2,'Pythia_scans_completed':0,'scientific_model_launches':1,'scientific_model_failures':0}
    require(report['totals']['masked_forward_passes']==527 and report['totals']['nonidentity_substitutions']==10013,'Frozen full-run total not met')
    require(sha(ARM/manifest['esm2']['checkpoint']['path'])==manifest['esm2']['checkpoint']['sha256'],'Checkpoint changed since freeze')
    report['verifier_sha256']=sha(__file__)
    dest=ARM/'verification'; dest.mkdir(exist_ok=True)
    with (dest/'paper_ESM_score_comparison.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(all_comparisons[0])); writer.writeheader(); writer.writerows(all_comparisons)
    (dest/'artifact_QA.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ['verified_utc','totals','cases','reference_score_comparison']},indent=2))
