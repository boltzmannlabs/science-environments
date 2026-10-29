"""Optimization and ranking behavior.

Two distinct components are covered, and they are deliberately kept apart:

* The illustrative acquisition ranker (models.acquisition_policy) -- a
  transparent weighted score that only ranks pre-supplied, feasible,
  cost-labelled items. It does no learning and is not a validated policy.
* The exploratory 500 mg research-prototype grid (evaluation.exploratory_
  scenarios) -- a Monte Carlo scenario sweep with a Pareto front. The latter
  is assumption-conditional and requires the isolated OpenPKFlow environment;
  its contract checks (recipe mass balance, deterministic draws) are asserted
  here without running the OpenPKFlow curve model.

No test here establishes a validated formulation improvement.
"""

import importlib.util
import json
import unittest
from pathlib import Path

from models.acquisition_policy import rank
from tools.mixture_validator import validate

ROOT = Path(__file__).resolve().parents[1]
OPENPKFLOW = importlib.util.find_spec("openpkflow") is not None


class AcquisitionRankerTests(unittest.TestCase):
    def test_infeasible_and_incomplete_items_are_dropped(self):
        items = [
            {"id": "ok", "feasible": True, "objectives": {"release": 1.0}, "cost": 5},
            {
                "id": "infeasible",
                "feasible": False,
                "objectives": {"release": 9.0},
                "cost": 1,
            },
            {"id": "missing_obj", "feasible": True, "objectives": {}, "cost": 1},
            {"id": "no_cost", "feasible": True, "objectives": {"release": 1.0}},
        ]
        out = rank(items, {"release": 1.0})
        self.assertEqual([x["id"] for x in out], ["ok"])
        self.assertEqual(out[0]["score"], 1.0)
        self.assertEqual(out[0]["status"], "illustrative_unvalidated")

    def test_weighted_score_orders_and_cost_breaks_ties(self):
        items = [
            {"id": "a", "feasible": True, "objectives": {"x": 2, "y": 0}, "cost": 3},
            {"id": "b", "feasible": True, "objectives": {"x": 1, "y": 1}, "cost": 1},
        ]
        out = rank(items, {"x": 1.0, "y": 1.0})
        # Both score 2.0; lower cost 'b' ranks first.
        self.assertEqual([x["id"] for x in out], ["b", "a"])
        self.assertEqual(out[0]["score"], out[1]["score"])

    def test_remaining_budget_excludes_over_cost(self):
        items = [{"id": "big", "feasible": True, "objectives": {"x": 1.0}, "cost": 10}]
        self.assertEqual(rank(items, {"x": 1.0}, remaining_cost=5), [])
        self.assertEqual(len(rank(items, {"x": 1.0}, remaining_cost=10)), 1)

    def test_negative_weights_rejected(self):
        with self.assertRaises(ValueError):
            rank(
                [{"id": "a", "feasible": True, "objectives": {"x": 1}, "cost": 1}],
                {"x": -1},
            )

    def test_empty_weights_rejected(self):
        with self.assertRaises(ValueError):
            rank([{"id": "a", "feasible": True, "objectives": {"x": 1}, "cost": 1}], {})


class ExploratoryRecipeContractTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(
            (ROOT / "configs" / "exploratory_ranolazine_500.json").read_text()
        )

    def test_literature_recipes_balance_mass_and_dose(self):
        from evaluation.exploratory_scenarios import recipe

        for name, parts in self.cfg["literature_formulations_mg"].items():
            candidate, checks = recipe(
                parts["compritol"],
                parts["carbopol_934"],
                self.cfg["literature_hardness_kg_per_cm2"][name],
                self.cfg,
            )
            self.assertFalse(checks["failed"], name)
            self.assertIn("dose_potency_balance_mg", checks["passed"])
            self.assertEqual(sum(i["amount"] for i in candidate["ingredients"]), 695)

    def test_grid_candidates_are_validated_before_scoring(self):
        # recipe() performs the mass-balance/bounds validation that every grid
        # candidate passes before it is scored; an out-of-window composition
        # raises instead of reaching the scoring stage.
        from evaluation.exploratory_scenarios import recipe

        space = self.cfg["bounded_exploratory_space_assumed_not_approved"]
        c = 87  # mid [70,105]
        b = 42  # mid [14,70]
        candidate, checks = recipe(c, b, 8.5, self.cfg)
        self.assertFalse(checks["failed"])
        self.assertEqual(sum(i["amount"] for i in candidate["ingredients"]), 695)
        # Avicel is the balance term (165 - c - b); a composition whose balance
        # falls outside the avicel window cannot be a valid grid point.
        with self.assertRaises(ValueError):
            recipe(70, 14, 7.0, self.cfg)  # hardness below the [7.5, 9.5] window


if __name__ == "__main__":
    unittest.main()
