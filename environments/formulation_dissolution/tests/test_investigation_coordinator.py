"""Bounded six-role coordination and source integrity regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from agents.investigation_coordinator import InvestigationRequest, coordinate

DATA=Path(__file__).resolve().parent.parent/'data'


class CoordinatorTests(unittest.TestCase):
    def test_case_abstains_without_experiment_data(self):
        result=coordinate(InvestigationRequest(DATA/'processed/D-0092-2024.dailymed.episode.json',DATA/'raw',DATA/'processed/openpkflow_package_demo.json'))
        self.assertEqual(result['status'],'insufficient_data_for_optimization')
        self.assertEqual(len(result['roles']),6)
        self.assertEqual(result['candidate_compositions'],[])
        self.assertEqual(result['predicted_dissolution_profiles'],[])
        self.assertEqual(result['roles']['Independent Validation Agent']['verifier_findings'],[])
        self.assertTrue(all(result['roles']['Evidence Retrieval Agent']['source_hashes_match'].values()))
        self.assertEqual(result['roles']['Dissolution Modeling Agent']['openpkflow']['purpose'],'OpenPKFlow software smoke test only; no recalled-lot fitting')

    def test_reject_other_product_and_corrupted_source(self):
        with self.assertRaisesRegex(ValueError,'Glenmark'):
            coordinate(InvestigationRequest(DATA/'processed/D-0010-2027.dailymed.episode.json',DATA/'raw'))
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)
            for name in ('fda-res-D-0092-2024.json','fda-spl-glenmark.json','dailymed-glenmark.xml'):
                (raw/name).write_bytes((DATA/'raw'/name).read_bytes())
            (raw/'fda-res-D-0092-2024.json').write_text('tampered')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                coordinate(InvestigationRequest(DATA/'processed/D-0092-2024.dailymed.episode.json',raw))


if __name__=='__main__':unittest.main()
