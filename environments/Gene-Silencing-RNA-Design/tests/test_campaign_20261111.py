"""Artifact-level tests for the executed Run-3 campaign. No model reruns or scientific fixture claims."""
import unittest,pathlib,json,csv,hashlib,math
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN='Run-3_2026-11-11';OUT=ROOT/'benchmark/011_Campaign-reproduction'/RUN

def load(p):return json.loads(pathlib.Path(p).read_text())
def rows(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
class TestExecutedCampaign(unittest.TestCase):
 def test_all_tasks_accounted_without_false_completion(self):
  rs=load(OUT/'task_execution_status.json');self.assertEqual(len(rs),11)
  self.assertEqual({r['task'].split('_')[0] for r in rs},{f'{i:03d}' for i in range(1,12)})
  self.assertTrue(all(not r['full_task_complete'] for r in rs))
  for r in rs:self.assertTrue((ROOT/r['results']/'REPORT.md').is_file())
 def test_old_artifacts_unchanged(self):
  for tree in ['results','benchmark']:
   for line in (ROOT/tree/'PROVENANCE.sha256').read_text().splitlines():
    want,path=line.split(maxsplit=1);self.assertEqual(hashlib.sha256((ROOT/tree/path).read_bytes()).hexdigest(),want)
 def test_generation_and_orientation(self):
  for task in ['003_genetic-disease-total-lowering','005_metabolic-liver-galnac','008_inflammation-immune','002_oncology','010_gene-regulation']:
   d=ROOT/'results'/task/RUN;seq=''.join((d/'00_inputs/transcript.fa').read_text().splitlines()[1:]);pool=rows(d/'00_inputs/candidate_pool.csv')
   self.assertEqual(len(pool),len(seq)-18)
   for r in pool:
    self.assertEqual(r['passenger_sequence'],seq[int(r['target_start'])-1:int(r['target_end'])]);self.assertEqual(r['guide_sequence'],r['passenger_sequence'].translate(str.maketrans('AUCG','UAGC'))[::-1])
    self.assertTrue(math.isfinite(float(r['oligoformer_native_score'])))
   battery=rows(d/'per_dimension_evidence.csv');self.assertEqual(len(battery),24)
   self.assertGreater(max(float(r['same_gene_isoform_hits']) for r in battery),0)
 def test_panels_are_gate_clean_diverse_and_unblended(self):
  for p in (ROOT/'results').glob('*/'+RUN+'/ranking_and_stability.json'):
   rep=load(p);d=p.parent;panel=rows(d/'delivered_panel.csv');gates={r['candidate_id']:r for r in rows(d/'gate_decisions.csv')}
   self.assertIsNone(rep['best_design']);self.assertEqual(rep['evidence_tier'],'NEEDS_EXPERIMENTAL_VALIDATION')
   self.assertEqual(len(panel),len(rep['panel']));self.assertLessEqual(len(panel),6)
   self.assertEqual(len({r['guide_sequence'][1:8] for r in panel}),len(panel))
   starts=[int(float(r['target_start'])) for r in panel]
   self.assertTrue(all(abs(a-b)>=19 for i,a in enumerate(starts) for b in starts[i+1:]))
   for r in panel:
    self.assertEqual(gates[r['candidate_id']]['gate_pass'],'True');self.assertEqual(gates[r['candidate_id']]['missing'],'')
    self.assertNotIn('rank_score',r);self.assertNotIn('rank_components',r);self.assertEqual(r['E4e'],'NOT_RUN(broken-binary)')
    self.assertTrue(math.isfinite(float(r['eff_RN.Ai-Predict'])));self.assertTrue(math.isfinite(float(r['oligoformer_native_score'])))
   self.assertEqual(len(rep['post_diversity_panel_jaccard_pm25pct']),10)
 def test_no_labels_in_design_inputs(self):
  for p in (ROOT/'results').glob('*/'+RUN+'/00_inputs/battery_candidates.csv'):
   self.assertFalse({'label','efficacy','measured','ifn_induction_binary'} & set(rows(p)[0]))
 def test_simone_exact_prediction_replay(self):
  m=load(OUT/'simone/metrics.json');self.assertEqual(m['n'],322);self.assertEqual(m['n_paired_prior_predictions'],322);self.assertEqual(m['max_abs_prediction_delta_vs_prior'],0)
  self.assertAlmostEqual(m['auc'],.7021412837457097,places=12);self.assertEqual(m['n_excluded'],0)
  self.assertIsNone(m['per_accession']['NM_002467.6']['auc_ci95_stratified_row_bootstrap'])
 def test_primary_table_derived_reporters_and_censoring(self):
  rs=rows(OUT/'allele_reporter_energies.csv');self.assertEqual(len(rs),26);self.assertEqual(sum(r['discrimination_ratio_censored']=='True' for r in rs),5)
  for r in rs:
   self.assertEqual(len(r['guide_sequence']),21);self.assertEqual(len(r['reporter_match_footprint']),21)
   self.assertAlmostEqual(float(r['ddg_kcal_mol']),float(r['dg_mismatch_kcal_mol'])-float(r['dg_match_kcal_mol']))
  m=load(OUT/'allele_reporter_metrics.json');self.assertIn('BLOCKED',m['design_status']);self.assertEqual(m['n_uncensored_discrimination_ratios'],21)
 def test_immune_curation_is_not_a_safety_claim(self):
  m=load(OUT/'immune_metrics.json');self.assertEqual(m['n'],8);self.assertEqual(m['tp']+m['fn']+m['tn']+m['fp'],8)
  rs=rows(OUT/'immune_curated_evaluation.csv');self.assertFalse(any('siNP' in r['sequence_id'] for r in rs))
  self.assertTrue(all(r['corrected_pmid']=='19630977' for r in rs if r['sequence_id'].startswith('Goodchild')))
 def test_existing_run_guard_precedes_input_writes(self):
  import importlib.util
  from unittest.mock import patch
  spec=importlib.util.spec_from_file_location('campaign_guard',ROOT/'runtime/run_campaign_20261111.py')
  assert spec is not None and spec.loader is not None
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with patch.object(module,'setup') as setup:
   with self.assertRaisesRegex(RuntimeError,'Already evaluated'):module.evaluate('TTR')
   setup.assert_not_called()
 def test_no_remote_success_claim(self):
  m=load(OUT/'boltzmann_attempt.json');self.assertEqual(m['terminal_status'],'failed');self.assertFalse(m['resubmitted']);self.assertFalse(m['candidate_artifact_returned'])
 def test_transcript_identity_primary_verification(self):
  recs=load(OUT/'transcript_verification.json');self.assertEqual(len(recs),6)
  self.assertTrue(all(r['status'].startswith('VERIFIED') for r in recs))
  h=next(r for r in recs if r['gene']=='HIF1A');self.assertIn('(HIF1A)',h['header']);self.assertTrue(h['local_sequence_identical'])
 def test_manifest_target_files_exist(self):
  for p in (ROOT/'benchmark').glob('*/'+RUN+'/comparison_manifest.json'):
   m=load(p);self.assertEqual(hashlib.sha256((ROOT/m['primary_artifact']).read_bytes()).hexdigest(),m['primary_artifact_sha256'])
if __name__=='__main__':unittest.main()
