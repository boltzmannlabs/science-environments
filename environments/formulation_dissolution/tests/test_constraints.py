"""Composition, dose, unit and mass-balance constraints.

The mixture validator is deterministic arithmetic. Unknown constraints are
reported as not_evaluated, never silently assumed. All inputs here are
synthetic test objects, not real product compositions.
"""

import unittest
from tools.mixture_validator import validate


def _candidate(x=30, y=70, tablet_mass=100, api=None, dose=None, potency=None):
    c = {
        "ingredients": [
            {"material_id": "X", "amount": x, "unit": "mg"},
            {"material_id": "Y", "amount": y, "unit": "mg"},
        ],
        "tablet_mass": tablet_mass,
    }
    if api is not None:
        c.update(
            api_material_id=api,
            dose=dose,
            dose_unit="mg",
            potency=potency,
            potency_unit="fraction",
        )
    return c


class CompositionBoundsTests(unittest.TestCase):
    def test_balanced_candidate_passes_and_flags_unknown_bounds(self):
        c = validate(_candidate())
        self.assertTrue(c.valid)
        self.assertIn("tablet_mass_balance_mg", c.passed)
        self.assertIn("bound:X", c.not_evaluated)
        self.assertIn("process_limits", c.not_evaluated)

    def test_bound_violation_fails(self):
        c = validate(_candidate(), {"X": (0, 20)})
        self.assertIn("bound:X", c.failed)
        self.assertFalse(c.valid)

    def test_tablet_mass_mismatch_fails(self):
        c = validate(_candidate(tablet_mass=101))
        self.assertIn("tablet_mass_balance_mg", c.failed)
        self.assertFalse(c.valid)


class PercentBasisTests(unittest.TestCase):
    def _pct(self, x, y):
        return {
            "ingredients": [
                {"material_id": "X", "amount": x, "unit": "% w/w"},
                {"material_id": "Y", "amount": y, "unit": "% w/w"},
            ]
        }

    def test_percent_composition_sums_to_100(self):
        self.assertIn(
            "composition_total_100_percent", validate(self._pct(30, 70)).passed
        )

    def test_percent_composition_not_summing_to_100_fails(self):
        c = validate(self._pct(31, 70))
        self.assertIn("composition_total_100_percent", c.failed)
        self.assertFalse(c.valid)


class DoseAndPotencyTests(unittest.TestCase):
    def test_mg_basis_balanced(self):
        c = validate(_candidate(api="X", dose=30, potency=1.0))
        self.assertIn("dose_potency_balance_mg", c.passed)
        self.assertTrue(c.valid)

    def test_mg_basis_dose_potency_mismatch_fails(self):
        # 30 mg API present, but 30 mg dose at 0.5 potency requires 60 mg API.
        c = validate(_candidate(api="X", dose=30, potency=0.5))
        self.assertIn("dose_potency_balance_mg", c.failed)


class UnitAndIdentityTests(unittest.TestCase):
    def test_mixed_units_are_rejected(self):
        c = _candidate()
        c["ingredients"][1]["unit"] = "% w/w"
        self.assertIn("ingredient_units_missing_or_inconsistent", validate(c).failed)

    def test_negative_amount_rejected(self):
        self.assertIn("ingredient_amount_invalid", validate(_candidate(x=-1)).failed)

    def test_duplicate_material_rejected(self):
        c = _candidate()
        c["ingredients"][1]["material_id"] = "X"
        self.assertIn("ingredient_identity_invalid_or_duplicate", validate(c).failed)


if __name__ == "__main__":
    unittest.main()
