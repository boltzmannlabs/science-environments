"""Consistency of published task, literature and achieved-metric artifacts."""
import csv
import json
from pathlib import Path
import unittest

ENV = Path(__file__).resolve().parents[1]


class PublishedEvidenceTests(unittest.TestCase):
    def test_benchmark_metrics_match_result_summary(self):
        metrics = json.loads((ENV / 'benchmark/achieved_metrics.json').read_text())
        summary = json.loads((ENV / 'results/screening_summary.json').read_text())
        self.assertEqual(metrics['targets'], summary['targets'])
        self.assertFalse(metrics['experimental_comparison']['chemical_superiority_demonstrated'])
        self.assertIsNone(metrics['racemic_ibuprofen']['route_count'])
        self.assertIsNone(metrics['experimental_comparison']['project_measured_yield'])

    def test_all_model_rows_preserved(self):
        with (ENV / 'results/screening_routes.csv').open(newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 19)
        self.assertEqual(sum(int(r['reaction_nodes']) for r in rows), 59)
        self.assertEqual(len({(r['target'], r['route_id']) for r in rows}), 19)

    def test_named_task_and_reference_documents_exist(self):
        for name in ('task_001_ibuprofen_impurity_a.md', 'task_002_ibuprofen_impurity_m.md', 'task_003_racemic_ibuprofen.md'):
            body = (ENV / 'tasks' / name).read_text()
            self.assertIn('Expected deliverables', body)
            self.assertIn('Current outcome', body)
        body = (ENV / 'benchmark/literature_comparison.md').read_text()
        for citation in ('CN108794319B', 'WO2003043625A1', '10.1021/cs401075z', 'Kuchar', 'Bellezza', 'Ramesh', 'Aramini', 'WO2013014448A1', 'Cross', '1983'):
            self.assertIn(citation, body)
        self.assertTrue((ENV / 'results/literature_findings.md').is_file())


if __name__ == '__main__':
    unittest.main()
