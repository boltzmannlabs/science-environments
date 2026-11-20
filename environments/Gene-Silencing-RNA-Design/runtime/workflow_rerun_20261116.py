"""Run-6: rerun approved installed pretrained workflows and compare public benchmark targets.
Preserve prior runs. No new training, package installation, endpoint blending or gate relaxation.
"""
import pathlib,sys,json,copy,datetime,subprocess,os,shutil,math,csv,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
import importlib.util
_spec=importlib.util.spec_from_file_location('run6_sweep_context',ROOT/'runtime/config_sweep_20261116.py')
assert _spec is not None and _spec.loader is not None
from typing import Any
S: Any=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(S)
RUN='Run-6_2026-11-16';OUT=ROOT/'benchmark/014_Workflow-rerun'/RUN
PREV=ROOT/'benchmark/012_Config-sweep/Run-4_2026-11-16';UPGRADE=ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16'
LEGACY=pathlib.Path('/home/boltzmann13/.sci/profiles/imran/workspace/oligoformer-integration/venv/bin/python')
def configure():
 S.RUN=RUN;S.OUT=OUT;S.CFG=copy.deepcopy(S.CFG);S.CFG[3]['purpose']='Fresh native paired OligoFormer forward inference; no cached efficacy scores in final comparisons.'
configure()
def dump(p,o):S.dump(p,o)
def read(p):return json.loads(pathlib.Path(p).read_text())
def prepare():
 if OUT.exists():raise RuntimeError('Fresh run directory required; never overwrite prior results')
 OUT.mkdir(parents=True);(OUT/'sources').mkdir()
 plan=read(PREV/'frozen_plan.json');plan.update(run_id=RUN,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='FROZEN_BEFORE_FRESH_WORKFLOW_INFERENCE',question='Rerun executable pretrained/physical workflows and compare with measured public targets and published model references.',config_order=S.CFG,provider='Approved installed local backends under explicit prior fresh-run/local authorization. Current Boltzmann contract inspected; no remote resubmission or service charges.',prior_run_plan_sha256=S.sha(PREV/'frozen_plan.json'),weights_downloaded=False,models_refitted=False)
 plan['execution_details']={'RN.Ai_Predict':'Fresh C00/C01 on all 322 measured pairs and TTR 598 windows; identical TTR input projections explicitly reuse one identical vector.','RNAiSpline':'Fresh on 322 measured pairs and 598 TTR windows.','OligoFormer':'Fresh native -i2 paired inference on all 322 measured guides across six transcripts and all 598 TTR windows. Historical cache retained only as a named intermediate reference, excluded from final efficacy vectors.','native_OligoFormer_limitation':'Upstream CLI leaves training/dropout mode active. Fixed seed 42 and ascending coordinate order frozen; subset/order effects are not a model improvement. Native pos column is an input ordinal, not a transcript coordinate.','HTT':'Four fresh RNAduplex configurations and three fresh degraded-context RN.Ai controls; not allele/CNS design validation.','immune':'Fresh unchanged motif scan, curated outcomes, pathogen-target exclusion; descriptive only.','no_new_generation':True,'panels_reranked':False,'no_new_training':True,'blocked_new_models':'SiaRNA/ENsiRNA/BERT readiness remains blocked as documented in Run-5; no synthetic features or fallback training.'}
 plan['selection_protocol']['common_oligoformer_cohort_n_expected']=322
 dump(OUT/'frozen_plan.json',plan)
 inputs=S.readcsv(PREV/'measured_input_audit.csv');txs=S.fasta(S.BASE/'external/siRNADiscovery/Data/Simone/mrna_Simone.fas');jobs=[]
 for acc in sorted(txs):
  rr=sorted([r for r in inputs if r['accession']==acc],key=lambda r:(int(r['site_index_0based']),r['row_id']))
  if not rr:continue
  payload={'accession':acc,'transcript':txs[acc],'pairs':[{'row_id':r['row_id'],'guide':r['guide_source'][:19],'site_index_0based':int(r['site_index_0based'])} for r in rr]};p=OUT/'00_inputs'/('oligo_'+acc+'.json');dump(p,payload);jobs.append({'name':acc,'input':str(p),'input_sha256':S.sha(p),'cohort':'Simone','count':len(rr)})
 tx=''.join((ROOT/'results/003_genetic-disease-total-lowering'/S.OLD/'00_inputs/transcript.fa').read_text().splitlines()[1:]);rr=sorted([r for r in S.readcsv(PREV/'ttr_pool_predictions.csv') if r['config_id']==S.CFG[0]['config_id']],key=lambda r:int(r['site_index_0based']));payload={'accession':'ENST00000237014.8','transcript':tx,'pairs':[{'row_id':r['row_id'],'guide':r['guide_source'],'site_index_0based':int(r['site_index_0based'])} for r in rr]};p=OUT/'00_inputs/oligo_TTR.json';dump(p,payload);jobs.append({'name':'TTR','input':str(p),'input_sha256':S.sha(p),'cohort':'TTR','count':len(rr)})
 dump(OUT/'oligoformer_job_plan.json',jobs)
 for task in S.TASKS:
  cd=ROOT/'config'/task/RUN;rd=ROOT/'results'/task/RUN;cd.mkdir(exist_ok=False);rd.mkdir(exist_ok=False)
  configs=S.configset(task);dump(cd/'eligibility.json',{'task':task,'configs':len(configs),'reason':S.SKIP.get(task,'Published cohort/reporter/anchor evaluation only; not full application completion.')})
  for c in configs:
   dump(cd/c['config_id']/'benchmark_config.json',{'task':task,'run_id':RUN,'config':c,'mode':'benchmark_evaluate_only','status':'FROZEN_BEFORE_INFERENCE','frozen_plan_sha256':S.sha(OUT/'frozen_plan.json'),'thresholds_sha256':plan['immutable_gates']['sha256'],'labels_used_for_candidate_generation':False,'best_design':None})
  if not configs:dump(rd/'status.json',{'status':'SKIPPED_NO_MATCHED_BENCHMARK','reason':S.SKIP[task],'new_model_training':False,'best_design':None})
 dump(OUT/'blocked_model_status.json',{'source_run':str((UPGRADE/'REPORT.md').relative_to(ROOT)),'source_sha256':S.sha(UPGRADE/'REPORT.md'),'readiness':read(UPGRADE/'challenger_readiness.json'),'BERT':'No fine-tuned checkpoint found in inspected author tree/releases. No custom training permitted.'})
 print('FROZEN',RUN,'native OligoFormer jobs',len(jobs),'task configs',sum(len(S.configset(t)) for t in S.TASKS),flush=True)
