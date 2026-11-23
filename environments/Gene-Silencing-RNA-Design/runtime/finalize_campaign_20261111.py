"""Postprocess only: no regenerated pools or new model predictions except the two declared TTR anchors."""
import pathlib,sys,json,csv,statistics,os
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
import run_campaign_20261111 as C
import benchmark_campaign_20261111 as B
RUN=C.RUN;OUT=C.BMD

def finalize_panels():
 for gene,task in C.OWNERS.items():
  owner=ROOT/'results'/task/RUN;rs=C.rows(owner/'per_dimension_evidence.csv')
  for r in rs:
   r.pop('rank_score',None);r.pop('rank_components',None)
   for key in list(r):
    v=C.number(r,key)
    if v is not None:r[key]=v
  C.csvout(owner/'per_dimension_evidence.csv',rs)
  for t,(g,_) in C.TASKS.items():
   if gene==g:C.rank_task(t,gene,rs,owner)
 # Recompute uncertainty from the already executed fresh predictions, no second inference.
 p=OUT/'simone/metrics.json';m=json.loads(p.read_text());rs=C.rows(OUT/'simone/predictions.csv')
 for a in m['per_accession']:
  rr=[r for r in rs if r['accession']==a]
  mm=B.metrics([float(r['label']) for r in rr],[float(r['rnai_percent']) for r in rr])
  mm['adequacy_note']='Exploratory small n; no row-bootstrap interval when either class has fewer than five observations.' if min(mm['n_positive'],mm['n']-mm['n_positive'])<5 else 'Within-gene overlapping windows; descriptive uncertainty only.'
  m['per_accession'][a]=mm
 m['delta_auc_vs_prior_rounded']=round(m['auc'],4)-m['prior_auc'];m['prior_delta_note']='The tiny unrounded delta is rounding, not a changed prediction; all 322 paired scores match exactly.'
 C.dump(p,m)
 summary=json.loads((OUT/'endpoint_summary.json').read_text());summary['simone']=m;C.dump(OUT/'endpoint_summary.json',summary)

def gene_joins():
 measured=C.rows(OUT/'simone/predictions.csv');comparison=[]
 for gene,acc in [('HK2','NM_000189.5'),('MYC','NM_002467.6')]:
  owner=ROOT/'results'/C.OWNERS[gene]/RUN;pool=C.rows(owner/'generation/candidate_pool_historical.csv');pool.sort(key=lambda r:-float(r['oligoformer_native_score']))
  bysite={int(r['target_start']): (i+1,r) for i,r in enumerate(pool)};joined=[]
  for m in measured:
   if m['accession']!=acc:continue
   rank,r=bysite[int(m['site_index_0based'])+1]
   assert r['guide_sequence'] in (m['guide'][:19],m['guide'][2:21],m['guide'])
   joined.append({'siRNA':m['siRNA'],'candidate_id':r['candidate_id'],'site':r['target_start'],'label':float(m['label']),'rnai_fresh':float(m['rnai_percent']),'oligoformer_historical':float(r['oligoformer_native_score']),'pool_rank':rank,'pool_size':len(pool)})
  of=B.metrics([r['label'] for r in joined],[r['oligoformer_historical'] for r in joined]);rn=B.metrics([r['label'] for r in joined],[r['rnai_fresh'] for r in joined])
  top=sorted(joined,key=lambda r:-r['label'])[:min(10,len(joined))];pcts=[100*(1-r['pool_rank']/r['pool_size']) for r in top]
  report={'gene':gene,'n_joined':len(joined),'OligoFormer':of,'RN.Ai_fresh':rn,'top_measured_percentile_median':statistics.median(pcts),'selection':'Labels joined only after frozen candidate selection and ranking; historical full OligoFormer pool reused, not fresh generation.','comparison_to_published':'OligoFormer paper Huesken->Mixset AUC .8163 is different cohort, not a superiority comparator. MYC n=7 one positive: metrics exploratory, no robust discrimination claim.'}
  C.csvout(OUT/(gene+'_posthoc_join.csv'),joined);C.dump(OUT/(gene+'_posthoc_metrics.json'),report)
  priorfile=ROOT/('benchmark/002_Oncology-HPSE-HK2-cohorts/HK2_benchmark_join.json' if gene=='HK2' else 'benchmark/010_Gene-regulation-MYC-cohort/MYC_benchmark_join.json');prior=json.loads(priorfile.read_text())
  comparison.append({'benchmark':gene+'_OligoFormer','endpoint':'AUC cutoff .7','published_value':.8163,'published_comparability':'Different cohort; no direct delta','prior_value':prior.get('OligoFormer',{}).get('auc'),'run3_value':of['auc'],'run3_generation':'HISTORICAL_POOL_REUSED','run3_inference':'Fresh RN.Ai; reused OligoFormer scores','n':len(joined)})
 return comparison

