"""Environment initialization, configuration loading and state round-trip.

These checks use only the Python standard library and synthetic inputs. They
establish that the episode state, action contract, budget and config loader
behave correctly; they do not establish ranolazine scientific performance.
"""

import json
import tempfile
import unittest
from pathlib import Path

from environment.state import Episode
from environment.actions import Action, execute
from environment.observations import Observation, Value, LABELS, STATUSES
from tools.mixture_validator import validate

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationLoadingTests(unittest.TestCase):
    def test_task_config_is_json_valid_and_required_fields_present(self):
        # configs/task.yaml is documented as JSON text (a valid YAML 1.2 subset).
        cfg = json.loads((ROOT / "configs" / "task.yaml").read_text())
        for key in (
            "task_id",
            "dosage_form",
            "strength_mg",
            "affected_batch_id",
            "evidence_labels",
            "guardrails",
            "history",
            "budgets",
        ):
            self.assertIn(key, cfg)
        self.assertEqual(cfg["task_id"], "ranolazine_er_dissolution_investigation")
        # Budgets are intentionally null: no optimization loop may launch.
        self.assertIsNone(cfg["budgets"]["max_tool_calls"])

    def test_benchmark_config_is_json_valid(self):
        cfg = json.loads((ROOT / "configs" / "benchmark.yaml").read_text())
        self.assertIn("track", cfg)
        self.assertIn("metrics", cfg)

    def test_exploratory_config_is_json_valid_and_labelled_assumed(self):
        cfg = json.loads(
            (ROOT / "configs" / "exploratory_ranolazine_500.json").read_text()
        )
        self.assertIn("release_assumptions_unfitted", cfg)
        self.assertIn("bounded_exploratory_space_assumed_not_approved", cfg)
        self.assertIn("sampling_and_search", cfg)


class StateAndObservationTests(unittest.TestCase):
    def test_episode_round_trip_and_atomic_save(self):
        state = Episode({"task_id": "t1"})
        state.sources["s1"] = {
            "source_id": "s1",
            "citation": "fixture",
            "document_id": "d1",
            "verified_by": "test",
        }
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "episode.json"
            state.save(target)
            loaded = Episode.load(target)
            self.assertEqual(loaded.task["task_id"], "t1")
            self.assertEqual(set(loaded.sources), {"s1"})
            self.assertEqual(loaded.status, "open")
            self.assertTrue(target.exists())

    def test_observation_status_and_label_enums(self):
        obs = Observation("t1", "success", result_type="predicted")
        self.assertIn(obs.status, STATUSES)
        self.assertIn(obs.result_type, LABELS)
        with self.assertRaises(ValueError):
            Observation("t1", "not_a_status")
        with self.assertRaises(ValueError):
            Observation("t1", "success", result_type="not_a_label")

    def test_numeric_value_requires_unit(self):
        with self.assertRaises(ValueError):
            Value("r", 42, None, "derived")
        v = Value("r", 42, "%", "derived")
        self.assertEqual(v.unit, "%")

    def test_invalid_action_kind_rejected(self):
        with self.assertRaises(ValueError):
            Action("launch_physical_experiment", {})


class ValidationActionTests(unittest.TestCase):
    def test_validate_candidate_rejects_unregistered_material(self):
        state = Episode({"task_id": "t"})
        execute(
            state,
            Action(
                "verify_source",
                {
                    "source_id": "s",
                    "citation": "fx",
                    "document_id": "d",
                    "verified_by": "test",
                },
            ),
        )
        execute(
            state, Action("register_material", {"material_id": "A", "source_id": "s"})
        )
        # Ingredient B is not a registered material: the transition fails and
        # no candidate record is written.
        obs = execute(
            state,
            Action(
                "validate_candidate",
                {
                    "candidate": {
                        "candidate_id": "c1",
                        "ingredients": [
                            {"material_id": "B", "amount": 10, "unit": "mg"}
                        ],
                    }
                },
            ),
        )
        self.assertEqual(obs.status, "failure")
        self.assertNotIn("c1", state.candidates)

    def test_predict_with_no_adapter_is_tool_unavailable(self):
        state = Episode({"task_id": "t"})
        execute(
            state,
            Action(
                "verify_source",
                {
                    "source_id": "s",
                    "citation": "fx",
                    "document_id": "d",
                    "verified_by": "test",
                },
            ),
        )
        execute(
            state, Action("register_material", {"material_id": "A", "source_id": "s"})
        )
        execute(
            state,
            Action(
                "validate_candidate",
                {
                    "candidate": {
                        "candidate_id": "c1",
                        "ingredients": [
                            {"material_id": "A", "amount": 100, "unit": "mg"}
                        ],
                        "tablet_mass": 100,
                    }
                },
            ),
        )
        obs = execute(state, Action("predict_dissolution", {"candidate_id": "c1"}))
        self.assertEqual(obs.status, "tool_unavailable")


if __name__ == "__main__":
    unittest.main()
