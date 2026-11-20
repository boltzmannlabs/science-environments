"""Deterministic composition gates, distinct from pharmaceutical performance."""
from decimal import Decimal
from math import isfinite

NAMES = (
    'Clarithromycin', 'Microcrystalline Cellulose', 'Crospovidone',
    'Povidone K30', 'Colloidal Silicon Dioxide', 'Magnesium Stearate',
    'Hypromellose', 'Titanium Dioxide', 'PEG 4000',
)
BOUNDS = dict(zip(NAMES[1:], (
    (15, 32.5), (2, 6), (1.5, 4.5), (.25, 1.25), (.25, 1.25),
    (1, 3), (.5, 1.5), (.5, 2),
)))


def validate_composition(masses, existing=()):
    """Return all detected hard failures. Empty list is composition-only pass."""
    if set(masses) != set(NAMES):
        return ['INGREDIENT_IDENTITIES']
    try:
        if not all(isfinite(float(masses[n])) for n in NAMES):
            return ['NONFINITE_MASS']
        values = {n: Decimal(str(masses[n])) for n in NAMES}
    except (ValueError, TypeError, ArithmeticError):
        return ['NONNUMERIC_MASS']
    failures = []
    if any(v < 0 for v in values.values()):
        failures.append('NEGATIVE_MASS')
    if values[NAMES[0]] != 500:
        failures.append('API_DOSE')
    total = sum(values.values())
    if total != 800:
        failures.append('FIXED_TABLET_MASS')
    if abs(total / 8 - 100) > Decimal('0.1'):
        failures.append('PERCENT_SUM')
    for n, (lo, hi) in BOUNDS.items():
        if not Decimal(str(lo)) <= values[n] / 8 <= Decimal(str(hi)):
            failures.append('BOUND:' + n)
    if any(max(abs(values[n] - Decimal(str(other[n]))) for n in NAMES[1:]) < 1
           for other in existing):
        failures.append('DUPLICATE_OR_NEAR_DUPLICATE_LT_1MG')
    return failures
