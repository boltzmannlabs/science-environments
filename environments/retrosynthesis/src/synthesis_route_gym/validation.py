"""Deterministic route gates; independent chemical review remains separate."""
from collections import defaultdict
from .chemistry import elements, element_counts, matches_pattern, reaction_identity
from .schemas import CostEstimate, Finding, RouteAssessment, RouteCandidate, Task


def _graph_findings(task, route):
    findings = []
    if route.target != task.target:
        findings.append(Finding(code="wrong_target", severity="error", message="Route target differs from task"))
    producers = {step.product: step for step in route.steps}
    if len(producers) != len(route.steps) or len({s.step_id for s in route.steps}) != len(route.steps):
        findings.append(Finding(code="duplicate_step", severity="error", message="Step IDs and intermediate producers must be unique"))
    visited, active = set(), set()

    def visit(molecule):
        if molecule in active:
            findings.append(Finding(code="cycle", severity="error", message="Route has a dependency cycle"))
            return
        if molecule in visited or molecule not in producers:
            return
        active.add(molecule)
        for use in producers[molecule].reactants:
            visit(use.smiles)
        active.remove(molecule)
        visited.add(molecule)

    visit(task.target)
    if route.steps and task.target not in producers:
        findings.append(Finding(code="missing_target_product", severity="error", message="No step produces the target"))
    for step in route.steps:
        if step.product not in visited:
            findings.append(Finding(code="disconnected_step", severity="error", message="Step does not contribute to target", step_id=step.step_id))
        sources = frozenset().union(*(elements(u.smiles) for u in step.reactants + step.reagents))
        if elements(step.product) - sources:
            findings.append(Finding(code="missing_element_source", severity="error", message="Product element absent from declared inputs", step_id=step.step_id))
        uses = step.reactants + step.reagents
        if step.condition_inputs is not None:
            declared = {u.smiles for u in uses}
            if set(step.condition_inputs.values()) - declared:
                findings.append(Finding(code="undeclared_condition_material", severity="error", message="Condition model materials must be declared as reaction inputs", step_id=step.step_id))
            substrate = step.condition_inputs.get("aryl halide")
            if substrate is not None and substrate not in {u.smiles for u in step.reactants}:
                findings.append(Finding(code="condition_substrate_mismatch", severity="error", message="Condition substrate is absent from reaction reactants", step_id=step.step_id))
        if step.product_amount_mmol is not None and all(u.amount_mmol is not None for u in uses):
            for element, count in element_counts(step.product).items():
                available = sum(element_counts(u.smiles)[element] * u.amount_mmol for u in uses)
                if count * step.product_amount_mmol > available + 1e-9:
                    findings.append(Finding(code="element_amount_deficit", severity="error", message="Product amount exceeds available elemental amount", step_id=step.step_id))
                    break
    return findings, producers


def _constraint_findings(task, route):
    findings = []
    if len(route.steps) > task.constraints.max_steps:
        findings.append(Finding(code="step_limit", severity="error", message="Route exceeds preparative step limit"))
    structures = {route.target} | {u.smiles for s in route.steps for u in s.reactants + s.reagents} | {s.product for s in route.steps}
    structures = structures | {m for s in route.steps for m in (s.condition_inputs or {}).values()}
    for molecule in sorted(structures):
        excluded = molecule in task.constraints.forbidden_smiles
        excluded = excluded or any(matches_pattern(molecule, pattern) for pattern in task.constraints.forbidden_smarts)
        if excluded:
            findings.append(Finding(code="excluded_material", severity="error", message=f"Excluded material: {molecule}"))
    for step in route.steps:
        if set(step.required_equipment) - set(task.constraints.available_equipment):
            findings.append(Finding(code="equipment_unavailable", severity="error", message="Required equipment unavailable", step_id=step.step_id))
        if set(step.operations) & set(task.constraints.forbidden_operations):
            findings.append(Finding(code="excluded_operation", severity="error", message="Excluded operation", step_id=step.step_id))
        if not step.conditions_complete:
            severity = "error" if task.constraints.require_complete_conditions else "unknown"
            findings.append(Finding(code="conditions_incomplete", severity=severity, message="Reagents and operational requirements may be incomplete", step_id=step.step_id))
    return findings


