"""Verify a complete Pythia landscape from retained native outputs; no model rerun."""
import argparse
import csv
import hashlib
import json
import math
import pathlib
import numpy as np
from scipy.stats import pearsonr,spearmanr

ARM=pathlib.Path(__file__).resolve().parents[1]
AA='ACDEFGHIKLMNPQRSTVWY'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def rows(p):
 with pathlib.Path(p).open(newline='') as f:return list(csv.DictReader(f))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--run-id',required=True);args=parser.parse_args()
 run=ARM/'pythia_runs'/args.run_id;job=json.loads((run/'job.json').read_text());manifest=json.loads((run/'INPUT_MANIFEST.json').read_text())
 require(job['status']=='completed_full_Pythia_raw_landscape','Full Pythia producer not complete')
 require(job['model_forward_passes_completed']==2,'Both C/P models were not evaluated')
 require(job['handoff_manifest_sha256']==sha(run/'INPUT_MANIFEST.json'),'Handoff changed')
 seq=manifest['sequence']; require(sha(manifest['structure']['path'])==manifest['structure']['sha256'],'Exact structure changed')
 raw=np.load(run/'raw_model_outputs.npz',allow_pickle=False)
 deltas={}
 for model in ['C','P']:
  logits=np.asarray(raw[model+'_logits']);p=np.asarray(raw[model+'_probabilities']);delta=np.asarray(raw[model+'_negative_LLR'])
  require(logits.shape==p.shape==delta.shape==(len(seq),21),'Raw arrays not complete')
  require(np.isfinite(logits).all() and np.isfinite(p).all() and np.isfinite(delta).all(),'Nonfinite raw model values')
  independently=np.exp(logits.astype(float)-logits.max(-1,keepdims=True))
  independently/=independently.sum(-1,keepdims=True)
  require(np.max(abs(independently-p))<2e-6,'Retained probabilities do not match raw logits')
  index=np.asarray([AA.index(wt) for wt in seq]);derived=-np.log(p/p[np.arange(len(seq)),index,None])
  require(np.max(abs(delta-derived))<1e-6,'Retained per-model scores not raw negative likelihood ratios')
  deltas[model]=derived
 full=rows(run/'all_scores_including_identity.csv');mutants=rows(run/'all_substitutions.csv');ranked=rows(run/'ranked_unfiltered_substitutions.csv');threshold=rows(run/'thresholded_unfiltered_substitutions.csv');best=rows(run/'best_per_position_unfiltered.csv')
 expected={(i,mt) for i,wt in enumerate(seq,1) for mt in AA if mt!=wt}
 require(len(mutants)==len(expected) and {(int(r['sequence_position']),r['mutant']) for r in mutants}==expected,'Missing/duplicated full nonidentity cells')
 require(len(full)==len(seq)*20,'Full grid with controls incomplete')
 for r in full:
  pos=int(r['sequence_position']);mt=r['mutant'];column=AA.index(mt);require(r['wild_type']==seq[pos-1] and r['mutation']==f'{seq[pos-1]}{pos}{mt}','Mutation/background mismatch')
  value=float(r['Pythia_sum_negative_LLR']);c=float(deltas['C'][pos-1,column]);p=float(deltas['P'][pos-1,column])
  require(math.isfinite(value) and abs(value-(c+p))<1e-6,'Summed score differs from raw per-model outputs')
  require(abs(float(r['Pythia_mean_score_sensitivity_only'])-value/2)<1e-9,'Mean sensitivity convention wrong')
  require((r['below_minus_3_sum']=='True')==(value < -3),'Threshold convention wrong')
  require(r['paper_site_eligibility']=='unresolved','Source eligibility was silently invented')
  if mt==seq[pos-1]:require(value==0,'Nonzero identity control')
 key=lambda r:(float(r['Pythia_sum_negative_LLR']),int(r['sequence_position']),r['mutant'])
 require(ranked==sorted(mutants,key=key),'Global ranking wrong')
 require(threshold==[r for r in ranked if float(r['Pythia_sum_negative_LLR']) < -3],'Strict threshold output wrong')
 expectbest=sorted([min([r for r in mutants if int(r['sequence_position'])==pos],key=key) for pos in range(1,len(seq)+1)],key=key)
 require(sorted(best,key=key)==expectbest,'Best-per-position outputs wrong')
 table='Table_S1.csv' if job['construct']=='cellulase_WT' else 'Table_S5.csv'
 bymut={r['mutation']:r for r in mutants};comparison=[]
 for r in rows(ARM/'paper_reference'/table):
  mutation=r['Mutation']
  if mutation=='Wild type':continue
  require(mutation in bymut,'Reference mutation absent or wrong WT identity: '+mutation)
  q=bymut[mutation];comparison.append({'construct':job['construct'],'mutation':mutation,'paper_reference_Pythia_score':float(r['Pythia scores']),'new_Pythia_sum_score':float(q['Pythia_sum_negative_LLR']),'new_Pythia_mean_sensitivity':float(q['Pythia_mean_score_sensitivity_only']),'paper_Tm_C':r['Tm (℃)'],'paper_relative_activity_percent':r['Relative activity (%)'],'reference_measurements_not_new_experiments':True})
 a=np.asarray([r['paper_reference_Pythia_score'] for r in comparison]);b=np.asarray([r['new_Pythia_sum_score'] for r in comparison])
 stats={'n':len(comparison),'mean_absolute_error':float(np.mean(abs(a-b))),'root_mean_squared_error':float(np.sqrt(np.mean((a-b)**2))),'Pearson_r':float(pearsonr(a,b).statistic),'Spearman_rho':float(spearmanr(a,b).statistic),'strict_threshold_membership_agreement':int(np.sum((a < -3)==(b < -3)))}
 destination=ARM/'verification/pythia';destination.mkdir(exist_ok=True)
 cp=destination/(job['construct']+'_paper_score_comparison.csv')
 with cp.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(comparison[0]));writer.writeheader();writer.writerows(comparison)
 qa={'schema':'Pythia-full-landscape-QA.v1','run_id':args.run_id,'construct':job['construct'],'all_raw_landscape_invariants_passed':True,'positions':len(seq),'nonidentity_substitutions':len(mutants),'identity_controls':len(seq),'coverage_fraction':1.0,'model_forward_passes':2,'thresholded_unfiltered_substitutions':len(threshold),'thresholded_unfiltered_positions':len([r for r in best if float(r['Pythia_sum_negative_LLR']) < -3]),'source_qualified_selection_complete':False,'site_exclusion_uncertainty_retained':True,'comparison_scope':'Reported Pythia model-score agreement, not biological accuracy; new matched-method AF2 coordinates are not the original coordinates','paper_score_comparison':stats,'comparison_table':str(cp.relative_to(ARM)),'source_structure':manifest['structure'],'new_model_inference_jobs':0,'verifier_sha256':sha(__file__),'artifacts':[{'path':str(p.relative_to(ARM)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in run.iterdir() if p.is_file()]}
 (destination/(job['construct']+'_QA.json')).write_text(json.dumps(qa,indent=2)+'\n')
 print(json.dumps({k:qa[k] for k in ['construct','positions','nonidentity_substitutions','thresholded_unfiltered_substitutions','thresholded_unfiltered_positions','all_raw_landscape_invariants_passed','paper_score_comparison']},indent=2))
