"""Full original-source Pythia C+P mutation landscape on a verified exact WT structure.
No catalytic eligibility is invented: all raw cells are scored; selection is unfiltered/provisional.
"""
import argparse
import csv
import datetime
import fcntl
import hashlib
import json
import os
import pathlib
import resource
import sys
import time
import traceback

ARM=pathlib.Path(__file__).resolve().parents[1]
AA='ACDEFGHIKLMNPQRSTVWY'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest()
def save(path,data):
 p=pathlib.Path(path); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n'); os.replace(t,p)
def require(ok,message):
 if not ok: raise ValueError(message)

if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('--construct',required=True,choices=['cellulase_WT','beta_glucanase_WT']); parser.add_argument('--run-id',required=True); args=parser.parse_args()
 plan_path=ARM/'PYTHIA_RUN_PLAN_v2.json'; plan=json.loads(plan_path.read_text())
 require(plan['status']=='frozen_for_full_raw_landscapes','Pythia continuation plan not frozen')
 require(plan['runner_sha256']==sha(__file__),'Pythia runner changed after freeze')
 structure_QA=ARM/('verification/structures/'+args.construct+'_QA.json')
 qa=json.loads(structure_QA.read_text()); require(qa['all_required_artifacts_passed'],'Structure QA not passed')
 source=ARM/qa['primary_relaxed_structure']['path']; require(sha(source)==qa['primary_relaxed_structure']['sha256'],'Exact verified structure bytes changed')
 seq=plan['constructs'][args.construct]['sequence']; require(qa['sequence_sha256']==hashlib.sha256(seq.encode()).hexdigest(),'Structure construct/background mismatch')
 run=ARM/'pythia_runs'/args.run_id; require(not run.exists(),'Existing run ID; do not duplicate')
 run.mkdir(parents=True); start=time.monotonic()
 manifest={'schema':'Pythia-exact-structure-handoff.v1','construct':args.construct,'sequence':seq,'sequence_sha256':qa['sequence_sha256'],'structure':{'path':str(source),'sha256':sha(source)},'structure_QA':{'path':str(structure_QA),'sha256':sha(structure_QA)},'residue_mapping':qa['residue_mapping'],'pythia_plan_sha256':sha(plan_path),'threshold_convention':'strict summed C+P score < -3.0, unfiltered; paper eligibility unresolved'}
 save(run/'INPUT_MANIFEST.json',manifest)
 job={'run_id':args.run_id,'construct':args.construct,'pid':os.getpid(),'started_utc':now(),'status':'waiting_CPU_model_slot','model_forward_passes_expected':2,'model_forward_passes_completed':0,'positions_expected':len(seq),'nonidentity_substitutions_expected':len(seq)*19,'selection_eligibility':'unresolved_no_exclusions_invented','source_structure_sha256':sha(source),'handoff_manifest_sha256':sha(run/'INPUT_MANIFEST.json'),'raw_model_seconds':0.0}
 save(run/'job.json',job)
 try:
  with open(plan['resources']['lock'],'a+') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX); slot=time.monotonic()
   resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3)); os.sched_setaffinity(0,[0,1,2,3])
   import numpy as np
   import torch
   import torch.nn.functional as F
   from Bio.PDB.Polypeptide import index_to_one
   sys.path.insert(0,plan['source_root'])
   from pythia.masked_ddg_scan import get_torch_model
   from pythia.pdb_utils import read_pdb_to_protbb,get_neighbor
   torch.set_num_threads(4); torch.set_num_interop_threads(1); torch.manual_seed(0); torch.use_deterministic_algorithms(True)
   require(torch.version.cuda is None,'Expected CPU-only Torch')
   job.update(status='running_full_landscape',lock_acquired_utc=now(),lock_wait_seconds=slot-start,address_space_soft_hard_bytes=list(resource.getrlimit(resource.RLIMIT_AS)),cpu_affinity=sorted(os.sched_getaffinity(0)),torch_threads=torch.get_num_threads(),device='cpu')
   save(run/'job.json',job)
   prot=read_pdb_to_protbb(str(source))
   observed=''.join(index_to_one(int(x.item())) for x in prot.seq)
   require(observed==seq,'Upstream Pythia parser drops/changes exact input residues')
   node,edge,parent=get_neighbor(prot,noise_level=0.0)
   raw={}; scores={}; probabilities={}; model_stats={}
   with torch.inference_mode():
    for model_id in ['C','P']:
     checkpoint=pathlib.Path(plan['checkpoints'][model_id]['path'])
     require(sha(checkpoint)==plan['checkpoints'][model_id]['sha256'],'Checkpoint changed')
     begin=time.monotonic(); model=get_torch_model(str(checkpoint),device='cpu')
     logits,_=model(node.to('cpu'),edge.to('cpu'))
     prob=F.softmax(logits,dim=-1).detach().cpu().numpy()
     elapsed=time.monotonic()-begin
     require(prob.shape==(len(seq),21) and np.isfinite(prob).all() and (prob>0).all(),'Invalid upstream probability grid')
     wt=np.asarray([int(x.item()) for x in prot.seq])
     delta=-np.log(prob/prob[np.arange(len(seq)),wt,None])
     raw[model_id+'_logits']=logits.detach().cpu().numpy(); probabilities[model_id]=prob; scores[model_id]=delta
     raw[model_id+'_probabilities']=prob; raw[model_id+'_negative_LLR']=delta
     model_stats[model_id]={'parameters':sum(p.numel() for p in model.parameters()),'checkpoint_sha256':sha(checkpoint),'seconds_loading_and_forward':elapsed,'output_shape':list(prob.shape),'feature_node_shape':list(node.shape),'feature_edge_shape':list(edge.shape)}
     job['raw_model_seconds']+=elapsed; job['model_forward_passes_completed']+=1
     save(run/'job.json',job)
     del model,logits
   np.savez_compressed(run/'raw_model_outputs.npz',**raw)
   rows=[]
   for index,wt in enumerate(seq):
    for mt_index,mt in enumerate(AA):
     c=float(scores['C'][index,mt_index]); p=float(scores['P'][index,mt_index]); summed=c+p
     rows.append({'background':args.construct,'sequence_position':index+1,'wild_type':wt,'mutant':mt,'mutation':f'{wt}{index+1}{mt}','identity_control':wt==mt,'Pythia_C':c,'Pythia_P':p,'Pythia_sum_negative_LLR':summed,'Pythia_mean_score_sensitivity_only':summed/2,'below_minus_3_sum':summed < -3.0,'below_minus_3_mean_sensitivity_only':summed/2 < -3.0,'paper_site_eligibility':'unresolved','source_structure_sha256':manifest['structure']['sha256'],'predictor_score_not_energy_or_temperature':True})
   mutants=[r for r in rows if not r['identity_control']]
   ranked=sorted(mutants,key=lambda r:(r['Pythia_sum_negative_LLR'],r['sequence_position'],r['mutant']))
   best=sorted([min([r for r in mutants if r['sequence_position']==pos],key=lambda r:(r['Pythia_sum_negative_LLR'],r['mutant'])) for pos in range(1,len(seq)+1)],key=lambda r:(r['Pythia_sum_negative_LLR'],r['sequence_position']))
   tables={'all_scores_including_identity.csv':rows,'all_substitutions.csv':mutants,'ranked_unfiltered_substitutions.csv':ranked,'thresholded_unfiltered_substitutions.csv':[r for r in ranked if r['below_minus_3_sum']],'best_per_position_unfiltered.csv':best,'thresholded_best_per_position_unfiltered.csv':[r for r in best if r['below_minus_3_sum']]}
   for name,table in tables.items():
    with (run/name).open('w',newline='') as f:
     w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(table)
   job.update(status='completed_full_Pythia_raw_landscape',completed_utc=now(),positions_scored=len(seq),nonidentity_substitutions_scored=len(mutants),identity_controls=len(seq),model_details=model_stats,thresholded_unfiltered_substitutions=len(tables['thresholded_unfiltered_substitutions.csv']),thresholded_unfiltered_positions=len(tables['thresholded_best_per_position_unfiltered.csv']),elapsed_including_lock_seconds=time.monotonic()-start,model_slot_seconds=time.monotonic()-slot,max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_user_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,cpu_system_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime,artifacts=[{'path':str(p.relative_to(ARM)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(run.iterdir()) if p.is_file() and p.name!='job.json'])
   save(run/'job.json',job); print(json.dumps(job,indent=2),flush=True)
 except BaseException as exc:
  job.update(status='failed',error=repr(exc),traceback=traceback.format_exc(),failed_utc=now()); save(run/'job.json',job)
  with (ARM/'errors.jsonl').open('a') as f: f.write(json.dumps({'category':'full_Pythia_scientific_launch_failure','run_id':args.run_id,'construct':args.construct,'error':repr(exc),'job_record':str((run/'job.json').relative_to(ARM))})+'\n')
  raise
