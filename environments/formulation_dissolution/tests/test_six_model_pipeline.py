"""Contracts for six-model fitting and grouped synthetic-only evaluation."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from evaluation.six_model_pipeline import MODELS, synthetic_batches, fitted_curve, evaluate_synthetic, evaluate_literature, scores
from evaluation.six_model_verifier import verify

ROOT=Path(__file__).resolve().parents[1]

class SixModelTests(unittest.TestCase):
    def test_synthetic_labels_and_frozen_batches(self):
        rows=synthetic_batches()
        self.assertEqual(len(rows),24)
        self.assertTrue(all(r['data_origin']=='synthetic' and r['evidence_label']!='measured' for r in rows))
        self.assertEqual(len({r['batch_id'] for r in rows}),len(rows))
        self.assertEqual(scores([10,20],[12,22])['bias_pp'],2)
    def test_bad_time_grid_rejected(self):
        with self.assertRaises(ValueError):fitted_curve([0,2,2,3,4],[0,10,10,20,30],'fixture')
    @unittest.skipUnless(importlib.util.find_spec('openpkflow'),'requires isolated OpenPKFlow v2.9.0')
    def test_all_six_models_and_verifier(self):
        syn=evaluate_synthetic()
        self.assertEqual(len(syn['models']),len(MODELS))
        self.assertEqual(syn['batch_counts'],{'train':12,'validation':4,'test':8})
        self.assertEqual(syn['selected_by_synthetic_validation_macro_RMSE_NOT_product_reliability'],'weibull')
        lit=evaluate_literature(ROOT/'data/processed/literature_profiles.json')
        self.assertTrue(all(x['fit_to_same_curve'] for x in lit['fits']))
        result={'synthetic':syn,'published':lit,'approved_ajanta_lot_QC':'not_evaluated',
                'mixture_model':{'status':'not_trained'},'PTCalc':{'status':'tool_unavailable'},
                'mechanistic_model':{'status':'not_evaluated'}}
        self.assertEqual(verify(result,synthetic_batches()),[])
        result['synthetic']['per_test_batch_scores'][0]['mae_pp']=0
        self.assertIn('per_batch_score_mismatch',verify(result,synthetic_batches()))

if __name__=='__main__':unittest.main()
