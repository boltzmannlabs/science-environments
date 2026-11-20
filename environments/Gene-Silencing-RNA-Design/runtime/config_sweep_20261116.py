"""Fixed, retrospective configuration sweep. Preserve old runs; no label-tuned gates or ensembles.
Use the pinned siRNA-Bench Python. Prepare freezes every config before inference.
"""
import argparse,csv,datetime,hashlib,json,math,os,pathlib,subprocess,sys,time
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN='Run-4_2026-11-16'
OLD='Run-3_2026-11-11';OLD_B=ROOT/'benchmark/011_Campaign-reproduction'/OLD
OUT=ROOT/'benchmark/012_Config-sweep'/RUN
EXTERNAL=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/siRNA-Design-Task-Specific')
BASE=pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench')
sys.path[:0]=[str(ROOT/'runtime'),str(BASE/'src')]
from sirna_context_audit import AuditedPredictors,rc
TASKS=['001_general','002_oncology','003_genetic-disease-total-lowering','004_genetic-disease-allele-selective','005_metabolic-liver-galnac','006_systemic-lnp','007_neuro-cns','008_inflammation-immune','009_functional-genomics','010_gene-regulation','011_drug-target-validation']
CFG=[{'config_id':'C00_rnai_native21','ordinal':0,'model':'RN.Ai-Predict','guide_projection':'source_verbatim_19_to_21','score_units':'predicted_percent_inhibition','purpose':'Prior RN.Ai convention; explicit site/context audit added.'},{'config_id':'C01_rnai_core19','ordinal':1,'model':'RN.Ai-Predict','guide_projection':'first_19_nt','score_units':'predicted_percent_inhibition','purpose':'Input-length ablation: zero-pad guide tokens 20/21 rather than retaining source overhang tokens.'},{'config_id':'C02_rnaispline_core19','ordinal':2,'model':'RNAiSpline','guide_projection':'first_19_nt','score_units':'native_effective_class_softmax','purpose':'Alternate independent efficacy endpoint; never averaged with RN.Ai/OligoFormer.'},{'config_id':'C03_oligoformer_core19','ordinal':3,'model':'OligoFormer','guide_projection':'first_19_nt','score_units':'native_class1_times_1.341','purpose':'Reuse full-pool native scores with coordinate/sequence identity checks; no fresh OligoFormer forward pass.'}]
DUPLEX=[{'config_id':'D00_dangles2','ordinal':0,'dangles':2,'noLP':False},{'config_id':'D01_dangles0','ordinal':1,'dangles':0,'noLP':False},{'config_id':'D02_dangles1','ordinal':2,'dangles':1,'noLP':False},{'config_id':'D03_dangles2_noLP','ordinal':3,'dangles':2,'noLP':True}]
NEURO=[{'config_id':'N00_rnai_native21_Nflanks','ordinal':0,'projection':'native21','context':'N19_core19_N19'},{'config_id':'N01_rnai_core19_Nflanks','ordinal':1,'projection':'core19','context':'N19_core19_N19'},{'config_id':'N02_rnai_native21_footprint_only','ordinal':2,'projection':'native21','context':'reported_guide_reverse_complement_only'}]
SKIP={'005_metabolic-liver-galnac':'No matched measured PCSK9 sequence-efficacy cohort verified; clinical inclisiran outcomes are not predictor labels.','008_inflammation-immune':'No matched TNF efficacy cohort; immune set has only one retained negative and is unsuitable for performance-driven rule tuning. Frozen hazard rules unchanged.'}
GENES={'NM_001530.4':'HIF1A','NM_001098540.3':'HPSE','NM_000189.5':'HK2','NM_002467.6':'MYC','NM_001904.4':'not_optimized_NM_001904.4','NM_004456.5':'not_optimized_NM_004456.5'}

