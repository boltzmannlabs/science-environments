import json
import unittest
from pathlib import Path

from evaluation.literature_benchmark import benchmark


class LiteratureBenchmarkTests(unittest.TestCase):
    def test_single_endpoint_discrepancy_and_no_validation_claim(self):
        root = Path(__file__).resolve().parents[1]
        result = json.loads((root / "data/processed/ranolazine_research_scenario_results.json").read_text())
        report = benchmark(result)
        self.assertEqual(report["status"], "sanity_check_only_NOT_validation")
        self.assertEqual(report["holdout_benchmark_status"], "not_evaluated")
        self.assertEqual(report["n_literature_endpoints"], 1)
        self.assertAlmostEqual(report["models"]["first_order"]["absolute_median_error_percentage_points"], 10.119094270281295)
        self.assertAlmostEqual(report["models"]["weibull"]["absolute_median_error_percentage_points"], 10.03071222113573)
        self.assertFalse(report["models"]["first_order"]["literature_endpoint_within_scenario_p05_p95"])

    def test_rejects_wrong_scenario_status(self):
        with self.assertRaises(ValueError):
            benchmark({"status": "measured", "literature_endpoint_sanity_check": {}})


if __name__ == "__main__":
    unittest.main()
