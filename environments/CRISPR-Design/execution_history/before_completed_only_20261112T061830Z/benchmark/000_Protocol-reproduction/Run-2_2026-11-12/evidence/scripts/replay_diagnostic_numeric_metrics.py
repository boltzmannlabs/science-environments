"""Literature numeric-metric replay only: do NOT load sequence columns or score/design pathogen guides."""
import pathlib,json,pandas as pd,numpy as np
from scipy.stats import spearmanr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
cols=['No.','true value','CNND','CNN12a','CNN12ae','TransformerD','Transformer12a','Transformer12ae','type'];x=pd.read_excel(ROOT/'sources/EasyDesign/data/Table S2.xlsx',sheet_name='Test data',usecols=cols);rows=[]
models=['CNN12ae','CNN12a','CNND','Transformer12ae','Transformer12a','TransformerD']
for col in ['true value']+models:
 original=x[col].copy();x[col]=pd.to_numeric(x[col],errors='coerce');unexpected=original.notna()&x[col].isna()&~original.astype(str).isin(['-','NA','N/A',''])
 assert not unexpected.any(),('Unexpected nonnumeric token',col,original[unexpected].unique())
common=x.dropna(subset=['true value']+models).copy();common_rows=[]
for col in models:
 z=x[['No.','true value',col,'type']].dropna(subset=['true value',col]).copy();assert len(z)>100
 a=pd.to_numeric(z['true value']).to_numpy();p=pd.to_numeric(z[col]).to_numpy();v=[]
 for b in range(1000):
  i=np.random.RandomState(b).choice(len(z),len(z),replace=True);v.append(float(spearmanr(a[i],p[i]).statistic))
 r={'model':col,'n':len(z),'Spearman':float(spearmanr(a,p).statistic),'guide_pair_bootstrap_ci_low':float(np.quantile(v,.025)),'guide_pair_bootstrap_ci_high':float(np.quantile(v,.975)),'mode':'AUTHOR_NUMERIC_PREDICTION_REPLAY_ONLY'};rows.append(r);print(json.dumps(r))
pd.DataFrame(rows).to_csv(ROOT/'reports/diagnostic_published_numeric_metric_replay.csv',index=False)
summary={'status':'REVIEW_ONLY_NUMERIC_METRIC_REPLAY_COMPLETED','source_commit':'5c06a30d0a43be28a958831587f6ab706c2d4876','source':'TableS2 Test data, paired true value and original author prediction columns','number_of_rows_with_numeric_truth':int(x['true value'].notna().sum()),'author_rows_retrieved':len(x),'type_counts':x['type'].value_counts().to_dict(),'metrics':rows,'source_expected_test_rows_from_paper':862,'new_sequence_generation':False,'new_pathogen_sequence_model_scoring':False,'sequence_columns_loaded':False,'local_23nt_TTTV_pipeline_validated':False,'limitations':['Author numeric-score replay is literature review, not operational pathogen guide evaluation or native workflow validation','Only21nt/TTTN original fluorescence model context is represented; previous synthetic23nt/TTTV geometry is a different workflow','No clinical sensitivity, specificity, fluorescence LoD, or independent experimental validation inferred from rank correlation','Bootstrap guide-pair intervals do not account for shared template/target dependencies']}
(ROOT/'reports/diagnostic_review_only_replay_status.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='metrics'},indent=2))
