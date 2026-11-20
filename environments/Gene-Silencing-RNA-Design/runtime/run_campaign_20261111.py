"""Approved computational campaign. Immutable inputs; new directories; no label-based selection.
Run with the pinned siRNA-Bench Python. --gene evaluates one explicitly configured target.
Existing full OligoFormer pools may be reused only with a historical-source manifest.
"""
import argparse,csv,hashlib,json,os,pathlib,subprocess,sys,time,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
RUN='Run-3_2026-11-11'
BMD=ROOT/'benchmark/011_Campaign-reproduction'/RUN
SOURCE=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/siRNA-Design-Task-Specific')
BENCH=pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench')
GEN=pathlib.Path('/home/boltzmann13/.sci/profiles/imran/workspace/oligoformer-integration')
BIO=BENCH/'external/envs/biotools/bin'
sys.path[:0]=[str(ROOT/'runtime'),str(BENCH/'src')]
from immune_scan import scan,add_cohort_deciles
from rank_by_requirements import run as rank_run
from sirna_bench.adapters import offtarget,seed_toxicity
TASKS={
 '001_general':('TTR','001_design.request.example.json'),
 '002_oncology':('HK2','002_oncology.request.example.json'),
 '003_genetic-disease-total-lowering':('TTR','003_genetic-disease-total-lowering.request.example.json'),
 '005_metabolic-liver-galnac':('PCSK9','005_metabolic-liver-galnac.request.example.json'),
 '006_systemic-lnp':('TTR','006_systemic-lnp.request.example.json'),
 '008_inflammation-immune':('TNF','008_inflammation-immune.request.example.json'),
 '009_functional-genomics':('HK2','009_functional-genomics.request.example.json'),
 '010_gene-regulation':('MYC','010_gene-regulation.request.example.json'),
 '011_drug-target-validation':('HK2','011_drug-target-validation.request.example.json')}
OWNERS={'TTR':'003_genetic-disease-total-lowering','HK2':'002_oncology','MYC':'010_gene-regulation','PCSK9':'005_metabolic-liver-galnac','TNF':'008_inflammation-immune'}
ACCESSIONS={'TTR':'ENST00000237014.8','HK2':'NM_000189.5','MYC':'NM_002467.6','PCSK9':'NM_174936.4','TNF':'NM_000594.4'}
ENV=os.environ.copy();ENV.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2')
ENV['PATH']=str(pathlib.Path(sys.executable).parent)+os.pathsep+str(BIO)+os.pathsep+ENV.get('PATH','')
TH=json.loads((ROOT/'config/thresholds.v1.0.frozen.json').read_text())

