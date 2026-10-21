from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents.campaign import (  # noqa: E402
    CampaignConfigurationError,
    CampaignRunner,
    parse_xyz,
    validate_electron_parity,
)


class CampaignTests(unittest.TestCase):
    def test_active_manifest_has_three_cases_for_all_eighteen_environments(self) -> None:
        runner = CampaignRunner(ROOT)
        manifest = runner.load_manifest(ROOT / "campaign/manifests/initial_54_cases.json")
        self.assertEqual(len(manifest["cases"]), 54)
        self.assertNotIn("13", manifest["execution_priority"])
        self.assertNotIn("16", manifest["execution_priority"])

    def test_common_baseline_has_six_applicable_environments(self) -> None:
        runner = CampaignRunner(ROOT)
        manifest = runner.load_manifest(ROOT / "campaign/manifests/common_water_baseline.json")
        self.assertEqual(len(manifest["cases"]), 6)
        self.assertEqual(
            [case["environment_id"] for case in manifest["cases"]],
            ["01", "02", "06", "07", "08", "09"],
        )

    def test_common_water_fixture_and_parity(self) -> None:
        structure = parse_xyz(ROOT / "campaign/fixtures/structures/water.xyz")
        self.assertEqual(structure.elements, ("O", "H", "H"))
        validate_electron_parity(structure, charge=0, multiplicity=1)

    def test_xyz_atom_count_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.xyz"
            path.write_text("2\nbad\nH 0 0 0\n", encoding="utf-8")
            with self.assertRaisesRegex(CampaignConfigurationError, "declared 2 atoms"):
                parse_xyz(path)

    def test_campaign_runs_without_fabricating_engine_results(self) -> None:
        runner = CampaignRunner(ROOT)
        manifest = runner.load_manifest(ROOT / "campaign/manifests/initial_54_cases.json")
        outcomes = runner.run(manifest)
        self.assertEqual(len(outcomes), 54)
        self.assertFalse(any(item.energy_difference_hartree is not None for item in outcomes))
        self.assertFalse(any(item.provenance.get("adapter_called") is True for item in outcomes))
        qc = [item for item in outcomes if item.environment_id == "20"]
        self.assertEqual([item.test_status for item in qc], ["pass", "pass", "pass"])


if __name__ == "__main__":
    unittest.main()
