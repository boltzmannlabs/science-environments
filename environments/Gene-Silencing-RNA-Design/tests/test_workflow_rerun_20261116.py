"""Read-only regression/artifact tests for actual Run-6 pretrained workflow execution."""
import unittest,pathlib,sys,json,csv,hashlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
import workflow_rerun_20261116 as R
B=R.OUT

def j(p):return json.loads(pathlib.Path(p).read_text())
def rows(p):
 with pathlib.Path(p).open() as f:return list(csv.DictReader(f))
class WorkflowRerunTests(unittest.TestCase):
 def test_all_configs_have_actual_outputs_and_identical_config_copies(self):
  ledger=rows(B/'config_execution_ledger.csv');self.assertEqual(len(ledger),35)
  for x in ledger:
   cfg=ROOT/x['config_path'];d=ROOT/x['results_path'];self.assertEqual(cfg.read_bytes(),(d/'benchmark_config.json').read_bytes());self.assertEqual(hashlib.sha256(cfg.read_bytes()).hexdigest(),x['config_sha256']);self.assertTrue((d/'predictions.csv').is_file());self.assertTrue((d/'metrics.json').is_file());self.assertIsNone(j(d/'provenance.json')['best_design']);self.assertEqual(j(cfg.parent/'execution.json')['predictions_sha256'],hashlib.sha256((d/'predictions.csv').read_bytes()).hexdigest())
 def test_all_measured_models_are_scored_on_the_same_322_rows(self):
  rs=rows(B/'all_measured_predictions.csv');sets=[]
  for cfg in R.S.CFG:
   a=[r for r in rs if r['config_id']==cfg['config_id']];self.assertEqual(len(a),322);sets.append({r['row_id'] for r in a});self.assertTrue(all(r['execution'].startswith('FRESH_') for r in a))
  self.assertTrue(all(a==sets[0] for a in sets));self.assertEqual(len(rs),1288)
  a=[r for r in rs if r['config_id']==R.S.CFG[3]['config_id']];self.assertTrue(all(r['execution']=='FRESH_NATIVE_OLIGOFORMER_PAIRED_INFERENCE' for r in a));self.assertTrue((B/'C03_historical_reference_only.csv').exists())
 def test_seven_native_jobs_verified_920_pairs_and_assets_unchanged(self):
  ms=j(B/'fresh_native_oligoformer_jobs.json');self.assertEqual(len(ms),7);self.assertEqual(sum(r['pairs_returned'] for r in ms),920)
  for m in ms:
   self.assertEqual(m['status'],'COMPLETED');self.assertEqual(m['returncode'],0);self.assertFalse(m['labels_supplied_to_model']);self.assertTrue(m['original_assets_unchanged']);self.assertTrue(m['disposable_execution_tree_removed'])
   for p,h in m['author_files'].items():self.assertEqual(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(),h)
   result=j(B/'native_oligoformer'/m['job']/'predictions.json');self.assertEqual([x['native_input_ordinal'] for x in result],list(range(1,len(result)+1)))
 def test_ttr_count_native_identity_and_identical_input_reuse(self):
  rr=rows(B/'ttr_pool_predictions.csv');by={c['config_id']:[r for r in rr if r['config_id']==c['config_id']] for c in R.S.CFG}
  self.assertTrue(all(len(v)==598 for v in by.values()));self.assertEqual([r['score'] for r in by[R.S.CFG[0]['config_id']]],[r['score'] for r in by[R.S.CFG[1]['config_id']]])
  self.assertTrue(all(r['execution']=='IDENTICAL_19NT_INPUTS_REUSE_CONFIG00_PREDICTIONS' for r in by[R.S.CFG[1]['config_id']]))
  self.assertTrue(all(r['execution']=='FRESH_NATIVE_OLIGOFORMER_PAIRED_INFERENCE' for r in by[R.S.CFG[3]['config_id']]))
  anchors=rows(B/'TTR_anchor_metrics.csv');a={r['anchor']:float(r['rank']) for r in anchors if r['config_id']==R.S.CFG[3]['config_id']};self.assertEqual(a,{'patisiran':107.,'vutrisiran':62.})
 def test_physical_context_and_immune_outcomes_are_honestly_scoped(self):
  dd=j(B/'HTT_duplex_metrics.json');self.assertEqual(len(dd),4);self.assertTrue(all(r['n']==26 and r['n_uncensored']==21 for r in dd));self.assertEqual(len(rows(B/'htt_duplex_predictions.csv')),104)
  self.assertEqual(len(rows(B/'htt_context_control_predictions.csv')),78)
  for r in rows(B/'htt_context_control_predictions.csv'):self.assertEqual(r['context_quality'],'NO_REAL_FLANKS_DEGRADED_CONTROL')
  im=j(B/'immune_metrics.json');self.assertEqual(im['n'],8);self.assertEqual(im['tp']+im['fn']+im['tn']+im['fp'],8)
  self.assertTrue(any(r['reason']=='REVIEW_ONLY_PATHOGEN_TARGET_NOT_EVALUATED' for r in rows(B/'immune_exclusions.csv')))
 def test_publication_comparison_does_not_manufacture_matched_superiority(self):
  rs=j(B/'published_target_comparison.json');self.assertEqual(len(rs),40);self.assertTrue(all(r['matched_protocol_delta'] is None and not r['published_target_reproduced'] for r in rs))
  ms=j(B/'full_cohort_metrics.json');self.assertEqual(len(ms),4);self.assertTrue(all(m['n']==322 and m['n_labels_exactly_0p7']==4 for m in ms))
  self.assertEqual(j(B/'comparison_complete.json')['matched_published_protocol_superiority_claims'],0)
 def test_frozen_runs_and_module_context_are_isolated(self):
  import config_sweep_20261116 as original
  self.assertEqual(original.RUN,'Run-4_2026-11-16');self.assertNotEqual(original.OUT,R.OUT)
  with self.assertRaisesRegex(RuntimeError,'Fresh run directory'):R.prepare()
  with self.assertRaisesRegex(RuntimeError,'already completed'):R.infer()
  with self.assertRaisesRegex(RuntimeError,'already completed'):R.analyze()
 def test_run5_and_other_historical_manifests_still_match(self):
  p=ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16/PROVENANCE.sha256'
  for line in p.read_text().splitlines():
   sha,name=line.split('  ',1);self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha,name)
if __name__=='__main__':unittest.main()
