"""Reproduce published bacterial gene-held-out metric arithmetic, not model inference."""
import pathlib,json,ast,pandas as pd,numpy as np
from scipy.stats import spearmanr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
x=pd.read_csv(ROOT/'sources/bacterial_crispri/3_Segregating_gene_effects/test/iteration_predictions.csv',sep='\t');parts=[]
for _,r in x.iterrows():
 a={k:ast.literal_eval(r[k]) for k in ['log2FC','pred','dataset','clusters']};assert len({len(v) for v in a.values()})==1
 z=pd.DataFrame(a);z['iteration']=int(r.iteration);parts.append(z)
z=pd.concat(parts,ignore_index=True);assert np.isfinite(z[['log2FC','pred']]).all().all();assert z.groupby('clusters').iteration.nunique().max()==1,'Public artifact does not support gene-held-out interpretation'
metrics=[]
for gene,g in z.groupby('clusters'):
 if len(g)<3 or g.log2FC.nunique()<2 or g.pred.nunique()<2:continue
 metrics.append(dict(gene_cluster=gene,n=len(g),rho=float(spearmanr(g.log2FC,g.pred).statistic),fold=int(g.iteration.iloc[0])))
m=pd.DataFrame(metrics);m.to_csv(ROOT/'reports/bacterial_author_gene_OOF_replay.csv',index=False)
vals=[]
for b in range(1000):
 i=np.random.RandomState(b).choice(len(m),len(m),replace=True);vals.append(float(np.median(m.rho.to_numpy()[i])))
summary={'status':'AUTHOR_PREDICTION_METRIC_REPLAY_ONLY','model':'MERF/CIAO fixed-effect RF, public gene-held-out prediction artifact','n_observations':len(z),'gene_clusters':z.clusters.nunique(),'evaluable_clusters':len(m),'folds':z.iteration.nunique(),'cluster_fold_overlap':0,'median_within_gene_Spearman':float(m.rho.median()),'mean_within_gene_Spearman':float(m.rho.mean()),'median_gene_bootstrap_ci95':np.quantile(vals,[.025,.975]).tolist(),'paper_reported_gene_CV_median':.396,'not_independent_screen':'This replays gene-held-out CV from training-source studies, not the9-gene purine validation screen','not_fresh_inference':'No mammalian score used. Fresh bacterial features/models not executed; sequence identities and training memberships cannot be fully audited from this serialized prediction artifact alone. Do not label the prior lacZ design workflow validated.'}
(ROOT/'reports/bacterial_metric_replay.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
