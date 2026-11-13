"""Completed-only publication integrity and native retry tests. Scientific validation scope is model-specific."""
import pathlib,json,hashlib,re,sys
import pandas as pd,numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score
E=pathlib.Path(__file__).resolve().parents[1];B=E/'benchmark';checks=[]
def check(name,fn):
 try:r=fn();checks.append({'name':name,'status':'PASS','detail':r})
 except Exception as e:checks.append({'name':name,'status':'FAIL','detail':str(e)})
def completed():
 l=json.loads((B/'completed_benchmarks.json').read_text());assert len(l)==7 and all(r['status']=='COMPLETED' and r['heuristic_or_surrogate_scores_added'] is False for r in l)
 dirs={p.name for p in B.iterdir() if p.is_dir()};expected={pathlib.Path(r['report']).parts[1] for r in l};assert dirs==expected,(dirs,expected)
 for r in l:assert (E/r['report']).is_file()
 for p in [B/'README.md',B/'BENCHMARK_RUNS.md']:
  assert not any(k in p.read_text() for k in ['NOT_EXECUTED','Future slot','BLOCKED_MATCHED'])
 return '7 completed native-model endpoint packages; no partial task folders/planning placeholders'
def hashes():
 m=json.loads((B/'PROVENANCE.json').read_text())
 for r in m:assert hashlib.sha256((E/r['destination']).read_bytes()).hexdigest()==r['sha256'];assert hashlib.sha256(pathlib.Path(r['source']).read_bytes()).hexdigest()==r['sha256']
 return f'{len(m)} copied files match immutable source and stored SHA256'
def fresh():
 root=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/06_completed_benchmark_retry/CURRENT.txt').read_text();d=json.loads((pathlib.Path(root)/'reports/fresh_native_verification.json').read_text());assert d['status']=='PASS' and len(d['models'])==5
 for r in d['models']:assert r['native_inference_exit_code']==0 and max(r['max_absolute_prediction_differences'].values())==0
 return '5 actual fresh native inference reruns verified, identical predictions at saved precision'
def metrics():
 models={r['model']:E/r['report'] for r in json.loads((B/'completed_benchmarks.json').read_text())}
 d=models['RS3_Sequence'].parent;x=pd.read_csv(d/'predictions.csv');m=pd.read_csv(d/'metrics.csv');assert len(x)==26915 and len(m)==6
 for ds,z in x.groupby('dataset'):assert abs(float(spearmanr(z['sgRNA Activity'],z.RS3_Sequence_fresh).statistic)-m.loc[m.cohort==ds,'spearman'].iloc[0])<1e-12
 d=models['BEHive_BE4'].parent;x=pd.read_csv(d/'predictions.csv');m=pd.read_csv(d/'metrics.csv');assert len(x)==9975 and abs(spearmanr(x.Y,x.BEHive_predicted_logit_score).statistic-m.spearman.iloc[0])<1e-12
 d=models['DeepPrime_PE2'].parent;x=pd.read_csv(d/'predictions.csv');m=pd.read_csv(d/'metrics.csv');assert len(x)==28883 and not x.exact_predictive_input_training_overlap.any() and not x.unedited_target74_training_overlap.any();assert abs(spearmanr(x.Measured_PE_efficiency,x.DeepPrime_fresh_score).statistic-m.spearman.iloc[0])<1e-12
 d=models['CFD2016'].parent;x=pd.read_csv(d/'predictions.csv');m=json.loads((d/'metrics.json').read_text());assert len(x)==1684 and abs(average_precision_score(x.positive_source_concordant,x.CFD2016)-m['average_precision'])<1e-12
 d=models['RFcombined'].parent;m=pd.read_csv(d/'metrics.csv');v=json.loads((d/'independent_verification.json').read_text());assert len(m)==1000 and v['replicates_verified']==1000 and v['all_partition_train_test_disjoint']
 return 'RS3,BE-Hive,DeepPrime,CFD metrics independently recomputed;1000correctedRF refits verified'
def links():
 docs=[E/'README.md',E/'STATUS.md',E/'ENVIRONMENT_SPEC.md',E/'MODELS_AND_TOOLS.md',E/'runtime/CONTRACTS.md',E/'tests/ACCEPTANCE.md',E/'results/README.md']+list((E/'tasks').glob('*.md'))+list(B.rglob('*.md'))+list(E.glob('results/*/Run*/REPORT.md'));n=0
 for p in docs:
  for s in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)',p.read_text()):
   if s.startswith(('http:','https:','mailto:')):continue
   assert (p.parent/s).exists(),str(p)+' -> '+s;n+=1
 return f'{n} active document links resolve; archived evidence is outside benchmark/'
def archive():
 d=json.loads((E/'execution_history/LATEST_COMPLETED_ONLY_REORGANIZATION.json').read_text());a=pathlib.Path(d['archive']);inv=json.loads((a/'archive_inventory.json').read_text())
 for r in inv:assert hashlib.sha256((a/r['path']).read_bytes()).hexdigest()==r['sha256']
 return f'{len(inv)} former benchmark files preserved byte-identically outside active benchmark section'
for n,f in [('completed_only_scope',completed),('copied_artifact_hashes',hashes),('fresh_native_inference',fresh),('measured_metrics',metrics),('active_links',links),('archived_history',archive)]:check(n,f)
result={'passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'checks':checks};(E/'tests/completed_benchmarks_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));sys.exit(bool(result['failed']))
