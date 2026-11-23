"""DailyMed cross-check safeguards using public read-only FDA source snapshots."""
import tempfile
import unittest
from pathlib import Path
from import_dailymed import crosscheck

DATA = Path(__file__).resolve().parent.parent/'data'


class DailyMedTests(unittest.TestCase):
    def test_both_cases_crosscheck_without_lab_data(self):
        with tempfile.TemporaryDirectory() as d:
            for case, label in [('D-0092-2024','glenmark'),('D-0010-2027','ajanta')]:
                state = crosscheck(DATA/'processed'/f'{case}.episode.json', DATA/'raw'/f'dailymed-{label}.xml',Path(d)/f'{case}.json')
                self.assertEqual(len(state.sources),3)
                self.assertEqual(len(state.evidence),8)
                self.assertFalse(any(x.get('label') == 'measured' for x in state.evidence))
                self.assertTrue(all(not s.get('authorized_measurement',False) for s in state.sources.values()))

    def test_cross_product_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'SPL label ID or version'):
                crosscheck(DATA/'processed'/'D-0092-2024.episode.json', DATA/'raw'/'dailymed-ajanta.xml',Path(d)/'bad.json')
            self.assertFalse((Path(d)/'bad.json').exists())


if __name__ == '__main__': unittest.main()
