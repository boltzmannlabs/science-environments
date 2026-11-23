"""Regression checks for evidence integrity, CLI status and fixture-only laboratory flow."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.dissolution_history import profile_rows, normalize, archive_profile_origins, validate_profile, write_history
from tools.dissolution_analysis import analyze, comparable
from tools.dissolution_runner import submit, poll, ingest
from evaluation.sequential_replay import Replay, benchmark

class HistoryTests(unittest.TestCase):
    def test_reference_once_and_source_distinction(self):
        rows=profile_rows()
        self.assertEqual(sum(r['profile_id']=='201741007784_Ranexa_1g' for r in rows),8)
        self.assertEqual(len({r['profile_id'] for r in rows}),12)
        self.assertTrue(all(r['batch_id']!='DJ25134' for r in rows))
        self.assertTrue(all(r['evidence_label']=='literature_reported' for r in rows))
    def test_units_missing_and_over100(self):
        rows=profile_rows()
        self.assertEqual(normalize(next(r for r in rows if r['profile_id']=='zenodo_F8_endpoint'))['derived_time_min'],1440)
        self.assertEqual(next(r for r in rows if r['profile_id']=='US6525057_SR_B' and r['time_value']==24)['release_value'],105.6)
        self.assertIsNone(next(r for r in rows if r['profile_id']=='US6525057_IR' and r['time_value']==24)['release_value'])
        self.assertFalse(validate_profile({**rows[0],'time_unit':None})['valid'])
    def test_method_and_dose_separation(self):
        rows=profile_rows()
        self.assertFalse(comparable(rows[0],next(r for r in rows if r['profile_id']=='US6525057_SR_B')))
        self.assertFalse(comparable(rows[0],next(r for r in rows if r['profile_id']=='zenodo_F8_endpoint')))
        result=analyze(rows,'201741007784_Ranexa_1g')
        self.assertEqual(result['specification_attainment']['status'],'not_evaluated')
        self.assertEqual(result['baseline_differences']['US6525057_SR_B']['status'],'not_evaluated')
    def test_manifest_and_prior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);legacy=root/'archive';prior=root/'prior';out=root/'out'
            csv=legacy/'dissolution_data_curation/data/processed/profiles.csv';csv.parent.mkdir(parents=True)
            csv.write_text('source_type,release\nsimulation,20\nexperimental,30\n')
            result=write_history(out,legacy,prior)
            self.assertEqual(json.loads((out/'archive_row_origins.json').read_text()),{'simulation':1,'experimental':1})
            self.assertEqual(result['counts']['usable_affected_lot_profiles'],0)
            self.assertTrue((out/'history_manifest.csv').is_file())

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.plan={'plan_id':'P','method_id':'M','sample_ids':['S1'],'idempotency_key':'K'}
    def tearDown(self):self.tmp.cleanup()
    def test_approval_is_not_string(self):
        self.assertEqual(submit('laboratory',self.root,plan=self.plan,authorization='A',backend='fixture')['status'],'approval_required')
        self.assertEqual(submit('laboratory',self.root,plan=self.plan,backend='fixture',dry_run=True)['status'],'dry_run')
        (self.root/'approvals.json').write_text(json.dumps({'A':{'status':'approved','issuer':'fixture_test','plan_id':'P'}}))
        first=submit('laboratory',self.root,plan=self.plan,authorization='A',backend='fixture')
        self.assertEqual(first['run_id'],submit('laboratory',self.root,plan=self.plan,authorization='A',backend='fixture')['run_id'])
        self.assertEqual(poll(self.root,first['run_id'])['status'],'submitted')
        self.assertEqual(ingest(self.root,first['run_id'])['status'],'not_evaluated')
        self.assertIsNone(first['evidence_label'])
    def test_unavailable_and_replay(self):
        self.assertEqual(submit('laboratory',self.root,plan=self.plan,authorization='A',backend='real')['status'],'approval_required')
        self.assertEqual(submit('predict',self.root)['status'],'insufficient_data')
        replay=Replay({'A':{'data_origin':'experimental','evidence_label':'literature_reported','value':50},'B':{'data_origin':'synthetic','value':40}},1)
        self.assertNotIn('value',replay.catalog()[0])
        self.assertEqual(replay.select('B')['status'],'unscorable_candidate')
        self.assertEqual(replay.select('A')['observation']['event_type'],'historical_replay_not_new_measurement')
        self.assertEqual(replay.select('A')['status'],'already_revealed')
        self.assertEqual(benchmark()['status'],'not_evaluated')

if __name__=='__main__': unittest.main()
