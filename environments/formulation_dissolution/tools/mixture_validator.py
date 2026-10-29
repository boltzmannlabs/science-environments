"""Deterministic composition checks; unknown constraints are never invented."""
from dataclasses import dataclass, field
from math import isclose, isfinite


@dataclass
class Check:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    not_evaluated: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.failed

    def as_dict(self):
        return {'passed': self.passed, 'failed': self.failed, 'not_evaluated': self.not_evaluated}


def validate(candidate: dict, bounds: dict | None = None, limits: dict | None = None) -> Check:
    """Candidate: ingredients [{material_id, amount, unit}], optional tablet_mass/dose/potency.

    Mass values use mg; percent values use % w/w. No cross-unit summation.
    Limits/bounds must come from caller-approved sources, not library defaults.
    """
    r = Check()
    parts = candidate.get('ingredients')
    if not isinstance(parts, list) or not parts:
        r.failed.append('ingredients_missing')
        return r
    ids = [p.get('material_id') for p in parts if isinstance(p, dict)]
    if len(ids) != len(parts) or any(not i or not isinstance(i, str) for i in ids) or len(ids) != len(set(ids)):
        r.failed.append('ingredient_identity_invalid_or_duplicate')
    units = {p.get('unit') for p in parts if isinstance(p, dict)}
    if len(units) != 1 or not units <= {'mg', '% w/w'}:
        r.failed.append('ingredient_units_missing_or_inconsistent')
    else:
        r.passed.append('ingredient_units_consistent')
    for p in parts:
        if not isinstance(p, dict) or isinstance(p.get('amount'), bool) or not isinstance(p.get('amount'), (float, int)) or not isfinite(p['amount']) or p['amount'] < 0:
            r.failed.append('ingredient_amount_invalid')
            continue
        name = p.get('material_id')
        if bounds and name in bounds:
            lo, hi = bounds[name]
            (r.passed if lo <= p['amount'] <= hi else r.failed).append('bound:' + str(name))
        else:
            r.not_evaluated.append('bound:' + str(name))
    if 'ingredient_amount_invalid' not in r.failed and len(units) == 1 and units <= {'mg', '% w/w'}:
        total = sum(p['amount'] for p in parts)
        if '% w/w' in units:
            (r.passed if isclose(total, 100, abs_tol=1e-6) else r.failed).append('composition_total_100_percent')
        elif candidate.get('tablet_mass') is not None:
            m = candidate['tablet_mass']
            (r.passed if isinstance(m, (float, int)) and not isinstance(m, bool) and m > 0 and isclose(total, m, abs_tol=1e-6) else r.failed).append('tablet_mass_balance_mg')
        else:
            r.not_evaluated.append('tablet_mass_balance_mg')
    if candidate.get('dose') is None or candidate.get('potency') is None or candidate.get('api_material_id') is None:
        r.not_evaluated.append('dose_potency_basis')
    else:
        dose, potency = candidate['dose'], candidate['potency']
        api = [p for p in parts if isinstance(p, dict) and p.get('material_id') == candidate['api_material_id']]
        if candidate.get('dose_unit') != 'mg' or candidate.get('potency_unit') != 'fraction' or units != {'mg'} or not isinstance(dose, (int,float)) or isinstance(dose,bool) or not isinstance(potency, (int,float)) or isinstance(potency,bool) or not 0 < potency <= 1 or dose < 0 or not api or not isinstance(api[0].get('amount'), (int,float)):
            r.failed.append('dose_potency_basis_invalid')
        else:
            (r.passed if isclose(api[0]['amount'] * potency, dose, abs_tol=1e-6) else r.failed).append('dose_potency_balance_mg')
    if limits:
        for key, (lo, hi) in limits.items():
            val = candidate.get('process', {}).get(key)
            if val is None:
                r.not_evaluated.append('process:' + key)
            elif not isinstance(val, (float,int)) or isinstance(val,bool) or not lo <= val <= hi:
                r.failed.append('process:' + key)
            else:
                r.passed.append('process:' + key)
    else:
        r.not_evaluated.append('process_limits')
    return r
