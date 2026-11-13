import pathlib,json,hashlib,shutil,os,subprocess,time
import pandas as pd,numpy as np
from scipy.stats import spearmanr,pearsonr,rankdata
from sklearn.metrics import ndcg_score
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text());P=ROOT/'predictions/RS3_common_holdout_fresh.csv';x=pd.read_csv(P)
assert not x[['RS3_train_overlap','CRISPRon_train_overlap','Azimuth_train_overlap','DeepSpCas9_train_overlap']].any().any();assert x['sgRNA Context Sequence'].nunique()==23629
identity=json.loads((ROOT/'protocols/RS3_inference_identity.json').read_text());modelpath=pathlib.Path(identity['model_path']);b=modelpath.read_bytes();gitsha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();tree=json.loads((ROOT/'sources/rs3_tree.json').read_text());target=next(r['sha'] for r in tree['tree'] if r['path']=='rs3/RuleSet3.pkl')
identity['upstream_git_blob_sha']=target;identity['local_git_blob_sha']=gitsha;identity['matches_pinned_upstream_model']=gitsha==target
# Copy weights inside evaluation root for an independently rerunnable model identity.
local=ROOT/'sources/rs3/rs3/RuleSet3.pkl';shutil.copy2(modelpath,local);identity['frozen_weight_copy']=str(local);(ROOT/'protocols/RS3_inference_identity.json').write_text(json.dumps(identity,indent=2))
rows=[];ndcgrows=[]
for ds,z in x.groupby('dataset',sort=True):
 truth=z['sgRNA Activity'].to_numpy();n=len(z)
 for model,col,mode in [('RS3 Sequence','RS3_Sequence_fresh','FRESH_INFERENCE'),('CRISPRon','CRISPRon_author_archive','AUTHOR_SCORE_REPLAY'),('DeepSpCas9','DeepSpCas9_author_archive','AUTHOR_SCORE_REPLAY'),('Rule Set 2','Rule Set 2_author_archive','AUTHOR_SCORE_REPLAY')]:
  pred=z[col].to_numpy();assert np.isfinite(pred).all();rho=float(spearmanr(truth,pred).statistic);pear=float(pearsonr(truth,pred).statistic)
  vals=[]
  for i in range(1000):
   # Mirrors source core.py's guide-row sampling; exact stream order across model groups is not claimed.
   idx=np.random.RandomState(i).choice(n,n,replace=True);vals.append(float(spearmanr(truth[idx],pred[idx]).statistic))
  row=dict(dataset=ds,model=model,inference_mode=mode,n=n,unique_contexts=z['sgRNA Context Sequence'].nunique(),spearman=rho,ci95_lo=float(np.quantile(vals,.025)),ci95_hi=float(np.quantile(vals,.975)),pearson=pear,training_overlap=0,model_weight_matches_upstream=(gitsha==target) if model=='RS3 Sequence' else None)
  if z.genomewide.iloc[0]:
   losses=[];gvals=[]
   for gene,g in z.groupby('sgRNA Target'):
    if len(g)<2:continue
    a=g['sgRNA Activity'].to_numpy();p=g[col].to_numpy();losses.extend(np.abs(rankdata(-a)-rankdata(-p)))
    gain=rankdata(a)/len(a);v=float(ndcg_score(gain[None,:],p[None,:],k=min(20,len(g)),ignore_ties=False));gvals.append(v)
    ndcgrows.append(dict(dataset=ds,model=model,gene=gene,n=len(g),ndcg20_rank_relevance=v))
   row.update(mean_absolute_within_gene_rank_loss=float(np.mean(losses)),supplemental_mean_gene_ndcg20=float(np.mean(gvals)),n_genes=len(gvals))
  rows.append(row)
  print(ds,model,'n',n,'rho',round(rho,6),'CI',round(row['ci95_lo'],6),round(row['ci95_hi'],6),flush=True)
pd.DataFrame(rows).to_csv(ROOT/'reports/cas9_RS3_protocol_metrics.csv',index=False);pd.DataFrame(ndcgrows).to_csv(ROOT/'reports/cas9_supplemental_per_gene_ndcg.csv',index=False)
(ROOT/'protocols/cas9_metric_definitions.json').write_text(json.dumps({'primary':'Spearman activity correlation per dataset, author-defined positive efficacy orientation','CI':'1000 guide-row percentile bootstraps with seeds0..999; observed rows may share genes; source-style not independent-target generalization CI','rank_loss':'source-style within-gene mean absolute rank difference; 4 genomewide datasets only','ndcg':'SUPPLEMENTAL not an original RS3 metric; linear within-gene percentile-rank relevance, k=min(20,n), tie-averaged sklearn ndcg_score; not interchangeable with previous binary-top20 metric','cohort_note':'23629 unique contexts match publication; current per-dataset row totals differ from cached notebook annotations, recorded rather than force-adjusted'},indent=2))
# Prepare the same held-out panel for fresh CRISPRon inference; no labels passed to predictor.
u=x[['sgRNA Context Sequence']].drop_duplicates().sort_values('sgRNA Context Sequence').reset_index(drop=True);assert u['sgRNA Context Sequence'].str.fullmatch('[ACGT]{30}').all();assert u['sgRNA Context Sequence'].str[25:27].eq('GG').all()
u['ID']=['CP_holdout_%06d'%i for i in range(len(u))];u.to_csv(ROOT/'data/crispron_holdout_input_manifest.csv',index=False)
with open(ROOT/'data/crispron_holdout_input.fa','w') as f:
 for r in u.to_dict('records'):f.write('>'+r['ID']+'\n'+r['sgRNA Context Sequence']+'\n')
protocol={'model':'CRISPRon v1','evaluation':'external held-out panel from RS3 publication common-exclusion protocol, not CRISPRon_v0 internal test replication','train_exclusion':'exact 20mer union of all four compared models; original CRISPRon paper additionally applies <=3mm exclusion, NOT claimed here','label_types':'author-processed integrated-target and genomewide phenotypes; separated by dataset, no mixing with Day10+dox','n_unique_inputs':len(u),'input_sha256':hashlib.sha256((ROOT/'data/crispron_holdout_input.fa').read_bytes()).hexdigest(),'previous_reference_predictions_used_for_selection':False,'calibration_or_tuning':False}
(ROOT/'protocols/CRISPRon_external_panel.json').write_text(json.dumps(protocol,indent=2))
print('MODEL_WEIGHT_MATCH',identity['matches_pinned_upstream_model'],'UNIQUE_CP_INPUTS',len(u),flush=True)