def _requirements(task, route, producers):
    external, internal = defaultdict(list), defaultdict(list)
    for step in route.steps:
        for use in step.reactants:
            (internal if use.smiles in producers else external)[use.smiles].append(use.amount_mmol)
        for use in step.reagents:
            external[use.smiles].append(use.amount_mmol)
        declared = {u.smiles for u in step.reactants + step.reagents}
        for molecule in set((step.condition_inputs or {}).values()) - declared:
            external[molecule].append(None)
    if not route.steps:
        external[task.target].append(task.target_amount_mmol)
    elif task.target_amount_mmol is not None and task.target in producers:
        internal[task.target].append(task.target_amount_mmol)
    return dict(external), dict(internal)


def _quantity_status(task, external, internal, producers):
    stock = {item.smiles: item for item in task.inventory}
    unknown = False
    if producers and task.target not in producers:
        return "insufficient"
    for requirements, is_internal in ((external, False), (internal, True)):
        for molecule, demands in requirements.items():
            available = producers[molecule].product_amount_mmol if is_internal else (
                stock[molecule].available_mmol if molecule in stock else 0)
            if available is not None and sum(x for x in demands if x is not None) > available:
                return "insufficient"
            unknown = unknown or available is None or any(x is None for x in demands)
    if task.target_amount_mmol is None:
        return "not_requested"
    return "unknown" if unknown else "complete"


def _cost(task, external):
    stock = {item.smiles: item for item in task.inventory}
    currencies = {stock[m].currency for m in external if m in stock and stock[m].price_per_mmol is not None}
    if len(currencies) > 1:
        return CostEstimate(missing_materials=tuple(sorted(external)))
    known, missing = [], []
    for molecule, amounts in external.items():
        item = stock.get(molecule)
        if item is None or item.price_per_mmol is None or any(x is None for x in amounts):
            missing.append(molecule)
        else:
            known.append(sum(amounts) * item.price_per_mmol)
    total = sum(known)
    return CostEstimate(total=total if not missing else None, known_subtotal=total,
                        currency=next(iter(currencies), None), missing_materials=tuple(sorted(missing)))


def _evidence(task, route, trusted_evidence):
    registry = {record.evidence_id: record for record in task.evidence}
    statuses, conditions = {}, {}
    order = {"predicted": 0, "unresolved": 1, "proxy": 2, "literature_analogue": 3, "literature_exact": 4, "measured": 5}
    for step in route.steps:
        candidates = []
        for evidence_id in step.evidence_ids:
            record = registry.get(evidence_id)
            status = "unresolved"
            if record is not None and record.verified_by and record in trusted_evidence:
                status = record.kind
                if status in {"literature_exact", "measured"}:
                    exact = record.product is not None and reaction_identity(record.reactants, record.product) == reaction_identity([u.smiles for u in step.reactants], step.product)
                    status = status if exact else "unresolved"
            candidates.append((status, record.conditions_scope if record else "unknown"))
        best = max(candidates, key=lambda item: order[item[0]], default=("predicted", "unknown"))
        statuses[step.step_id], conditions[step.step_id] = best
    return statuses, conditions


def assess_route(task: Task, route: RouteCandidate, *, trusted_evidence=()) -> RouteAssessment:
    graph, producers = _graph_findings(task, route)
    constraints = _constraint_findings(task, route)
    external, internal = _requirements(task, route, producers)
    stock = {item.smiles: item for item in task.inventory}
    unstocked = tuple(sorted(m for m in external if m not in stock or stock[m].available_mmol == 0))
    evidence, conditions = _evidence(task, route, trusted_evidence)
    findings = graph + constraints + [Finding(code="material_unavailable", severity="error", message=f"Required material unavailable: {m}") for m in unstocked]
    findings += [Finding(code="stoichiometry_unverified", severity="unknown", message="Element source checks do not establish atom balance, selectivity, or feasibility")]
    return RouteAssessment(
        route_id=route.route_id,
        graph_valid=not any(f.severity == "error" for f in graph),
        inventory_complete=not unstocked,
        quantity_status=_quantity_status(task, external, internal, producers),
        constraint_compliant=not any(f.severity == "error" for f in constraints),
        acquisition_only=not route.steps and task.target in stock,
        evidence_status=evidence, conditions_evidence=conditions,
        cost=_cost(task, external), findings=tuple(findings), unstocked=unstocked,
        weak_steps=tuple(s.step_id for s in route.steps if evidence[s.step_id] not in {"literature_exact", "measured"}),
    )
