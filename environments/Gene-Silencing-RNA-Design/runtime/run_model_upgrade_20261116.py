"""Run-5: fail-closed published model upgrade assessment plus actual incumbent control replay.
No new model training, synthetic learned features, patched author source or fictional challenger scores.
"""
import argparse,pathlib,sys,json,csv,hashlib,datetime,ast,math,subprocess
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
import config_sweep_20261116 as S
from sirna_context_audit import AuditedPredictors,rc
RUN='Run-5_2026-11-16';B=ROOT/'benchmark/013_Model-upgrade'/RUN;PREV=S.OUT
ACTIVE=['001_general','002_oncology','003_genetic-disease-total-lowering','006_systemic-lnp','009_functional-genomics','010_gene-regulation','011_drug-target-validation']
PRIMARY=['HIF1A','HPSE','HK2'];IDS=['U00_retained_rnai','U01_siarna_pretrained','U02_ensirna_pretrained']
WHY={'004_genetic-disease-allele-selective':'On-target efficacy models do not establish allele discrimination; reference-verified allele design inputs remain unresolved.','005_metabolic-liver-galnac':S.SKIP['005_metabolic-liver-galnac'],'007_neuro-cns':'HTT reporters lack genuine transcript flanks and resolved CNS reference/isoform inputs. Do not fabricate context or apply new efficacy models as CNS validation.','008_inflammation-immune':S.SKIP['008_inflammation-immune']}
def dump(p,x):S.dump(p,x)
def read(p):return json.loads(pathlib.Path(p).read_text())
def model_gate(name):
 if name=='SiaRNA':
  p=read(B/'acquisition_provenance.json');root=pathlib.Path(p['local_asset_root']);tree=ast.parse((root/'preprocess.py').read_text());random_nodes=[n for n in ast.walk(tree) if isinstance(n,ast.Assign) and 'np.random.randn' in ast.unparse(n)]
  if not random_nodes:raise RuntimeError('Audited author source changed; this frozen assessment cannot authorize new inference. Create a new run.')
  return {'model':name,'status':'BLOCKED_INVALID_FEATURE_PIPELINE','stage_verified':'Strict pretrained state_dict load and executable software diagnostic passed; efficacy forward pass intentionally not run.','reason':'Author preprocess.py overwrites computed mRNA folding vectors with unseeded random vectors. Genuine cohort AGO2 features unavailable. Native CLI returns first pair only. No substitutions allowed.','evidence':'siarna_software_probe.json','efficacy_predictions_produced':0,'software_diagnostics_only':True}
 if name=='ENsiRNA':
  a=read(B/'ENsiRNA_asset_assessment.json');attempts=a['public_structure_access_attempts'];assert any('401' in x.get('error','') for x in attempts)
  return {'model':name,'status':'BLOCKED_MISSING_STRUCTURAL_INPUTS','stage_verified':'Author CSVs/implementation inspected and public structure access tried by download and file-view routes.','reason':'Pre-folded PDB link redirects to Google sign-in; file-view returned HTTP 401. No verified per-row PDBs or authorized Rosetta installation available. RNA-FM/PyG dependencies also absent. No zero coordinates, substituted structures or Rosetta terms accepted.','evidence':'ENsiRNA_asset_assessment.json','efficacy_predictions_produced':0,'software_diagnostics_only':True}
 raise ValueError('Unknown published model')
