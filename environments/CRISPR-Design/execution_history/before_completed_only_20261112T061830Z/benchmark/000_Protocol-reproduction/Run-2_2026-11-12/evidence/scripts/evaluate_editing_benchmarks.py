import pathlib,json,pandas as pd,numpy as np
from scipy.stats import spearmanr,pearsonr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
x=pd.read_csv(ROOT/'predictions/BEHive_BE4_HEK293T_external_predictions.csv');true=x.Y.to_numpy();pred=x.BEHive_predicted_logit_score.to_numpy();assert np.isfinite(pred).all() and np.isfinite(true).all()
vals=[]
for b in range(1000):
 i=np.random.RandomState(b).choice(len(x),len(x),replace=True);vals.append([spearmanr(true[i],pred[i]).statistic,pearsonr(true[i],pred[i]).statistic])
vals=np.asarray(vals);m={'status':'COMPLETED_QUALIFIED_EDITOR_MATCHED_EXTERNAL_EFFICIENCY_BENCHMARK','cell':'HEK293T','editor':'BE4','n':len(x),'known_12k_training_20mer_and31nt_overlaps':0,'spearman':float(spearmanr(true,pred).statistic),'pearson':float(pearsonr(true,pred).statistic),'guide_bootstrap_Spearman_ci95':np.quantile(vals[:,0],[.025,.975]).tolist(),'guide_bootstrap_Pearson_ci95':np.quantile(vals[:,1],[.025,.975]).tolist(),'endpoint':'author-normalized replicate-mean logit any-edit efficiency Y; NOT intended-edit purity','probability_calibration':'NOT_FIT; native logit score, no test-set mean/std fitting','limitations':['Known released training-pool exclusions are verified; full original tuning-split membership and whole-gene exclusion not established','This validates efficiency only, not BE-Hive bystander genotype distributions or a BE4max model','Guide bootstrap treats observations as independent; parent-target dependence may make these intervals optimistic']}
(ROOT/'reports/BEHive_external_efficiency_metrics.json').write_text(json.dumps(m,indent=2));print('BEHIVE',json.dumps(m,indent=2))
# More appropriate target-cluster CIs for PRIDICT2 OOF predictions, supplementing guide-row intervals.
x=pd.read_csv(ROOT/'predictions/PRIDICT2_OOF/OOF_ensemble_predictions_with_labels.csv');nans=json.loads((ROOT/'data/PRIDICT2_cell_missing_indices.json').read_text());data=pd.read_csv(ROOT/'sources/PRIDICT2/dataset/proc_v2/data_23k_v1.csv');rows=[]
for cell,z in x.groupby('dataset_name'):
 bad=set(data.iloc[nans[cell]].seq_id);z=z[~z.seq_id.isin(bad)].reset_index(drop=True);groups=[g.index.to_numpy() for _,g in z.groupby('grp_id')]
 for pc,lc in [('pred_averageedited','averageedited'),('pred_averageindel','averageunintended')]:
  a=z[cell+lc+'_clamped'].to_numpy();p=z[pc].to_numpy();v=[]
  for b in range(1000):
   rng=np.random.RandomState(b);ids=np.concatenate([groups[i] for i in rng.choice(len(groups),len(groups),replace=True)]);v.append(float(spearmanr(a[ids],p[ids]).statistic))
  r={'cell':cell,'endpoint':lc,'n':len(z),'target_groups':len(groups),'spearman':float(spearmanr(a,p).statistic),'target_cluster_ci_low':float(np.quantile(v,.025)),'target_cluster_ci_high':float(np.quantile(v,.975))};rows.append(r);print('PRIDICT_TARGET_CI',json.dumps(r))
pd.DataFrame(rows).to_csv(ROOT/'reports/PRIDICT2_target_cluster_confidence_intervals.csv',index=False)
