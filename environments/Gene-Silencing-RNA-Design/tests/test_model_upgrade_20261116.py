"""Read-only Run-5 software/artifact tests; do not treat as biological validation."""
import unittest,pathlib,sys,json,csv,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
import run_model_upgrade_20261116 as U
B=U.B

def j(p):return json.loads(pathlib.Path(p).read_text())
def rows(p):
 with pathlib.Path(p).open() as f:return list(csv.DictReader(f))
class ModelUpgradeTests(unittest.TestCase):
 def test_all_task_workflow_pairs_and_declined_training(self):
  self.assertFalse(j(B/'training_scope_decision.json')['custom_training_permitted'])
  for t in U.S.TASKS:
   a=ROOT/'config'/t/U.RUN/'workflow.json';b=ROOT/'results'/t/U.RUN/'workflow.json';self.assertEqual(a.read_bytes(),b.read_bytes())
  self.assertEqual(len(j(B/'task_status.json')),11)
 def test_new_challenger_branches_fail_closed_without_fake_metrics(self):
  ledger=rows(B/'config_execution_ledger.csv');self.assertEqual(len(ledger),21)
  for r in ledger:
   d=ROOT/r['result_path'];cfg=ROOT/r['config_path'];self.assertEqual(cfg.read_bytes(),(d/'benchmark_config.json').read_bytes())
   self.assertEqual(hashlib.sha256(cfg.read_bytes()).hexdigest(),j(d/'provenance.json')['config_sha256'])
   if r['config_id']!=U.IDS[0]:
    self.assertFalse((d/'predictions.csv').exists());self.assertFalse((d/'metrics.json').exists());self.assertIsNone(j(d/'status.json')['auc']);self.assertEqual(r['new_model_efficacy_predictions'],'0')
 def test_control_score_vectors_exactly_replay(self):
  a=rows(B/'measured_control_predictions.csv');b=rows(U.PREV/'C00_rnai_native21_measured_predictions.csv');self.assertEqual(len(a),322);self.assertEqual([r['row_id'] for r in a],[r['row_id'] for r in b]);self.assertEqual([r['score'] for r in a],[r['score'] for r in b])
  a=rows(B/'ttr_control_predictions.csv');b=[r for r in rows(U.PREV/'ttr_pool_predictions.csv') if r['config_id']=='C00_rnai_native21'];self.assertEqual(len(a),598);self.assertEqual([r['score'] for r in a],[r['score'] for r in b])
 def test_summary_has_no_new_model_or_unsupported_improvement(self):
  s=j(B/'results_summary.json');self.assertEqual(s['macro_auc_delta'],0);self.assertEqual(s['new_challenger_efficacy_predictions'],0);self.assertIsNone(s['new_model_promoted']);self.assertEqual(s['fully_complete_application_tasks'],0);self.assertFalse(s['new_training'])
  self.assertEqual(j(ROOT/'results/001_general'/U.RUN/U.IDS[0]/'metrics.json')['n'],301)
 def test_readiness_diagnostics_and_input_limits(self):
  p=j(B/'siarna_software_probe.json');self.assertEqual(p['checkpoint_strict_load'],'PASSED');self.assertGreater(p['preprocessing_random_override']['max_absolute_difference'],0)
  a=rows(B/'native_input_applicability.csv');self.assertEqual(len(a),322);self.assertTrue(all(r['native_siarna_guide_length_ok']=='True' and r['native_siarna_mrna_length_ok']=='False' for r in a))
  self.assertEqual(len({r['gene'] for r in a}),6)
  for n in ['SiaRNA','ENsiRNA']:self.assertTrue(U.model_gate(n)['status'].startswith('BLOCKED'))
 def test_author_assets_and_historical_manifests_unchanged(self):
  for r in j(B/'acquisition_provenance.json')['files']:self.assertEqual(hashlib.sha256(pathlib.Path(r['path']).read_bytes()).hexdigest(),r['sha256'])
  for rel in ['benchmark/011_Campaign-reproduction/Run-3_2026-11-11/PROVENANCE.sha256','benchmark/012_Config-sweep/Run-4_2026-11-16/PROVENANCE.sha256']:
   for line in (ROOT/rel).read_text().splitlines():
    sha,p=line.split('  ',1);self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),sha,p)
 def test_new_figures_decode_and_are_not_empty(self):
  from PIL import Image,ImageStat
  fs=j(B/'figure_validation.json');self.assertEqual(len(fs),8)
  for r in fs:
   with Image.open(ROOT/r['path']) as im:self.assertEqual(im.width,r['width']);self.assertGreater(max(ImageStat.Stat(im.convert('RGB')).stddev),5)
 def test_completed_run_cannot_overwrite_frozen_workflows(self):
  with self.assertRaisesRegex(RuntimeError,'already frozen'):U.prepare()
  with self.assertRaisesRegex(RuntimeError,'already executed'):U.run()
  with self.assertRaisesRegex(RuntimeError,'Report frozen'):U.report()
if __name__=='__main__':unittest.main()
