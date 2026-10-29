"""Replace one stored intermediate preparation with another exact-identity subtree."""

from .chemistry import canonical_smiles
from .planning import _route_id
from .schemas import RouteCandidate
from .validation import assess_route


def _producers(route):
    by_product = {step.product: step for step in route.steps}
    if len(by_product) != len(route.steps):
        raise ValueError('Route has duplicate intermediate producers')
    return by_product


def _reachable(root, producers):
    active, found = set(), set()

    def visit(product):
        if product in active:
            raise ValueError('Replacement route contains a cycle')
        if product in found or product not in producers:
            return
        active.add(product)
        for material in producers[product].reactants:
            visit(material.smiles)
        active.remove(product)
        found.add(product)

    visit(root)
    return found


def _connectivity(steps):
    return sorted((step.product, tuple(sorted(use.smiles for use in step.reactants)))
                  for step in steps)


def graft_intermediate(task, parent, donor, intermediate):
    """Return a new full-target route; source/evidence fields stay with their steps."""
    intermediate = canonical_smiles(intermediate)
    if parent.target != task.target or not assess_route(task, parent).graph_valid:
        raise ValueError('Parent must be a connected route for the task target')
    parent_map, donor_map = _producers(parent), _producers(donor)
    used = {task.target} | {material.smiles for step in parent.steps
                            for material in step.reactants}
    if intermediate not in used or intermediate not in donor_map:
        raise ValueError('Select an intermediate shared by the parent and donor')
    donor_products = _reachable(intermediate, donor_map)
    donor_steps = tuple(donor_map[product] for product in sorted(donor_products))
    checked_task = task.model_copy(update={'target': intermediate})
    subroute = RouteCandidate(route_id='donor-subtree', target=intermediate, steps=donor_steps)
    donor_check = assess_route(checked_task, subroute)
    if not donor_check.graph_valid or not donor_check.constraint_compliant:
        raise ValueError('Donor preparation is structurally invalid or violates constraints')
    if set(donor_products - {intermediate}) & set(parent_map):
        raise ValueError('Donor preparation would replace another parent intermediate')
    combined = {**parent_map, **{product: donor_map[product] for product in donor_products}}
    selected = _reachable(task.target, combined)
    steps = tuple(combined[product] for product in sorted(selected))
    if _connectivity(steps) == _connectivity(parent.steps):
        raise ValueError('No connectivity change')
    route = RouteCandidate(route_id=_route_id(steps), target=task.target,
                           steps=steps, parent_route_id=parent.route_id)
    assessment = assess_route(task, route)
    if not assessment.graph_valid or not assessment.constraint_compliant:
        raise ValueError('Grafted route is structurally invalid or violates constraints')
    return route
