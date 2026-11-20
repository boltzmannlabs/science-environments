"""Integration regressions use synthetic test objects, never laboratory claims."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from simulation import execute, load_problem
from evaluation.profile_comparison import compare

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def manifest(self, directory, candidates=117, scenarios=256):
        obj = json.loads((ROOT / "configs/environment.yaml").read_text())
        obj["scenario_config"] = str(ROOT / "configs/exploratory_ranolazine_500.json")
        obj["budget"].update(
            max_candidates=candidates, max_scenarios_per_candidate=scenarios
        )
        path = Path(directory) / "problem.json"
        path.write_text(json.dumps(obj))
        return path

    def test_configuration_and_all_grid_constraints(self):
        _, cfg, _, grid = load_problem(ROOT / "configs/environment.yaml")
        self.assertEqual(len(grid), 117)
        self.assertEqual(cfg["paper_mass_mg"]["ranolazine"], 500)

    def test_budget_failure_before_model_calls(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out"
            result = execute(self.manifest(d, candidates=1), out)
            self.assertEqual(result["status"], "budget_exhausted")
            self.assertEqual(result["evaluated_candidates"], 0)
            self.assertIsNone(result["experimental_observations"])
            self.assertFalse((out / "candidates.json").exists())
            with self.assertRaises(FileExistsError):
                execute(self.manifest(d), out)

    def test_invalid_budget_and_units_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.manifest(d, candidates=-1)
            with self.assertRaises(ValueError):
                load_problem(path)
            path = self.manifest(d)
            manifest = json.loads(path.read_text())
            cfg = json.loads(
                (ROOT / "configs/exploratory_ranolazine_500.json").read_text()
            )
            cfg["bounded_exploratory_space_assumed_not_approved"]["strength_mg"] = 1000
            source = Path(d) / "scenario.json"
            source.write_text(json.dumps(cfg))
            manifest["scenario_config"] = str(source)
            path.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                load_problem(path)

    @unittest.skipUnless(
        importlib.util.find_spec("openpkflow"), "optional simulation extra"
    )
    def test_end_to_end_seed_and_candidate_records(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.manifest(d)
            a, b = execute(path, Path(d) / "a"), execute(path, Path(d) / "b")
            self.assertEqual(a["status"], "completed_scenario_only")
            self.assertEqual(a, b)
            candidates = json.loads((Path(d) / "a/candidates.json").read_text())
            self.assertEqual(len(candidates), 117)
            self.assertTrue(
                all(
                    c["data_origin"] == "synthetic"
                    and c["experimental_observations"] is None
                    and not c["constraint_violations"]
                    for c in candidates
                )
            )
            self.assertTrue(
                all(
                    c["compatibility"]["status"] == "insufficient_data"
                    for c in candidates
                )
            )


class SuppliedProfileTests(unittest.TestCase):
    def pair(self):
        context = dict(
            api="test_API",
            strength_mg=500,
            dosage_form="ER",
            method_id="test_method",
            method_version="1",
            storage_condition="test_condition",
            time_unit="h",
            release_unit="%",
            dose_basis="nominal_dose",
            candidate_id="test_candidate",
            time=[0, 2, 4, 8],
            values=[0, 20, 40, 60],
        )
        return (
            {**context, "evidence_label": "predicted"},
            {
                **context,
                "evidence_label": "measured",
                "data_origin": "experimental",
                "source_id": "SYNTHETIC_CONTRACT_TEST_NOT_REAL_MEASUREMENT",
            },
        )

    def test_missing_data_stays_missing(self):
        p, _ = self.pair()
        self.assertEqual(compare(p, None)["status"], "not_evaluated")

    def test_identical_profiles_and_context_mismatch(self):
        p, o = self.pair()
        r = compare(p, o)
        self.assertEqual(r["mae_pp"], 0)
        self.assertEqual(r["f1_math_only"], 0)
        self.assertEqual(r["f2_math_only"], 100)
        self.assertEqual(r["regulatory_similarity"], "not_evaluated")
        o["method_version"] = "different"
        self.assertEqual(compare(p, o)["status"], "not_evaluated")

    def test_synthetic_relabelling_and_nonfinite_rejected(self):
        p, o = self.pair()
        o["data_origin"] = "synthetic"
        with self.assertRaises(ValueError):
            compare(p, o)
        p, o = self.pair()
        o["values"] = [0, float("nan"), 40, 60]
        with self.assertRaises(ValueError):
            compare(p, o)

    def test_grid_mismatch_rejected_and_late_f2_abstention(self):
        p, o = self.pair()
        o["time"] = [0, 1, 4, 8]
        with self.assertRaises(ValueError):
            compare(p, o)
        p, o = self.pair()
        p["values"] = o["values"] = [0, 20, 90, 100]
        r = compare(p, o)
        self.assertEqual(r["mae_pp"], 0)
        self.assertIsNone(r["f2_math_only"])


if __name__ == "__main__":
    unittest.main()
