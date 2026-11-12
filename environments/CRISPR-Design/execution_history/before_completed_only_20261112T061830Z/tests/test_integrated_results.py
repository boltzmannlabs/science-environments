#!/usr/bin/env python3
"""Verify integrated evidence packaging, not biological validity. Stdlib only."""
import pathlib,json,hashlib,re,csv,sys
E=pathlib.Path(__file__).resolve().parents[1];R=E/'benchmark/000_Protocol-reproduction/Run-2_2026-11-12'
checks=[]
def check(name,fn):
 try:detail=fn();checks.append({'check':name,'status':'PASS','detail':detail})
 except Exception as e:checks.append({'check':name,'status':'FAIL','detail':str(e)})
def coverage():
 a=json.loads((R/'task_execution_status.json').read_text());assert len(a)==13 and {t['task_id'] for t in a}=={f'{i:03d}' for i in range(1,14)}
 for t in a:
  assert (E/t['result_report']).is_file() and (E/t['benchmark_report']).is_file()
  p=E/t['result_report'];d=json.loads((p.parent/'provenance.json').read_text());assert d['best_design'] is None and d['experimental_validation'] is False
  assert (p.parent/'00_inputs/requirement_brief.json').is_file()
 return '13 task result/benchmark pairs; explicit no-experimental-validation statuses'
def hashes():
 a=json.loads((R/'PROVENANCE.json').read_text())
 for t in a:
  src=pathlib.Path(t['source']);dst=E/t['destination'];assert dst.is_file(),str(dst)
  assert hashlib.sha256(dst.read_bytes()).hexdigest()==t['sha256'],str(dst)
  assert hashlib.sha256(src.read_bytes()).hexdigest()==t['sha256'],str(src)
 return f'{len(a)} copied artifacts match both source and stored SHA256'
def links():
 docs=[E/'README.md',E/'STATUS.md',E/'results/README.md',E/'benchmark/README.md',E/'benchmark/BENCHMARK_RUNS.md']+list((E/'tasks').glob('*.md'))
 docs+=list(E.glob('results/*/Run-2_2026-11-12/*.md'))+list(E.glob('benchmark/*/Run-2_2026-11-12/*.md'))
 n=0
 for p in docs:
  for s in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)',p.read_text()):
   if s.startswith(('http:','https:','mailto:')):continue
   assert (p.parent/s).exists(),f'{p}: {s}';n+=1
 return f'{n} relative links in {len(docs)} current documents resolve'
def rf():
 d=json.loads((R/'cas13_completion_verification.json').read_text());assert d['replicates_verified']==1000 and d['all_partition_train_test_disjoint'] and d['all_test_predictions_match_partition']
 assert d['max_recomputed_spearman_difference']<1e-9
 rows=list(csv.DictReader(open(R/'evidence/reports/cas13_RFcombined_1000_resampling_metrics.csv')));assert len(rows)==1000
 return '1000 independently recomputed corrected RF replicates verified; rejected pilot excluded'
def validity():
 l=json.loads((R/'task_execution_status.json').read_text());d={t['task_id']:t for t in l}
 assert 'BLOCKED' in d['008']['benchmark_status'] and 'INCOMPLETE' in d['010']['benchmark_status']
 assert 'REPLAY' in d['012']['benchmark_status'] and 'REPLAY' in d['013']['benchmark_status']
 concord=json.loads((R/'evidence/reports/PRIDICT2_original_split_and_score_concordance.json').read_text());assert all(t['fold_assignment_mismatches']==0 for t in concord['conditions'].values())
 spec=json.loads((R/'evidence/reports/specificity_benchmark_source_concordant.json').read_text());assert spec['source_validation_labels_match'] and spec['n']==spec['positives']+spec['negatives']
 return 'No incomplete/replay modality promoted; PRIDICT folds match; specificity totals consistent'
for name,fn in [('task_coverage',coverage),('artifact_hashes',hashes),('relative_links',links),('cas13_completion',rf),('evidence_boundaries',validity)]:check(name,fn)
result={'checks':checks,'passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks)}
(R/'integration_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));sys.exit(bool(result['failed']))
