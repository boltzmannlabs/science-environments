import pathlib,json,ast,pandas as pd,numpy as np
from scipy.stats import spearmanr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
x=pd.read_csv(ROOT/'sources/bacterial_crispri/3_Segregating_gene_effects/test/iteration_predictions.csv',sep='\t');records=[]
for _,r in x.iterrows():
 d={k:ast.literal_eval(r[k]) for k in ['log2FC','pred','dataset','clusters']};a=pd.DataFrame(d)
 for (dataset,gene),g in a.groupby(['dataset','clusters']):
  rho=float(spearmanr(g.log2FC,g.pred).statistic) if len(g)>=2 else None
  records.append({'iteration':int(r.iteration),'dataset':dataset,'gene_cluster':gene,'n':len(g),'rho':rho})
p=pd.DataFrame(records);p.to_csv(ROOT/'reports/bacterial_source_faithful_gene_dataset_metrics.csv',index=False);valid=p[p.rho.notna()].reset_index(drop=True);groups=[g.index.to_numpy() for _,g in valid.groupby('gene_cluster')];v=[]
for b in range(1000):
 rng=np.random.RandomState(b);idx=np.concatenate([groups[i] for i in rng.choice(len(groups),len(groups),replace=True)]);v.append(float(valid.rho.iloc[idx].median()))
s={'status':'COMPLETED_SOURCE_METRIC_REPLAY_NOT_FRESH_INFERENCE','source':'MERF_crispri.py lines954-976, pinned commit2dad9153ea61db49001e2cb48095fbb2eac46003','aggregation':'Within each heldout fold, compute Spearman per gene PER SOURCE DATASET; median of valid gene-dataset values, exactly as source. Do not pool raw depletion measurements from different experiments within a gene.','gene_dataset_comparisons':len(p),'valid_comparisons':len(valid),'median_spearman':float(valid.rho.median()),'mean_spearman':float(valid.rho.mean()),'gene_cluster_bootstrap_median_ci95':np.quantile(v,[.025,.975]).tolist(),'by_dataset':valid.groupby('dataset').rho.agg(['median','mean','count']).reset_index().to_dict('records'),'paper_reported_rounded_median':.396,'limitations':['Public prediction-file metric replay only, not fresh bacterial model inference or feature reconstruction','Not the independent9-gene purine screen','Prior pooled-gene aggregation retained as sensitivity but is not the published endpoint']}
(ROOT/'reports/bacterial_source_faithful_replay.json').write_text(json.dumps(s,indent=2));print(json.dumps(s,indent=2))
