"""Verify matching workspaces and traceable archived results for every task."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE = Path(__file__).resolve().parents[1]


class TestWorkspace(unittest.TestCase):
    def test_all_task_folders_match_across_sections(self):
        def folders(section):
            return {p.name for p in (BASE / section).iterdir() if p.is_dir()}

        tasks = folders('tasks')
        self.assertTrue(tasks)
        for section in ('benchmark', 'benchmarks', 'results'):
            self.assertEqual(tasks, folders(section), section)
        for task in tasks:
            for section in ('tasks', 'benchmark', 'benchmarks', 'results'):
                self.assertTrue((BASE / section / task / 'README.md').is_file(), (section, task))
            report = BASE / 'results' / task / 'comparison_report.md'
            self.assertTrue(report.is_file(), task)
            self.assertIn('literature', report.read_text().lower())
            benchmark = (BASE / 'benchmarks' / task / 'README.md').read_text()
            self.assertIn(f'../../tasks/{task}/README.md', benchmark)
            self.assertIn(f'../../results/{task}/README.md', benchmark)
            self.assertIn(f'../../benchmark/{task}/', benchmark)

    def test_documented_target_structures_match_source_records(self):
        task01 = (BASE / 'tasks/task-01-fluorinated-quinoline-retrosynthesis/README.md').read_text()
        route = json.loads((BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json').read_text())
        self.assertIn(route['target_smiles'], task01)
        task02 = (BASE / 'tasks/task-02-impurity-retrosynthesis/README.md').read_text()
        config = json.loads((BASE.parent / 'impurity-retrosynthesis/config/targets.json').read_text())
        self.assertIn('candidate_smiles', json.dumps(config))
        candidates = re.findall(r'"candidate_smiles"\s*:\s*"([^"]+)"', json.dumps(config))
        self.assertEqual(len(candidates), 2)
        for smiles in candidates:
            self.assertIn(smiles, task02)
        parent = json.loads((BASE / 'results/task-02-impurity-retrosynthesis/racemic_ibuprofen_recovered.json').read_text())
        self.assertIn(parent['original_input_smiles'], task02)

    def test_all_environment_markdown_local_links(self):
        for source in BASE.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', source.read_text()):
                url = urlsplit(target)
                if url.scheme or not url.path:
                    continue
                with self.subTest(file=source.relative_to(BASE), target=target):
                    self.assertTrue((source.parent / unquote(url.path)).exists())


if __name__ == '__main__':
    unittest.main()
