"""Independent Task - 01 contracts; no model/lab success inferred from filenames."""
from pathlib import Path
import hashlib
import json
import sys
import unittest
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

ENV = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENV / 'src'))
from formulation_environment.task_01_clarithromycin_ir_formulation_dissolution.constraints import NAMES, BOUNDS, validate_composition

TASK_FOLDER = 'task-01-clarithromycin-ir-formulation-dissolution'
BENCH = ENV / 'benchmark' / TASK_FOLDER
RESULTS = ENV / 'results' / TASK_FOLDER
V2 = RESULTS / 'v2'


def load(path):
    return json.loads(Path(path).read_text())


class Task01ContractTests(unittest.TestCase):
    def test_objective_title_and_overall_scope(self):
        text = (ENV / 'tasks' / TASK_FOLDER / 'README.md').read_text()
        for phrase in ['Clarithromycin 500 mg', '## Overall task', '## Objective', '## Actual outcome']:
            self.assertIn(phrase, text)

    def test_frozen_config_matches_constraint_code(self):
        config = load(ENV / 'config/task-01-clarithromycin-ir-formulation-dissolution/contract.json')
        self.assertEqual(config['API_mg'], 500)
        self.assertEqual(config['finished_tablet_mg'], 800)
        self.assertEqual(config['allowed_excipients'], list(NAMES[1:]))
        self.assertEqual(config['bounds_percent_finished_tablet'], {n: list(v) for n, v in BOUNDS.items()})

    def test_task_record_does_not_claim_physical_superiority(self):
        record = load(RESULTS / 'task_record.json')
        self.assertEqual(record['task_id'], 'Task - 01')
        self.assertEqual(record['candidate_lab_observations'], 0)
        self.assertEqual(record['candidate_recipe_predictions'], 0)
        self.assertIsNone(record['efficacy_rank'])
        self.assertEqual(record['literature_product_superiority'], 'NOT_ESTABLISHED')


class ConstraintTests(unittest.TestCase):
    def setUp(self):
        self.base = {x['name']: x['mg'] for x in load(V2 / 'expanded_candidates.json')[1]['ingredients']}

    def test_valid_base(self):
        self.assertEqual(validate_composition(self.base), [])

    def test_wrong_api_rejected(self):
        m = self.base.copy(); m['Clarithromycin'] -= 1; m['Microcrystalline Cellulose'] += 1
        self.assertIn('API_DOSE', validate_composition(m))

    def test_missing_identity_rejected(self):
        m = self.base.copy(); del m['PEG 4000']
        self.assertEqual(validate_composition(m), ['INGREDIENT_IDENTITIES'])

    def test_extra_identity_rejected(self):
        self.assertEqual(validate_composition({**self.base, 'Lactose': 0}), ['INGREDIENT_IDENTITIES'])

    def test_nonfinite_rejected(self):
        self.assertEqual(validate_composition({**self.base, 'Crospovidone': float('nan')}), ['NONFINITE_MASS'])

    def test_negative_rejected(self):
        self.assertIn('NEGATIVE_MASS', validate_composition({**self.base, 'Crospovidone': -1}))

    def test_out_of_bounds_rejected(self):
        m = self.base.copy(); m['Microcrystalline Cellulose'] -= 5; m['Magnesium Stearate'] += 5
        self.assertIn('BOUND:Magnesium Stearate', validate_composition(m))

    def test_fixed_mass_error_rejected(self):
        m = self.base.copy(); m['Microcrystalline Cellulose'] += .4
        self.assertIn('FIXED_TABLET_MASS', validate_composition(m))

    def test_duplicate_and_near_duplicate_rejected(self):
        self.assertIn('DUPLICATE_OR_NEAR_DUPLICATE_LT_1MG', validate_composition(self.base, [self.base]))
        m = self.base.copy(); m['Crospovidone'] += .5; m['Microcrystalline Cellulose'] -= .5
        self.assertIn('DUPLICATE_OR_NEAR_DUPLICATE_LT_1MG', validate_composition(m, [self.base]))

    def test_one_mg_boundary_is_not_near_duplicate(self):
        m = self.base.copy(); m['Crospovidone'] += 1; m['Microcrystalline Cellulose'] -= 1
        self.assertNotIn('DUPLICATE_OR_NEAR_DUPLICATE_LT_1MG', validate_composition(m, [self.base]))


class ScientificRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pred = pd.read_csv(V2 / 'all_evaluation_predictions.csv')
        cls.records = load(V2 / 'expanded_candidates.json')
        cls.fits = load(V2 / 'all_fit_parameters.json')

    def test_28_unique_composition_valid_designs(self):
        self.assertEqual(len(self.records), 28)
        seen = []
        for row in self.records:
            masses = {x['name']: x['mg'] for x in row['ingredients']}
            self.assertEqual(validate_composition(masses, seen), [], row['formulation_id'])
            self.assertAlmostEqual(sum(masses.values()), 800, places=8)
            self.assertAlmostEqual(row['core_mg'] + row['coat_mg'], 800, places=8)
            for ing in row['ingredients']:
                self.assertAlmostEqual(ing['w_w_percent'], ing['mg'] / 8)
            seen.append(masses)

    def test_all_candidate_response_fields_abstain(self):
        for row in self.records:
            self.assertEqual(row['status'], 'DESIGN_ONLY')
            self.assertEqual(row['dissolution']['status'], 'NOT_PREDICTED')
            self.assertIsNone(row['dissolution']['predicted_profile'])
            self.assertIsNone(row['dissolution']['measured_profile'])
            self.assertIsNone(row['rank'])
            self.assertIsNone(row['model']['external_validation'])

    def test_original_24_preserved(self):
        original = load(BENCH / 'inputs/candidates.json')
        self.assertEqual(len(original), 24)
        self.assertEqual(self.records[:24], original)

    def test_input_hashes(self):
        check = load(V2 / 'verification.json')
        for file, key in [('candidates.json', 'benchmark_candidates_source_sha256'), ('literature_profiles.json', 'literature_profiles_source_sha256')]:
            self.assertEqual(hashlib.sha256((BENCH / 'inputs' / file).read_bytes()).hexdigest(), check[key])

    def test_all_published_observations_preserved_not_clipped(self):
        source = load(BENCH / 'inputs/literature_profiles.json')
        mapping = {p['id']: dict(zip(p['time_min'], p['reported_mean_percent'])) for p in source}
        self.assertEqual(len(source), 16)
        self.assertEqual(self.pred.profile_id.nunique(), 15)
        self.assertGreater(self.pred.literature_percent.max(), 100)
        for row in self.pred.itertuples():
            self.assertAlmostEqual(row.literature_percent, mapping[row.profile_id][row.time_min])

    def test_heldout_splits_disjoint_and_counts(self):
        self.assertEqual(len(self.fits), 1155)
        self.assertEqual(len(self.pred), 1815)
        for fit in self.fits:
            if fit['split'] != 'in_sample_all5':
                self.assertFalse(set(fit['train_times_min']) & set(fit['test_times_min']))
        for model, g in self.pred.groupby('model'):
            self.assertEqual(len(g[g.split == 'LOTO']), 75, model)
            self.assertEqual(len(g[g.split == 'forward30']), 15, model)

    def test_forward30_is_same_loto_fold_not_independent(self):
        for model, g in self.pred.groupby('model'):
            a = g[(g.split == 'LOTO') & (g.time_min == 30)].sort_values('profile_id')
            b = g[g.split == 'forward30'].sort_values('profile_id')
            self.assertEqual(list(a.profile_id), list(b.profile_id))
            np.testing.assert_allclose(a.fitted_or_heldout_percent, b.fitted_or_heldout_percent, atol=1e-9)

    def test_every_aggregate_metric_recomputed(self):
        expected = load(BENCH / 'expected_metrics.json')
        for row in expected['metrics']:
            g = self.pred[(self.pred.model == row['model']) & (self.pred.split == row['split'])]
            self.assertEqual(len(g), row['test_points'])
            self.assertAlmostEqual(float(np.sqrt(np.mean(g.signed_error_pp**2))), row['RMSE_pp'], places=7)
            self.assertAlmostEqual(float(abs(g.signed_error_pp).mean()), row['MAE_pp'], places=7)
            self.assertAlmostEqual(float(abs(g.relative_error_percent).mean()), row['MAPE_percent'], places=7)

    def test_signed_errors_are_not_release_improvements(self):
        np.testing.assert_allclose(self.pred.fitted_or_heldout_percent - self.pred.literature_percent, self.pred.signed_error_pp, atol=1e-9)

    def test_bounded_output_limits(self):
        bounded = self.pred[self.pred.model.str.endswith(('cap100', 'fixed100'))]
        self.assertLessEqual(bounded.fitted_or_heldout_percent.max(), 100 + 1e-8)
        self.assertGreaterEqual(bounded.fitted_or_heldout_percent.min(), -1e-8)

    def test_worse_outcomes_not_suppressed(self):
        changes = load(V2 / 'before_after_comparison.json')
        self.assertEqual(len(changes), 9)
        self.assertTrue(any(x['RMSE_reduction_percent'] < 0 for x in changes))
        self.assertTrue(any(x['RMSE_reduction_percent'] > 0 for x in changes))

    def test_factorial_interaction_matrix_rank(self):
        designs = load(V2 / 'factorial_design.json')
        self.assertEqual(len(designs), 9)
        matrix = []
        for row in designs:
            x, z = row['factor_codes']['CP'], row['factor_codes']['PVP']
            matrix.append([1, x, z, x*z, x*x, z*z])
        self.assertEqual(np.linalg.matrix_rank(matrix), 6)
        self.assertEqual(len(designs) - np.linalg.matrix_rank(matrix), 3)
        self.assertEqual(sum(x['formulation_id'].startswith('I') for x in designs), 4)

    def test_planned_measurements_are_empty(self):
        plan = pd.read_csv(V2 / 'planned_measurement_template.csv')
        self.assertEqual(len(plan), 1980)
        self.assertTrue((plan.status == 'PLANNED_NOT_RUN').all())
        self.assertTrue(plan.measured_intact_API_percent.isna().all())
        self.assertTrue(plan.measured_degradants_percent.isna().all())
        self.assertEqual(len(plan[['batch_id', 'medium_id', 'unit_id']].drop_duplicates()), 198)

    def test_reports_have_verified_table_and_figure_counts(self):
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
        for path, tables, figures in [(RESULTS / 'v1/clarithromycin_800mg_benchmark_report.docx', 16, 6), (V2 / 'clarithromycin_improvements_v2_report.docx', 8, 4)]:
            with zipfile.ZipFile(path) as z:
                self.assertIsNone(z.testzip())
                root = ET.fromstring(z.read('word/document.xml'))
                self.assertEqual(len(root.findall('.//w:tbl', ns)), tables)
                self.assertEqual(len(root.findall('.//wp:inline', ns)), figures)


if __name__ == '__main__':
    unittest.main()
