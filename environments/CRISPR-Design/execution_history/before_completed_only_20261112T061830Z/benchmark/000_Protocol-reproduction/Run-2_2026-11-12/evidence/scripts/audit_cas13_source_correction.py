import pathlib,pandas as pd,numpy as np,json,psutil
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();R=pathlib.Path(ROOT)
a=pd.read_csv(R/'sources/Cas13_original/PredictiveModel_AllScreens/data/CompleteFeatureSet.csv');b=pd.read_csv(R/'data/cas13_feature_table.csv');key=['Screen','GuideName'];print('KEY_UNIQUE',not a.duplicated(key).any(),not b.duplicated(key).any());j=a.merge(b,on=key,suffixes=('_author','_inherited'),validate='one_to_one');print('JOIN',len(j),'LABEL_MAX_DIFF',float((j.normCS_author-j.normCS_inherited).abs().max()))
print('ALL_NA_ROWS',int(a.isna().any(axis=1).sum()));print('AUTHOR_NA_COLS',a.columns[a.isna().any()].to_list())
if not (R/'data/cas13_feature_table.inherited.csv').exists():(R/'data/cas13_feature_table.inherited.csv').write_bytes((R/'data/cas13_feature_table.csv').read_bytes())
a.to_csv(R/'data/cas13_feature_table.author_order.csv',index=False)
for p in psutil.process_iter(['pid','ppid','cmdline']):
 try:
  cmd=p.info['cmdline'] or []
  if any(str(R/'scripts/cas13_full_reproduction.R')==arg for arg in cmd):print('STILL_RUNNING_OLD_JOB',p.info['pid'],p.info['ppid'])
 except psutil.Error:pass
(R/'protocols/cas13_rejected_pilot.json').write_text(json.dumps({'status':'REJECTED_NOT_VALIDATION','reason':'Pilot used global instead of per-training-split scaling and inherited row order/arbitrary seed schedule. Original source was recovered and the pilot was stopped. Outputs preserved but must not be pooled with corrected run.','old_process_session':'proc_3c29267af6b1','old_output_directory':'predictions/cas13_RFcombined_repeated_holdout','author_source_commit':'c864b4f267e22e0ef1a9f28651744f6d04d58eaf','author_data_exact_key_join':len(j),'label_difference_after_key_join':float((j.normCS_author-j.normCS_inherited).abs().max())},indent=2))
