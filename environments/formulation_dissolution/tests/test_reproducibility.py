"""Reproducibility: fixed seeds, deterministic generators and artifact hashes.

Reproduction here means bit-identical regeneration from a declared seed and
config, and that committed derived artifacts are still hash-consistent with
their inputs. It does not mean scientific validation of a product.
"""

import hashlib
import json
import unittest
from pathlib import Path

from evaluation.six_model_pipeline import SEED, synthetic_batches
from evaluation.exploratory_scenarios import draw_scenarios

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "configs" / "exploratory_ranolazine_500.json"
CFG = json.loads(CFG_PATH.read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FixedSeedTests(unittest.TestCase):
    def test_synthetic_fixture_is_seeded(self):
        # synthetic_batches() uses the module-level SEED constant directly.
        self.assertIsInstance(SEED, int)
        a, b = synthetic_batches(), synthetic_batches()
        self.assertEqual(a, b)
        self.assertEqual(a[0]["batch_id"], "SYN_F1_B0")

    def test_exploratory_scenario_draws_are_deterministic(self):
        draws = list(draw_scenarios(CFG))
        self.assertEqual(draws, list(draw_scenarios(CFG)))
        expected = (
            CFG["sampling_and_search"]["samples_per_model"] * 2
        )  # first-order + weibull
        self.assertEqual(len(draws), expected)
        self.assertEqual({d["model"] for d in draws}, {"first_order", "weibull"})

    def test_seeded_generator_draws_are_reproducible_under_same_seed(self):
        import random

        rng_a, rng_b = random.Random(2931), random.Random(2931)
        for _ in range(100):
            self.assertEqual(rng_a.gauss(0, 1), rng_b.gauss(0, 1))


class CommittedArtifactConsistencyTests(unittest.TestCase):
    def test_synthetic_split_manifest_matches_regenerated_batches(self):
        manifest = json.loads(
            (
                ROOT
                / "data"
                / "processed"
                / "six_model_pipeline"
                / "synthetic_split_manifest.json"
            ).read_text()
        )
        regenerated = {}
        for row in synthetic_batches():
            regenerated.setdefault(row["split"], []).append(row["batch_id"])
        for split in ("train", "validation", "test"):
            self.assertEqual(sorted(regenerated[split]), manifest[split])
        self.assertEqual(
            len(manifest["train"])
            + len(manifest["validation"])
            + len(manifest["test"]),
            24,
        )

    def test_selected_benchmark_input_hash_matches_scenario_artifact(self):
        scenario = (
            ROOT / "data" / "processed" / "ranolazine_500_exploratory_new_run.json"
        )
        benchmark = (
            ROOT / "data" / "processed" / "ranolazine_500_selected_benchmark.json"
        )
        self.assertTrue(scenario.exists() and benchmark.exists())
        record = json.loads(benchmark.read_text())
        self.assertEqual(record["input_sha256"], _sha(scenario))
        self.assertEqual(
            record["status"],
            "exploratory_assumption_conditional_NOT_product_prediction",
        )
        self.assertEqual(record["data_origin"], "synthetic")
        self.assertEqual(record["validated_improvement"], "not_established")

    def test_six_model_verifier_has_no_findings(self):
        verification = json.loads(
            (
                ROOT / "data" / "processed" / "six_model_pipeline" / "verification.json"
            ).read_text()
        )
        self.assertEqual(verification["findings"], [])
        self.assertIn("NOT_scientifically_validated", verification["status"])


if __name__ == "__main__":
    unittest.main()
