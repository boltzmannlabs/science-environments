#!/usr/bin/env python3
"""Environment software tests only. No generated designs or experimental measurements."""
from pathlib import Path
import argparse,csv,json,subprocess,sys,tempfile,unittest,hashlib
ENV=Path(__file__).resolve().parents[1];SCRATCH=None

def load(path):return json.loads(Path(path).read_text())
class EnvironmentTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='sirna-environment-fixtures-',dir=SCRATCH);self.p=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def invoke(self,*args,expected=0):
  proc=subprocess.run([sys.executable,'-B',str(ENV/'scripts/run.py'),*args],capture_output=True,text=True,timeout=60);self.assertEqual(proc.returncode,expected,(proc.stdout,proc.stderr));return json.loads(proc.stdout)
 def test_describe_does_not_claim_inference_or_biology(self):
  r=self.invoke('describe');self.assertEqual(r['project_name'],'siRNA Designing Harness');self.assertFalse(r['scientific_backend_dispatch']);self.assertFalse(r['biological_validation'])
 def test_project_structure_and_local_links(self):self.assertEqual(self.invoke('check-project')['status'],'PASSED')
 def test_full_skill_payload_hashes(self):self.assertEqual(self.invoke('check-skill')['status'],'PASSED')
 def test_blank_preflight_is_honest_blocker(self):self.assertEqual(self.invoke('preflight','--config',str(ENV/'config/environment.example.json'),expected=2)['status'],'BLOCKED_MISSING_CONFIGURATION')
 def test_shared_KRAS_intake_not_reference_validation(self):
  r=self.invoke('validate-objective','--objective',str(ENV/'tasks/kras-shared-review.json'));self.assertEqual(r['status'],'VALID_REQUEST_REFERENCE_VALIDATION_REQUIRED');self.assertEqual(r['mutation_arm_status'],'NOT_APPLICABLE')
 def test_comparative_example_blocks_mutant_construction(self):
  r=self.invoke('validate-objective','--objective',str(ENV/'tasks/kras-mutation-blocked.json'));self.assertEqual(r['mutation_arm_status'],'BLOCKED_PENDING_MUTATION_SPECIFICATION');self.assertFalse(r['mutant_constructed'])
 def test_unspecified_objective_refused(self):self.assertEqual(self.invoke('validate-objective','--objective',str(ENV/'config/objective.example.json'),expected=2)['status'],'FAILED')
 def test_unresolved_gate_template_cannot_qualify(self):
  r=self.invoke('check-gates','--gates',str(ENV/'config/gates.example.json'),expected=2);self.assertFalse(r['fully_qualified']);self.assertEqual(r['configured_required_evidence_state'],'BLOCKED_MISSING_EVIDENCE')
 def test_other_modality_not_accepted(self):
  obj=load(ENV/'tasks/kras-shared-review.json');obj['design_type']='shrna';path=self.p/'objective.json';path.write_text(json.dumps(obj));self.assertEqual(self.invoke('validate-objective','--objective',str(path),expected=2)['status'],'FAILED')
 def test_label_table_fixture_not_independent_data(self):
  path=self.p/'SOFTWARE_FIXTURE_NOT_MEASURED.csv';path.write_text('guide,label\nACGU,1\nACGU,\n');r=self.invoke('audit-label-table','--dataset',str(path),'--sequence-column','guide','--label-column','label','--label-unit','SOFTWARE_FIXTURE_UNITS',expected=2);self.assertEqual(r['missing_or_nonfinite_labels'],1);self.assertEqual(r['predictions_attempted'],0);self.assertFalse(r['independence_established'])
 def test_missing_history_not_fabricated(self):self.assertEqual(self.invoke('verify-history','--evidence-root',str(self.p),expected=2)['status'],'BLOCKED_MISSING_EVIDENCE')
 def test_tampered_history_is_a_failure(self):
  registry=load(ENV/'results/historical_evidence_index.json');path=self.p/registry['records'][0]['source_files'][0]['relative_path'];path.parent.mkdir(parents=True);path.write_text('{}');r=self.invoke('verify-history','--evidence-root',str(self.p),expected=2);self.assertEqual(r['status'],'FAILED');self.assertTrue(r['mismatches'])
 def test_historical_result_counts_are_explicit(self):
  registry=load(ENV/'results/historical_evidence_index.json');r={x['evidence_id']:x['metrics'] for x in registry['records']};self.assertEqual(r['shared_design']['generated_records'],5288);self.assertEqual(r['shared_design']['fully_qualified'],0);self.assertEqual(r['workflow_comparison']['exact_pair_overlap_conditional14'],0);self.assertEqual(r['independent_benchmark']['benchmark_status'],'BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET')
 def test_fifteen_unique_capability_categories(self):
  r=load(ENV/'config/capability_registry.json');self.assertEqual(len({x['category'] for x in r['capabilities']}),15)
 def test_task_modes_and_NO_auto_jobs(self):
  for name in ['audit','sensitivity','benchmark','literature-comparison']:
   r=load(ENV/'tasks'/(name+'.json'));self.assertTrue(r['outputs']);self.assertTrue(r['prohibited']);self.assertIn('mode',r)
 def test_output_status_contract(self):
  r=load(ENV/'config/output_contracts.json');self.assertEqual(set(r['gate_statuses']),{'PASSED','FAILED','BLOCKED_MISSING_EVIDENCE','NOT_RUN','NOT_APPLICABLE'});self.assertIn('verification_receipt.json',r['minimum_design_artifacts'])
 def test_no_backend_paths_hardcoded_in_CLI(self):self.assertNotIn('/home/boltzmann13',(ENV/'scripts/run.py').read_text())
 def test_no_scientific_backend_dispatch_command(self):
  p=subprocess.run([sys.executable,'-B',str(ENV/'scripts/run.py'),'generate'],capture_output=True,text=True);self.assertEqual(p.returncode,2);self.assertIn('invalid choice',p.stderr)
 def test_no_existing_profile_or_service_configuration_changed_by_import(self):
  # The entry point exposes only described technical commands; no model/service imports.
  text=(ENV/'scripts/run.py').read_text();self.assertNotIn('import torch',text);self.assertNotIn('import sci_bootstrap',text);self.assertNotIn('urlopen',text)
 def test_benchmark_snapshot_integrity(self):
  r=self.invoke('verify-benchmark');self.assertEqual(r['status'],'PASSED');self.assertEqual(r['copied_source_files'],85);self.assertEqual(r['scientific_runs'],0)
 def test_benchmark_status_not_biological_validation(self):
  r=self.invoke('verify-benchmark');self.assertEqual(r['biological_status'],'PARTIAL');self.assertEqual(r['independent_benchmark_status'],'BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET');self.assertEqual(r['mutation_arm_status'],'BLOCKED_PENDING_MUTATION_SPECIFICATION')
 def test_profile_configuration_template_has_no_tokens(self):
  r=load(ENV/'config/environment.example.json');self.assertFalse(r['remote_transfer_authorized']);self.assertTrue(all(x['path'] is None for x in r['assets']))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--scratch',required=True);args=parser.parse_args();SCRATCH=str(Path(args.scratch).resolve());Path(SCRATCH).mkdir(parents=True,exist_ok=True);unittest.main(argv=[sys.argv[0]],verbosity=2)
