"""Executed configuration-sweep artifact and inference-guard tests; no model fitting or scientific fixtures."""
import unittest,pathlib,csv,json,hashlib,sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'benchmark/012_Config-sweep/Run-4_2026-11-16';RUN='Run-4_2026-11-16'
sys.path.insert(0,str(ROOT/'runtime'))
from sirna_context_audit import validate_pair

def j(p):return json.loads(pathlib.Path(p).read_text())
def rows(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
class TestConfigSweep(unittest.TestCase):
 def test_all_task_config_folders_and_original_examples_preserved(self):
  status=j(OUT/'task_status.json');self.assertEqual(len(status),11)
  for r in status:self.assertTrue((ROOT/'config'/r['task']/'README.md').is_file())
  for r in j(OUT/'config_copy_provenance.json'):
   self.assertEqual(sha(ROOT/r['original']),r['sha256']);self.assertEqual(sha(ROOT/r['copy']),r['sha256'])
 def test_frozen_config_and_result_pairing(self):
  ledger=rows(OUT/'config_execution_ledger.csv');self.assertEqual(len(ledger),35)
  for r in ledger:
   p=ROOT/r['config_path'];d=ROOT/r['results_path'];self.assertEqual(sha(p),r['config_sha256']);self.assertEqual(sha(d/'benchmark_config.json'),r['config_sha256']);self.assertEqual(j(p)['frozen_plan_sha256'],sha(OUT/'frozen_plan.json'))
   self.assertEqual(j(p.parent/'execution.json')['status'],'EXECUTED');self.assertTrue((d/'metrics.json').is_file());self.assertTrue((d/'performance_until_this_config.png').is_file())
 def test_frozen_thresholds_unchanged(self):
  plan=j(OUT/'frozen_plan.json');self.assertEqual(sha(ROOT/plan['immutable_gates']['path']),plan['immutable_gates']['sha256'])
 def test_prior_run3_manifest_all_entries_unchanged(self):
  manifest=ROOT/'benchmark/011_Campaign-reproduction/Run-3_2026-11-11/PROVENANCE.sha256';lines=manifest.read_text().splitlines();self.assertEqual(len(lines),341)
  for line in lines:
   want,path=line.split(maxsplit=1);self.assertEqual(sha(ROOT/path),want,path)
 def test_model_predictions_and_missing_coverage_not_imputed(self):
  rs=rows(OUT/'all_measured_predictions.csv');ids={r['config_id'] for r in rs};self.assertEqual(len(ids),4)
  for cid in ids:self.assertEqual(sum(r['config_id']==cid for r in rs),308 if cid.startswith('C03') else 322)
  self.assertEqual(len(rows(OUT/'oligoformer_exclusions.csv')),14)
  self.assertEqual(j(OUT/'inference_summary.json')['native_baseline_max_abs_score_delta_vs_prior'],0)
 def test_identical_ttr_inputs_are_explicitly_reused(self):
  rs=rows(OUT/'ttr_pool_predictions.csv');a={r['row_id']:r for r in rs if r['config_id'].startswith('C00')};b={r['row_id']:r for r in rs if r['config_id'].startswith('C01')};self.assertEqual(len(a),598);self.assertEqual(set(a),set(b))
  for key in a:self.assertEqual(a[key]['score'],b[key]['score']);self.assertIn('IDENTICAL',b[key]['execution'])
  m=rows(OUT/'TTR_anchor_metrics.csv');self.assertEqual(len(m),8)
  self.assertEqual({r['anchor']:float(r['rank']) for r in m if r['config_id'].startswith('C03')},{'patisiran':107,'vutrisiran':62})
 def test_context_guard_missing_match_invalid_letters_unknown_flanks(self):
  with self.assertRaises(ValueError):validate_pair('A'*19,'C'*57)
  with self.assertRaises(ValueError):validate_pair('A'*18,'U'*57)
  with self.assertRaises(ValueError):validate_pair('A'*19,'N'*19+'U'*19+'N'*19)
  audit=validate_pair('A'*19,'N'*19+'U'*19+'N'*19,allow_unknown_flanks=True);self.assertEqual(audit['context_quality'],'DEGRADED_OR_EDGE_CONTEXT');self.assertEqual(audit['real_left_flank_nt'],0);self.assertEqual(audit['real_right_flank_nt'],0)
 def test_batch_native_agreement_is_real(self):
  checks=j(OUT/'batch_native_checks.json');self.assertGreater(len(checks),0)
  self.assertTrue(all(c['absolute_delta']<=.011 for c in checks))
 def test_target_out_selection_does_not_select_on_held_gene(self):
  metrics={(r['config_id'],r['gene']):r for r in j(OUT/'measured_metrics.json')};steps=j(OUT/'retrospective_target_out_selection.json');self.assertEqual(len(steps),4)
  for step in steps:
   allowed=['C00_rnai_native21','C01_rnai_core19','C02_rnaispline_core19','C03_oligoformer_core19'][:step['step']+1]
   for f in step['folds']:
    self.assertNotIn(f['held_gene'],f['selection_genes']);self.assertEqual(len(f['selection_genes']),2)
    best=max(allowed,key=lambda c:sum(metrics[c,g]['auc'] for g in f['selection_genes'])/2);self.assertEqual(f['chosen_config'],best);self.assertEqual(f['held_gene_auc'],metrics[best,f['held_gene']]['auc'])
 def test_small_n_and_unsupported_tasks_are_not_promoted(self):
  for r in j(OUT/'measured_metrics.json'):
   if r['gene']=='MYC':self.assertIsNone(r['auc_ci95_row_bootstrap'])
  summary=j(OUT/'sweep_summary.json');self.assertEqual(summary['new_models_trained'],0);self.assertEqual(summary['new_generation_runs'],0);self.assertEqual(summary['full_application_tasks_completed'],0)
  for task in ['005_metabolic-liver-galnac','008_inflammation-immune']:self.assertEqual(j(ROOT/'results'/task/RUN/'status.json')['configs_executed'],0)
 def test_all_image_artifacts_decode_and_have_history(self):
  images=j(OUT/'figure_validation.json')+j(OUT/'snapshot_image_validation.json');self.assertEqual(len(images),45)
  for r in images:
   with Image.open(ROOT/r['path']) as im:im.verify()
   self.assertGreater(r['width'],1000);self.assertGreater(r['height'],500)
  self.assertEqual((ROOT/'results/001_general'/RUN/'performance_overview.png').read_bytes(),(OUT/'performance_overview.png').read_bytes())
 def test_reranked_panels_preserve_gates_and_diversity(self):
  ledger=rows(OUT/'config_execution_ledger.csv')
  for x in ledger:
   d=ROOT/x['results_path'];p=d/'panel.csv'
   if not p.exists():continue
   panel=rows(p);st=j(d/'panel_stability.json');good={r['candidate_id'] for r in rows(ROOT/st['gate_decision_source']) if r['gate_pass']=='True'}
   self.assertEqual(sha(ROOT/st['gate_decision_source']),st['gate_source_sha256']);self.assertTrue({r['candidate_id'] for r in panel}<=good);self.assertEqual(len({r['guide_sequence'][1:8] for r in panel}),len(panel))
   starts=[int(float(r['target_start'])) for r in panel];self.assertTrue(all(abs(a-b)>=19 for i,a in enumerate(starts) for b in starts[i+1:]));self.assertEqual(len(st['stability_post_diversity_jaccard']),10)
   for r in panel:self.assertEqual(r['evidence_status'],'NEEDS_EXPERIMENTAL_VALIDATION');self.assertNotIn('rank_score',r)
 def test_reporter_sensitivity_retains_rows_and_censoring(self):
  rs=rows(OUT/'htt_duplex_predictions.csv');self.assertEqual(len(rs),104)
  for cid in {r['config_id'] for r in rs}:
   rr=[r for r in rs if r['config_id']==cid];self.assertEqual(len(rr),26);self.assertEqual(sum(r['censored']=='True' for r in rr),5)
  self.assertEqual(len(rows(OUT/'htt_context_control_predictions.csv')),78)
if __name__=='__main__':unittest.main()
