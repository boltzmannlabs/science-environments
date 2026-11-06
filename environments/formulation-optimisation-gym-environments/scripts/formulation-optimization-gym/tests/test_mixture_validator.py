"""Composition checks with intentionally synthetic unit-test inputs only."""
import unittest
from tools.mixture_validator import validate


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.c = {'ingredients':[{'material_id':'X','amount':30,'unit':'mg'},{'material_id':'Y','amount':70,'unit':'mg'}], 'tablet_mass':100}

    def test_balance_bounds_unknown(self):
        c = validate(self.c)
        self.assertTrue(c.valid)
        self.assertIn('bound:X', c.not_evaluated)
        self.assertIn('dose_potency_basis', c.not_evaluated)
        self.assertIn('bound:X', validate(self.c, {'X':(0,20)}).failed)
        self.c['tablet_mass'] = 101
        self.assertIn('tablet_mass_balance_mg', validate(self.c).failed)

    def test_invalid_units_and_dose_basis(self):
        self.c['ingredients'][1]['unit'] = '% w/w'
        self.assertIn('ingredient_units_missing_or_inconsistent', validate(self.c).failed)
        self.c['ingredients'][1]['unit'] = 'mg'
        self.c.update(api_material_id='X',dose=30,dose_unit='mg',potency=0.5,potency_unit='fraction')
        self.assertIn('dose_potency_balance_mg', validate(self.c).failed)
        self.c['ingredients'][0]['amount'] = -1
        self.assertIn('ingredient_amount_invalid', validate(self.c).failed)

    def test_percent(self):
        for p in self.c['ingredients']:
            p['unit'] = '% w/w'
        self.assertTrue(validate(self.c).valid)
        self.c['ingredients'][0]['amount'] = 31
        self.assertFalse(validate(self.c).valid)


if __name__ == '__main__': unittest.main()
