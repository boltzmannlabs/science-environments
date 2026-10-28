"""Bounded inventory planning reports over registered route declarations.

Amounts are declared material flows, not an inferred stoichiometric balance.
Source assertions and supplied assessments cannot become experimental authority.
"""
from collections import defaultdict
import hashlib
import json

from .schemas import RouteAssessment, RouteCandidate, Task
from .validation import assess_route

SCHEMA_VERSION = 'srg-inventory-report-v1'
MAX_ROUTES = 3
MAX_STEPS = 12
MAX_EVENTS = 100000
_EVIDENCE_FIELDS = frozenset({'evidence_status', 'conditions_evidence', 'weak_steps'})
_STATUSES = frozenset({'ok', 'error', 'unavailable', 'interrupted', 'cancelled', 'budget_exhausted'})


def _json(value):
    if hasattr(value, 'model_dump'):
        value = value.model_dump(mode='json')
    return json.loads(json.dumps(value, allow_nan=False))


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _strict_numbers(value):
    """Reject bool/coerced numeric values at the raw application boundary."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {'amount_mmol', 'available_mmol', 'target_amount_mmol',
                       'product_amount_mmol', 'price_per_mmol', 'predicted_yield', 'proposal_score'}:
                if item is not None and type(item) not in {int, float}:
                    raise ValueError('Declared numeric fields require numbers, not coercion')
            _strict_numbers(item)
    elif isinstance(value, list):
        for item in value:
            _strict_numbers(item)


def _inputs(task, routes):
    raw = _json(task)
    _strict_numbers(raw)
    checked_task = Task.model_validate(raw)
    if not isinstance(routes, (tuple, list)) or not 1 <= len(routes) <= MAX_ROUTES:
        raise ValueError('Inventory report requires one to three route records')
    checked_routes = []
    for route in routes:
        payload = _json(route)
        _strict_numbers(payload)
        candidate = RouteCandidate.model_validate(payload)
        if len(candidate.steps) > MAX_STEPS:
            raise ValueError('Inventory report supports at most twelve steps per route')
        if len({step.step_id for step in candidate.steps}) != len(candidate.steps):
            raise ValueError('Ambiguous duplicate step IDs')
        checked_routes.append(candidate)
    if len({route.route_id for route in checked_routes}) != len(checked_routes):
        raise ValueError('Inventory report route IDs must be unique')
    return checked_task, tuple(checked_routes)


def _check_assessments(routes, expected, supplied):
    if supplied is None:
        return
    if not isinstance(supplied, (tuple, list)) or len(supplied) != len(routes):
        raise ValueError('Assessments must correspond to the registered route records')
    for route, actual, raw in zip(routes, expected, supplied):
        supplied_row = RouteAssessment.model_validate(_json(raw)).model_dump(mode='json')
        canonical = actual.model_dump(mode='json')
        if any(supplied_row[key] != canonical[key] for key in canonical if key not in _EVIDENCE_FIELDS):
            raise ValueError('Supplied assessment differs from deterministic task/route checks')
        if set(supplied_row['evidence_status']) != {step.step_id for step in route.steps}:
            raise ValueError('Supplied evidence step identities differ')
        if set(supplied_row['conditions_evidence']) != {step.step_id for step in route.steps}:
            raise ValueError('Supplied condition step identities differ')


def _requirements(task, route):
    producers = {step.product: step for step in route.steps}
    external, internal = defaultdict(list), defaultdict(list)
    for step in route.steps:
        for use in step.reactants:
            target = internal if use.smiles in producers else external
            target[use.smiles].append((step.step_id, 'reactant', use.amount_mmol))
        for use in step.reagents:
            external[use.smiles].append((step.step_id, 'reagent', use.amount_mmol))
        declared = {use.smiles for use in step.reactants + step.reagents}
        for smiles in sorted(set((step.condition_inputs or {}).values()) - declared):
            external[smiles].append((step.step_id, 'undeclared_condition_input', None))
    if not route.steps:
        external[task.target].append((None, 'target_acquisition', task.target_amount_mmol))
    elif task.target in producers and task.target_amount_mmol is not None:
        internal[task.target].append((None, 'required_target_output', task.target_amount_mmol))
    return producers, external, internal


def _quantity_row(smiles, demands, available, producer=None):
    known = sum(amount for _, _, amount in demands if amount is not None)
    total = known if all(amount is not None for _, _, amount in demands) else None
    status = 'unknown'
    if available is not None:
        if known > available:
            status = 'insufficient'
        elif total is not None:
            status = 'complete'
    return {'smiles': smiles, 'producer_step_id': producer,
            'consumer_step_ids': sorted({ident for ident, _, _ in demands if ident is not None}),
            'uses': [{'step_id': ident, 'role': role, 'amount_mmol': amount} for ident, role, amount in demands],
            'declared_demand_mmol': total, 'known_demand_subtotal_mmol': known,
            'available_mmol': available, 'quantity_status': status}


def _material_rows(task, producers, external, internal):
    stock = {item.smiles: item for item in task.inventory}
    external_rows = [_quantity_row(smiles, uses,
        stock[smiles].available_mmol if smiles in stock else 0.0)
        for smiles, uses in sorted(external.items())]
    internal_rows = [_quantity_row(smiles, uses, producers[smiles].product_amount_mmol,
        producer=producers[smiles].step_id) for smiles, uses in sorted(internal.items())]
    return external_rows, internal_rows


def _route_row(task, route, assessment):
    producers, external, internal = _requirements(task, route)
    external_rows, internal_rows = _material_rows(task, producers, external, internal)
    checked = assessment.model_dump(mode='json')
    eligible = (assessment.graph_valid and assessment.inventory_complete and assessment.constraint_compliant
                and assessment.quantity_status in {'complete', 'not_requested'} and not assessment.acquisition_only)
    convergent = [step.step_id for step in route.steps
                  if len({use.smiles for use in step.reactants if use.smiles in producers}) > 1]
    shared = [row['smiles'] for row in internal_rows if len(row['consumer_step_ids']) > 1]
    return {'route_id': route.route_id, 'parent_route_id': route.parent_route_id,
            'route_sha256': _digest(route.model_dump(mode='json')), 'step_count': len(route.steps),
            'deterministically_eligible': eligible, 'assessment': checked,
            'quantity_status': assessment.quantity_status,
            'quantity_verification': 'declared_flow_only' if task.target_amount_mmol is not None else 'not_requested',
            'external_requirements': external_rows, 'internal_requirements': internal_rows,
            'convergent_step_ids': convergent, 'shared_intermediate_smiles': shared,
            'missing_materials': list(assessment.unstocked),
            'blocking_codes': sorted({f.code for f in assessment.findings if f.severity == 'error'}),
            'evidence_status': dict(assessment.evidence_status),
            'source_support_status': 'not_independently_verified',
            'route_yield': None, 'experimental_validation': False}


def _backend_count(event):
    result = event.get('result')
    if not isinstance(result, dict):
        return None
    envelope = result.get('tool_result', result)
    if not isinstance(envelope, dict):
        return None
    usage = envelope.get('usage')
    count = usage.get('backend_calls') if isinstance(usage, dict) else None
    return count if type(count) is int and 0 <= count <= 1 else None


def _search_accounting(events):
    if not isinstance(events, (list, tuple)) or len(events) > MAX_EVENTS:
        raise ValueError('Expected bounded recorded episode history')
    for index, event in enumerate(events):
        if (not isinstance(event, dict) or type(event.get('index')) is not int or event['index'] != index
                or not isinstance(event.get('action'), str) or not 1 <= len(event['action']) <= 200
                or event.get('status') not in _STATUSES):
            raise ValueError('Invalid recorded event metadata')
    expansions = [event for event in events if event['action'] in {'expand', 'retrosynthesis'}]
    counts = [_backend_count(event) for event in expansions]
    return {'scope': 'Recorded host episode history; no new search or independent ledger verification.',
            'recorded_actions': len(events), 'expansion_attempts': len(expansions),
            'successful_expansions': sum(event['status'] == 'ok' for event in expansions),
            'failed_actions': sum(event['status'] != 'ok' for event in events),
            'known_backend_calls': sum(count for count in counts if count is not None),
            'unconfirmed_expansion_results': sum(count is None for count in counts),
            'actual_backend_calls': sum(counts) if all(count is not None for count in counts) else None,
            'llm_tokens': None}


def build_inventory_report(task, routes, *, assessments=None, events=()):
    """Report canonical stored declarations; callers own authorization/event trust."""
    task, routes = _inputs(task, routes)
    deterministic = tuple(assess_route(task, route) for route in routes)
    _check_assessments(routes, deterministic, assessments)
    rows = [_route_row(task, route, assessment) for route, assessment in zip(routes, deterministic)]
    eligible = [row['route_id'] for row in rows if row['deterministically_eligible']]
    return {'schema_version': SCHEMA_VERSION, 'application': 'inventory_planning',
            'task_sha256': _digest(task.model_dump(mode='json')),
            'target': task.target, 'target_amount_mmol': task.target_amount_mmol,
            'inventory_sha256': _digest([item.model_dump(mode='json') for item in task.inventory]),
            'routes': rows, 'eligible_route_ids': eligible,
            'ineligible_route_ids': [row['route_id'] for row in rows if not row['deterministically_eligible']],
            'top_k_route_ids': eligible[:task.budget.top_k],
            'ranking_basis': 'input_preference_among_deterministically_eligible_records',
            'search_accounting': _search_accounting(events), 'experimental_validation': False,
            'limitations': ['Declared amounts reconcile shared demand but do not prove reaction stoichiometry or yield.',
                'Input preference is not a learned ranking, optimal search result or probability of synthesis success.',
                'Missing amounts, complete procedures and independent source verification remain unresolved.',
                'Predicted route yields and supplied assessment evidence claims never establish experimental support.']}
