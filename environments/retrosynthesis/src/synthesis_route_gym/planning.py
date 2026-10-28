"""Fixed deterministic AND/OR route search using the same environment as agents."""
from collections import deque
import hashlib
import json
from .schemas import MaterialUse, ReactionStep, RouteCandidate


def _route_id(steps):
    signature = sorted((s.product, sorted(u.smiles for u in s.reactants)) for s in steps)
    return "route-" + hashlib.sha256(json.dumps(signature).encode()).hexdigest()[:16]


def _step(prediction):
    signature = json.dumps([prediction["product"], sorted(prediction["reactants"])])
    return ReactionStep(
        step_id="step-" + hashlib.sha256(signature.encode()).hexdigest()[:16],
        product=prediction["product"],
        reactants=tuple(MaterialUse(smiles=s) for s in prediction["reactants"]),
        source_tool=prediction["source"]["tool"], source_version=prediction["source"]["version"],
        proposal_score=prediction.get("score"),
    )


def run_fixed_workflow(env, *, expansion_top_k=10, max_frontier_states=10000):
    """Breadth-first fixed policy; all generated chemistry remains predicted.

    In-memory expansion caching is episode-local. Failed calls are charged by
    the environment and retained. Search never accesses reviewer labels.
    """
    unbudgeted = env.task.budget.regime == 'unbudgeted'
    valid_frontier = ((max_frontier_states is None and unbudgeted) or
        (type(max_frontier_states) is int and 1 <= max_frontier_states <= 100000))
    if type(expansion_top_k) is not int or not 1 <= expansion_top_k <= 100 or not valid_frontier:
        raise ValueError("Invalid fixed-search limits")
    if unbudgeted:
        max_frontier_states = None
    stock = {s.smiles for s in env.task.inventory if s.available_mmol != 0}
    frontier = deque([((env.task.target,), ())])
    cache, seen, candidates = {}, set(), []
    states, stop_reason = 0, "frontier_exhausted"
    while frontier and len(candidates) < env.task.budget.top_k:
        if env.inspect()["truncated"] or env.inspect()["terminated"]:
            stop_reason = "episode_closed"
            break
        if max_frontier_states is not None and states >= max_frontier_states:
            stop_reason = "frontier_state_budget"
            break
        pending, steps = frontier.popleft()
        states += 1
        products = {s.product for s in steps}
        pending = tuple(dict.fromkeys(s for s in pending if s not in stock and s not in products))
        if not pending:
            route_id = _route_id(steps)
            if route_id in seen:
                continue
            seen.add(route_id)
            route = RouteCandidate(route_id=route_id, target=env.task.target, steps=steps)
            proposed = env.dispatch("propose_route", {"route": route.model_dump(mode="json")})
            assessment = proposed['result'].get('assessment', {})
            eligible = (assessment.get('graph_valid') and assessment.get('inventory_complete')
                and assessment.get('constraint_compliant') and not assessment.get('acquisition_only')
                and assessment.get('quantity_status') in {'complete', 'not_requested'})
            if proposed["status"] == "ok" and (not unbudgeted or eligible):
                candidates.append(route_id)
            continue
        if len(steps) >= env.task.constraints.max_steps:
            continue
        molecule = pending[0]
        if molecule not in cache:
            expanded = env.dispatch("expand", {"smiles": molecule, "top_k": expansion_top_k})
            if expanded["status"] == "budget_exhausted":
                stop_reason = "expansion_budget"
                break
            if expanded['status'] != 'ok' and unbudgeted:
                stop_reason = 'backend_failure'
                break
            cache[molecule] = expanded["result"].get("predictions", []) if expanded["status"] == "ok" else []
        for prediction in cache[molecule]:
            try:
                step = _step(prediction)
            except (ValueError, TypeError, KeyError):
                continue
            if step.product != molecule or any(u.smiles in products | {molecule} for u in step.reactants):
                continue
            remaining = pending[1:] + tuple(u.smiles for u in step.reactants)
            if max_frontier_states is None or len(frontier) < max_frontier_states:
                frontier.append((remaining, steps + (step,)))
    if unbudgeted and len(candidates) >= env.task.budget.top_k:
        stop_reason = 'route_quota'
    if not env.inspect()["terminated"] and not env.inspect()["truncated"]:
        env.dispatch("submit", {"route_ids": candidates})
    return {"method": "fixed_workflow", "algorithm": "breadth_first_AND_OR",
            "stop_reason": stop_reason, "search_states": states,
            "expansion_top_k": expansion_top_k, "max_frontier_states": max_frontier_states,
            "episode": env.export()}


