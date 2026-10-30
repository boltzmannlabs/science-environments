"""State transitions, approval, provenance, recovery."""
import unittest
from environment.actions import Action, execute
from environment.state import Episode
from environment.budget import Budget


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.s = Episode({'task_id':'t'})
        self.source = {'source_id':'s','citation':'fixture','document_id':'fixture-1','verified_by':'test','verified_fields':['primary_recall_record'],'authorized_measurement':True,'measurement_authorization_id':'fixture-auth'}
        execute(self.s, Action('verify_source',self.source))

    def test_candidate_and_recovery(self):
        execute(self.s, Action('register_material',{'material_id':'X','source_id':'s'}))
        c = {'candidate_id':'c','ingredients':[{'material_id':'X','amount':100,'unit':'mg'}],'tablet_mass':100}
        self.assertEqual(execute(self.s,Action('validate_candidate',{'candidate':c})).status,'success')
        self.assertEqual(execute(self.s,Action('predict_dissolution',{'candidate_id':'c'})).status,'tool_unavailable')
        self.assertEqual(execute(self.s,Action('update_ranking',{'ranking':['c']})).status,'success')
        self.s.evidence.append({'text':'synthetic test-only claim','label':'literature_reported','source_id':'s'})
        self.assertEqual(execute(self.s,Action('finalize_episode')).status,'success')
        self.assertEqual(self.s.status,'finalized')
        self.assertEqual(execute(self.s, Action('update_ranking',{'ranking':[]})).status,'failure')

    def test_measurement_guard(self):
        p = {'experiment_id':'e','factors':['x'],'responses':['y'],'controls':['c'],'replicates':1,'rationale':'fixture'}
        self.assertEqual(execute(self.s,Action('design_experiment',p)).status,'approval_required')
        fake = {'experiment_id':'e','source_id':'s','confirmed_by':'tester','approval_id':'approval-fixture','values':[{'name':'r','value':2,'unit':'%','label':'predicted','source_id':'s'}]}
        self.assertEqual(execute(self.s,Action('record_measurement',fake)).status,'failure')
        self.assertEqual(self.s.experiments['e']['status'],'proposed')
        fake['values'][0]['label'] = 'measured'
        self.assertEqual(execute(self.s,Action('record_measurement',fake)).status,'success')
        self.assertEqual(self.s.experiments['e']['status'],'completed')

    def test_budget(self):
        b = Budget({'actions':0})
        self.assertEqual(execute(self.s,Action('finalize_episode'),budget=b).status,'failure')
        self.assertEqual(self.s.status,'open')


if __name__ == '__main__': unittest.main()
