"""Full five-model AlphaFold2-mononer prediction via unchanged upstream ColabFold.
One exact published construct per native invocation, never a pilot or partial model list.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import logging
import os
import pathlib
import resource
import sys
import time
import traceback

ARM=pathlib.Path(__file__).resolve().parents[1]

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest()
def save(path,data):
 path=pathlib.Path(path); t=path.with_suffix(path.suffix+'.tmp')
 t.write_text(json.dumps(data,indent=2,allow_nan=False,default=str)+'\n'); os.replace(t,path)
def require(ok,message):
 if not ok: raise ValueError(message)

if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('--construct',required=True); parser.add_argument('--run-id',required=True); args=parser.parse_args()
 plan_path=ARM/'STRUCTURAL_RUN_PLAN_v2.json'
 plan=json.loads(plan_path.read_text())
 require(plan['status']=='frozen_for_full_execution','Structural plan not frozen')
 require(plan['runner_sha256']==sha(__file__),'Runner changed after freeze')
 construct=plan['constructs'][args.construct]
 require(sha(construct['msa']['path'])==construct['msa']['sha256'],'Frozen MSA changed')
 require(sha(construct['fasta'])==construct['fasta_sha256'],'Frozen exact FASTA changed')
 for p in plan['parameters']:
  require(sha(p['path'])==p['sha256'],'Frozen model parameter file changed')
 run=ARM/'structural_runs'/args.run_id
 require(not run.exists(),'Run ID already exists; reconcile before any recovery')
 run.mkdir(parents=True)
 start=time.monotonic()
 job={'schema':'local-AF2-scientific-job.v1','run_id':args.run_id,'construct':args.construct,'pid':os.getpid(),'command':sys.argv,'started_utc':now(),'status':'waiting_CPU_model_slot','structural_plan_sha256':sha(plan_path),'sequence_sha256':construct['sequence_sha256'],'model_predictions_expected':5,'models_completed':[],'predict_calls':[],'local_GPU':False,'model_inference_seconds_including_JIT':0.0,'remote_model_job':None}
 save(run/'job.json',job)
 try:
  with open(plan['resources']['lock'],'a+') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   slot=time.monotonic()
   resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
   os.sched_setaffinity(0,plan['resources']['cpu_affinity'])
   job.update(status='importing_CPU_runtime',lock_acquired_utc=now(),lock_wait_seconds=slot-start,address_space_soft_hard_bytes=list(resource.getrlimit(resource.RLIMIT_AS)),cpu_affinity=sorted(os.sched_getaffinity(0)))
   save(run/'job.json',job)
   import importlib.metadata
   import numpy as np
   import jax
   from alphafold.common import residue_constants
   from alphafold.model import model as af_model
   from colabfold import batch
   from colabfold.input import get_queries
   require(all(d.platform=='cpu' for d in jax.devices()),'Non-CPU JAX device')
   jax.config.update('jax_default_matmul_precision','highest')
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s',stream=sys.stdout,force=True)
   job['software_versions']={p:importlib.metadata.version(p) for p in ['colabfold','alphafold-colabfold','jax','jaxlib','numpy','openmm']}
   job['jax_devices']=[{'platform':d.platform,'device':str(d)} for d in jax.devices()]
   job['effective_environment']={k:os.environ.get(k) for k in ['CUDA_VISIBLE_DEVICES','JAX_PLATFORMS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OPENMM_CPU_THREADS','XLA_FLAGS','MALLOC_ARENA_MAX']}
   queries,is_complex=get_queries(construct['msa']['path'])
   require(len(queries)==1 and not is_complex and queries[0][1]==construct['sequence'],'Upstream query parser changed exact construct')
   # Pure observation around the upstream call; no model config, parameters or returned values altered.
   original_predict=af_model.RunModel.predict
   def audited_predict(self,*call_args,**call_kwargs):
    index=len(job['predict_calls'])+1
    config=self.config.to_dict()
    require(config['model']['num_recycle']==3,'Recycle count changed')
    require(config['model']['global_config']['bfloat16'] is False,'Unexpected bfloat16 inference')
    require(config['data']['eval']['num_ensemble']==1,'Ensemble count changed')
    save(run/f'effective_model_config_{index}.json',config)
    entry={'index':index,'started_utc':now(),'status':'running','effective_config':f'effective_model_config_{index}.json'}
    job['predict_calls'].append(entry); job['status']='running_full_model_inference'; save(run/'job.json',job)
    before=time.monotonic()
    result=original_predict(self,*call_args,**call_kwargs)
    jax.block_until_ready(result)
    elapsed=time.monotonic()-before
    job['model_inference_seconds_including_JIT']+=elapsed
    entry.update(status='completed',completed_utc=now(),seconds_including_JIT_and_recycles=elapsed)
    save(run/'job.json',job)
    return result
   af_model.RunModel.predict=audited_predict
   def features_callback(features):
    raw=np.asarray(features['aatype'])
    ids=raw.argmax(-1) if raw.ndim==2 else raw
    sequence=''.join((residue_constants.restypes+['X'])[int(i)] for i in ids)
    require(sequence==construct['sequence'],'Feature sequence differs from exact original construct')
    summary={k:{'shape':list(np.shape(v)),'dtype':str(getattr(v,'dtype',type(v).__name__))} for k,v in features.items()}
    save(run/'feature_shapes.json',{'sequence_verified':True,'sequence_sha256':construct['sequence_sha256'],'features':summary})
   def prediction_callback(protein,lengths,result,features,tag):
    sequence=''.join((residue_constants.restypes+['X'])[int(i)] for i in protein.aatype)
    require(sequence==construct['sequence'],'Predicted coordinates changed exact sequence or length')
    confidence=np.asarray(result['plddt'],dtype=float)
    require(confidence.shape==(len(sequence),) and np.isfinite(confidence).all(),'Invalid per-residue pLDDT')
    entry={'tag':str(tag[0]),'length':len(sequence),'sequence_sha256':construct['sequence_sha256'],'mean_plddt':float(confidence.mean()),'min_plddt':float(confidence.min()),'max_plddt':float(confidence.max()),'completed_utc':now()}
    job['models_completed'].append(entry)
    save(run/'job.json',job)
    print(json.dumps({'actual_prediction_completed':entry}),flush=True)
   settings=dict(plan['upstream_settings'])
   settings.update(queries=queries,result_dir=run/'outputs',data_dir=pathlib.Path(plan['data_dir']),prediction_callback=prediction_callback,feature_dict_callback=features_callback)
   (run/'outputs').mkdir()
   batch.run(**settings)
   require(len(job['models_completed'])==5 and len(job['predict_calls'])==5,'Upstream run did not complete all five requested full model predictions')
   unrelaxed=sorted((run/'outputs').glob('*_unrelaxed_rank_???_alphafold2_model_[1-5]_seed_???.pdb'))
   relaxed=sorted((run/'outputs').glob('*_relaxed_rank_???_alphafold2_model_[1-5]_seed_???.pdb'))
   require(len(unrelaxed)==5 and len(relaxed)==5,'Missing complete five-model unrelaxed/relaxed output set')
   job['artifacts']=[{'path':str(p.relative_to(ARM)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((run/'outputs').iterdir()) if p.is_file()]
   job.update(status='completed_full_five_model_AF2_and_CPU_relax',completed_utc=now(),elapsed_including_lock_seconds=time.monotonic()-start,model_slot_seconds=time.monotonic()-slot,max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_user_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,cpu_system_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime)
   save(run/'job.json',job)
   print(json.dumps({k:job[k] for k in ['run_id','construct','status','model_inference_seconds_including_JIT','model_slot_seconds','max_rss_KiB','models_completed']},indent=2),flush=True)
 except BaseException as exc:
  job.update(status='failed',failed_utc=now(),error=repr(exc),traceback=traceback.format_exc(),max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
  save(run/'job.json',job)
  with (ARM/'errors.jsonl').open('a') as f: f.write(json.dumps({'category':'full_AF2_scientific_launch_failure','run_id':args.run_id,'construct':args.construct,'error':repr(exc),'job_record':str((run/'job.json').relative_to(ARM))})+'\n')
  raise
