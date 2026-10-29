import copy
import json
from pathlib import Path
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from leadopt_env.core import CampaignStore, digest
from leadopt_env.contracts import SCHEMAS, validate_task
from leadopt_env.evaluation import evaluate


def read(path):
    return json.loads((ROOT / path).read_text())


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'campaigns.sqlite3'
        self.store = CampaignStore(self.path)
        self.task = read('tasks/synthetic/task.json')
        self.store.dispatch('create', 'campaign', {'task': self.task})
        for record in read('tasks/synthetic/candidates.json'):
            self.call('candidate', record)
        for record in read('tasks/synthetic/observations.json'):
            self.call('observation', record)

    def call(self, operation, payload=None):
        return self.store.dispatch(operation, 'campaign', payload)

    def freeze(self):
        return self.call('freeze', dict(id='final', candidate_ids=['candidate-a'], rationale='synthetic comparison', stopping_reason='fixture complete'))

    def test_schema_exports_match_runtime(self):
        for name, schema in SCHEMAS.items():
            exported = read('config/' + name + '.schema.json')
            exported.pop('$schema')
            self.assertEqual(exported, schema)
        validate_task(self.task)

    def test_comparisons_and_constraints_remain_separate(self):
        report = self.call('report')
        rows = {r['candidate_id']: r for r in report['comparisons']}
        self.assertEqual(rows['candidate-a']['delta'], 2)
        self.assertEqual(rows['candidate-a']['status'], 'pass')
        self.assertEqual(rows['candidate-b']['status'], 'fail')
        self.assertEqual(next(r for r in report['assessments'] if r['candidate_id'] == 'candidate-b')['status'], 'fail')
        self.assertFalse(report['coverage']['complete'])

    def test_missing_scientific_input_warns_but_creates(self):
        report = self.store.dispatch('create', 'incomplete', {'task': dict(schema_version=1,id='minimal',version='1')})
        self.assertTrue(report['warnings'])
        self.assertEqual(report['campaign_id'], 'incomplete')

    def test_atomic_creation_failure(self):
        task = copy.deepcopy(self.task)
        task['initial_observations'][0]['candidate_id'] = 'absent'
        with self.assertRaises(ValueError):
            self.store.dispatch('create', 'bad', {'task': task})
        with self.assertRaises(KeyError):
            self.store.dispatch('report', 'bad')

    def test_identity_records_are_immutable(self):
        c = read('tasks/synthetic/candidates.json')[0]
        self.assertTrue(self.call('candidate', c)['idempotent'])
        c['representation'] = 'different'
        with self.assertRaises(ValueError):
            self.call('candidate', c)

    def test_warn_and_continue_preserves_pending_attempt(self):
        check = self.call('check', dict(id='advice',job='forbidden',candidate_ids=['candidate-a'],resource_requests={'scientific_submissions':3}))
        self.assertTrue(check['can_continue'])
        self.assertIn('job_not_allowed', [w['code'] for w in check['warnings']])
        action = dict(id='event1',attempt_id='attempt1',job='forbidden',candidate_ids=['candidate-a'],status='unknown',check_id='advice',source='synthetic exception after submission')
        self.assertTrue(self.call('action', action)['recorded'])
        self.store = CampaignStore(self.path)
        report = self.call('report')
        self.assertEqual(len(report['unresolved_usage_commitments']), 1)
        self.assertEqual(report['unresolved_usage_commitments'][0]['resource_requests']['scientific_submissions'], 3)
        self.assertEqual(len(report['actions']), 1)
        self.assertIn('job_not_allowed', [w['code'] for w in report['warnings']])
        self.assertTrue(self.call('action', action)['idempotent'])

    def test_attempt_completion_is_recorded_without_resubmission(self):
        action = dict(id='event1',attempt_id='attempt1',job='synthetic_assessment',candidate_ids=['candidate-a'],status='accepted',source='fixture',job_id='job1')
        self.call('action', action)
        self.call('action', {**action, 'id':'event2', 'status':'completed'})
        self.assertFalse(self.call('report')['unresolved_usage_commitments'])
        with self.assertRaises(ValueError):
            self.call('action', {**action, 'id':'event3', 'status':'running'})

    def test_usage_categories_are_not_added_together(self):
        for category, amount in [('requested',3),('observed',1),('estimated',4),('unknown',None)]:
            self.call('usage', dict(id=category,unit='scientific_submissions',amount=amount,category=category,scope='campaign',source='synthetic'))
        summary = self.call('report')['resource_summary']['scientific_submissions']
        self.assertEqual(summary['observed|campaign']['amount'], 1)
        self.assertIsNone(summary['unknown|campaign']['amount'])
        with self.assertRaises(ValueError):
            self.call('usage', dict(id='bad',unit='u',amount=0,category='unknown',scope='campaign',source='fixture'))

    def test_observation_cannot_claim_success_from_incomplete_action(self):
        self.store.dispatch('create', 'execution', {'task': self.task})
        def call(op, payload=None):
            return self.store.dispatch(op, 'execution', payload)
        call('candidate', read('tasks/synthetic/candidates.json')[0])
        action = dict(id='accepted',attempt_id='attempt',job='synthetic_assessment',candidate_ids=['candidate-a'],status='accepted',source='fixture')
        call('action', action)
        record = {**read('tasks/synthetic/observations.json')[0], 'action_id':'accepted'}
        call('observation', record)
        row = next(r for r in call('report')['comparisons'] if r['candidate_id'] == 'candidate-a')
        self.assertEqual(row['status'], 'unresolved')
        call('action', {**action, 'id':'completed', 'status':'completed'})
        row = next(r for r in call('report')['comparisons'] if r['candidate_id'] == 'candidate-a')
        self.assertEqual(row['status'], 'pass')
        with self.assertRaises(ValueError):
            call('observation', {**record,'id':'wrong-candidate','candidate_id':'lead','form_id':'lead-form'})

    def test_minimization_and_target_distance(self):
        from leadopt_env.assessment import assess
        report = self.call('report')
        candidates = {c['id']: c for c in report['candidates']}
        task = copy.deepcopy(self.task)
        task['objectives'][0].update(direction='minimize')
        rows, _ = assess(task, candidates, report['observations'])
        self.assertEqual(next(r for r in rows if r['candidate_id']=='candidate-b')['improvement'], 2)
        task['objectives'][0].update(direction='range',target_min=3,target_max=5)
        rows, _ = assess(task, candidates, report['observations'])
        self.assertEqual(next(r for r in rows if r['candidate_id']=='candidate-a')['improvement'], 1)

    def test_nan_and_boolean_are_not_numeric_observations(self):
        record = read('tasks/synthetic/observations.json')[0]
        for invalid in (float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                self.call('observation', {**record, 'id':'invalid', 'value':invalid})

    def test_decision_cannot_cite_nonexistent_evidence(self):
        with self.assertRaises(ValueError):
            self.call('decision', dict(id='d',question='fixture',outcome='supported',evidence_ids=['absent'],next_action='stop',rationale='fixture'))

    def test_frozen_submission_unchanged_after_new_evidence(self):
        frozen = self.freeze()
        extra = read('tasks/synthetic/observations.json')[0]
        self.call('observation', {**extra, 'id':'later', 'value':100})
        self.assertEqual(self.freeze(), frozen)
        self.assertNotEqual(len(self.call('report')['observations']), len(frozen['snapshot']['observations']))

    def test_offline_evaluator_uses_reference_not_search_score(self):
        self.call('usage', dict(id='count',unit='scientific_submissions',amount=1,category='observed',scope='campaign',source='fixture'))
        frozen = self.freeze()
        result = evaluate(frozen, read('tests/synthetic-reference.json'), frozen['digest'])
        self.assertEqual(result['results'][0]['objectives'][0]['improvement'], 1)
        self.assertTrue(result['results'][0]['all_objectives_met'])
        self.assertFalse(result['isolation_verified'])
        self.assertIn('Artificial', result['claim'])

    def test_tampering_and_wrong_task_reference_rejected(self):
        frozen = self.freeze()
        reference = read('tests/synthetic-reference.json')
        altered = copy.deepcopy(frozen)
        altered['snapshot']['submission']['candidate_ids'] = ['candidate-b']
        altered['digest'] = digest(altered['snapshot'])
        with self.assertRaises(ValueError):
            evaluate(altered, reference, frozen['digest'])
        reference['task_digest'] = 'other'
        with self.assertRaises(ValueError):
            evaluate(frozen, reference, frozen['digest'])

    def test_reference_identity_mismatch_rejected(self):
        frozen = self.freeze()
        reference = read('tests/synthetic-reference.json')
        reference['candidates'][1]['representation'] = 'other-form'
        with self.assertRaises(ValueError):
            evaluate(frozen, reference, frozen['digest'])

    def test_budget_overrun_is_reported_not_erased(self):
        self.call('usage', dict(id='count',unit='scientific_submissions',amount=3,category='observed',scope='campaign',source='fixture'))
        frozen = self.freeze()
        result = evaluate(frozen, read('tests/synthetic-reference.json'), frozen['digest'])
        self.assertEqual(result['results'][0]['eligibility'], 'fail')
        self.assertTrue(result['results'][0]['all_objectives_met'])
        self.assertEqual(frozen['snapshot']['resource_summary']['scientific_submissions']['observed|campaign']['amount'],3)


if __name__ == '__main__':
    unittest.main()
