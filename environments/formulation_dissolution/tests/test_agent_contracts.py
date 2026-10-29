"""Bounded agent contract/abstention tests."""
import unittest
from agents.formulation_design import DesignRequest, propose
from agents.compatibility_stability import CompatibilityRequest, assess
from agents.property_prediction import PredictionRequest, predict
from agents.experimental_design import ExperimentRequest, design
from agents.constraint_critic import CriticRequest, critique
from agents.evidence_auditor import AuditRequest, audit


class AgentsTests(unittest.TestCase):
    def test_contracts_and_abstentions(self):
        self.assertEqual(propose(DesignRequest({}, {'ingredients':[{'material_id':'x'}]})).status,'insufficient_data')
        self.assertEqual(assess(CompatibilityRequest(('x',))).status,'insufficient_data')
        self.assertEqual(predict(PredictionRequest('t','c',{})).status,'insufficient_data')
        self.assertEqual(audit(AuditRequest((),{})).decision,'abstain')
        self.assertIn('dose_potency_basis', critique(CriticRequest({'ingredients':[{'material_id':'x','amount':100,'unit':'% w/w'}]})).not_evaluated)
        self.assertEqual(design(ExperimentRequest('hypothesis',('x',),('y',),('control',),2,'discriminate')).status,'proposed')
        with self.assertRaises(ValueError): ExperimentRequest('',(),(),(),0,'')
        with self.assertRaises(TypeError): propose({})

    def test_auditor_rejects_predictions_as_measurements(self):
        c = ({'text':'test','label':'measured','source_id':'s'},)
        self.assertEqual(audit(AuditRequest(c, {'s':{'citation':'fixture'}})).decision,'revise')


if __name__ == '__main__': unittest.main()