def environment_tool_schemas():
    def schema(name, description, properties, required):
        return {"name": name, "description": description, "parameters": {
            "type": "object", "properties": properties, "required": required, "additionalProperties": False}}
    schemas = [
        schema("inspect", "Compact task/state summary. Request exact inventory matches, inventory pages, route details or evidence by ID.", {
            "inventory_offset": {"type": "integer", "minimum": 0, "maximum": 100000},
            "inventory_limit": {"type": "integer", "minimum": 1, "maximum": 200},
            "inventory_smiles": {"type": "array", "maxItems": 100, "items": {"type": "string"}},
            "route_ids": {"type": "array", "maxItems": 20, "items": {"type": "string"}},
            "evidence_ids": {"type": "array", "maxItems": 20, "items": {"type": "string"}},
            "evidence_offset": {"type": "integer", "minimum": 0, "maximum": 100000},
            "evidence_limit": {"type": "integer", "minimum": 1, "maximum": 20},
            "condition_offset": {"type":"integer","minimum":0,"maximum":100000},
            "condition_limit": {"type":"integer","minimum":1,"maximum":100},
        }, []),
        schema("expand", "Generate predicted precursor sets for a molecule. Predictions are not evidence of success.",
               {"smiles": {"type": "string"}, "top_k": {"type": "integer", "minimum": 1, "maximum": 100}}, ["smiles"]),
        schema("propose_route", "Store a route or a revision with a new route_id, and receive deterministic checks.",
               {"route": RouteCandidate.model_json_schema()}, ["route"]),
        schema("validate", "Check a candidate route without claiming independent chemical acceptance.",
               {"route_id": {"type": "string"}}, ["route_id"]),
        schema("submit", "Submit ranked candidate IDs, or an empty list when no suitable route was found. Ends episode.",
               {"route_ids": {"type": "array", "items": {"type": "string"}}}, ["route_ids"]),
        schema("predict_conditions", "Predict yields for declared aryl halide, ligand, additive and base within the Dreher-Doyle screening domain. No experimental or general feasibility claim.",
               {"candidates": {"type": "array", "minItems": 1, "maxItems": 1000, "items": {
                   "type": "object", "properties": {key: {"type": "string"} for key in ("id", "aryl halide", "ligand", "additive", "base")},
                   "required": ["id", "aryl halide", "ligand", "additive", "base"], "additionalProperties": False}}}, ["candidates"]),
        schema("rank_routes", "Rank stored routes with deterministic gates and host condition predictions. Unknown yields remain unknown; utility is a heuristic, not success probability.",
               {"route_ids": {"type": "array", "maxItems": 1000, "items": {"type": "string"}}}, ["route_ids"]),
    ]
    route_parameters = schemas[2]["parameters"]
    definitions = route_parameters["properties"]["route"].pop("$defs", {})
    route_parameters["$defs"] = definitions
    from .tool_registry import ToolRegistry
    registered = {row['name']: row for row in ToolRegistry().describe()}
    # Replace existing scientific schemas, then append new canonical capabilities.
    schemas = [{**item, 'parameters': registered[item['name']]['input_schema']} if item['name'] in registered else item
               for item in schemas]
    names = {item['name'] for item in schemas}
    schemas += [{'name': name, 'description': row['scope'], 'parameters': row['input_schema']}
                for name, row in registered.items() if name not in names]
    schemas.append(schema('capabilities', 'Inspect available scientific capabilities, versions, limits and evidence scopes.', {}, []))
    schemas.append(schema('review_routes',
        'Review up to three stored routes using deterministic findings and already accessible sources. '
        'Uncertainty is not proof of impossibility; this action does not change routes or submit them.',
        {'route_ids':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':3,'uniqueItems':True}},
        ['route_ids']))
    from .application_contracts import tool_schemas
    return schemas + tool_schemas()