def infer():
 if (OUT/'fresh_inference_complete.json').exists():raise RuntimeError('Fresh inference already completed; do not overwrite')
 if not (OUT/'initial_stage_summary.json').exists():
  # Existing audited orchestration runs fresh RN.Ai/RNAiSpline, HTT physical/context controls.
  S.infer()
  for a,b in [('inference_summary.json','initial_stage_summary.json'),('C03_oligoformer_core19_measured_predictions.csv','C03_historical_reference_only.csv'),('all_measured_predictions.csv','initial_stage_all_measured_predictions.csv'),('ttr_pool_predictions.csv','initial_stage_ttr_pool_predictions.csv')]:
   (OUT/a).rename(OUT/b)
 jobs=read(OUT/'oligoformer_job_plan.json');allpred={};native_meta=[]
 for job in jobs:
  p=pathlib.Path(job['input']);assert S.sha(p)==job['input_sha256'];d=OUT/'native_oligoformer'/job['name']
  if d.exists():
   m=read(d/'execution.json')
   if m['status']!='COMPLETED':raise RuntimeError('Existing native job did not complete: '+str(d)+'; preserve it, do not silently repeat.')
   assert m['input_sha256']==job['input_sha256'] and S.sha(d/'predictions.json')==m['output_sha256']
  else:
   args=[str(LEGACY),'-B',str(ROOT/'runtime/oligoformer_pairs_20261116.py'),'--input',str(p),'--out',str(d)]
   d.parent.mkdir(exist_ok=True)
   with (d.parent/(job['name']+'_driver.log')).open('w') as log:proc=subprocess.run(args,env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,timeout=1900)
   if proc.returncode:raise RuntimeError('Native OligoFormer job failed: '+str(d.parent/(job['name']+'_driver.log')))
   m=read(d/'execution.json')
  native_meta.append({'cohort':job['cohort'],'job':job['name'],**m})
  for r in read(d/'predictions.json'):allpred[(job['cohort'],r['row_id'])]=r
  print('FRESH_OLIGOFORMER',job['name'],m['pairs_returned'],flush=True)
 measured=S.readcsv(OUT/'measured_input_audit.csv');oligo=[]
 for r in measured:
  v=allpred['Simone',r['row_id']];assert v['guide']==r['guide_source'][:19] and v['accession']==r['accession'] and int(r['site_index_0based'])==v['site_index_0based']
  oligo.append({**r,'score':v['score'],'status':'ok','config_id':S.CFG[3]['config_id'],'model':'OligoFormer','model_guide':v['guide'],'score_units':'native_class1_times_1.341','execution':v['execution']})
 S.csvout(OUT/'C03_oligoformer_core19_measured_predictions.csv',oligo)
 other=[r for r in S.readcsv(OUT/'initial_stage_all_measured_predictions.csv') if r['config_id']!=S.CFG[3]['config_id']];S.csvout(OUT/'all_measured_predictions.csv',other+oligo)
 tt=S.readcsv(OUT/'initial_stage_ttr_pool_predictions.csv')
 for r in tt:
  if r['config_id']==S.CFG[3]['config_id']:
   v=allpred['TTR',r['row_id']];assert v['guide']==r['guide_source'];r.update(score=v['score'],execution=v['execution'])
 S.csvout(OUT/'ttr_pool_predictions.csv',tt)
 # Reuse curated immune labels, not their previous predictions; pathogen examples excluded before scanning.
 import benchmark_campaign_20261111 as bc
 bc.OUT=OUT;immune=bc.immune()
 summary=read(OUT/'initial_stage_summary.json');summary.update(common_measured_rows=len(oligo),fresh_oligoformer_pairs=len(allpred),notes='Final OligoFormer vectors are fresh native paired inference; the explicitly named initial-stage files retain the cached reference only. Identical TTR C00/C01 inputs share one identical vector. No new generation, training or panel reranking.',oligoformer_native_mode='Training/dropout behavior retained; seed=42, coordinate order frozen; do not attribute subset/order variation to improved model quality.')
 dump(OUT/'inference_summary.json',summary);dump(OUT/'fresh_native_oligoformer_jobs.json',native_meta);dump(OUT/'fresh_inference_complete.json',{'status':'COMPLETED_RUNNABLE_WORKFLOWS','fresh_oligoformer_pairs':len(allpred),'fresh_measured_rows_per_efficacy_config':len(measured),'ttr_windows_per_efficacy_config':598,'immune_metrics':immune,'new_training':False,'new_generation':False});print('ALL_RUNNABLE_INFERENCE_COMPLETED',flush=True)
