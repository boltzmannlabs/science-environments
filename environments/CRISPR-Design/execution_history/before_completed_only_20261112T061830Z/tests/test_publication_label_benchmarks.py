"""Verify Run3 publication-label metric execution and compare metrics independently."""
import pathlib,json,hashlib,re,sys
import pandas as pd,numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score
E=pathlib.Path(__file__).resolve().parents[1];R=E/'benchmark/000_Publication-label-benchmarks/Run-3_2026-11-12';SRC=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/Run_20261111T113324Z')
checks=[]
def test(name,fn):
 try:d=fn();checks.append({'name':name,'status':'PASS','detail':d})
 except Exception as e:checks.append({'name':name,'status':'FAIL','detail':str(e)})
def provenance():
 a=json.loads((R/'input_provenance.json').read_text())
 for r in a:assert hashlib.sha256(pathlib.Path(r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
 a=json.loads((R/'execution_completed.json').read_text());assert a['new_model_inference'] is False and a['correlation_rows']==18 and a['diagnostic_rows']==12
 return 'All retained input hashes match; completed metric execution is not labeled new inference'
def correlations():
 m=pd.read_csv(R/'reports/measured_label_correlations.csv');assert len(m)==18;assert m.spearman.between(-1,1).all();assert (m.ci_low<=m.spearman).all() and (m.ci_high>=m.spearman).all()
 native=pd.read_csv(SRC/'predictions/cas9_fresh_shared_holdout_joined.csv');n=0
 for ds,g in native.groupby('dataset'):
  for model,col in [('RS3 Sequence','RS3_Sequence_fresh'),('CRISPRon v1','CRISPRon')]:
   row=m[(m.model==model)&(m.cohort==ds)].iloc[0];assert row.n==len(g);assert abs(spearmanr(g['sgRNA Activity'],g[col]).statistic-row.spearman)<1e-12;n+=1
 return f'{n} Cas9 correlations independently recomputed; all18 intervals/numeric rows coherent'
def diagnostics():
 x=pd.read_csv(R/'data/diagnostic_numeric_inputs_only.csv');assert not any('seq' in c.lower() or 'target' in c.lower() for c in x.columns)
 models=['CNN12ae','CNN12a','CNND','Transformer12ae','Transformer12a','TransformerD'];common=x.dropna(subset=['true value']+models);assert len(common)==859
 m=pd.read_csv(R/'reports/diagnostic_metrics.csv');assert len(m)==12
 for model in models:
  row=m[(m.model==model)&(m.cohort=='all_six_models_common')].iloc[0];assert row.n==859;assert abs(spearmanr(common['true value'],common[model]).statistic-row.spearman)<1e-12
 q=json.loads((R/'protocols/diagnostic_review_limits.json').read_text());assert q['sequence_columns_loaded'] is False and q['new_model_inference'] is False
 return '6 matched common-row diagnostic correlations verified; numeric-only859row comparison'
def specificity():
 x=pd.read_csv(SRC/'predictions/specificity_v2_verified_pairs.csv');r=json.loads((R/'reports/specificity.json').read_text());assert r['sites']==len(x)==1684
 assert r['positives']+r['negatives']==1684;assert abs(average_precision_score(x.positive_source_concordant,x.CFD2016)-r['average_precision'])<1e-12
 return 'CFD assayed-panel AP and positive/negative counts independently recomputed'
def registry():
 t=json.loads((R/'task_execution_status.json').read_text());c=pd.read_csv(R/'task_execution_status.csv',dtype={'task_id':str});assert len(t)==len(c)==13
 for a in t:
  assert (E/a['benchmark_report']).is_file();b=json.loads((E/a['benchmark_report']).with_name('execution_status.json').read_text());assert a['benchmark_status']==b['benchmark_status'] and a['benchmark_report']==b['benchmark_report']
 d={r['task_id']:r for r in t};assert d['010']['benchmark_status']=='COMPLETED_NUMERIC_AUTHOR_SCORE_REPLAY';assert d['008']['benchmark_status'].startswith('BLOCKED')
 return '13 latest task reports/JSON/CSV statuses agree; true blockers retained'
def links():
 docs=[E/'benchmark/BENCHMARK_RUNS.md',E/'benchmark/README.md',R/'README.md',R/'REPORT.md']+list(E.glob('benchmark/*/Run-3_2026-11-12/README.md'))+list((E/'tasks').glob('*.md'));n=0
 for p in docs:
  for s in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)',p.read_text()):
   if s.startswith(('http','mailto:')):continue
   assert (p.parent/s).exists(),f'{p}:{s}';n+=1
 return f'{n} relative links resolve'
for name,fn in [('provenance',provenance),('correlations',correlations),('numeric_diagnostic_review',diagnostics),('specificity',specificity),('task_registry',registry),('links',links)]:test(name,fn)
result={'passed':sum(r['status']=='PASS' for r in checks),'failed':sum(r['status']=='FAIL' for r in checks),'checks':checks};(R/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));sys.exit(bool(result['failed']))
