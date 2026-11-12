"""Replay author-provided plant scores against actual in-planta InDel labels.
No human label substitution, genome-context fabrication or new guide design.
"""
import pathlib,json,openpyxl,pandas as pd,numpy as np
from scipy.stats import spearmanr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT);p=ROOT/'data/plant_published_supplement.xlsx';w=openpyxl.load_workbook(p,read_only=True,data_only=True)
truth={};active=None
for row in w['Data 2'].iter_rows(values_only=True):
 if row[0] in ['Dataset 1','Dataset 2']:active=int(row[0][-1])
 elif active and isinstance(row[0],str) and isinstance(row[7],(float,int)) and row[0]!='gRNA Code':truth[(active,row[0])]=float(row[7])
assert sum(k[0]==1 for k in truth)==20 and sum(k[0]==2 for k in truth)==32
# Explicit original independent-score table blocks and columns; integrated/combined scores excluded.
configs=[(1,'Data 3',5,24,{'CRISPick_Doench2022_author':1,'CRISPRon_author':3,'DeepSpCas9_author':9,'DeepHF_author':11}),(2,'Data 5',4,35,{'CRISPick_Doench2022_author':3,'CRISPRon_author':5,'DeepSpCas9_author':4,'DeepHF_author':6})]
rows=[]
for ds,sheet,first,last,cols in configs:
 for row in w[sheet].iter_rows(min_row=first,max_row=last,values_only=True):
  gid=row[0];assert (ds,gid) in truth,(ds,gid)
  for name,c in cols.items():rows.append({'dataset':ds,'guide_code':gid,'model':name,'observed_mean_indel_percent':truth[(ds,gid)],'author_prediction':float(row[c])})
w.close();z=pd.DataFrame(rows);z.to_csv(ROOT/'data/plant_author_scores_and_measured_truth.csv',index=False)
(ROOT/'protocols/plant_metric_replay.json').write_text(json.dumps({'mode':'AUTHOR_SCORE_METRIC_REPLAY_ONLY','species':'Nicotiana benthamiana','labels':'mean in-planta InDel frequencies from original Data2, not mammalian efficacy','n_guides':52,'source':'10.1007/s00299-026-03820-x SupplementaryData1/Data3/Data5','not_fresh_model_inference':'Original webtool scores reused as explicit publication artifacts; native plant context/scaffold/reference adapter not independently reconstructed','model_selection':'Four prespecified source score columns for both datasets; no integrated score averaging','CI':'1000 guide-row bootstraps; small guide numbers and gene clustering limit interpretation'},indent=2))
metrics=[]
for (ds,name),g in z.groupby(['dataset','model']):
 a=g.observed_mean_indel_percent.to_numpy();b=g.author_prediction.to_numpy();v=[]
 for k in range(1000):
  i=np.random.RandomState(k).choice(len(g),len(g),replace=True);s=float(spearmanr(a[i],b[i]).statistic)
  if np.isfinite(s):v.append(s)
 r={'dataset':int(ds),'model':name,'n':len(g),'spearman':float(spearmanr(a,b).statistic),'guide_bootstrap_ci_low':float(np.quantile(v,.025)),'guide_bootstrap_ci_high':float(np.quantile(v,.975)),'mode':'AUTHOR_SCORE_REPLAY'};metrics.append(r);print(json.dumps(r))
pd.DataFrame(metrics).to_csv(ROOT/'reports/plant_assay_matched_score_replay.csv',index=False)
(ROOT/'reports/plant_validation_status.json').write_text(json.dumps({'status':'COMPLETED_ASSAY_MATCHED_METRIC_REPLAY_NOT_NATIVE_WORKFLOW_VALIDATION','metrics':metrics,'scope_limit':'Matches published plant assay outcomes; does not activate a generic rice/plant design workflow or demonstrate fresh model feature reconstruction. No mammalian phenotype substituted.'},indent=2))
# Compact inspection of independent bacterial phenotype fields, ignoring formatting-only empty columns.
w=openpyxl.load_workbook(ROOT/'data/bacterial_CRISPRi_primary_supplement.xlsx',read_only=True,data_only=True)
for name in ['TableS13_purine_screen_guides','TableS14_purine_genes_validatio']:
 s=w[name];print('BACTERIAL_COMPACT',name,s.max_row)
 for row in s.iter_rows(min_row=1,max_row=4,values_only=True):
  nonempty=[i for i,a in enumerate(row) if a is not None];print(row[:max(nonempty)+1] if nonempty else ())
w.close()
