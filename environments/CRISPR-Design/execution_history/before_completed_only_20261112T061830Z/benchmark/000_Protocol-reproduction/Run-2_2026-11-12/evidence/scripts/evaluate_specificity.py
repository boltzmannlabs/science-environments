import pathlib,json,numpy as np,pandas as pd
from sklearn.metrics import average_precision_score,precision_recall_curve,auc
from scipy.stats import spearmanr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
x=pd.read_csv(ROOT/'data/specificity_assayed_cohort.csv');p=pd.read_csv(ROOT/'predictions/CFD_assayed_scores.csv');x=x.merge(p[['candidate_id','CFD2016']],on='candidate_id',validate='one_to_one');assert x.CFD2016.notna().all()
y=x.positive.astype(int).to_numpy();score=x.CFD2016.to_numpy();precision,recall,threshold=precision_recall_curve(y,score)
AP=float(average_precision_score(y,score));PR=float(auc(recall,precision));groups={k:z for k,z in x.groupby('On_target_site')};keys=sorted(groups);boots=[]
for b in range(1000):
 rng=np.random.RandomState(b);z=pd.concat([groups[keys[i]] for i in rng.choice(len(keys),len(keys),replace=True)],ignore_index=True)
 if z.positive.nunique()<2:continue
 boots.append(float(average_precision_score(z.positive.astype(int),z.CFD2016)))
ks=[1,5,10,20,50,100,500];rank=[]
for guide,z in groups.items():
 z=z.sort_values(['CFD2016','candidate_id'],ascending=[False,True]);positives=int(z.positive.sum());n=len(z)
 for k in ks:
  take=z.head(k);hits=int(take.positive.sum());rank.append(dict(guide=guide,K=k,n_assayed=n,n_positive=positives,n_retrieved=min(k,n),recall=hits/positives if positives else None,precision=hits/len(take),candidate_panel_exhausted=(k>=n),scope='assayed panel only, not genomewide recall'))
rank=pd.DataFrame(rank);rank.to_csv(ROOT/'reports/specificity_per_guide_recall_at_K.csv',index=False)
coverage=x.workflow_enumerable_ungapped_NGG_le3mm
summary={'status':'COMPLETED_ASSAY_MATCHED_PANEL_BENCHMARK','n':len(x),'guides':len(groups),'positives':int(y.sum()),'negatives':int((1-y).sum()),'positive_threshold_percent':'>0.1 background-corrected indels','average_precision':AP,'average_precision_guide_cluster_bootstrap_ci95':np.quantile(boots,[.025,.975]).tolist(),'cluster_bootstrap_valid_resamples':len(boots),'trapezoid_PR_AUC':PR,'Spearman_CFD_vs_corrected_indel':float(spearmanr(x.CFD2016,x.indel_corrected_percent).statistic),'prior_workflow_NGG_le3mm_positive_coverage':float(x.loc[coverage,'positive'].sum()/x.positive.sum()),'prior_workflow_NGG_le3mm_retained_sites':int(coverage.sum()),'positive_threshold_ge01_sensitivity':{'n_positive':int(x.indel_corrected_percent.ge(.1).sum()),'AP':float(average_precision_score(x.indel_corrected_percent.ge(.1),score))},'noncanonical_target_PAM_sites':int((~x.PAM.str[1:].eq('GG')).sum()),'nominal_assay_detection_limit':'0.1%, as curated study AmpliSeq sensitivity; raw read depths absent, individual-site LoD not inferred','population_limitations':'No population variants, haplotypes, SVs, bulges or ancestry representation evaluated','not_a_clinical_claim':'Negatives mean not exceeding threshold in this matched assayed condition, not absence of cleavage at all conditions or true genomewide negatives','ranking_limit':'K capped at actual assayed panel size; exhausted-panel recall@500 not evidence of genomewide top500 recall','training_scope':'WT SpCas9 CFD2016 rules, no retraining on evaluation labels; source study28459459 not the Doench2016 training source'}
macro=[]
for k,g in rank.groupby('K'):
 macro.append(dict(K=int(k),macro_recall=float(g.recall.dropna().mean()),macro_precision=float(g.precision.mean()),guides_panel_exhausted=int(g.candidate_panel_exhausted.sum()),guides_total=len(g)))
summary['macro_recall_at_K']=macro
(ROOT/'reports/specificity_benchmark.json').write_text(json.dumps(summary,indent=2));x.to_csv(ROOT/'predictions/specificity_assay_joined.csv',index=False);pd.DataFrame({'precision':precision,'recall':recall,'threshold':list(threshold)+[None]}).to_csv(ROOT/'reports/specificity_PR_curve.csv',index=False)
print(json.dumps(summary,indent=2))
