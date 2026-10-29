#!/usr/bin/env python3
"""Technical-report software acceptance. Mutations are labelled SOFTWARE_FIXTURE.
No model inference, new biological designs or experimental results are produced.
"""
from pathlib import Path
import argparse,csv,json,shutil,subprocess,sys,tempfile,unittest
ENV=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ENV/'scripts'))
import technical_reporting as t
SCRATCH=None
CASE=ENV/'results/case_studies/KRAS_14_technical_validation';POLICY=ENV/'config/technical_gate_policy.json'

class TechnicalReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='technical-report-SOFTWARE_FIXTURE-',dir=SCRATCH);self.root=Path(self.tmp.name);self.case=self.root/'case';shutil.copytree(CASE,self.case);self.bundle=self.case/'bundle.json';self.policy=self.root/'policy.json';shutil.copy2(POLICY,self.policy)
        b=t.load(self.bundle);b['evidence_origin']='SOFTWARE_FIXTURE_NOT_SCIENTIFIC_RESULT';b['source_job']='fixture-current';b['reproducibility_source_job']='fixture-earlier';self.put(self.bundle,b)
    def tearDown(self):self.tmp.cleanup()
    def put(self,p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
    def path(self,key):return self.case/t.load(self.bundle)['inputs'][key]['path']
    def rebind(self,key):
        b=t.load(self.bundle);b['inputs'][key]['sha256']=t.sha(self.path(key));self.put(self.bundle,b)
    def change_csv(self,key,fun):
        rows=t.read_csv(self.path(key));fun(rows)
        with self.path(key).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        self.rebind(key)
    def ev(self):return t.evaluate(self.bundle,self.policy)
    def test_recorded_case_has14_positive_technical_passes(self):
        r=t.evaluate(CASE/'bundle.json',POLICY);self.assertEqual(r['technical_status'],'PASSED_DECLARED_TECHNICAL_GATES');self.assertEqual(r['technical_pass_count'],14);self.assertEqual(r['evidence_origin'],'RECORDED_LOCAL_SIRNA_BENCH_RUN')
    def test_fixture_origin_is_explicit(self):self.assertEqual(self.ev()['evidence_origin'],'SOFTWARE_FIXTURE_NOT_SCIENTIFIC_RESULT')
    def test_recorded_snapshot_hashes(self):self.assertEqual(t.verify_case(CASE)['status'],'PASSED')
    def test_evaluation_leaves_originals_unchanged(self):
        before={p:t.sha(p) for p in CASE.rglob('*') if p.is_file()};t.evaluate(CASE/'bundle.json',POLICY);self.assertEqual(before,{p:t.sha(p) for p in before})
    def test_pair_error_fails(self):
        self.change_csv('candidates',lambda r:r[0].update(guide_sequence='A'*19));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_native_sequence_change_fails(self):
        self.change_csv('bench_results',lambda r:r[0].update(guide='A'*19));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_zero_coordinate_fails(self):
        self.change_csv('candidates',lambda r:r[0].update(target_start='0'));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_wrong_transcript_token_fails(self):
        self.change_csv('candidates',lambda r:r[0].update(transcript_id='NM_004985.4'));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_duplicate_candidate_refused(self):
        self.change_csv('candidates',lambda r:r.append(dict(r[0])))
        with self.assertRaises(ValueError):self.ev()
    def test_missing_native_row_refused(self):
        self.change_csv('bench_results',lambda r:r.pop())
        with self.assertRaises(ValueError):self.ev()
    def test_required_model_NOT_RUN_blocks(self):
        self.change_csv('bench_results',lambda r:r[0].update({'eff_RN.Ai-Predict_status':'NOT_RUN'}));self.assertEqual(self.ev()['technical_status'],'BLOCKED_MISSING_TECHNICAL_EVIDENCE')
    def test_missing_numeric_evidence_blocks(self):
        self.change_csv('bench_results',lambda r:r[0].update(guide_target_duplex_delta_g_kcal_mol=''));self.assertEqual(self.ev()['technical_status'],'BLOCKED_MISSING_TECHNICAL_EVIDENCE')
    def test_nonfinite_numeric_evidence_cannot_pass(self):
        self.change_csv('bench_results',lambda r:r[0].update(guide_target_duplex_delta_g_kcal_mol='nan'));self.assertNotEqual(self.ev()['technical_status'],'PASSED_DECLARED_TECHNICAL_GATES')
    def test_explicit_property_failure_fails(self):
        self.change_csv('bench_results',lambda r:r[0].update({'eff_RN.Ai-Predict':'40'}));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_native_explicit_failure_fails(self):
        self.change_csv('bench_gates',lambda r:r[1].update(passed='False',failed_criteria='SOFTWARE_FIXTURE_FAILURE'));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_failed_criteria_override_native_True(self):
        self.change_csv('bench_gates',lambda r:r[1].update(passed='True',failed_criteria='SOFTWARE_FIXTURE_FAILURE'));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_required_gate_missing_blocks(self):
        self.change_csv('bench_gates',lambda r:r.pop(1));self.assertEqual(self.ev()['technical_status'],'BLOCKED_MISSING_TECHNICAL_EVIDENCE')
    def test_unknown_native_missing_evidence_blocks(self):
        self.change_csv('bench_gates',lambda r:r[1].update(missing_evidence='required computational evidence missing'));self.assertEqual(self.ev()['technical_status'],'BLOCKED_MISSING_TECHNICAL_EVIDENCE')
    def test_experimental_True_with_missing_is_retained_not_promoted(self):
        r=self.ev();self.assertEqual(r['technical_status'],'PASSED_DECLARED_TECHNICAL_GATES');self.assertTrue(all(any(f['flag']=='SEPARATE_SCOPE_MISSING_EVIDENCE' for f in c['review_flags']) for c in r['candidates']));self.assertNotIn('fully_qualified',r)
    def test_orientation_gap_independently_checked_but_preserved(self):
        self.assertTrue(all(any(f.get('detail')=='orientation_documentation' for f in c['review_flags']) for c in self.ev()['candidates']))
    def test_code_only_model_is_never_successful_inference(self):
        self.assertTrue(all(c['raw_model_statuses']['siRNADiscovery']=='code_only' for c in self.ev()['candidates']))
    def test_reproducibility_mismatch_fails(self):
        self.change_csv('reproducibility_results',lambda r:r[0].update({'eff_RN.Ai-Predict':'1'}));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_reproducibility_missing_value_blocks(self):
        self.change_csv('reproducibility_results',lambda r:r[0].update({'eff_RN.Ai-Predict':''}));self.assertEqual(self.ev()['technical_status'],'BLOCKED_MISSING_TECHNICAL_EVIDENCE')
    def test_same_job_as_own_reproducibility_refused(self):
        b=t.load(self.bundle);b['reproducibility_source_job']=b['source_job'];self.put(self.bundle,b)
        with self.assertRaises(ValueError):self.ev()
    def test_mandatory_gates_cannot_be_removed(self):
        p=t.load(self.policy);p['required_technical_gates'].pop();self.put(self.policy,p)
        with self.assertRaises(ValueError):self.ev()
    def test_nonfinite_JSON_policy_refused(self):
        self.policy.write_text('{"schema_version":NaN}')
        with self.assertRaises(ValueError):self.ev()
    def test_changed_bytes_without_new_binding_refused(self):
        self.path('candidates').write_text(self.path('candidates').read_text()+'\n')
        with self.assertRaises(ValueError):self.ev()
    def test_path_traversal_refused(self):
        b=t.load(self.bundle);b['inputs']['candidates']['path']='../outside.csv';self.put(self.bundle,b)
        with self.assertRaises(ValueError):self.ev()
    def test_absolute_evidence_path_refused(self):
        b=t.load(self.bundle);b['inputs']['candidates']['path']=str(self.path('candidates'));self.put(self.bundle,b)
        with self.assertRaises(ValueError):self.ev()
    def test_symlink_evidence_refused(self):
        p=self.path('candidates');q=self.root/'elsewhere.csv';shutil.copy2(p,q);p.unlink();p.symlink_to(q)
        with self.assertRaises(ValueError):self.ev()
    def test_duplicate_csv_headers_refused(self):
        self.path('candidates').write_text('candidate_id,candidate_id\na,b\n');self.rebind('candidates')
        with self.assertRaises(ValueError):self.ev()
    def test_duplicate_json_keys_refused(self):
        self.bundle.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(ValueError):self.ev()
    def test_reference_DNA_conversion_requires_literal_approval(self):
        b=t.load(self.bundle);b['allow_DNA_reference_comparison']=1;self.put(self.bundle,b)
        with self.assertRaises(ValueError):self.ev()
    def test_reference_alphabet_is_not_silently_repaired(self):
        r=t.load(self.path('references'));r[0]['alphabet']='RNA';self.put(self.path('references'),r);self.rebind('references')
        with self.assertRaises(ValueError):self.ev()
    def test_reference_gene_metadata_conflict_refused(self):
        r=t.load(self.path('references'));r[0]['gene']='OTHER';self.put(self.path('references'),r);self.rebind('references')
        with self.assertRaises(ValueError):self.ev()
    def test_repeated_primary_site_fails_unique_mapping(self):
        r=t.load(self.path('references'));r[0]['sequence']*=2;self.put(self.path('references'),r);self.rebind('references');self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_missing_coverage_in_one_reference_fails(self):
        r=t.load(self.path('references'));r[1]['sequence']='A'*len(r[1]['sequence']);self.put(self.path('references'),r);self.rebind('references');self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_report_output_never_overwritten(self):
        out=self.root/'report';t.write_report(self.bundle,self.policy,out)
        with self.assertRaises(ValueError):t.write_report(self.bundle,self.policy,out)
    def test_positive_report_serialization_and_manifest(self):
        out=self.root/'report';r=t.write_report(self.bundle,self.policy,out);self.assertEqual(r['technical_pass_count'],14)
        m=t.load(out/'output_manifest.json');receipt=t.load(out/'verification_receipt.json');self.assertEqual(receipt['output_manifest_sha256'],t.sha(out/'output_manifest.json'))
        for item in m['files']:self.assertEqual(t.sha(out/item['path']),item['sha256'])
        self.assertIn('14 of 14 candidates passed', (out/'technical_report.md').read_text())
    def test_risk_flags_survive_positive_headline(self):
        r=self.ev();self.assertEqual(sum(any(f['flag']=='RIDGE_EXTRAPOLATION' for f in c['review_flags']) for c in r['candidates']),9);self.assertEqual(sum(any(f['flag']=='PASSENGER_SEED_ANNOTATION_LT50' for f in c['review_flags']) for c in r['candidates']),4)
    def test_failure_precedes_missing(self):
        self.change_csv('candidates',lambda r:r[0].update(guide_sequence='A'*19));self.change_csv('bench_results',lambda r:r[0].update({'eff_RN.Ai-Predict_status':'NOT_RUN'}));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_snapshot_tamper_detected(self):
        self.path('candidates').write_text(self.path('candidates').read_text()+'\n');self.assertEqual(t.verify_case(self.case)['status'],'FAILED')
    def test_supplemental_sequence_identity_mismatch_fails(self):
        self.change_csv('supplemental_annotations',lambda r:r[0].update(guide_sequence='A'*19));self.assertEqual(self.ev()['technical_status'],'FAILED_DECLARED_TECHNICAL_GATES')
    def test_recorded_near_match_counts_remain_visible(self):
        r=self.ev();site=next(c for c in r['candidates'] if c['candidate_id'].endswith('_280'));self.assertTrue(any(f['flag']=='RECORDED_NEAR_MATCH_OPPORTUNITIES' for f in site['review_flags']))
    def test_shared_scope_notes_are_not_repeated_per_candidate(self):
        out=self.root/'report';t.write_report(self.bundle,self.policy,out);text=(out/'technical_report.md').read_text();self.assertEqual(text.count('no experimental measurements supplied'),1);self.assertIn('14 of 14 candidates passed',text)
    def test_cli_explicit_failed_status_exit2(self):
        self.change_csv('candidates',lambda r:r[0].update(guide_sequence='A'*19));proc=subprocess.run([sys.executable,'-B',str(ENV/'scripts/run.py'),'technical-report','--bundle',str(self.bundle),'--policy',str(self.policy),'--out',str(self.root/'cli-report')],capture_output=True,text=True);self.assertEqual(proc.returncode,2);self.assertEqual(json.loads(proc.stdout)['status'],'FAILED_DECLARED_TECHNICAL_GATES')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);a=p.parse_args();SCRATCH=str(Path(a.scratch).resolve());Path(SCRATCH).mkdir(parents=True,exist_ok=True);unittest.main(argv=[sys.argv[0]],verbosity=2)
