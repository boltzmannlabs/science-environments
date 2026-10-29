"""Audit declared route flows and comparable material-cost estimates.

Inputs are host-selected stored routes. This module does not infer reaction
stoichiometry, measured yields, missing quantities, prices, or process validity.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime
import hashlib
import json
from typing import Annotated, Literal

from pydantic import Field, field_validator

from .schemas import Record, RouteCandidate, Task
from .validation import assess_route

MAX_INPUT_BYTES = 2_000_000
MAX_AMOUNT_OR_PRICE = 1e12
MAX_ROUTES = 3
Text = Annotated[str, Field(strict=True, min_length=1, max_length=2000)]
Number = Annotated[float, Field(ge=0, allow_inf_nan=False)]
NUMERIC_FIELDS = frozenset({'amount_mmol', 'available_mmol', 'product_amount_mmol',
                            'target_amount_mmol', 'price_per_mmol', 'predicted_yield'})


class ProcessBasis(Record):
    purity_basis: Text | None = None
    exclusions: Annotated[tuple[Text, ...], Field(max_length=100)] | None = None
    valuation_date: Text | None = None
    price_evidence_kind: Literal['unknown', 'illustrative', 'supplied_quote'] = 'unknown'

    @field_validator('purity_basis')
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError('Purity basis must be nonblank')
        return value

    @field_validator('exclusions')
    @classmethod
    def unique_exclusions(cls, values):
        if values is not None and (any(not x.strip() for x in values) or len(set(values)) != len(values)):
            raise ValueError('Exclusions must be distinct nonblank descriptions')
        return values

    @field_validator('valuation_date')
    @classmethod
    def date_only(cls, value):
        if value is not None and date.fromisoformat(value).isoformat() != value:
            raise ValueError('Valuation date must be YYYY-MM-DD')
        return value


class FlowLine(Record):
    smiles: str
    required_mmol: Number | None
    known_required_mmol: Number
    available_mmol: Number | None
    surplus_mmol: float | None
    status: Literal['complete', 'unknown', 'insufficient', 'ambiguous_producer']
    uses: tuple[dict, ...]


class CostLine(FlowLine):
    price_per_mmol: Number | None
    currency: str | None
    source: str | None
    quoted_at: str | None
    quote_date: str | None
    extended_cost: Number | None
    quote_usable: bool
    reasons: tuple[str, ...]


class ProcessRouteReport(Record):
    route_id: str
    route_sha256: str
    target: str
    scale_mmol: Number | None
    steps: int
    assessment: dict
    material_balance: dict
    cost_lines: tuple[CostLine, ...]
    material_cost: Number | None
    known_subtotal: Number | None
    currency: str | None
    price_evidence_kind: str
    cost_status: Literal['supplied_estimate', 'incomplete']
    comparison_eligible: bool
    ineligible_reasons: tuple[str, ...]
    route_yield: None = None
    experimental_validation: Literal[False] = False


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _plain(value):
    return value.model_dump(mode='json') if hasattr(value, 'model_dump') else value


def _bounded_inputs(task, routes, basis):
    if not isinstance(routes, (list, tuple)) or not 1 <= len(routes) <= MAX_ROUTES:
        raise ValueError('Expected one to three stored routes')
    if basis is not None and not isinstance(basis, (dict, ProcessBasis)):
        raise ValueError('Process basis must be an object')
    raw = [_plain(task), [_plain(route) for route in routes], _plain(basis)]
    try:
        encoded = json.dumps(raw, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError('Process input must be finite JSON') from exc
    if len(encoded.encode()) > MAX_INPUT_BYTES:
        raise ValueError('Process input exceeds byte limit')
    for item in _numeric_values(raw):
        if type(item) not in (int, float) or not 0 <= item <= MAX_AMOUNT_OR_PRICE:
            raise ValueError('Amounts and prices must be bounded finite numbers, not booleans')
    parsed_task = Task.model_validate(raw[0])
    parsed_routes = tuple(RouteCandidate.model_validate(row) for row in raw[1])
    if len({r.route_id for r in parsed_routes}) != len(parsed_routes):
        raise ValueError('Process route IDs must be unique')
    if any(sum(len(s.reactants) + len(s.reagents) for s in r.steps) > 4000 for r in parsed_routes):
        raise ValueError('Process route has too many material uses')
    return parsed_task, parsed_routes, ProcessBasis.model_validate(raw[2] or {})


def _numeric_values(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in NUMERIC_FIELDS and item is not None:
                yield item
            else:
                yield from _numeric_values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _numeric_values(item)


def _demands(route, task):
    """Reactants made in-route are internal; declared reagents remain purchased."""
    products = {step.product for step in route.steps}
    external, internal = {}, {}
    for step in route.steps:
        for role, uses in (('reactant', step.reactants), ('reagent', step.reagents)):
            for use in uses:
                destination = internal if role == 'reactant' and use.smiles in products else external
                destination[use.smiles] = (*destination.get(use.smiles, ()),
                    {'step_id': step.step_id, 'role': role, 'amount_mmol': use.amount_mmol})
        declared = {u.smiles for u in step.reactants + step.reagents}
        for molecule in sorted(set((step.condition_inputs or {}).values()) - declared):
            external[molecule] = (*external.get(molecule, ()),
                {'step_id': step.step_id, 'role': 'undeclared_condition_material', 'amount_mmol': None})
    if not route.steps:
        external[task.target] = ({'step_id': None, 'role': 'acquisition', 'amount_mmol': task.target_amount_mmol},)
    elif task.target in products:
        internal[task.target] = (*internal.get(task.target, ()),
            {'step_id': None, 'role': 'target_delivery', 'amount_mmol': task.target_amount_mmol})
    return external, internal


def _flow(molecule, uses, available, ambiguous=False):
    known = sum(u['amount_mmol'] for u in uses if u['amount_mmol'] is not None)
    required = known if all(u['amount_mmol'] is not None for u in uses) else None
    if ambiguous:
        status = 'ambiguous_producer'
    elif available is not None and known > available + 1e-9:
        status = 'insufficient'
    else:
        status = 'unknown' if required is None or available is None else 'complete'
    return FlowLine(smiles=molecule, required_mmol=required, known_required_mmol=known,
        available_mmol=available, surplus_mmol=None if required is None or available is None else available-required,
        status=status, uses=uses).model_dump(mode='json')


def _quote_date(value):
    if not isinstance(value, str) or value != value.strip():
        return None
    try:
        if len(value) == 10:
            parsed = date.fromisoformat(value)
            return parsed if parsed.isoformat() == value else None
        parsed = datetime.fromisoformat(value)
        return parsed.date() if parsed.tzinfo is not None else None
    except ValueError:
        return None


def _cost_line(molecule, uses, item, basis):
    flow = _flow(molecule, uses, item.available_mmol if item is not None else 0)
    price = item.price_per_mmol if item is not None else None
    quote = _quote_date(item.quoted_at) if item is not None else None
    reasons = []
    if item is None:
        reasons.append('material_unavailable')
    if flow['required_mmol'] is None:
        reasons.append('unknown_feed_amount')
    if price is None:
        reasons.append('missing_price')
    if item is None or not item.source or not item.source.strip():
        reasons.append('missing_price_source')
    if item is None or item.quoted_at is None:
        reasons.append('missing_quote_date')
    elif quote is None:
        reasons.append('invalid_quote_date')
    if quote is not None and basis.valuation_date and quote > date.fromisoformat(basis.valuation_date):
        reasons.append('quote_after_valuation_date')
    cost = None if flow['required_mmol'] is None or price is None else flow['required_mmol'] * price
    return CostLine(**flow, price_per_mmol=price, currency=item.currency if item else None,
        source=item.source if item else None, quoted_at=item.quoted_at if item else None,
        quote_date=quote.isoformat() if quote else None, extended_cost=cost,
        quote_usable=not reasons, reasons=tuple(reasons)).model_dump(mode='json')


def _flow_report(task, route, stock):
    external, internal = _demands(route, task)
    producers = {s.product: s for s in route.steps}
    counts = Counter(s.product for s in route.steps)
    internal_lines = [_flow(m, uses, producers[m].product_amount_mmol if counts[m] == 1 else None,
                            ambiguous=counts[m] != 1) for m, uses in sorted(internal.items())]
    return external, {'scope': 'declared_flow_reconciliation_only', 'stoichiometry_status': 'unverified',
        'internal': internal_lines,
        'external': [_flow(m, uses, stock[m].available_mmol if m in stock else 0)
                     for m, uses in sorted(external.items())],
        'yield_propagation_performed': False,
        'limitations': ['Declared flows are not atom-balanced stoichiometric equations.',
                       'Unreported coproducts, recovery, losses and process conditions remain unknown.']}


def _route_reasons(task, route, assessment, basis):
    reasons = [finding.code for finding in assessment.findings if finding.severity == 'error']
    if assessment.acquisition_only:
        reasons.append('acquisition_only')
    elif not route.steps:
        reasons.append('no_synthesis_steps')
    if task.target_amount_mmol is None:
        reasons.append('target_scale_unknown')
    target_steps = [s for s in route.steps if s.product == task.target]
    if len(target_steps) == 1 and target_steps[0].product_amount_mmol is None:
        reasons.append('target_output_amount_unknown')
    elif len(target_steps) == 1 and task.target_amount_mmol is not None:
        if abs(target_steps[0].product_amount_mmol - task.target_amount_mmol) > 1e-9:
            reasons.append('target_output_scale_mismatch')
    if assessment.quantity_status in {'unknown', 'insufficient'}:
        reasons.append('quantity_' + assessment.quantity_status)
    if basis.purity_basis is None:
        reasons.append('purity_basis_unknown')
    if basis.exclusions is None:
        reasons.append('cost_exclusions_unknown')
    return reasons


def _route_report(task, route, basis):
    assessment = assess_route(task, route)
    stock = {item.smiles: item for item in task.inventory}
    external, balance = _flow_report(task, route, stock)
    lines = tuple(_cost_line(m, uses, stock.get(m), basis) for m, uses in sorted(external.items()))
    reasons = _route_reasons(task, route, assessment, basis)
    reasons += [reason for line in lines for reason in line['reasons']]
    currencies = {line['currency'] for line in lines if line['extended_cost'] is not None}
    common_currency = len(currencies) == 1 and None not in currencies
    if len(currencies) > 1:
        reasons.append('mixed_currencies')
    if not lines:
        reasons.append('no_external_cost_basis')
    subtotal = sum(line['extended_cost'] or 0 for line in lines) if common_currency else None
    total = subtotal if lines and all(line['extended_cost'] is not None for line in lines) else None
    return ProcessRouteReport(route_id=route.route_id, route_sha256=_digest(route.model_dump(mode='json')),
        target=route.target, scale_mmol=task.target_amount_mmol, steps=len(route.steps),
        assessment=assessment.model_dump(mode='json'), material_balance=balance, cost_lines=lines,
        material_cost=total, known_subtotal=subtotal,
        currency=next(iter(currencies)) if common_currency else None,
        price_evidence_kind=basis.price_evidence_kind, cost_status='supplied_estimate' if total is not None else 'incomplete',
        comparison_eligible=not reasons and total is not None,
        ineligible_reasons=tuple(sorted(set(reasons)))).model_dump(mode='json')


def _comparable_rows(rows):
    currencies = {row['currency'] for row in rows if row['comparison_eligible']}
    if len(currencies) <= 1:
        return rows
    return [{**row, 'comparison_eligible': False,
             'ineligible_reasons': sorted(set(row['ineligible_reasons']) | {'comparison_currency_mismatch'})}
            if row['comparison_eligible'] else row for row in rows]


def build_process_report(task, routes, *, basis=None):
    """Return detached JSON; compare only complete, nonblocking, common-scale rows."""
    task, routes, basis = _bounded_inputs(task, routes, basis)
    rows = _comparable_rows([_route_report(task, route, basis) for route in routes])
    eligible = [row for row in rows if row['comparison_eligible']]
    def dominates(first, second):
        a, b = (first['material_cost'], first['steps']), (second['material_cost'], second['steps'])
        return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))
    pareto = [row['route_id'] for row in eligible if not any(dominates(other, row) for other in eligible)]
    return {'schema_version': 'srg-process-report-v1', 'application': 'process_route_selection',
        'task_sha256': _digest(task.model_dump(mode='json')),
        'inventory_sha256': _digest([item.model_dump(mode='json') for item in task.inventory]),
        'target': task.target, 'scale_mmol': task.target_amount_mmol, 'basis': basis.model_dump(mode='json'),
        'routes': rows, 'objectives': ['minimize_declared_material_cost', 'minimize_preparative_steps'],
        'pareto_route_ids': pareto, 'dominated_route_ids': [r['route_id'] for r in eligible if r['route_id'] not in pareto],
        'unranked_route_ids': [r['route_id'] for r in rows if not r['comparison_eligible']],
        'comparison_status': 'comparable_supplied_estimates' if eligible else 'insufficient_common_basis',
        'evidence_kind': 'declared_process_estimates', 'claims_manufacturing_savings': False,
        'claims_experimental_validation': False, 'scientific_validation_status': 'not_established',
        'limitations': ['Amounts and prices are host-supplied declarations, not independently authenticated measurements or quotes.',
            'No automatic scaling, foreign exchange conversion, route-yield multiplication or missing-value imputation.',
            'Pareto ranking concerns only complete cost/step estimates and does not establish synthetic feasibility.',
            'No unreported material, workup, waste, labor or equipment cost is included; exclusions must be reviewed.']}
