"""Task-02 cross-folder provenance/metrics and publication consistency checks."""
import csv
import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]
TASK = 'task-02-impurity-retrosynthesis'
RESULTS = BASE / 'results' / TASK
BENCH = BASE / 'benchmark' / TASK


class TestTask02(unittest.TestCase):
    def test_task_structure_and_expected_outcomes(self):
        for section in ('tasks', 'benchmark', 'results'):
            self.assertTrue((BASE / section / TASK / 'README.md').is_file())
        text = (BASE / 'tasks' / TASK / 'README.md').read_text()
        for heading in ('Overall objective', 'Problem statement', 'Execution approach', 'Expected outcomes', 'Actual outcomes'):
            self.assertIn(heading, text)

    def test_artifact_links_and_no_private_records(self):
        record = json.loads((RESULTS / 'task_record.json').read_text())
        self.assertEqual(record['task_id'], TASK)
        for key in ('task_definition', 'benchmark_definition', 'reference_catalog', 'metrics'):
            self.assertTrue((RESULTS / record[key]).is_file())
        for name in record['results']:
            self.assertTrue((RESULTS / name).is_file())
        for directory in (BASE / 'tasks' / TASK, BENCH, RESULTS):
            for file in directory.rglob('*'):
                if file.is_file():
                    text = file.read_text()
                    self.assertNotIn('X-Goog-Signature', text)
                    self.assertNotIn('/home/boltzmann6/', text)

    def test_numerical_summary_and_original_ids(self):
        metrics = json.loads((BENCH / 'achieved_metrics.json').read_text())
        summary = json.loads((RESULTS / 'screening_summary.json').read_text())
        self.assertEqual(metrics['targets'], summary['targets'])
        with (RESULTS / 'screening_routes.csv').open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 19)
        self.assertEqual(sum(int(row['reaction_nodes']) for row in rows), 59)
        self.assertEqual(len({(row['target'], row['route_id']) for row in rows}), 19)
        self.assertFalse(metrics['experimental_comparison']['chemical_superiority_demonstrated'])
        self.assertIsNone(metrics['racemic_ibuprofen']['route_count'])
        self.assertIsNone(metrics['experimental_comparison']['project_measured_yield'])

    def test_reference_catalog_and_gaps(self):
        text = (BENCH / 'papers.md').read_text()
        for token in ('CN108794319B', 'WO2003043625A1', '10.1021/cs401075z', 'Bellezza', 'Aramini', 'Kuchar', 'Ramesh', 'Cross', '1983'):
            self.assertIn(token, text)
        gap = (RESULTS / 'gaps_and_improvement_plan.md').read_text()
        for token in ('P0', 'P1', 'P2', 'isolated', 'safety', 'INR', 'uncertainty'):
            self.assertIn(token, gap)


if __name__ == '__main__':
    unittest.main()
