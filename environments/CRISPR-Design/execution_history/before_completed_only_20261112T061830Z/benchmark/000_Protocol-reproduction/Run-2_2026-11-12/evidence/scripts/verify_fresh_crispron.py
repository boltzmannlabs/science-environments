import pathlib,json,hashlib
import numpy as np,pandas as pd
from scipy.stats import spearmanr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
x=pd.read_csv(ROOT/'predictions/RS3_common_holdout_fresh.csv');cp=pd.read_csv(ROOT/'predictions/CRISPRon_fresh/crispron.csv')
# The upstream CLI enumerates extra NGG windows. Join only exact intended30mers, never ID suffixes.
cp=cp[['30mer','CRISPRon']].drop_duplicates();assert not cp['30mer'].duplicated().any()
x=x.merge(cp,left_on='sgRNA Context Sequence',right_on='30mer',how='left',validate='many_to_one');assert x.CRISPRon.notna().all()
x.to_csv(ROOT/'predictions/cas9_fresh_shared_holdout_joined.csv',index=False)
rows=[]
for ds,z in x.groupby('dataset'):
 a=z['sgRNA Activity'].to_numpy();p=z.CRISPRon.to_numpy();v=[]
 for i in range(1000):
  idx=np.random.RandomState(i).choice(len(z),len(z),replace=True);v.append(float(spearmanr(a[idx],p[idx]).statistic))
 d=dict(dataset=ds,model='CRISPRon_v1',inference_mode='FRESH_INFERENCE',n=len(z),spearman=float(spearmanr(a,p).statistic),ci95_lo=float(np.quantile(v,.025)),ci95_hi=float(np.quantile(v,.975)),max_abs_difference_from_author_archive=float((z.CRISPRon-z.CRISPRon_author_archive).abs().max()),training_overlap=0)
 rows.append(d);print(json.dumps(d))
pd.DataFrame(rows).to_csv(ROOT/'reports/CRISPRon_fresh_external_panel_metrics.csv',index=False)
assert len(rows)==6
(ROOT/'reports/cas9_reproduction_validation.json').write_text(json.dumps({'RS3_weight_identity_matches_pinned_author_weights':json.loads((ROOT/'protocols/RS3_inference_identity.json').read_text())['matches_pinned_upstream_model'],'unique_contexts_match_published_23629':x['sgRNA Context Sequence'].nunique()==23629,'all_fresh_predictions_present':bool(x[['RS3_Sequence_fresh','CRISPRon']].notna().all().all()),'training_exclusions_pass':not bool(x[['RS3_train_overlap','CRISPRon_train_overlap','Azimuth_train_overlap','DeepSpCas9_train_overlap']].any().any()),'per_dataset_counts_match_cached_notebook':False,'qualification':'Current official processed data yields26915 dataset observations and23629 unique contexts; cached notebook row-count annotations differ. Original CRISPRon_v0 internal protocol and <=3mm exclusion not claimed reproduced; this panel is the RS3-paper four-model common-exclusion evaluation.'},indent=2))
