"""Executed publication-label benchmark audit. No new candidate generation or model fitting.
Recompute accuracy from retained genuine predictions; distinguish model inference from metric execution.
Diagnostic review reads ONLY numeric author scores and measured labels, never target sequences.
"""
import pathlib,json,hashlib,csv,sys,datetime
import pandas as pd,numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score,precision_recall_curve,auc
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');SRC=REPO/'05_validated_benchmarks/Run_20261111T113324Z'
E=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/science-environments/environments/CRISPR-Design')
OUT=E/'benchmark/000_Publication-label-benchmarks/Run-3_2026-11-12'
if OUT.exists():
 assert not (OUT/'execution_completed.json').exists(),'Refusing to overwrite completed run'
else:OUT.mkdir(parents=True)
for name in ['protocols','data','reports','logs']:(OUT/name).mkdir(exist_ok=True)
NBOOT=1000;SEED=20261112;manifest=[];metrics=[];paired=[]
def load(rel,**kwargs):
 p=SRC/rel;manifest.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size});return pd.read_csv(p,**kwargs)
def ci_corr(a,p,groups=None,p2=None):
 a=np.asarray(a,float);p=np.asarray(p,float);assert np.isfinite(a).all() and np.isfinite(p).all();assert len(a)==len(p)
 n=len(a);rng=np.random.default_rng(SEED);vals=[];deltas=[]
 clusters=[np.where(np.asarray(groups)==g)[0] for g in pd.unique(groups)] if groups is not None else None
 for b in range(NBOOT):
  i=np.concatenate([clusters[k] for k in rng.integers(0,len(clusters),len(clusters))]) if clusters else rng.integers(0,n,n)
  r=float(spearmanr(a[i],p[i]).statistic)
  if np.isfinite(r):vals.append(r)
  if p2 is not None:
   q=float(spearmanr(a[i],np.asarray(p2)[i]).statistic)
   if np.isfinite(r) and np.isfinite(q):deltas.append(r-q)
 return {'spearman':float(spearmanr(a,p).statistic),'ci_low':float(np.quantile(vals,.025)),'ci_high':float(np.quantile(vals,.975)),'valid_resamples':len(vals),'n':n,'cluster_count':len(clusters) if clusters else None},deltas
