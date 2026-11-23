"""Validate the archived Task-03 transcript without running a prediction model."""
import csv
from pathlib import Path
import re
import unittest
from collections import Counter

BASE = Path(__file__).resolve().parents[1]
SLUG = 'task-03-indole-forward-prediction'
IDS = ('1a', '1b', '1c', '1d', '1e', '1f', '1g', '1j', '1k', '1l')
COUNTS = (29, 28, 31, 30, 29, 30, 30, 30, 30, 30)


class TestTask03(unittest.TestCase):
    def test_input_reference_and_transcript_completeness(self):
        request = (BASE / 'tasks' / SLUG / 'original_request.md').read_text()
        reference = (BASE / 'benchmarks' / SLUG / 'literature_products_reference.md').read_text()
        inputs = dict(re.findall(r'\| (1[a-z]) \| `([^`]+)`', request))
        refs = dict(re.findall(r'\| (1[a-z]) \| `([^`]+)`', reference))
        self.assertEqual(set(inputs), set(IDS))
        self.assertEqual(set(refs), set(IDS))
        out = BASE / 'results' / SLUG
        with (out / 'transcribed_1a_candidates.csv').open(newline='') as f:
            rows = list(csv.DictReader(f))
        with (out / 'indole_literature_similarity_1b_to_1l.csv').open(newline='') as f:
            rows.extend(csv.DictReader(f))
        self.assertEqual(Counter(r['reaction_id'] for r in rows), dict(zip(IDS, COUNTS)))
        for reaction in IDS:
            subset = [r for r in rows if r['reaction_id'] == reaction]
            self.assertEqual([int(r['original_rank']) for r in subset], list(range(1, len(subset) + 1)))
            for row in subset:
                self.assertTrue(row['candidate_smiles'])
                if 'reference_smiles' in row:
                    self.assertEqual(row['reference_smiles'], refs[reaction])
                    self.assertEqual(row['exact_match'], 'False')


if __name__ == '__main__':
    unittest.main()