def dump(p,obj):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,allow_nan=False,default=str)+'\n')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def rows(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def csvout(p,rs):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if not rs:p.write_text('candidate_id\n');return
 fields=list(dict.fromkeys(k for r in rs for k in r))
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def cmd(args,log,timeout=2400):
 t=time.monotonic()
 with open(log,'w') as f:r=subprocess.run([str(x) for x in args],env=ENV,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 dump(str(log)+'.command.json',{'command':[str(x) for x in args],'returncode':r.returncode,'elapsed_seconds':time.monotonic()-t})
 if r.returncode:raise RuntimeError('Command failed: '+str(log))
def number(r,k):
 try:
  v=float(r[k]);return v if math.isfinite(v) else None
 except (KeyError,TypeError,ValueError):return None

def setup(gene):
 owner=ROOT/'results'/OWNERS[gene]/RUN;inp=owner/'00_inputs';inp.mkdir(parents=True,exist_ok=True)
 fasta=inp/'transcript.fa'
 if not fasta.exists():fasta.write_bytes((BMD/(gene+'_RNA.fa')).read_bytes())
 seq=''.join(fasta.read_text().splitlines()[1:]);assert set(seq)<=set('AUCG')
 for task,(g,example) in TASKS.items():
  if g!=gene:continue
  d=ROOT/'results'/task/RUN;di=d/'00_inputs';di.mkdir(parents=True,exist_ok=True)
  b=json.loads((ROOT/'config'/example).read_text())
  b.update(brief_id=task+'_'+RUN,mode='design',success_criteria='Computational benchmark campaign only; no measured knockdown asserted.')
  b['target']={'organism':'human','gene':gene,'transcript':ACCESSIONS[gene],'sequence_supplied':True}
  b['objective']='Single-reference human '+gene+' computational knockdown reagent prioritization; application context only, not therapeutic validation.'
  b['constraints'].update(review_window=100,panel_size=6,seed_distinct=True)
  dump(di/'requirement_brief.json',b)
  dump(di/'thresholds.json',TH)
  dump(di/'resolution_decisions.json',{'approval':'User approved paper-backed targets and defaults; subsequently approved local fallback after Boltzmann terminal failure.','isoform_decision':'Declared single versioned reference only; do not claim all expressed isoforms or isoform selectivity.','target_selection':gene+' selected for exact public reference and existing measured-cohort or drug-anchor evidence. HK2 reused across application frames; not independent validations.','config_delta':'Fresh bounded same-engine battery replay; correct gene scoping; both-strand audit; explicit hard gates before requirement ranking. No gate loosening.','review_budget':100,'full_battery_budget':24,'site_diversity_minimum_start_distance_nt':19,'chemistry_delivery':'Context only; unmodified 19-nt cores, not clinical formulations.','WT_sparing':'Not established; total lowering is not mutant selective.','known_ranking_limits':'Original v1.1 ranker has no immune weighted component; hard immune filters applied upstream; remaining immune weight contributes zero. No new efficacy ensemble.','source_fasta':str(fasta),'source_sha256':sha(fasta),'engine':'repo runtime v1.2.1 + campaign fail-closed wrapper v1; originals unchanged.'})
  if di/'transcript.fa'!=fasta:(di/'transcript.fa').write_bytes(fasta.read_bytes())
 return owner,fasta,seq

def get_pool(gene,owner,fasta):
 gen=owner/'generation'
 if (gen/'manifest.json').exists():
  m=json.loads((gen/'manifest.json').read_text());assert m['status']=='completed'
  return gen/'all_generated_candidates.csv'
 # Reuse the exact historical full pools for the expensive benchmark targets, not a new generation claim.
 if gene in ('HK2','MYC'):
  src=SOURCE/'11_app_benchmarks'/gene.lower()/'generation/all_generated_candidates.csv'
  assert src.exists()
  gen.mkdir(exist_ok=False)
  (gen/'candidate_pool_historical.csv').write_bytes(src.read_bytes())
  dump(gen/'historical_reuse_manifest.json',{'status':'HISTORICAL_POOL_REUSED_FRESH_BATTERY','source':str(src),'sha256':sha(src),'generation_rerun':False,'reason':'Retain historical full pool for paired comparisons without refitting or label-guided selection.','original_generation_manifest':str(src.parent/'manifest.json')})
  return gen/'candidate_pool_historical.csv'
 cmd([GEN/'venv/bin/python','-B',GEN/'run_local.py','--fasta',fasta,'--out',gen,'--top','100'],owner/'generation_driver.log')
 return gen/'all_generated_candidates.csv'

def evaluate(gene):
 owner=ROOT/'results'/OWNERS[gene]/RUN
 if (owner/'campaign_evaluation.json').exists():raise RuntimeError('Already evaluated; do not overwrite a run')
 owner,fasta,seq=setup(gene)
 poolp=get_pool(gene,owner,fasta);pool=rows(poolp)
 assert len(pool)==len(seq)-18
 comp=str.maketrans('AUCG','UAGC')
 for r in pool:
  start=int(r['target_start'])-1;g=r['guide_sequence'];p=r['passenger_sequence']
  assert seq[start:start+19]==p and g==p.translate(comp)[::-1] and len(g)==19
 pool.sort(key=lambda r:-float(r['oligoformer_native_score']))
 # Freeze generation-only review before any benchmark label join.
 review=pool[:100];selected=[];decisions=[]
 for r in review:
  g,p=r['guide_sequence'],r['passenger_sequence'];flags=scan(g,p);gc=(g.count('G')+g.count('C'))/len(g)
  pots=offtarget.annotate_seed_pots(g).pots_percentile
  via=seed_toxicity.lookup(r['candidate_id'],g,None).viability
  reason=[]
  if flags['any_tlr7_motif']:reason.append('immune_ugugu_either_strand')
  if not TH['gc_min']['value']<=gc<=TH['gc_max']['value']:reason.append('gc')
  if pots is None or pots>TH['max_pots_percentile']['value']:reason.append('pots')
  if via is None or via<TH['min_seed_viability_avg_human']['value']:reason.append('viability')
  if not reason and len(selected)<24:
   selected.append({k:r[k] for k in ['candidate_id','guide_sequence','passenger_sequence','target_start','target_end']}|{'target_gene':gene,'transcript_id':ACCESSIONS[gene]})
  decisions.append({'candidate_id':r['candidate_id'],'cheap_funnel_reasons':';'.join(reason),'selected_for_battery':any(x['candidate_id']==r['candidate_id'] for x in selected)})
 csvout(owner/'00_inputs/review_window.csv',review);csvout(owner/'00_inputs/candidate_pool.csv',pool)
 csvout(owner/'00_inputs/battery_candidates.csv',selected);csvout(owner/'cheap_funnel_decisions.csv',decisions)
 if not selected:
  dump(owner/'campaign_evaluation.json',{'gene':gene,'status':'NO_CHEAP_FUNNEL_SURVIVORS','pool_windows':len(pool),'n_evaluated':0});return
 config=owner/'00_inputs/harness_thresholds.yaml';config.write_text('thresholds: '+json.dumps(TH)+'\n')
 cmd([sys.executable,'-B',BENCH/'inference.py','--transcript',fasta,'--candidates',owner/'00_inputs/battery_candidates.csv','--job-id',gene+'_'+RUN,'--out-dir',owner/'battery','--config',config],owner/'battery_driver.log')
 battery=rows(owner/'battery/final_ranked_candidates.csv');byid={r['candidate_id']:r for r in battery}
 # Explicit passenger near-match screen; harness already screens guides. Counts retain heuristic caps.
 extended=[]
 for r in selected:
  b=byid[r['candidate_id']];b.update(r)
  for key in list(b):
   v=number(b,key)
   if v is not None:b[key]=v
  hits=offtarget.full_length_hits(r['passenger_sequence'],ACCESSIONS[gene],target_gene=gene,max_mismatches=1,max_hits=50)
  b['passenger_full_length_offtarget_hits']=sum(not h.is_intended_target for h in hits)
  b['passenger_same_gene_isoform_hits']=sum(h.is_intended_target for h in hits)
  b['oligoformer_native_score']=float(next(x for x in pool if x['candidate_id']==r['candidate_id'])['oligoformer_native_score'])
  b['GC_fraction']=(r['guide_sequence'].count('G')+r['guide_sequence'].count('C'))/19
  b['E4e']='NOT_RUN(broken-binary)'
  b['offtarget_search_disclosure']='bowtie2 heuristic <=1 mismatch; max_hits=50 parameter requests up to 100 alignments; returned count is not exhaustive; same-gene isoforms excluded.'
  b.pop('rank_score',None);b.pop('rank_components',None)
  b['evidence_status']='NEEDS_EXPERIMENTAL_VALIDATION';extended.append(b)
 csvout(owner/'per_dimension_evidence.csv',extended)
 dump(owner/'campaign_evaluation.json',{'gene':gene,'status':'COMPUTATIONAL_BATTERY_EXECUTED','pool_windows':len(pool),'reviewed':len(review),'n_evaluated':len(extended),'generation_source':str(poolp),'generation_sha256':sha(poolp),'best_design':None,'not_run':['E4e RNAhybrid broken-binary','GTEx/HPA tissue context','OpenTargets orthogonal context','6/8-mer transcriptome counts (adapter provides only 7-mer)','experimental validation','sequence-based delivery/chemistry prediction'],'scope':'Single declared transcript; not all-isoform coverage; expression and clinical suitability unverified.'})
 for task,(g,example) in TASKS.items():
  if g==gene:rank_task(task,gene,extended,owner)
 print(json.dumps({'gene':gene,'windows':len(pool),'reviewed':len(review),'battery':len(extended)},indent=2),flush=True)

def rank_task(task,gene,extended,owner):
 # The inherited harness emits a blended legacy rank score. Preserve it only in raw battery outputs;
 # it is not a permitted endpoint or ranking signal for this campaign.
 extended=[{k:v for k,v in r.items() if k not in ('rank_score','rank_components')} for r in extended]
 d=ROOT/'results'/task/RUN;b=json.loads((d/'00_inputs/requirement_brief.json').read_text())
 flags=add_cohort_deciles([scan(r['guide_sequence'],r['passenger_sequence']) for r in extended])
 survivors=[];sflags=[];gate=[]
 for r,f in zip(extended,flags):
  failed=[];missing=[]
  checks=[('eff_RN.Ai-Predict',max(TH['min_rnai_predict_score']['value'],b['priorities']['min_standards'].get('rnai',0)),None),('full_length_offtarget_hits',None,10),('passenger_full_length_offtarget_hits',None,10),('seed_occurrence_fold_over_expected',None,2),('pots_seed_percentile',None,90),('seed_tox_viability_avg_human',50,None),('guide_target_duplex_delta_g_kcal_mol',-45,-25),('GC_fraction',.3,.7)]
  # Honor the frozen optional RNAiSpline threshold if the endpoint was actually supplied.
  if number(r,'eff_RNAiSpline') is not None:checks.append(('eff_RNAiSpline',.5,None))
  for col,lo,hi in checks:
   v=number(r,col)
   if v is None:missing.append(col)
   elif (lo is not None and v<lo) or (hi is not None and v>hi):failed.append(col)
  veto=b['priorities']['hard_vetoes']
  if 'immune_ugugu' in veto and f['any_tlr7_motif']:failed.append('immune_ugugu_either_strand')
  if 'gu_top_decile' in veto and f.get('GU_top_decile_flag'):failed.append('gu_top_decile')
  if 'paralog_full_length_hits' in veto and (number(r,'full_length_offtarget_hits') or number(r,'passenger_full_length_offtarget_hits')):failed.append('paralog_full_length_hits_conservative_any_other_gene')
  gate.append({'candidate_id':r['candidate_id'],'gate_pass':not failed and not missing,'failed':';'.join(failed),'missing':';'.join(missing)})
  if not failed and not missing:survivors.append(dict(r));sflags.append(f)
 csvout(d/'gate_decisions.csv',gate);dump(d/'immune_flags.json',flags)
 # Use the repository ranker only after fail-closed hard gates; no silent missing-dimension pass.
 bb=json.loads(json.dumps(b));bb['priorities']['hard_vetoes']=[];bb['priorities']['min_standards']={}
 rep=rank_run(survivors,bb,sflags,task+'_'+RUN)
 # R3 site-diverse panel from the ranked order, with exact 7-mer seed distinctness.
 def panel_for(weights):
  temp=json.loads(json.dumps(bb));temp['priorities']['weights']=weights;temp['constraints']['panel_size']=max(1,len(survivors))
  rr=rank_run(survivors,temp,sflags,'sensitivity')
  ids={r['candidate_id']:r for r in survivors};out=[];seen=set();starts=[]
  for c in rr['panel']:
   r=ids[c['candidate_id']];seed=r['guide_sequence'][1:8];start=int(r['target_start'])
   if seed in seen or any(abs(start-s)<19 for s in starts):continue
   seen.add(seed);starts.append(start);out.append(r|{'requirement_preference_score':c['S']})
   if len(out)>=b['constraints']['panel_size']:break
  return out
 panel=panel_for(b['priorities']['weights']);base={r['candidate_id'] for r in panel};stability={}
 for dim,w in b['priorities']['weights'].items():
  for fac in (.75,1.25):
   weights=dict(b['priorities']['weights']);weights[dim]=w*fac;other={r['candidate_id'] for r in panel_for(weights)}
   stability[dim+str(fac)]=len(base&other)/len(base|other) if base|other else None
 rep.update(panel=panel,post_diversity_panel_jaccard_pm25pct=stability,ordering_stable=all(v is not None and v==1 for v in stability.values()),best_design=None,evidence_tier='NEEDS_EXPERIMENTAL_VALIDATION',missing_weighted_dimensions=['immune (hard filters only)'],status='PARTIAL_APPLICATION_CONTEXT' if panel else 'NO_PANEL_UNDER_FROZEN_GATES',shared_battery=str(owner/'per_dimension_evidence.csv'),not_run=['E4e NOT_RUN(broken-binary)','GTEx/HPA expression context','OpenTargets orthogonal evidence','6/8-mer occurrence counts','CDS/UTR and Tm annotations'],interpretation='All predictions are computational; no negative screen proves safety or specificity; panels not synthesis/clinical-qualified.')
 dump(d/'ranking_and_stability.json',rep);csvout(d/'delivered_panel.csv',panel)
 if d!=owner:csvout(d/'per_dimension_evidence.csv',extended)
 dump(d/'provenance.json',{'shared_battery':str(owner),'brief_sha256':sha(d/'00_inputs/requirement_brief.json'),'threshold_sha256':sha(d/'00_inputs/thresholds.json'),'runner_sha256':sha(__file__),'runtime_ranker_sha256':sha(ROOT/'runtime/rank_by_requirements.py'),'source_inputs_read_only':True,'provider':'local approved fallback','generation_fresh':gene not in ('HK2','MYC'),'best_design':None})
 (d/'REPORT.md').write_text('# '+task+' '+RUN+'\n\nStatus: '+rep['status']+'; computational evidence only.\n\nPool reviewed: 100 maximum; full battery: '+str(len(extended))+'; gate survivors: '+str(len(survivors))+'; panel: '+str(len(panel))+'.\n\nNo wet-lab validation; best_design=null. E4e NOT_RUN(broken-binary). Missing expression/orthogonal/6-8mer/annotation stages prevent full task completion.\n\nHK2/MYC use historical full generation pools with fresh battery execution; TTR/PCSK9/TNF use fresh generation. Shared-target application frames are not independent biological benchmarks. Immune weight has no scoring component in the inherited ranker and contributes zero after hard filtering. Missing E4e/context is not imputed as a pass.\n\nSee per_dimension_evidence.csv, gate_decisions.csv, ranking_and_stability.json, and provenance.json.\n')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--gene',required=True,choices=list(OWNERS));a=ap.parse_args();evaluate(a.gene)