protocol={'run_id':'Run-3_2026-11-12','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'execution':'NEW_METRIC_EXECUTION_ON_RETAINED_PREDICTIONS; no new model inference claimed','scope':'publication-backed measured-label computational benchmarks, not validation of complete biological workflows','resampling':{'n':NBOOT,'seed':SEED,'generator':'numpy.default_rng','CI':'95% percentile, target-cluster where available; guide-level otherwise'},'no_model_tuning':True,'no_test_calibration':True,'comparison_policy':'Only compare models on identical rows/labels/features when supported; no cross-paper headline subtraction unless protocol is matched','paired_Cas9':'RS3 minus CRISPRon Spearman difference; paired bootstrap within each assay; exploratory intervals, not multiplicity-adjusted superiority tests','primary_Cas9_panel':'Deduplicated common context join, separately from original duplicate-weighted source replay','diagnostics':'Author numeric-score replay ONLY; paired common row subset plus per-model availability. No sequence columns loaded; no inference, guide design or pathogen performance optimization','blocked_stages':'Remain blocked, not converted into pass by choosing another endpoint'}
(OUT/'protocols/evaluation.json').write_text(json.dumps(protocol,indent=2))
# Case9: actual fresh predictions originally inferred with the exact30nt/tracr features.
x=load('predictions/cas9_fresh_shared_holdout_joined.csv');assert not x[['RS3_train_overlap','CRISPRon_train_overlap','Azimuth_train_overlap','DeepSpCas9_train_overlap']].any().any()
for ds,g in x.groupby('dataset'):
 g=g.reset_index(drop=True);a=g['sgRNA Activity'].to_numpy();cluster=g['sgRNA Target'].astype(str).to_numpy() if bool(g.genomewide.iloc[0]) else None
 for model,col in [('RS3 Sequence','RS3_Sequence_fresh'),('CRISPRon v1','CRISPRon')]:
  r,d=ci_corr(a,g[col].to_numpy(),cluster,g.CRISPRon.to_numpy() if model=='RS3 Sequence' else None)
  r.update(benchmark='Cas9',cohort=ds,model=model,inference_origin='RETAINED_FRESH_INFERENCE',resampling_unit='gene' if cluster is not None else 'guide',paper='PMC9448816',endpoint='official processed sgRNA activity');metrics.append(r)
  if d:paired.append({'cohort':ds,'n':len(g),'delta_RS3_minus_CRISPRon':r['spearman']-float(spearmanr(a,g.CRISPRon).statistic),'paired_ci_low':float(np.quantile(d,.025)),'paired_ci_high':float(np.quantile(d,.975)),'resampling_unit':r['resampling_unit']})
 print('CAS9_METRICS_DONE',ds,flush=True)
# Editing outcomes, no labels passed into any predictor in this re-evaluation.
x=load('predictions/BEHive_BE4_HEK293T_external_predictions.csv');r,_=ci_corr(x.Y,x.BEHive_predicted_logit_score);r.update(benchmark='Base editing',cohort='HEK293T BE4 external disease library',model='BE-Hive efficiency',inference_origin='RETAINED_FRESH_INFERENCE',resampling_unit='guide',paper='PMC7384975',endpoint='normalized logit any-edit efficiency Y');metrics.append(r)
x=load('predictions/DeepPrime_base_fixed_test_predictions.csv');assert x.split.eq('Test').all() and not x.exact_predictive_input_training_overlap.any() and not x.unedited_target74_training_overlap.any()
r,_=ci_corr(x.Measured_PE_efficiency,x.DeepPrime_fresh_score,x.Target74);r.update(benchmark='Prime editing',cohort='HEK293T PE2 conventional scaffold fixed test',model='DeepPrime base',inference_origin='RETAINED_FRESH_INFERENCE',resampling_unit='74nt target',paper='hkimlab/DeepPrime',endpoint='measured PE efficiency');metrics.append(r)
x=load('predictions/PRIDICT2_OOF/OOF_ensemble_predictions_with_labels.csv');p=SRC/'data/PRIDICT2_cell_missing_indices.json';manifest.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});bad=json.loads(p.read_text());original=load('sources/PRIDICT2/dataset/proc_v2/data_23k_v1.csv')
for cell,g in x.groupby('dataset_name'):
 excludes=set(original.iloc[bad[cell]].seq_id);g=g[~g.seq_id.isin(excludes)].reset_index(drop=True)
 for lab,pc in [('averageedited','pred_averageedited'),('averageunintended','pred_averageindel')]:
  r,_=ci_corr(g[cell+lab+'_clamped'],g[pc],g.grp_id);r.update(benchmark='Prime editing',cohort='Library-Diverse '+cell,model='PRIDICT2.0',inference_origin='RETAINED_FRESH_OOF_INFERENCE',resampling_unit='target group',paper='PMC7617539',endpoint=lab);metrics.append(r)
 print('PRIDICT_DONE',cell,flush=True)
# Cas13 refit results: these are not conventional bootstrap CIs.
x=load('reports/cas13_RFcombined_1000_resampling_metrics.csv');assert len(x)==1000
rf={'benchmark':'Cas13','model':'RFcombined','refits':len(x),'median_spearman':float(x.spearman.median()),'mean_spearman':float(x.spearman.mean()),'split_refit_interval':x.spearman.quantile([.025,.975]).to_list(),'paper_approx_spearman':.67,'comparison':'qualified source-method reimplementation, not an independent-target CI or exact replay of conflicting parameter variants'}
(OUT/'reports/cas13_refit_comparison.json').write_text(json.dumps(rf,indent=2))
# Specificity assayed negative/positive universe, study matched WT-SpCas9 labels.
x=load('predictions/specificity_v2_verified_pairs.csv');assert (x.Validation.astype(bool)==x.positive_source_concordant.astype(bool)).all();assert x.Bulge.isna().all() and x.Bulge2.isna().all()
y=x.positive_source_concordant.astype(int);s=x.CFD2016;precision,recall,_=precision_recall_curve(y,s);groups=[g for _,g in x.groupby('On_target_site')];rng=np.random.default_rng(SEED);v=[]
for b in range(NBOOT):
 g=pd.concat([groups[i] for i in rng.integers(0,len(groups),len(groups))]);
 if g.positive_source_concordant.nunique()==2:v.append(float(average_precision_score(g.positive_source_concordant,g.CFD2016)))