def analyze():
 if (OUT/'workflow_run_complete.json').exists():raise RuntimeError('Workflow analysis already completed; do not overwrite')
 if not (OUT/'fresh_inference_complete.json').exists():raise RuntimeError('Execute fresh inference first')
 import analyze_config_sweep_20261116 as a
 a.RUN=RUN;a.OUT=OUT;a.S=S;a.rank_panel=lambda task,cfg:None
 original=a.savefig
 def save(fig,d,name='performance'):
  for t in fig.findobj():
   if hasattr(t,'get_text') and hasattr(t,'set_text'):
    text=t.get_text()
    if 'cached OligoFormer' in text:t.set_text(text.replace('cached OligoFormer','fresh native OligoFormer'))
  return original(fig,d,name)
 a.savefig=save;a.main()
 # Calculate full-cohort threshold sensitivity and retain published-vs-local comparability explicitly.
 rows=S.readcsv(OUT/'all_measured_predictions.csv');full=[]
 for cfg in S.CFG:
  rr=[r for r in rows if r['config_id']==cfg['config_id']];m=a.metric(rr);m.update(config_id=cfg['config_id'],model=cfg['model'],auc_strict_gt_0p7=a.auc([float(r['label'])>.7 for r in rr],[float(r['score']) for r in rr]),n_labels_exactly_0p7=sum(float(r['label'])==.7 for r in rr));full.append(m)
 dump(OUT/'full_cohort_metrics.json',full)
 dump(OUT/'workflow_run_complete.json',{'status':'RUNNABLE_BENCHMARK_WORKFLOWS_EXECUTED_DESIGN_TASKS_PARTIAL','fresh_model_endpoints':['RN.Ai-Predict source guide','RN.Ai-Predict core19','RNAiSpline core19','OligoFormer native paired core19'],'frozen_task_config_count':sum(len(S.configset(t)) for t in S.TASKS),'new_pretrained_challengers_run':False,'no_training':True,'panels_reranked':False,'full_design_tasks_completed':0})
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','infer','analyze','all']);args=p.parse_args()
 if args.action in ['prepare','all']:prepare()
 if args.action in ['infer','all']:infer()
 if args.action in ['analyze','all']:analyze()
