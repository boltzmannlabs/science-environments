"""Check published tables and missing-evidence semantics against model records."""
import csv
import json
import re
from urllib.parse import unquote
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


class TestComparisons(unittest.TestCase):
    def test_metrics_match_routes(self):
        routes = json.loads((BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json').read_text())['routes']
        audit = json.loads((BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/top0_validation.json').read_text())
        m = json.loads((BASE / 'benchmark/task-01-fluorinated-quinoline-retrosynthesis/achieved_metrics.json').read_text())
        self.assertEqual(m['routes_generated'], len(routes))
        self.assertEqual(m['reaction_node_occurrences_across_routes'], sum(r['explicit_tree_steps'] for r in routes))
        self.assertEqual(m['selected_route_expected_product_rank1_count'], sum(s['forward_product_rank'] == 1 for s in audit['steps']))
        self.assertIsNone(m['measured_target_yield_pct'])
        self.assertIsNone(m['measured_target_selectivity_pct'])
        self.assertIsNone(m['matched_literature_yield_error'])
        self.assertFalse(m['literature_superiority_demonstrated'])

    def test_csv_all_routes(self):
        routes = json.loads((BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json').read_text())['routes']
        with (BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/route_yield_comparison.csv').open(newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), len(routes))
        for row, r in zip(rows, routes):
            self.assertEqual(row['route'], r['route'])
            self.assertAlmostEqual(float(row['illustrative_product_pct_NOT_observed_yield']), r['illustrative_sequential_product_pct'])
            self.assertEqual(row['measured_target_yield_pct'], 'not measured')

    def test_literature_is_not_same_substrate(self):
        refs = json.loads((BASE / 'benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.json').read_text())['references']
        self.assertEqual(len(refs), 5)
        self.assertTrue(all(not r['same_substrate'] for r in refs))
        numeric = [r for r in refs if r['experimental_yield_pct'] is not None]
        self.assertEqual([r['id'] for r in numeric], ['L3'])
        self.assertEqual(numeric[0]['experimental_yield_pct'], 32)

    def test_task_folder_layout(self):
        for section in ('tasks', 'benchmark', 'results'):
            self.assertTrue((BASE / section / 'task-01-fluorinated-quinoline-retrosynthesis' / 'README.md').is_file())
            loose = [f.name for f in (BASE / section).iterdir() if f.is_file() and f.name != 'README.md']
            self.assertEqual(loose, [], f'Task-specific files at section root: {section}')
        objective = (BASE / 'tasks/task-01-fluorinated-quinoline-retrosynthesis/README.md').read_text()
        self.assertIn('Overall objective', objective)
        self.assertIn('Acceptance criteria', objective)
        self.assertIn('Actual outcomes', objective)

    def test_local_links(self):
        locations = [BASE / s for s in ('benchmark', 'tasks', 'results')]
        for directory in locations:
            for f in directory.rglob('*.md'):
                for link in re.findall(r'\]\(([^)]+)\)', f.read_text()):
                    if not link.startswith(('https://', 'http://', '#')):
                        self.assertTrue((f.parent / unquote(link.split('#')[0])).exists(), f'{f}: {link}')


if __name__ == '__main__':
    unittest.main()
