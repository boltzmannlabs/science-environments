from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents import SPERegistry, build_system_prompt  # noqa: E402
from spe_agents.registry import ACTIVE_ENVIRONMENT_IDS  # noqa: E402


class SPERegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SPERegistry(ROOT / "environments")

    def test_exactly_eighteen_spe_environments_load(self) -> None:
        agents = self.registry.all()
        self.assertEqual(len(agents), 18)
        self.assertEqual([agent.id for agent in agents], list(ACTIVE_ENVIRONMENT_IDS))
        self.assertNotIn("13", ACTIVE_ENVIRONMENT_IDS)
        self.assertNotIn("16", ACTIVE_ENVIRONMENT_IDS)
        with self.assertRaises(KeyError):
            self.registry.get("13")
        with self.assertRaises(KeyError):
            self.registry.get("16")

    def test_lookup_by_id_slug_and_name(self) -> None:
        self.assertEqual(self.registry.get("01").slug, "small-molecule-spe")
        self.assertEqual(self.registry.get("basis-set-convergence").id, "07")
        self.assertEqual(self.registry.get("SPE Quality-Control and Recovery Agent").id, "20")

    def test_all_integrations_start_unverified(self) -> None:
        self.assertTrue(all(agent.integration_status == "unverified" for agent in self.registry.all()))

    def test_contracts_have_scientific_evaluation_and_recovery_rules(self) -> None:
        for agent in self.registry.all():
            self.assertTrue(agent.validation_checks)
            self.assertTrue(agent.scientific_constraints)
            self.assertTrue(agent.acceptance_criteria)
            self.assertTrue(agent.capability_boundaries)
            self.assertTrue(agent.human_review_when)

    def test_routing_distinguishes_major_workflows(self) -> None:
        cases = {
            "compare conformer energies": "03",
            "run a basis set convergence study": "07",
            "calculate a water cluster energy": "11",
            "audit spe reproducibility": "20",
        }
        for task, expected in cases.items():
            with self.subTest(task=task):
                matches = self.registry.route(task)
                self.assertTrue(matches)
                self.assertEqual(matches[0][0].id, expected)

    def test_prompt_contains_shared_and_specialist_rules(self) -> None:
        prompt = build_system_prompt(self.registry.get("12"), ROOT / "BASE_AGENT_INSTRUCTIONS.md")
        self.assertIn("Never fabricate an energy", prompt)
        self.assertIn("Metal-Ligand Coordination SPE Agent", prompt)
        self.assertIn("Independent acceptance criteria", prompt)
        self.assertIn("does not assign oxidation state from geometry alone", prompt)


if __name__ == "__main__":
    unittest.main()
