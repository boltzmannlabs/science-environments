"""Fresh public-cohort endpoint runs, paired historical comparisons, and primary-table curation.
No model fitting, threshold tuning, inferred genomic mutants, or clinical efficacy claims.
"""
import csv,json,math,pathlib,sys,os,re,subprocess,hashlib
import numpy as np
from scipy.stats import rankdata,pearsonr,spearmanr
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN='Run-3_2026-11-11'
OUT=ROOT/'benchmark/011_Campaign-reproduction'/RUN
BENCH=pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench')
sys.path[:0]=[str(BENCH/'src'),str(ROOT/'runtime')]
from sirna_bench.adapters.efficacy import RnAiPredictAdapter
from immune_scan import scan

def dump(p,obj):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,allow_nan=False,default=str)+'\n')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def csvout(p,rs):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with open(p,'w',newline='') as f:
  keys=list(dict.fromkeys(k for r in rs for k in r));w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
def rows(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def fasta(p):
 recs={};key=None
 for l in open(p):
  if l.startswith('>'):key=l[1:].split()[0];recs[key]=''
  elif key:recs[key]+=l.strip().upper()
 return recs
def rc(s):return s.translate(str.maketrans('AUCG','UAGC'))[::-1]
def auc(y,s):
 y=np.asarray(y);s=np.asarray(s);n1=int(y.sum());n0=len(y)-n1
 return float((rankdata(s)[y==1].sum()-n1*(n1+1)/2)/(n1*n0)) if n1 and n0 else None
def corr(x,y,rank=False):
 if len(x)<3 or len(set(x))<2 or len(set(y))<2:return None
 return float(spearmanr(x,y).statistic if rank else pearsonr(x,y).statistic)
def metrics(labels,scores,seed=42):
 y=np.array(labels)>=.7;s=np.array(scores);obs=auc(y,s)
 rng=np.random.default_rng(seed);boot=[]
 if obs is not None and min(int(y.sum()),int((~y).sum()))>=5:
  ip=np.where(y)[0];ineg=np.where(~y)[0]
  for _ in range(2000):
   ii=np.r_[rng.choice(ip,len(ip)),rng.choice(ineg,len(ineg))];boot.append(auc(y[ii],s[ii]))
 return {'n':len(y),'n_positive':int(y.sum()),'cutoff':.7,'auc':obs,'pearson':corr(labels,scores),'spearman':corr(labels,scores,True),'auc_ci95_stratified_row_bootstrap':np.quantile(boot,[.025,.975]).tolist() if boot else None,'bootstrap_replicates':len(boot),'ci_scope':'Within-cohort descriptive row resampling; overlapping sites and shared genes violate row independence. Not an external generalization CI.'}
def status(p):return getattr(p.inference_status,'value',p.inference_status)

def simone():
 data=BENCH/'external/siRNADiscovery/Data/Simone';d=OUT/'simone';d.mkdir(exist_ok=False)
 guides=fasta(data/'sirna_Simone.fas');mrnas=fasta(data/'mrna_Simone.fas');eff=rows(data/'Simone_efficacy.csv')
 dump(d/'inputs.json',{'sources':[{ 'path':str(data/x),'sha256':sha(data/x)} for x in ['sirna_Simone.fas','mrna_Simone.fas','Simone_efficacy.csv']],'cohort_source':'Sciabola PMID 23241392; local extraction; original paper dose and model protocols differ.','training_independence':'Historical repo claims independence; no fresh sequence-overlap audit of all training corpora performed.','selection':'All rows; no outcome-based selection; original core matching recipe retained.'})
 ad=RnAiPredictAdapter();output=[];excluded=[]
 for r in eff:
  sid=r['siRNA'];g=guides[sid].replace('T','U');tx=mrnas[r['mRNA']].replace('T','U');hit=None
  for core in [g[:19],g[2:21] if len(g)>=21 else '',g]:
   i=tx.find(rc(core)) if core else -1
   if i>=0:hit=(i,len(core));break
  if hit is None:excluded.append({'siRNA':sid,'reason':'SITE_NOT_FOUND'});continue
  i,n=hit;ctx=tx[max(0,i-19):i+n+19];p=ad.predict_pair(g,ctx)
  output.append({'siRNA':sid,'accession':r['mRNA'],'guide':g,'label':float(r['efficacy']),'site_index_0based':i,'mapped_core_nt':n,'ctx_len':len(ctx),'rnai_percent':p.raw_score,'inference_status':status(p),'applicability':p.applicability_status})
 csvout(d/'predictions.csv',output);dump(d/'excluded.json',excluded)
 ok=[r for r in output if r['inference_status']=='ok' and r['rnai_percent'] is not None]
 m=metrics([r['label'] for r in ok],[r['rnai_percent'] for r in ok]);m.update(n_total=len(eff),n_scored_ok=len(ok),n_excluded=len(excluded),fresh_inference=True,model='RN.Ai-Predict')
 m['per_accession']={a:metrics([r['label'] for r in ok if r['accession']==a],[r['rnai_percent'] for r in ok if r['accession']==a]) for a in sorted({r['accession'] for r in ok})}
 old={r['siRNA']:r for r in rows(ROOT/'benchmark/000_Simone-independent-evaluation/predictions.csv')}
 differences=[abs(r['rnai_percent']-float(old[r['siRNA']]['rnai_percent'])) for r in ok if r['siRNA'] in old]
 m.update(n_paired_prior_predictions=len(differences),max_abs_prediction_delta_vs_prior=max(differences),prior_auc=.7021,delta_auc_vs_prior=m['auc']-.7021,comparison_to_published_oligoformer_auc='Not like-for-like: different model, cohort and experimental protocol; no superiority delta.')
 # Cluster resampling by transcript acknowledges gene dependence, but only four clusters exist.
 rng=np.random.default_rng(42);clusters=sorted(m['per_accession']);bs=[]
 for _ in range(2000):
  selected=rng.choice(clusters,len(clusters));rr=[r for a in selected for r in ok if r['accession']==a];v=auc(np.array([r['label'] for r in rr])>=.7,[r['rnai_percent'] for r in rr])
  if v is not None:bs.append(v)
 m['auc_ci95_transcript_cluster_bootstrap']=np.quantile(bs,[.025,.975]).tolist();m['cluster_bootstrap_caution']='Only '+str(len(clusters))+' transcript clusters; exploratory interval, not robust cross-gene validation.'
 dump(d/'metrics.json',m);return m

def reporter():
 a=json.loads((OUT/'sources/PMC2746439.json').read_text());table=next(t for t in a['tables'] if t['id']=='T2')
 tab=[r for r in table['rows'] if r[0].startswith('rs')];assert len(tab)==26
 allele=[];neuro=[];raw=[];ad=RnAiPredictAdapter();binary=BENCH/'external/envs/biotools/bin/RNAduplex'
 for idx,r in enumerate(tab,1):
  g=re.search(r'[acgu]{19,27}',r[1]).group(0).upper();pos=int(r[2]);gb,tb=r[3].split(':');assert g[pos-1]==gb
  match=list(rc(g));mismatch=list(match)
  # These are paper-defined reporter footprints, not reference-verified patient alleles.
  if r[4]!='none':
   sp=int(r[4]);sg,st=r[5].split(':');assert g[sp-1]==sg
   match[len(g)-sp]=st;mismatch[len(g)-sp]=st
  mismatch[len(g)-pos]=tb;match=''.join(match);mismatch=''.join(mismatch)
  energies=[]
  for target in [match,mismatch]:
   p=subprocess.run([str(binary),'-T','37'],input=g+'\n'+target+'\n',capture_output=True,text=True,check=True,timeout=30)
   energy=float(re.search(r'\(\s*(-?\d+\.\d+)\s*\)',p.stdout).group(1));energies.append(energy);raw.append({'id':idx,'guide':g,'target':target,'stdout':p.stdout,'stderr':p.stderr})
  matchic=float(r[6].split()[0]);dr_censored=r[8].startswith('>');dr=float(r[8].lstrip('>'))
  allele.append({'candidate_id':'Pfister_HTT_%02d'%idx,'snp':r[0],'guide_sequence':g,'paper_primary_mismatch':r[3],'paper_primary_position':pos,'paper_secondary_position':r[4],'paper_secondary_mismatch':r[5],'reporter_match_footprint':match,'reporter_mismatch_footprint':mismatch,'dg_match_kcal_mol':energies[0],'dg_mismatch_kcal_mol':energies[1],'ddg_kcal_mol':energies[1]-energies[0],'discrimination_ratio_bound':dr,'discrimination_ratio_censored':dr_censored,'match_ic50_nM':matchic,'source':'PMC2746439 Table 2','target_derivation':'Reverse complement footprint plus EXACT paper-specified primary and secondary mismatch pairs; no genomic variant or mutant sequence inferred.'})
  # No real mRNA context: N-padded explicitly, never let length-only applicability become an in-domain claim.
  ctx='N'*19+rc(g[:19])+'N'*19;p=ad.predict_pair(g,ctx)
  neuro.append({'candidate_id':'Pfister_HTT_%02d'%idx,'guide_sequence':g,'ic50_match_nM':matchic,'rnai_percent':p.raw_score,'inference_status':status(p),'context_quality':'NO_REAL_FLANKS_N_PADDED_OUT_OF_DOMAIN','adapter_length_based_applicability_untrusted':p.applicability_status})
 d=ROOT/'results/004_genetic-disease-allele-selective'/RUN;d.mkdir(parents=True,exist_ok=True);csvout(d/'published_reporter_energies.csv',allele);dump(d/'RNAduplex_raw.json',raw)
 unc=[r for r in allele if not r['discrimination_ratio_censored']]
 m={'n_reporter_guides':len(allele),'n_uncensored_discrimination_ratios':len(unc),'n_censored_ratios':len(allele)-len(unc),'spearman_ddg_vs_log10_dr_uncensored':corr([r['ddg_kcal_mol'] for r in unc],[math.log10(r['discrimination_ratio_bound']) for r in unc],True),'method':'RNAduplex -T 37; exact PRIMARY TABLE reporter mismatch identities and secondary mismatches. Prior weakest-of-three method is not like-for-like.','design_status':'BLOCKED_PENDING_REFERENCE_VERIFIED_VARIANT_AND_ALLELE_OBJECTIVE','evaluation_status':'PUBLISHED_REPORTER_EVALUATION_EXECUTED','best_design':None,'limitations':'Reporter footprint reconstruction is not transcript/ClinVar/dbSNP/VEP verification; RNAduplex optimal local pairing may realign around a mismatch; thermodynamic margin is not cellular allele selectivity.'}
 dump(d/'evaluation_status.json',m);dump(OUT/'allele_reporter_metrics.json',m);csvout(OUT/'allele_reporter_energies.csv',allele)
 nd=ROOT/'results/007_neuro-cns'/RUN;nd.mkdir(parents=True,exist_ok=True);csvout(nd/'published_guides_predictions.csv',neuro)
 ok=[r for r in neuro if r['inference_status']=='ok' and r['rnai_percent'] is not None]
 nm={'n':len(ok),'spearman_vs_neglog10_ic50':corr([r['rnai_percent'] for r in ok],[-math.log10(r['ic50_match_nM']) for r in ok],True),'prior_spearman':.296,'fresh_inference':True,'context':'NO_REAL_FLANKS_N_PADDED_OUT_OF_DOMAIN; explicitly invalidates adapter length-only in_domain label. Not mathematically guaranteed to be a lower bound.','status':'DEGRADED_CONTEXT_EVALUATION_ONLY','design_status':'NOT_RUN_NO_CONFIRMED_CNS_ISOFORM_OR_REFERENCE','best_design':None}
 dump(nd/'evaluation_status.json',nm);dump(OUT/'neuro_metrics.json',nm)
 return m,nm

def immune():
 data=rows(ROOT/'benchmark/008_Inflammation-IFN-cohort/set1_inflammation.csv');out=[];ex=[];seen=set()
 for r in data:
  sid=r['sequence_id'];reason=None
  if 'siNP' in sid:reason='REVIEW_ONLY_PATHOGEN_TARGET_NOT_EVALUATED'
  elif r['ifn_induction_binary'] not in ('0','1'):reason='OUTCOME_UNVERIFIED'
  elif 'PARTIAL' in r['verification'] or 'LOWRES' in r['verification']:reason='PARTIAL_OR_LOW_RES_OUTCOME_MAPPING'
  if reason:ex.append({'sequence_id':sid,'reason':reason});continue
  def core(s):
   # Explicit assay-format derivation, not silent changes to source sequences.
   return re.sub(r'(?:dTdT|TT)$','',s).upper().replace('T','U')
  g=core(r['antisense_seq'] or r['sense_seq']);p=core(r['sense_seq']) if r['antisense_seq'] else None
  assert set(g)<=set('AUCG') and (p is None or set(p)<=set('AUCG'))
  key=tuple(sorted([g,p or '']))
  if key in seen:ex.append({'sequence_id':sid,'reason':'IDENTICAL_DUPLEX_DUPLICATE'});continue
  seen.add(key);f=scan(g,p)
  out.append({'sequence_id':sid,'guide_derived':g,'passenger_derived':p or '', 'source_sense_verbatim':r['sense_seq'],'source_antisense_verbatim':r['antisense_seq'],'label':int(r['ifn_induction_binary']),'predicted_flag':int(f['any_tlr7_motif']),'derivation':'Remove explicit terminal dTdT or TT notation only; uppercase; T->U; 19-nt core motif scan, not full-format length-class inference.','original_pmid':r['pmid'],'corrected_pmid':'19630977' if sid.startswith('Goodchild') else r['pmid'],'label_evidence':'Inherited source curation; Goodchild paper identity reverified; all per-row supplementary outcomes not independently re-extracted this run.'})
 tp=sum(r['label']==1 and r['predicted_flag']==1 for r in out);fn=sum(r['label']==1 and r['predicted_flag']==0 for r in out);tn=sum(r['label']==0 and r['predicted_flag']==0 for r in out);fp=sum(r['label']==0 and r['predicted_flag']==1 for r in out)
 m={'n':len(out),'tp':tp,'fn':fn,'tn':tn,'fp':fp,'sensitivity':tp/(tp+fn) if tp+fn else None,'specificity':tn/(tn+fp) if tn+fp else None,'prior_sensitivity':.1,'prior_specificity':1.0,'comparison':'NOT_LIKE_FOR_LIKE: stricter row exclusions, explicit pathogen exclusion and exact duplex deduplication; no rule tuning.','limitations':'Small heterogeneous assays; negative motif result does not establish immune safety; do not optimize immune-evasion sequences.'}
 csvout(OUT/'immune_curated_evaluation.csv',out);csvout(OUT/'immune_exclusions.csv',ex);dump(OUT/'immune_metrics.json',m);return m

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 m=simone();a,n=reporter();i=immune()
 dump(OUT/'endpoint_summary.json',{'simone':m,'allele_reporter':a,'neuro':n,'immune':i})
 print(json.dumps({'simone_auc':m['auc'],'simone_n':m['n'],'max_delta_prior':m['max_abs_prediction_delta_vs_prior'],'allele':a,'neuro':n,'immune':i},indent=2))