def prepare():
 if (B/'frozen_workflow_plan.json').exists():raise RuntimeError('Run already frozen. Create a new run instead of overwriting.')
 assert read(B/'training_scope_decision.json')['custom_training_permitted'] is False
 acq=read(B/'acquisition_provenance.json');gates=[model_gate('SiaRNA'),model_gate('ENsiRNA')];dump(B/'challenger_readiness.json',gates)
 # Explicit evaluation of interface applicability; no overhangs invented for a 21-nt model.
 rr=S.readcsv(PREV/'measured_input_audit.csv');txs=S.fasta(S.BASE/'external/siRNADiscovery/Data/Simone/mrna_Simone.fas');audit=[]
 for r in rr:
  g=r['guide_source'];tx=txs[r['accession']];audit.append({'row_id':r['row_id'],'gene':r['gene'],'guide_nt':len(g),'transcript_nt':len(tx),'native_siarna_guide_length_ok':len(g)==21,'native_siarna_mrna_length_ok':21<=len(tx)<=2000,'native_full_guide_exact_match':rc(g) in tx,'core19_exact_match':rc(g[:19]) in tx,'new_model_prediction':None})
 S.csvout(B/'native_input_applicability.csv',audit)
 # Author ENsiRNA test set covers multiple cohorts. Join only the existing public human rows by ID and sequence.
 with (B/'sources/ENsiRNA_ENsiRNA_dataset_test.csv').open() as f:test=list(csv.DictReader(f))
 train=[]
 for i in range(1,6):
  with (B/'sources'/('ENsiRNA_ENsiRNA_dataset_train_'+str(i)+'.csv')).open() as f:train+=list(csv.DictReader(f))
 canon=lambda s:s.upper().replace('T','U').replace(' ','')
 cores={canon(r['anti seq'])[:19] for r in train};accs={r['mRNA'].split('.')[0] for r in train};byid={r['siRNA']:r for r in test};matches=[]
 for r in rr:
  z=byid.get(r['row_id']);matches.append({'row_id':r['row_id'],'author_test_id_found':z is not None,'author_test_guide_core19_equal':z is not None and canon(z['anti seq'])[:19]==r['guide_source'][:19],'author_training_any_fold_exact_core19_overlap':r['guide_source'][:19] in cores,'author_training_any_fold_accession_base_overlap':r['accession'].split('.')[0] in accs})
 S.csvout(B/'ENsiRNA_cohort_identity_and_overlap.csv',matches)
 plan={'run_id':RUN,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Published pretrained models only; custom training explicitly declined.','question':'Can a published, runnable pretrained challenger justify changing the incumbent on the existing human benchmarks?','decision_rule':'No eligible challenger score exists: retain RN.Ai source-guide incumbent, do not cherry-pick per-target observed winners or loosen frozen gates.','new_models':gates,'control':{'config_id':IDS[0],'model':'RN.Ai-Predict','projection':'Source 19-21 nt guide verbatim','execution':'Fresh local inference on measured 322 pairs and TTR 598 historical windows; not new generation.','comparison':'Exact replay against Run-4 native scores within 0.011 percentage points.','not_a_model_upgrade':True},'provider':'Current Boltzmann RNA property contract checked: no SiaRNA/ENsiRNA model selector. Explicit local permission recorded. No remote job submitted.','input_sources':[{'path':str((PREV/'measured_input_audit.csv').relative_to(ROOT)),'sha256':S.sha(PREV/'measured_input_audit.csv')},{'path':str((PREV/'ttr_pool_predictions.csv').relative_to(ROOT)),'sha256':S.sha(PREV/'ttr_pool_predictions.csv')}],'threshold_sha256':S.sha(ROOT/'config/thresholds.v1.0.frozen.json'),'selection_uses_new_test_labels':False,'prior_data_exposure':'All cohorts previously examined; software replay is not an untouched validation.','new_training':False,'original_sources_modified':False,'best_design':None}
 dump(B/'frozen_workflow_plan.json',plan)
 for task in S.TASKS:
  d=ROOT/'config'/task/RUN;d.mkdir(exist_ok=False);rd=ROOT/'results'/task/RUN;rd.mkdir(exist_ok=False)
  cfg={'task':task,'run_id':RUN,'mode':'benchmark_evaluate_only','workflow_status':'CONTROL_PLUS_BLOCKED_CHALLENGERS' if task in ACTIVE else 'SKIPPED_UNSUPPORTED_BENCHMARK','plan_sha256':S.sha(B/'frozen_workflow_plan.json'),'retained_incumbent':IDS[0] if task in ACTIVE else None,'model_readiness':gates,'reason':WHY.get(task,'Control inference allowed; no eligible new challenger or workflow promotion.'),'full_application_complete':False,'best_design':None}
  dump(d/'workflow.json',cfg);dump(rd/'workflow.json',cfg)
  if task in ACTIVE:
   for cid in IDS:
    p=d/cid;p.mkdir();payload={'task':task,'config_id':cid,'run_id':RUN,'plan_sha256':cfg['plan_sha256'],'execution':'FRESH_CONTROL_INFERENCE' if cid==IDS[0] else 'READINESS_GATE_BLOCKED_NO_EFFICACY_SCORE','model':'RN.Ai-Predict' if cid==IDS[0] else ('SiaRNA' if cid==IDS[1] else 'ENsiRNA'),'source_guide_or_core_preserved':True,'no_training':True,'no_synthetic_learned_inputs':True,'threshold_sha256':plan['threshold_sha256'],'best_design':None};dump(p/'benchmark_config.json',payload)
 print('PREPARED',len(S.TASKS),'task workflows;',len(ACTIVE),'control routes and',2*len(ACTIVE),'blocked model routes',flush=True)
def run():
 if not (B/'frozen_workflow_plan.json').exists():raise RuntimeError('Prepare first')
 if (B/'control_inference_summary.json').exists():raise RuntimeError('Control already executed; refuse overwrite')
 for x in read(B/'frozen_workflow_plan.json')['input_sources']:assert S.sha(ROOT/x['path'])==x['sha256']
 gate_runs=[]
 for n in ['SiaRNA','ENsiRNA']:x=model_gate(n);gate_runs.append(x);print('EXECUTED_READINESS_GATE',n,x['status'],flush=True)
 dump(B/'executed_readiness_gates.json',gate_runs)
 preds=AuditedPredictors();rr=S.readcsv(PREV/'measured_input_audit.csv');vs=preds.rnai_batch([(r['guide_source'],r['context']) for r in rr]);out=[{**r,**v,'config_id':IDS[0],'model':'RN.Ai-Predict','execution':'FRESH_INCUMBENT_CONTROL_NOT_NEW_MODEL'} for r,v in zip(rr,vs)]
 delta=max(abs(float(r['prior_rnai'])-float(v['score'])) for r,v in zip(rr,vs));assert delta<=.011
 S.csvout(B/'measured_control_predictions.csv',out);print('FRESH_MEASURED_CONTROL',len(out),'max_delta',delta,flush=True)
 old=[r for r in S.readcsv(PREV/'ttr_pool_predictions.csv') if r['config_id']=='C00_rnai_native21'];vs=preds.rnai_batch([(r['guide_source'],r['context']) for r in old]);tout=[{**r,**v,'config_id':IDS[0],'model':'RN.Ai-Predict','execution':'FRESH_INCUMBENT_CONTROL_NOT_NEW_MODEL'} for r,v in zip(old,vs)];td=max(abs(float(r['score'])-float(v['score'])) for r,v in zip(old,vs));assert td<=.011;S.csvout(B/'ttr_control_predictions.csv',tout)
 # Check originals after both software probing and native control execution.
 for x in read(B/'acquisition_provenance.json')['files']:assert S.sha(x['path'])==x['sha256']
 dump(B/'batch_native_checks.json',preds.validation_checks)
 dump(B/'control_inference_summary.json',{'status':'CONTROL_REPLAY_COMPLETED_NEW_MODELS_BLOCKED','fresh_measured_pairs':len(out),'fresh_ttr_windows':len(tout),'measured_max_abs_delta_percentage_points':delta,'ttr_max_abs_delta_percentage_points':td,'new_challenger_efficacy_predictions':0,'training_performed':False,'author_assets_unchanged':True,'frozen_plan_sha256':S.sha(B/'frozen_workflow_plan.json'),'python':sys.executable,'environment':'Isolated run5 venv inherits pinned scientific dependencies read-only through .pth; no packages installed or existing environments changed.','versions':read(B/'siarna_software_probe.json')['versions']});print('CONTROL_COMPLETE',len(tout),'TTR windows',flush=True)
def report():
 if not (B/'control_inference_summary.json').exists():raise RuntimeError('Run real control inference first')
 if (B/'results_summary.json').exists():raise RuntimeError('Report frozen; do not overwrite')
 from analyze_config_sweep_20261116 import metric,paired_delta
 from scipy.stats import rankdata
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from PIL import Image,ImageStat
 old=read(PREV/'measured_metrics.json');rr=S.readcsv(B/'measured_control_predictions.csv');tt=S.readcsv(B/'ttr_control_predictions.csv');baseline=S.readcsv(PREV/'C00_rnai_native21_measured_predictions.csv');table=[]
 for g in PRIMARY+['MYC','FULL_SIMONE']:
  a=rr if g=='FULL_SIMONE' else [r for r in rr if r['gene']==g];bb=baseline if g=='FULL_SIMONE' else [r for r in baseline if r['gene']==g];m=metric(a);m.update(paired_delta(a,bb));m.update(gene=g,config_id=IDS[0],execution='FRESH_CONTROL_REPLAY');table.append(m)
 dump(B/'control_metrics.json',table);S.csvout(B/'control_metrics.csv',[{k:v for k,v in r.items() if not isinstance(v,(dict,list))} for r in table])
 lookup={r['gene']:r for r in table};macro=float(np.mean([lookup[g]['auc'] for g in PRIMARY]));prior_macro=float(np.mean([r['auc'] for r in old if r['config_id']=='C00_rnai_native21' and r['gene'] in PRIMARY]));assert abs(macro-prior_macro)<1e-12
 anchors=S.readcsv(PREV/'TTR_anchor_metrics.csv');ranks=rankdata([-float(r['score']) for r in tt]);newanchors=[]
 for a in [r for r in anchors if r['config_id']=='C00_rnai_native21']:
  # Anchor identity is bound to its saved source score/rank; explicitly verify exact guide from Run-3 anchor evidence.
  src=S.readcsv(S.OLD_B/'ttr_same_side/per_dimension_anchor_evidence.csv');guide=next(r['guide_sequence'] for r in src if r['candidate_id']==a['anchor']+'_derived_19nt_core');idx=next(i for i,r in enumerate(tt) if r['guide_source']==guide);rank=float(ranks[idx]);assert abs(rank-float(a['rank']))<1e-12
  newanchors.append({'config_id':IDS[0],'anchor':a['anchor'],'rank':rank,'pool_n':len(tt),'percentile':100*(1-(rank-1)/(len(tt)-1)),'native_score':float(tt[idx]['score']),'interpretation':'Projected core anchor recovery only; no measured clinical potency labels.'})
 S.csvout(B/'TTR_control_anchor_metrics.csv',newanchors)
 images=[];ledger=[];statuses=[]
 def save(fig,path):
  fig.savefig(path.with_suffix('.png'),dpi=180,bbox_inches='tight',facecolor='white');fig.savefig(path.with_suffix('.svg'),bbox_inches='tight',facecolor='white');plt.close(fig)
  with Image.open(path.with_suffix('.png')) as im:im.verify()
  with Image.open(path.with_suffix('.png')) as im:stat=ImageStat.Stat(im.convert('RGB'));assert im.width>800 and im.height>300 and max(stat.stddev)>5;images.append({'path':str(path.with_suffix('.png').relative_to(ROOT)),'width':im.width,'height':im.height,'decoded':True,'nonblank_pixel_variation':True})
 def plot(gene,d,title):
  fig,ax=plt.subplots(figsize=(12,5.2),layout='constrained');xx=range(5)
  for g in (PRIMARY if gene=='MACRO' else [gene]):
   vals=[next(r['auc'] for r in old if r['gene']==g and r['config_id']==c['config_id']) for c in S.CFG]+[lookup[g]['auc']];ax.plot(xx,vals,'-o',label=g)
  ax.axhline(.5,linestyle=':',color='grey');ax.set(xticks=range(7),xticklabels=['C00 old','C01 old','C02 old','C03 old','U00 replay','U01 SiaRNA','U02 ENsiRNA'],ylim=(0,1.05),ylabel='ROC AUC on the same measured target cohort',title=title,xlabel='Historical configurations, fresh incumbent replay, then unavailable challengers')
  for i in [5,6]:ax.text(i,.96,'NOT RUN\nblocked',ha='center',va='top',fontsize=9,color='#A33')
  ax.legend(loc='lower left');fig.supxlabel('No score is plotted for blocked models. Previously examined data; no new model improvement or biological validation.',fontsize=8);save(fig,d/'performance')
 for task in S.TASKS:
  d=ROOT/'results'/task/RUN;cf=ROOT/'config'/task/RUN
  if task not in ACTIVE:
   status={'task':task,'status':'SKIPPED_NO_APPLICABLE_NEW_MODEL_BENCHMARK','reason':WHY[task],'new_efficacy_predictions':0,'full_application_complete':False};dump(d/'status.json',status);statuses.append(status);continue
  anchor=task.startswith(('003','006'));gene='MYC' if task.startswith('010') else ('MACRO' if task.startswith('001') else 'HK2')
  control={'config_id':IDS[0],'status':'COMPLETED_CONTROL_REPLAY','model':'RN.Ai-Predict','new_model':False,'best_design':None,'full_application_complete':False}
  if anchor:control.update(anchors=newanchors,n=len(tt),metric='known_anchor_rank_no_efficacy_ground_truth');sub=tt
  elif gene=='MACRO':sub=[r for r in rr if r['gene'] in PRIMARY];control.update(metric(sub),macro_auc=macro,delta_macro_auc_vs_prior=macro-prior_macro)
  else:sub=[r for r in rr if r['gene']==gene];control.update(lookup[gene])
  for cid in IDS:
   cd=d/cid;cd.mkdir(exist_ok=False);config=cf/cid/'benchmark_config.json';(cd/'benchmark_config.json').write_bytes(config.read_bytes())
   if cid==IDS[0]:dump(cd/'metrics.json',control);S.csvout(cd/'predictions.csv',sub);result=control
   else:
    name='SiaRNA' if cid==IDS[1] else 'ENsiRNA';result=model_gate(name)|{'config_id':cid,'auc':None,'performance_delta':None,'best_design':None};dump(cd/'status.json',result)
   dump(cd/'provenance.json',{'config_sha256':S.sha(config),'plan_sha256':S.sha(B/'frozen_workflow_plan.json'),'fresh_control_not_upgrade':cid==IDS[0],'new_generation':False,'training':False,'original_gates_recomputed':False,'panels_reranked':False,'no_challenger_scores_fabricated':True})
   ledger.append({'task':task,'config_id':cid,'status':result['status'],'config_path':str(config.relative_to(ROOT)),'result_path':str(cd.relative_to(ROOT)),'efficacy_predictions':len(sub) if cid==IDS[0] else 0,'new_model_efficacy_predictions':0})
  if anchor:
   fig,ax=plt.subplots(figsize=(12,5.2),layout='constrained')
   for name in ['patisiran','vutrisiran']:
    vals=[float(next(r['percentile'] for r in anchors if r['anchor']==name and r['config_id']==c['config_id'])) for c in S.CFG]+[next(r['percentile'] for r in newanchors if r['anchor']==name)];ax.plot(range(5),vals,'-o',label=name)
   ax.set(xticks=range(7),xticklabels=['C00 old','C01 old','C02 old','C03 old','U00 replay','U01 blocked','U02 blocked'],ylim=(0,105),ylabel='Known projected core percentile among 598 windows',title=task+' — anchor diagnostic, not efficacy validation');ax.legend();fig.supxlabel('No new challenger score or invented 21-nt overhang. No clinical potency comparison.',fontsize=8);save(fig,d/'performance')
  else:plot(gene,d,task+(' — n=7, one positive; descriptive only' if gene=='MYC' else ' — fresh incumbent control; upgrades blocked'))
  dump(d/'performance_history.json',{'prior_run':S.RUN,'prior_results_reference':str((ROOT/'results'/task/S.RUN/'performance_history.json').relative_to(ROOT)),'fresh_control':control,'challengers':[model_gate('SiaRNA'),model_gate('ENsiRNA')],'interpretation':'This extends the run history with a software-control replay and explicitly unavailable challenger endpoints, not an improved model.'})
  (d/'REPORT.md').write_text('# '+task+' '+RUN+'\n\nFresh RN.Ai incumbent control executed; SiaRNA and ENsiRNA upgrade branches stopped at readiness gates. No new challenger metrics, model training, candidate generation, panel reranking or full application completion.\n\nSee performance.png and per-config predictions/status. Prior results and frozen biological gates remain unchanged.\n')
  status={'task':task,'status':'CONTROL_RERUN_COMPLETE_UPGRADE_BLOCKED','control_prediction_rows':len(sub),'new_model_efficacy_predictions':0,'full_application_complete':False};dump(d/'status.json',status);statuses.append(status)
 plot('MACRO',B,'Model-upgrade assessment: fresh control replay, no eligible challenger scores');(ROOT/'results/001_general'/RUN/'performance_overview.png').write_bytes((B/'performance.png').read_bytes());(ROOT/'results/001_general'/RUN/'performance_overview.svg').write_bytes((B/'performance.svg').read_bytes())
 dump(B/'figure_validation.json',images);dump(B/'task_status.json',statuses);S.csvout(B/'config_execution_ledger.csv',ledger)
 summary={'run_id':RUN,'status':'PARTIAL_CONTROL_REPLAY_COMPLETED_NEW_MODELS_BLOCKED','task_workflows':len(S.TASKS),'task_control_routes_executed':len(ACTIVE),'unique_incumbent_models_replayed':1,'fresh_unique_measured_pairs':len(rr),'fresh_unique_ttr_windows':len(tt),'blocked_challenger_task_routes':2*len(ACTIVE),'unique_new_challengers_assessed':2,'additional_BERT_candidate':'Code located; no checkpoint files found in current author repository tree. No training permitted.','new_challenger_efficacy_predictions':0,'new_model_promoted':None,'incumbent_retained':'RN.Ai-Predict source-guide convention','macro_auc_HIF1A_HPSE_HK2':macro,'prior_macro_auc_same_cohort':prior_macro,'macro_auc_delta':macro-prior_macro,'fully_complete_application_tasks':0,'new_training':False,'new_design_generation':False,'all_previous_runs_preserved':True,'no_confirmed_performance_improvement':True};dump(B/'results_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run','report','all']);a=p.parse_args()
 if a.action in ['prepare','all']:prepare()
 if a.action in ['run','all']:run()
 if a.action in ['report','all']:report()