def dump(p,o):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,allow_nan=False,default=str)+'\n')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def readcsv(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def csvout(p,rs):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 fields=list(dict.fromkeys(k for r in rs for k in r)) or ['row_id']
 with open(p,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def fasta(p):
 records={};key=None
 with open(p) as f:
  for line in f:
   if line.startswith('>'):key=line[1:].split()[0];records[key]=''
   elif key:records[key]+=line.strip().upper().replace('T','U')
 return records

def configset(task):
 if task in SKIP:return []
 if task.startswith('004'):return DUPLEX
 if task.startswith('007'):return NEURO
 return CFG

def prepare():
 if OUT.exists():raise RuntimeError('Fresh sweep directory required; do not overwrite a prior sweep')
 OUT.mkdir(parents=True)
 plan={'run_id':RUN,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FIXED_CONFIGS_FROZEN_BEFORE_NEW_INFERENCE','question':'Do explicitly declared input projections or existing independent predictors improve retrospective measured-cohort ordering over native RN.Ai?','provider':'Pinned local backends under prior explicit local-fallback approval; no new remote jobs. Boltzmann siRNA contract inspected; it exposes no RN.Ai core-tokenization, RNAiSpline, batching or physical-dangle configuration controls.','config_order':CFG,'duplex_sensitivity_configs':DUPLEX,'degraded_context_controls':NEURO,'selection_protocol':{'comparison_cohorts':['HIF1A','HPSE','HK2'],'small_n_descriptive_only':['MYC'],'common_oligoformer_cohort_n_expected':308,'primary_efficacy_metric':'ROC AUC at observed label >=0.7; native endpoints kept separate','selection':'For each of three eligible target genes, choose among each prefix of frozen configs using mean AUC on the OTHER TWO genes; report selected config AUC on that gene. No ensemble or refit.','exposure_warning':'All these historical cohorts were examined previously. Retrospective leave-one-target-out is NOT an untouched prospective holdout.','bootstrap':'1000 paired class-stratified row resamples for exploratory AUC/delta intervals; shared/overlapping sites violate row independence; no superiority claim. Small class counts <5 suppress intervals.','TTR':'Two fixed known drug-core anchors ranked among all 598 windows. No config is selected to optimize their rank. Clinical outcomes never treated as sequence labels.','HTT':'Thermodynamic dangle/noLP and missing-context sensitivity only. No new allele/CNS design or config promotion.'},'immutable_gates':{'path':'config/thresholds.v1.0.frozen.json','sha256':sha(ROOT/'config/thresholds.v1.0.frozen.json')},'models_refitted':False,'weights_downloaded':False,'prior_results_overwritten':False}
 dump(OUT/'frozen_plan.json',plan)
 copied=[]
 for task in TASKS:
  parent=ROOT/'config'/task;parent.mkdir(exist_ok=True)
  num=task.split('_')[0];examples=sorted((ROOT/'config').glob(num+'_*.request.example.json'))
  for p in examples:
   dest=parent/p.name
   if dest.exists():raise RuntimeError('Refuse to overwrite existing task configuration copy '+str(dest))
   dest.write_bytes(p.read_bytes());copied.append({'original':str(p.relative_to(ROOT)),'copy':str(dest.relative_to(ROOT)),'sha256':sha(p)})
  d=parent/RUN;d.mkdir(exist_ok=False)
  status='SKIPPED_NO_VALID_OPTIMIZATION_BENCHMARK' if task in SKIP else ('DESCRIPTIVE_ONLY' if task.startswith(('003','004','006','007','010')) else 'RETROSPECTIVE_MEASURED_COHORT_SWEEP')
  for cfg in configset(task):
   cf=d/cfg['config_id'];cf.mkdir()
   payload={'task':task,'run_id':RUN,'config':cfg,'mode':'benchmark_or_evaluate_only','status':'PLANNED','selection_status':status,'frozen_plan_sha256':sha(OUT/'frozen_plan.json'),'thresholds_sha256':plan['immutable_gates']['sha256'],'labels_used_for_candidate_generation':False,'data_exposure':'Previously examined retrospective public-cohort data','best_design':None}
   dump(cf/'benchmark_config.json',payload)
   old=ROOT/'results'/task/OLD/'00_inputs/requirement_brief.json'
   if old.exists():(cf/'prior_requirement_brief_reference.json').write_bytes(old.read_bytes())
  dump(d/'eligibility.json',{'task':task,'status':status,'reason':SKIP.get(task,'Evaluation configs fixed; full application completion and biological efficacy not asserted.'),'config_count':len(configset(task))})
  (parent/'README.md').write_text('# '+task+' configurations\n\nRoot-level examples are preserved byte-identical; copies here are syntax references, not approved defaults.\n\n'+RUN+': '+status+'. '+SKIP.get(task,'See frozen per-config benchmark_config.json files and matching results folders.')+'\n\nAll models are separate endpoints; frozen biological gates are unchanged. The config order is a fixed experiment grid, not a guaranteed convergent training process.\n')
  rd=ROOT/'results'/task/RUN;rd.mkdir(parents=True,exist_ok=False)
  if task in SKIP:dump(rd/'status.json',{'status':status,'reason':SKIP[task],'configs_executed':0,'best_design':None})
 dump(OUT/'config_copy_provenance.json',copied)
 print(json.dumps({'run_id':RUN,'tasks':len(TASKS),'configs':sum(len(configset(t)) for t in TASKS),'skipped_tasks':SKIP},indent=2))

def pool_paths():
 return {'HIF1A':EXTERNAL/'07_case_study/generation/all_generated_candidates.csv','HPSE':EXTERNAL/'11_app_benchmarks/hpse/generation/all_generated_candidates.csv','HK2':ROOT/'results/002_oncology'/OLD/'generation/candidate_pool_historical.csv','MYC':ROOT/'results/010_gene-regulation'/OLD/'generation/candidate_pool_historical.csv'}

def infer():
 if not (OUT/'frozen_plan.json').exists():raise RuntimeError('Prepare/freeze configs first')
 if (OUT/'inference_summary.json').exists():raise RuntimeError('Inference completed; do not overwrite it')
 old=readcsv(OLD_B/'simone/predictions.csv');mrnas=fasta(BASE/'external/siRNADiscovery/Data/Simone/mrna_Simone.fas')
 measured=[]
 for r in old:
  g=r['guide'];tx=mrnas[r['accession']];i=int(r['site_index_0based']);assert tx[i:i+19]==rc(g[:19]);ctx=tx[max(0,i-19):i+38]
  measured.append({'row_id':r['siRNA'],'gene':GENES[r['accession']],'accession':r['accession'],'guide_source':g,'context':ctx,'site_index_0based':i,'label':float(r['label']),'cohort':'Simone','prior_rnai':float(r['rnai_percent'])})
 csvout(OUT/'measured_input_audit.csv',measured)
 preds=AuditedPredictors();allout=[];timings=[]
 for cfg in CFG[:3]:
  t=time.monotonic();cid=cfg['config_id'];pairs=[(r['guide_source'] if cfg['ordinal']==0 else r['guide_source'][:19],r['context']) for r in measured]
  vals=preds.spline_batch(pairs) if cfg['model']=='RNAiSpline' else preds.rnai_batch(pairs)
  out=[{**r,**v,'config_id':cid,'model':cfg['model'],'model_guide':pairs[i][0],'score_units':cfg['score_units'],'execution':'FRESH_LOCAL_INFERENCE'} for i,(r,v) in enumerate(zip(measured,vals))]
  csvout(OUT/(cid+'_measured_predictions.csv'),out);allout+=out;timings.append({'config_id':cid,'dataset':'Simone','rows':len(out),'elapsed_seconds':time.monotonic()-t})
  print('EXECUTED',cid,len(out),flush=True)
 # Native cached OligoFormer comparison; exact sequence and coordinate join, never invented scores.
 cfg=CFG[3];lookups={};sources=[]
 for gene,path in pool_paths().items():
  pool=readcsv(path);lookups[gene]={int(r['target_start'])-1:r for r in pool};sources.append({'gene':gene,'path':str(path),'sha256':sha(path),'fresh_generation':False})
 out=[];missing=[]
 for r in measured:
  if r['gene'] not in lookups:missing.append({'row_id':r['row_id'],'reason':'No verified historical OligoFormer pool for transcript'});continue
  p=lookups[r['gene']][r['site_index_0based']];assert p['guide_sequence']==r['guide_source'][:19]
  out.append({**r,'score':float(p['oligoformer_native_score']),'status':'ok','config_id':cfg['config_id'],'model':cfg['model'],'model_guide':r['guide_source'][:19],'score_units':cfg['score_units'],'execution':'HASH_BOUND_HISTORICAL_NATIVE_SCORE_REUSE'})
 csvout(OUT/(cfg['config_id']+'_measured_predictions.csv'),out);allout+=out;dump(OUT/'oligoformer_pool_sources.json',sources);csvout(OUT/'oligoformer_exclusions.csv',missing)
 csvout(OUT/'all_measured_predictions.csv',allout)
 # Full TTR pool is fixed. Anchor identities are joined only after all score vectors are produced.
 path=ROOT/'results/003_genetic-disease-total-lowering'/OLD/'00_inputs/candidate_pool.csv';pool=readcsv(path);tx=''.join((ROOT/'results/003_genetic-disease-total-lowering'/OLD/'00_inputs/transcript.fa').read_text().splitlines()[1:]);tt=[]
 for r in pool:
  i=int(r['target_start'])-1;g=r['guide_sequence'];assert rc(g)==tx[i:i+19]
  tt.append({'row_id':r['candidate_id'],'gene':'TTR','guide_source':g,'context':tx[max(0,i-19):i+38],'site_index_0based':i,'oligoformer_native_score':float(r['oligoformer_native_score'])})
 tout=[];rnvals=None
 for cfg in CFG:
  t=time.monotonic();cid=cfg['config_id']
  if cfg['ordinal']==0:
   rnvals=preds.rnai_batch([(r['guide_source'],r['context']) for r in tt]);vals=rnvals;execution='FRESH_LOCAL_INFERENCE'
  elif cfg['ordinal']==1:vals=rnvals;execution='IDENTICAL_19NT_INPUTS_REUSE_CONFIG00_PREDICTIONS'
  elif cfg['ordinal']==2:vals=preds.spline_batch([(r['guide_source'],r['context']) for r in tt]);execution='FRESH_LOCAL_INFERENCE'
  else:vals=[{'score':r['oligoformer_native_score'],'status':'ok'} for r in tt];execution='HASH_BOUND_HISTORICAL_NATIVE_SCORE_REUSE'
  rr=[{**r,**v,'config_id':cid,'execution':execution,'score_units':cfg['score_units']} for r,v in zip(tt,vals)]
  tout+=rr;timings.append({'config_id':cid,'dataset':'TTR','rows':len(rr),'elapsed_seconds':time.monotonic()-t});print('EXECUTED TTR',cid,len(rr),flush=True)
 csvout(OUT/'ttr_pool_predictions.csv',tout)
 # HTT missing-context controls are not therapeutic design or valid-context model optimization.
 src=readcsv(OLD_B/'allele_reporter_energies.csv');nout=[]
 for cfg in NEURO:
  pairs=[]
  for r in src:
   g=r['guide_sequence'][:19] if cfg['projection']=='core19' else r['guide_sequence'];ctx='N'*19+rc(r['guide_sequence'][:19])+'N'*19 if cfg['context'].startswith('N19') else rc(r['guide_sequence'])
   pairs.append((g,ctx))
  vals=preds.rnai_batch(pairs,allow_unknown_flanks=True)
  for r,(g,c),v in zip(src,pairs,vals):nout.append({'row_id':r['candidate_id'],'config_id':cfg['config_id'],'guide_source':r['guide_sequence'],'model_guide':g,'context':c,'ic50_match_nM':float(r['match_ic50_nM']),**v,'context_quality':'NO_REAL_FLANKS_DEGRADED_CONTROL','biological_design_status':'NOT_RUN'})
 csvout(OUT/'htt_context_control_predictions.csv',nout)
 # Thermodynamic sensitivity uses exact paper-defined reporter footprints only, temperature held at 37 C.
 dout=[];binary=BASE/'external/envs/biotools/bin/RNAduplex'
 for cfg in DUPLEX:
  for r in src:
   energies=[];raw=[];command=[str(binary),'-T','37','-d',str(cfg['dangles'])]+(['--noLP'] if cfg['noLP'] else [])
   for target in [r['reporter_match_footprint'],r['reporter_mismatch_footprint']]:
    p=subprocess.run(command,input=r['guide_sequence']+'\n'+target+'\n',capture_output=True,text=True,check=True,timeout=30)
    import re
    m=re.search(r'\(\s*(-?\d+\.\d+)\s*\)',p.stdout)
    if m is None:raise RuntimeError('No numeric RNAduplex result')
    energies.append(float(m.group(1)));raw.append(p.stdout)
   dout.append({'row_id':r['candidate_id'],'config_id':cfg['config_id'],'dg_match':energies[0],'dg_mismatch':energies[1],'ddg':energies[1]-energies[0],'log10_DR':math.log10(float(r['discrimination_ratio_bound'])),'censored':r['discrimination_ratio_censored'],'command':json.dumps(command),'raw_match':raw[0],'raw_mismatch':raw[1]})
  print('EXECUTED',cfg['config_id'],flush=True)
 csvout(OUT/'htt_duplex_predictions.csv',dout)
 native=[r for r in allout if r['config_id']==CFG[0]['config_id']];delta=max(abs(r['score']-r['prior_rnai']) for r in native)
 if delta>.011:raise RuntimeError('Fresh RN.Ai baseline differs from prior native predictions')
 dump(OUT/'batch_native_checks.json',preds.validation_checks);csvout(OUT/'timings.csv',timings)
 dump(OUT/'inference_summary.json',{'status':'COMPLETED','measured_rows':len(measured),'common_measured_rows':len(out),'configurations':len(CFG),'native_baseline_max_abs_score_delta_vs_prior':delta,'model_fit_performed':False,'upstream_code_modified':False,'helper_sha256':sha(ROOT/'runtime/sirna_context_audit.py'),'frozen_plan_sha256':sha(OUT/'frozen_plan.json'),'timings':timings,'notes':'Identical TTR C00/C01 inputs share predictions explicitly. OligoFormer scores are reused, not freshly generated. Three HTT context and four physical-model controls are descriptive only.'})
 print('INFERENCE_COMPLETE',OUT,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','infer']);a=p.parse_args();prepare() if a.action=='prepare' else infer()
