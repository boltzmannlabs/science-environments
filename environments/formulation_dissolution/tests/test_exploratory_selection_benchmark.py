"""Exercise selection safety and negative-control benchmark using real OpenPKFlow if installed."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from evaluation.exploratory_selection_benchmark import run

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'configs/exploratory_ranolazine_500.json'
SCENARIO=ROOT/'data/processed/ranolazine_500_exploratory_new_run.json'

class SelectedBenchmarkTests(unittest.TestCase):
    def test_rejects_inconsistent_scenario(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bad.json';path.write_text(json.dumps({'status':'measured','config':{}}))
            with self.assertRaises(ValueError):run(CFG,path,Path(tmp)/'out.json')
    @unittest.skipUnless(importlib.util.find_spec('openpkflow'),'OpenPKFlow only in isolated scenario environment')
    def test_selection_and_zero_effect_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=run(CFG,SCENARIO,Path(tmp)/'result.json')
            self.assertEqual(result['selected_id'],'grid_C84_B42_H8.5')
            self.assertEqual(result['ajanta_specification_attainment'],'not_evaluated')
            self.assertEqual(result['validated_improvement'],'not_established')
            negative=result['zero_effect_negative_control']
            self.assertEqual(negative['selected']['median_release_percent_at_24h'],negative['F8_same_assumed_hardness']['median_release_percent_at_24h'])
            self.assertGreater(negative['F1_lowest_polymer_same_assumed_hardness']['toy_score'],negative['selected']['toy_score'])

if __name__=='__main__': unittest.main()
