#!/usr/bin/env python3
"""Software fixtures ONLY: no experimental measurements, real design or model inference."""
from pathlib import Path
import argparse,unittest,tempfile,importlib.util,json,csv,random,os,sys
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
h=module('sirna_portable');t=module('transfer_skill');SCRATCH=None
class PortableTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='sirna-software-fixtures-',dir=SCRATCH);self.p=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def js(self,name,value):
  path=self.p/name;path.write_text(json.dumps(value));return path
 def objective(self,**changes):
  value={'schema_version':1,'design_type':'sirna','experiment_id':'SOFTWARE_FORMAT_FIXTURE_ONLY','organism':'Homo sapiens','target':{'primary_accession_version':'NM_004985.5'},'coverage_references':['NM_033360.4'],'requested_count':20,'representation':'paired19nt_RNA_cores','study_mode':'shared','mutation_specification':None};value.update(changes);return self.js('objective.json',value)
 def candidate(self):
  rng=random.Random(17);seq=''.join(rng.choice('ACGU') for _ in range(120));core=seq[40:59];assert seq.count(core)==1
  fa=self.p/'software_fixture.fasta';fa.write_text('>SOFTWARE_FIXTURE_NOT_A_BIOLOGICAL_TARGET\n'+seq+'\n');row={'candidate_id':'SOFTWARE_FIXTURE1','guide_sequence':h.rc(core),'passenger_sequence':core,'target_start':'41','target_end':'59'};csvpath=self.p/'candidates.csv';self.table(csvpath,[row]);return csvpath,fa,row,seq
 def table(self,path,data):
  with Path(path).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 def gates(self,overrides=None):
  evidence=self.p/'SOFTWARE_EVIDENCE_ONLY.txt';evidence.write_text('Not experimental evidence; tests gate algebra only.');gates=[{'name':name,'required':True,'status':'PASSED','evidence_refs':[evidence.name],'failed_criteria':[],'missing_evidence':[],'warnings':[],'method_version':'SOFTWARE_FIXTURE'} for name in sorted(h.MIN_GATES)]
  if overrides:gates[0].update(overrides)
  return self.js('gates.json',{'gates':gates})
 def package(self):
  p=self.p/'source skill with spaces';p.mkdir();(p/'assets').mkdir();(p/'SKILL.md').write_text('---\nname: sirna-harness\nversion: 2.0.0\n---\nSoftware installation fixture only.\n');(p/'assets/LICENSE.txt').write_text('Original software fixture; not scientific assets.');self.seal(p);return p
 def seal(self,p):(p/t.MANIFEST).write_text(json.dumps({'skill_name':'sirna-harness','version':'2.0.0','files':t.inventory(p)}))
 def test_objective_format_and_no_implicit_validation(self):self.assertEqual(h.objective_check(self.objective())['status'],'VALID_REQUEST_REFERENCE_VALIDATION_REQUIRED')
 def test_missing_parameters_fail(self):self.assertEqual(h.objective_check(self.objective(organism=None))['status'],'FAILED')
 def test_other_RNA_modality_rejected(self):self.assertEqual(h.objective_check(self.objective(design_type='aso'))['status'],'FAILED')
 def test_accession_not_repaired(self):self.assertEqual(h.objective_check(self.objective(target={'primary_accession_version':' NM_004985.5'}))['status'],'FAILED')
 def test_comparative_mutation_blocked(self):self.assertEqual(h.objective_check(self.objective(study_mode='comparative'))['mutation_arm_status'],'BLOCKED_PENDING_MUTATION_SPECIFICATION')
 def test_provided_mutation_not_validated_or_constructed(self):
  spec={'exact_nucleotide_change_or_verified_mutant_sequence':'UNVALIDATED_USER_TOKEN','reference_accession_version':'NM_004985.5','mutant_vs_wild_type_objective':'USER_MUST_DEFINE'};result=h.objective_check(self.objective(study_mode='mutation_selective',mutation_specification=spec));self.assertEqual(result['mutation_arm_status'],'SPECIFIED_REQUIRES_REFERENCE_ALLELE_VALIDATION');self.assertFalse(result['mutant_constructed'])
 def test_core_pair_mapping_positive(self):
  path,fa,_,_=self.candidate();r=h.candidates_check(path,fa,'RNA');self.assertEqual(r['status'],'PASSED');self.assertTrue(r['records'][0]['default_model_input_eligible'])
 def test_DNA_reference_requires_explicit_alphabet(self):
  path,fa,_,seq=self.candidate();fa.write_text('>FIXTURE\n'+seq.replace('U','T')+'\n');self.assertEqual(h.candidates_check(path,fa,'DNA')['status'],'PASSED')
 def test_wrong_coordinate_fails(self):
  path,fa,row,_=self.candidate();row['target_start']='40';self.table(path,[row]);self.assertEqual(h.candidates_check(path,fa,'RNA')['status'],'FAILED')
 def test_no_silent_lowercase_repair(self):
  path,fa,row,_=self.candidate();row['guide_sequence']=row['guide_sequence'].lower();self.table(path,[row]);self.assertEqual(h.candidates_check(path,fa,'RNA')['status'],'FAILED')
 def test_duplicate_ids_fail(self):
  path,fa,row,_=self.candidate();self.table(path,[row,row]);self.assertEqual(h.candidates_check(path,fa,'RNA')['status'],'FAILED')
 def test_repeated_site_not_silently_first_matched(self):
  path,fa,row,seq=self.candidate();fa.write_text('>FIXTURE\n'+seq+row['passenger_sequence']+'\n');r=h.candidates_check(path,fa,'RNA');self.assertEqual(r['status'],'PASSED');self.assertFalse(r['records'][0]['default_model_input_eligible'])
 def test_missing_full_flanks_explicit(self):
  path,fa,row,seq=self.candidate();fa.write_text('>FIXTURE\n'+row['passenger_sequence']+seq+'\n');row['target_start']='1';row['target_end']='19';self.table(path,[row]);r=h.candidates_check(path,fa,'RNA');self.assertFalse(r['records'][0]['full19nt_flanks'])
 def test_all_gate_claims_do_not_certify_biology(self):
  r=h.gates_check(self.gates());self.assertEqual(r['configured_required_evidence_state'],'PASSED');self.assertFalse(r['fully_qualified'])
 def test_required_failure_precedes_missing(self):
  r=h.gates_check(self.gates({'status':'FAILED','failed_criteria':['SOFTWARE_FIXTURE_FAILURE'],'missing_evidence':['also missing']}));self.assertEqual(r['configured_required_evidence_state'],'FAILED')
 def test_passed_boolean_with_missing_not_a_pass(self):self.assertEqual(h.gates_check(self.gates({'missing_evidence':['absent']}))['configured_required_evidence_state'],'BLOCKED_MISSING_EVIDENCE')
 def test_string_Boolean_rejected(self):
  with self.assertRaises(ValueError):h.gates_check(self.gates({'required':'False'}))
 def test_required_NA_rejected(self):
  with self.assertRaises(ValueError):h.gates_check(self.gates({'status':'NOT_APPLICABLE'}))
 def test_empty_gate_list_rejected(self):
  with self.assertRaises(ValueError):h.gates_check(self.js('empty.json',{'gates':[]}))
 def test_missing_evidence_file_blocks(self):self.assertEqual(h.gates_check(self.gates({'evidence_refs':['absent.csv']}))['configured_required_evidence_state'],'BLOCKED_MISSING_EVIDENCE')
 def test_no_backend_inference_from_presence(self):
  r=h.preflight(self.js('config.json',{'schema_version':1,'executables':{'python':sys.executable},'assets':[]}));self.assertEqual(r['status'],'FILES_PRESENT_EXECUTION_UNVERIFIED');self.assertFalse(r['backend_inference_verified'])
 def test_missing_assets_block(self):self.assertEqual(h.preflight(self.js('config.json',{'schema_version':1,'assets':[{'name':'missing','path':None,'sha256':None}]}))['status'],'BLOCKED_MISSING_CONFIGURATION')
 def test_secret_values_rejected(self):
  with self.assertRaises(ValueError):h.preflight(self.js('config.json',{'schema_version':1,'api_key':'SOFTWARE_TEST_NOT_A_REAL_SECRET'}))
 def test_blank_repeated_headers_fail_closed(self):
  p=self.p/'bad.csv';p.write_text(',label,\nAAA,1,x\n')
  with self.assertRaises(ValueError):h.csv_rows(p)
 def test_table_quality_not_independence(self):
  p=self.p/'labels.csv';self.table(p,[{'sequence':'ACGU','label':'1'},{'sequence':'ACGU','label':''}]);r=h.benchmark_check(p,'sequence','label','SOFTWARE_TEST_UNITS_NOT_BIOLOGICAL');self.assertEqual(r['missing_or_nonfinite_labels'],1);self.assertFalse(r['independence_established']);self.assertEqual(r['predictions_attempted'],0)
 def test_package_integrity(self):self.assertEqual(t.check(self.package())['status'],'PASSED')
 def test_package_tamper_fails(self):
  p=self.package();(p/'SKILL.md').write_text('altered')
  with self.assertRaises(ValueError):t.check(p)
 def test_dry_run_no_write(self):
  p=self.package();dest=self.p/'new skills'/'sirna-harness';t.install(p,dest);self.assertFalse(dest.exists())
 def test_install_to_path_with_spaces(self):
  p=self.package();dest=self.p/'clean active profile'/'skills'/'sirna-harness';r=t.install(p,dest,True);self.assertTrue(r['installed']);self.assertEqual(t.check(dest)['status'],'PASSED');self.assertFalse(r['scientific_assets_installed'])
 def test_existing_destination_untouched(self):
  p=self.package();dest=self.p/'existing';dest.mkdir();keep=dest/'keep.txt';keep.write_text('UNCHANGED')
  with self.assertRaises(FileExistsError):t.install(p,dest,True)
  self.assertEqual(keep.read_text(),'UNCHANGED')
 def test_no_model_payload_bundling(self):
  p=self.package();(p/'assets/not_real_model.pth').write_text('Software rejection fixture, not weights')
  with self.assertRaises(ValueError):t.inventory(p)
 def test_no_symlink_payload(self):
  p=self.package()
  try:(p/'assets/link').symlink_to(p/'SKILL.md')
  except OSError:self.skipTest('Symlink operation unsupported on this platform')
  with self.assertRaises(ValueError):t.inventory(p)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--scratch',required=True);args=parser.parse_args();SCRATCH=str(Path(args.scratch).resolve());Path(SCRATCH).mkdir(parents=True,exist_ok=True);unittest.main(argv=[sys.argv[0]],verbosity=2)
