"""Synthetic scenario results must remain traceable, physical and non-empirical."""
import json
import math
import unittest
from pathlib import Path

from evaluation.exploratory_scenarios import recipe, draw_scenarios, percentile

CFG = Path(__file__).resolve().parent.parent/'configs/exploratory_ranolazine_500.json'


class ExploratoryContractTests(unittest.TestCase):
    def setUp(self):
        self.cfg=json.loads(CFG.read_text())

    def test_published_recipe_mass_dose_and_explicit_limits(self):
        for name,parts in self.cfg['literature_formulations_mg'].items():
            candidate,checks=recipe(parts['compritol'],parts['carbopol_934'],
                                    self.cfg['literature_hardness_kg_per_cm2'][name],self.cfg)
            self.assertFalse(checks['failed'])
            self.assertIn('dose_potency_balance_mg',checks['passed'])
            self.assertEqual(sum(x['amount'] for x in candidate['ingredients']),695)
            self.assertEqual(next(x['amount'] for x in candidate['ingredients'] if x['material_id']=='avicel_PH101'),parts['avicel_PH101'])
        with self.assertRaises(ValueError):
            recipe(105,70,9.0,self.cfg)  # MCC below literature design window
        with self.assertRaises(ValueError):
            recipe(84,35,11,self.cfg)

    def test_scenario_draws_deterministic_and_sign_uncertain(self):
        a=list(draw_scenarios(self.cfg)); b=list(draw_scenarios(self.cfg))
        self.assertEqual(a,b)
        self.assertEqual(len(a),256)
        self.assertTrue(any(x['compritol_log_rate_per_35mg']>0 for x in a))
        self.assertTrue(any(x['compritol_log_rate_per_35mg']<0 for x in a))
        self.assertEqual(percentile([1,2,3],.5),2)

    def test_full_run_if_openpkflow_installed(self):
        try:
            import openpkflow
        except ImportError:
            self.skipTest('optional isolated openpkflow environment')
        from evaluation.exploratory_scenarios import run
        result=run(self.cfg)
        self.assertEqual(result['product'],'research_prototype_NOT_Glenmark')
        self.assertEqual(result['grid_size'],117)
        self.assertIsNone(result['calibrated_uncertainty'])
        self.assertIsNone(result['experimental_validation'])
        for candidate in result['top_three_distinct_illustrative_compositions']:
            self.assertTrue(math.isclose(sum(candidate['mixture_percent_ww'].values()),100))
            self.assertEqual(candidate['mixture_mg']['ranolazine'],500)
            self.assertEqual(candidate['in_exploratory_window_only']['failed'],[])
            for model in ('first_order','weibull'):
                profile=candidate['simulated']['profiles_percent'][model]
                self.assertEqual(profile['0']['p50'],0)
                self.assertTrue(all(profile[str(t)]['p50']<=profile[str(u)]['p50']
                                    for t,u in zip([0,2,4,8,12,18],[2,4,8,12,18,24])))
        sens=result['sensitivity']
        self.assertGreater(sens['compritol_70_to_105mg_at_assumed_positive_slope']['delta_release_2h_percent'],0)
        self.assertLess(sens['compritol_70_to_105mg_at_assumed_negative_slope']['delta_release_2h_percent'],0)
        from evaluation.exploratory_verifier import verify_scenario
        self.assertEqual(verify_scenario(result,self.cfg),[])
        import copy
        changed=copy.deepcopy(result)
        changed['top_three_distinct_illustrative_compositions'][0]['score']+=.1
        self.assertIn('candidate_grid_mismatch',verify_scenario(changed,self.cfg))
        changed=copy.deepcopy(result)
        changed['top_three_distinct_illustrative_compositions'][0]['simulated']['profiles_percent']['weibull']['8']['p50']=200
        self.assertIn('release_bounds_or_quantiles',verify_scenario(changed,self.cfg))


if __name__=='__main__':unittest.main()
