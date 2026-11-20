"""FDA public snapshot integration checks; uses actual stored public API responses."""
import tempfile
import unittest
from pathlib import Path
from import_fda import import_case
from run import investigate

RAW = Path(__file__).resolve().parent.parent / 'data' / 'raw'


class FDAImportTests(unittest.TestCase):
    def test_two_separate_cases(self):
        with tempfile.TemporaryDirectory() as d:
            gl = import_case(RAW/'fda-res-D-0092-2024.json', RAW/'fda-spl-glenmark.json', Path(d)/'g.json')
            aj = import_case(RAW/'fda-res-D-0010-2027.json', RAW/'fda-spl-ajanta.json', Path(d)/'a.json')
            for state in (gl, aj):
                report = investigate(state)
                self.assertEqual(report['auditor']['decision'], 'accept')
                self.assertEqual(report['verifier_findings'], [])
                self.assertEqual(report['status'], 'insufficient_data')
                self.assertNotIn('primary_recall_record', report['unknowns'])
                self.assertIn('measured_profiles', report['unknowns'])
                self.assertEqual(state.experiments, {})
                self.assertTrue(all(v['label'] != 'measured' for v in state.evidence))
            self.assertNotEqual(gl.task['case_id'], aj.task['case_id'])
            self.assertFalse(set(gl.sources) & set(aj.sources))

    def test_reject_crosslinked_label(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'label SPL or package NDC'):
                import_case(RAW/'fda-res-D-0092-2024.json', RAW/'fda-spl-ajanta.json', Path(d)/'bad.json')
            self.assertFalse((Path(d)/'bad.json').exists())


if __name__ == '__main__': unittest.main()
