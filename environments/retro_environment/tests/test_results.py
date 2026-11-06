"""Validate curated retro_environment records without requiring platform access."""
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestRouteSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = json.loads((ROOT / 'results/route_summary.json').read_text())
        cls.audit = json.loads((ROOT / 'results/top0_validation.json').read_text())

    def test_target_and_unique_routes(self):
        self.assertEqual(self.routes['schema_version'], 1)
        self.assertEqual(len(self.routes['routes']), 16)
        self.assertEqual([r['route'] for r in self.routes['routes']], [f'top{i}' for i in range(16)])
        self.assertEqual(self.routes['target_smiles'], self.audit['target_smiles'])

    def test_explicit_steps_and_model_yields(self):
        for r in self.routes['routes']:
            self.assertEqual(r['explicit_tree_steps'], len(r['steps']))
            self.assertTrue(r['steps'])
            self.assertEqual(r['experimental_validation'], 'not established')
            yields = [s['model_reaction_yield_pct'] for s in r['steps']]
            self.assertTrue(all(isinstance(y, (int, float)) and 0 <= y <= 100 for y in yields))
            expected = round(100 * math.prod(y / 100 for y in yields), 2)
            self.assertAlmostEqual(r['illustrative_sequential_product_pct'], expected)
            self.assertTrue(all(s['reactants'] and s['product'] for s in r['steps']))

    def test_selected_route_and_cautions(self):
        a, b = self.routes['routes'][:2]
        self.assertEqual(a['explicit_tree_steps'], 3)
        self.assertEqual(b['explicit_tree_steps'], 3)
        self.assertEqual(a['illustrative_sequential_product_pct'], 30.91)
        self.assertEqual(b['illustrative_sequential_product_pct'], 39.15)
        self.assertEqual(len(self.audit['steps']), 3)
        self.assertEqual(self.audit['steps'][1]['forward_model_score'], 0)
        self.assertIn('catalyst missing', self.audit['steps'][1]['assessment'])
        self.assertIn('fluoride opposes', self.audit['steps'][0]['assessment'])
        self.assertNotIn('job_name', self.audit)
        self.assertNotIn('doc_id', self.audit)


if __name__ == '__main__':
    unittest.main()
