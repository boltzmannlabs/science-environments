"""Numerical behavior of the empirical kinetic and profile-comparison helpers.

The base suite runs without OpenPKFlow (standard library only) and checks the
metrics, the synthetic fixture generator and the stdlib first-order
reconstruction. The arithmetic f2 factor is checked only when OpenPKFlow is
installed; OpenPKFlow fits are exercised separately by the isolated
simulation tests (test_exploratory_scenarios / test_six_model_pipeline).
"""

import importlib.util
import math
import unittest

from evaluation.six_model_pipeline import (
    MODELS,
    TIMES,
    synthetic_batches,
    quantile,
    scores,
    clean,
)
from evaluation.published_benchmark import first_order_fit, metrics

OPENPKFLOW = importlib.util.find_spec("openpkflow") is not None


class MetricHelpersTests(unittest.TestCase):
    def test_scores_mae_rmse_bias(self):
        m = scores([10, 20], [12, 22])
        self.assertEqual(m["mae_pp"], 2)
        self.assertEqual(m["rmse_pp"], 2.0)
        self.assertEqual(m["bias_pp"], 2)

    def test_scores_rejects_length_mismatch(self):
        with self.assertRaises(ValueError):
            scores([10, 20], [12])

    def test_clean_maps_nonfinite_to_none(self):
        self.assertIsNone(clean(float("nan")))
        self.assertIsNone(clean(float("inf")))
        self.assertIsNone(clean(None))
        self.assertEqual(clean(2.5), 2.5)

    def test_metrics_mae_rmse(self):
        m = metrics([10, 20], [12, 22])
        self.assertEqual(m["mae_pp"], 2)
        self.assertEqual(m["rmse_pp"], 2.0)

    def test_linear_interpolated_quantile(self):
        self.assertEqual(quantile([1, 2, 3, 4], 0.5), 2.5)
        self.assertEqual(quantile([1, 2, 3], 1.0), 3)


class SyntheticFixtureTests(unittest.TestCase):
    def test_frozen_batches_labels_and_grid(self):
        rows = synthetic_batches()
        self.assertEqual(len(rows), 24)
        self.assertEqual(len({r["batch_id"] for r in rows}), 24)
        self.assertEqual({r["data_origin"] for r in rows}, {"synthetic"})
        self.assertEqual(
            {r["evidence_label"] for r in rows}, {"assumed_fixture_not_measured"}
        )
        self.assertEqual({r["split"] for r in rows}, {"train", "validation", "test"})
        counts = {
            s: sum(r["split"] == s for r in rows)
            for s in ("train", "validation", "test")
        }
        self.assertEqual(counts, {"train": 12, "validation": 4, "test": 8})
        for r in rows:
            self.assertEqual(r["time_min"], list(TIMES))
            self.assertTrue(all(0.0 <= v <= 100.0 for v in r["release_percent"]))
            self.assertEqual(r["release_percent"][0], 0.0)  # t=0 anchor

    def test_deterministic_under_fixed_seed(self):
        self.assertEqual(synthetic_batches(), synthetic_batches())


class FirstOrderReconstructionTests(unittest.TestCase):
    # Representative minute-scale ER times, mirroring the published pH 6.8 grid.
    PTS = {30: 18, 60: 26, 90: 29, 120: 34, 240: 57, 480: 73, 720: 75}

    def test_fit_is_monotone_bounded_and_deterministic(self):
        k1, fit1 = first_order_fit(self.PTS)
        k2, fit2 = first_order_fit(self.PTS)
        self.assertEqual(k1, k2)
        self.assertGreater(k1, 0)
        for t, v in fit1.items():
            self.assertTrue(0.0 <= v <= 100.0)
        ts = sorted(self.PTS)
        self.assertTrue(all(fit1[a] <= fit1[b] + 1e-9 for a, b in zip(ts, ts[1:])))

    def test_fit_is_not_perfect_on_realistic_curves(self):
        # An observed curve is not exactly first-order, so residuals must exist.
        _, fit = first_order_fit(self.PTS)
        self.assertGreater(min(abs(self.PTS[t] - fit[t]) for t in self.PTS), 0.0)


@unittest.skipUnless(
    OPENPKFLOW, "OpenPKFlow only in the isolated simulation environment"
)
class F2SimilarityTests(unittest.TestCase):
    def test_f2_of_identical_profiles_is_100(self):
        from openpkflow.dissolution.similarity import f2

        a = [10, 20, 30, 40, 50]
        self.assertAlmostEqual(f2(a, a, method="all_points"), 100.0, places=6)

    def test_f2_decreases_with_disagreement(self):
        from openpkflow.dissolution.similarity import f2

        a = [10, 20, 30, 40, 50]
        close = [11, 21, 31, 41, 51]
        far = [20, 40, 60, 80, 100]
        self.assertGreater(
            f2(a, close, method="all_points"), f2(a, far, method="all_points")
        )


if __name__ == "__main__":
    unittest.main()