sp={'model':'CFD2016','sites':len(x),'positives':int(y.sum()),'negatives':int((1-y).sum()),'guides':len(groups),'average_precision':float(average_precision_score(y,s)),'guide_cluster_AP_ci':np.quantile(v,[.025,.975]).tolist(),'PR_AUC_trapezoid':float(auc(recall,precision)),'endpoint':'corrected indels>=0.1% in matched assayed-site panel','detection_limit':'nominal0.1%, per-site raw-read LoD not available','not_genomewide':'recall@500 saturates because every tested panel has<500 sites','population_variants':'not evaluated'}
(OUT/'reports/specificity.json').write_text(json.dumps(sp,indent=2))
# Diagnostics: complete the previously failed numeric review without importing sequence fields.
p=SRC/'sources/EasyDesign/data/Table S2.xlsx';manifest.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});models=['CNN12ae','CNN12a','CNND','Transformer12ae','Transformer12a','TransformerD'];cols=['No.','true value']+models
x=pd.read_excel(p,sheet_name='Test data',usecols=cols)
missing=[]
for c in ['true value']+models:
 a=x[c].copy();x[c]=pd.to_numeric(a,errors='coerce');invalid=a.notna()&x[c].isna();assert a[invalid].astype(str).isin(['-','NA','N/A','']).all()
 missing.append({'column':c,'numeric_rows':int(x[c].notna().sum()),'missing_or_nonprediction_rows':int(x[c].isna().sum())})
common=x.dropna(subset=['true value']+models).copy();assert len(common)>100
x.to_csv(OUT/'data/diagnostic_numeric_inputs_only.csv',index=False);diag=[]
for cohort,z in [('per_model_available',x),('all_six_models_common',common)]:
 for model in models:
  g=z[['true value',model]].dropna();r,_=ci_corr(g['true value'],g[model]);r.update(benchmark='Diagnostics review',cohort=cohort,model=model,inference_origin='AUTHOR_NUMERIC_SCORE_REPLAY_ONLY',resampling_unit='row; shared-target dependence unmodeled',paper='PMC11316927',endpoint='original measured fluorescence activity');diag.append(r)
pd.DataFrame(diag).to_csv(OUT/'reports/diagnostic_metrics.csv',index=False);pd.DataFrame(missing).to_csv(OUT/'reports/diagnostic_missingness.csv',index=False)
(OUT/'protocols/diagnostic_review_limits.json').write_text(json.dumps({'sequence_columns_loaded':False,'new_model_inference':False,'new_pathogen_design':False,'common_rows':len(common),'available_truth_rows':int(x['true value'].notna().sum()),'interpretation':'Author-numeric prediction metric replay only. Per-model varying availability is not a paired comparison. Common subset permits paired numerical comparison but original split/target independence not fully audited. No sensitivity, specificity or detection-limit validation.'},indent=2))
pd.DataFrame(metrics).to_csv(OUT/'reports/measured_label_correlations.csv',index=False);pd.DataFrame(paired).to_csv(OUT/'reports/Cas9_paired_differences.csv',index=False)
# Plant and bacteria have literature-only score replays, not native adapter validation.
for name in ['plant_assay_matched_score_replay.csv','bacterial_source_faithful_gene_dataset_metrics.csv']:
 a=load('reports/'+name);a.to_csv(OUT/'data'/name,index=False)
pd.DataFrame(manifest).to_json(OUT/'input_provenance.json',orient='records',indent=2)
print('COMPLETED_METRIC_EXECUTION',OUT,flush=True);print(pd.DataFrame(metrics)[['model','cohort','endpoint','n','spearman','ci_low','ci_high']].to_string(index=False));print('DIAGNOSTICS',pd.DataFrame(diag)[['model','cohort','n','spearman']].to_string(index=False));print('SPECIFICITY',json.dumps(sp));print('CAS13',json.dumps(rf))
(OUT/'execution_completed.json').write_text(json.dumps({'status':'COMPLETED_MEASURED_LABEL_METRIC_EXECUTION','new_model_inference':False,'correlation_rows':len(metrics),'diagnostic_rows':len(diag),'input_artifacts':len(manifest),'source_predictions':'Original fresh native inference retained; numeric accuracy independently recomputed. Not a new independent biological validation.'},indent=2))