def anchors():
 historical=json.loads((ROOT/'benchmark/003_TTR-approved-drugs-cohort/drug_site_rank_audit.json').read_text())
 owner=ROOT/'results/003_genetic-disease-total-lowering'/RUN
 pool=C.rows(owner/'generation/all_generated_candidates.csv');pool.sort(key=lambda r:-float(r['oligoformer_native_score']))
 d=OUT/'ttr_same_side';d.mkdir(exist_ok=False);inp=[];rankrows=[]
 for name,rec in historical['drug_sites'].items():
  # Declared 19-nt core projection, not evaluation of the clinical-format modified duplex.
  g=rec['guide'][:19];p=B.rc(g);idx=next(i for i,r in enumerate(pool) if r['guide_sequence']==g);r=pool[idx]
  inp.append({'candidate_id':name+'_derived_19nt_core','target_gene':'TTR','transcript_id':'ENST00000237014.8','guide_sequence':g,'passenger_sequence':p,'target_start':r['target_start'],'target_end':r['target_end']})
  rankrows.append({'drug':name,'prior_rank':rec['rank_in_pool'],'run3_rank':idx+1,'rank_delta':idx+1-rec['rank_in_pool'],'pool_size':len(pool),'prior_oligoformer_score':rec['oligoformer_score'],'run3_oligoformer_score':float(r['oligoformer_native_score']),'sequence_provenance':'Historical hash-bound drug-site audit; not newly independently reverified clinical drug substance. Explicit guide[:19] projection; does not model chemical modifications or clinical overhangs.'})
 C.csvout(d/'anchor_candidates.csv',inp)
 C.cmd([sys.executable,'-B',C.BENCH/'inference.py','--candidates',d/'anchor_candidates.csv','--transcript',owner/'00_inputs/transcript.fa','--job-id','TTR_anchors_'+RUN,'--out-dir',d/'battery','--config',owner/'00_inputs/harness_thresholds.yaml'],d/'execution.log')
 raw=C.rows(d/'battery/final_ranked_candidates.csv');out=[]
 from sirna_bench.adapters import offtarget
 for r in raw:
  i=next(z for z in inp if z['candidate_id']==r['candidate_id']);f=C.scan(i['guide_sequence'],i['passenger_sequence']);hits=offtarget.full_length_hits(i['passenger_sequence'],'ENST00000237014.8',target_gene='TTR')
  rr={k:v for k,v in r.items() if k not in ('rank_score','rank_components')};rr.update(i);rr['immune_ugugu_either_strand']=f['any_tlr7_motif'];rr['passenger_full_length_offtarget_hits']=sum(not h.is_intended_target for h in hits);out.append(rr)
 panel=C.rows(owner/'delivered_panel.csv');cols=['eff_RN.Ai-Predict','guide_target_duplex_delta_g_kcal_mol','pots_seed_percentile','seed_tox_viability_avg_human','full_length_offtarget_hits','passenger_full_length_offtarget_hits']
 summary={col:{'anchor_core_median':statistics.median(float(r[col]) for r in out),'generated_panel_median':statistics.median(float(r[col]) for r in panel),'units':'Native column units; not pooled across dimensions'} for col in cols}
 C.csvout(d/'per_dimension_anchor_evidence.csv',out);C.dump(d/'site_rank_comparison.json',rankrows);C.dump(d/'same_side_comparison.json',{'n_anchor_cores':len(out),'n_generated_panel':len(panel),'metrics':summary,'interpretation':'Descriptive same-battery comparison of unmodified 19-nt projected cores; NOT a comparison of clinical drugs or experimental potency. No fitted labels, no efficacy blending; raw harness legacy composite ignored.','offtarget_caveat':'Heuristic bowtie2 <=1 mismatch; max_hits=50 parameter may return up to 100 alignments; counts not exhaustive.'})
 return rankrows

if __name__=='__main__':
 finalize_panels();comparisons=gene_joins();a=anchors();C.csvout(OUT/'gene_model_comparisons.csv',comparisons);print(json.dumps({'gene_comparisons':comparisons,'TTR_anchor_ranks':a},indent=2))
