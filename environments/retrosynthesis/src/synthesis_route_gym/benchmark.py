"""Held-out evaluation, isolated review records and honest unknown outcomes."""
import hashlib
import json
from .chemistry import canonical_smiles
from .schemas import RouteCandidate


def _reviewable_route(route):
    route = RouteCandidate.model_validate(route)
    steps = [{"product": s.product,
              "reactants": sorted((u.model_dump() for u in s.reactants), key=lambda u: (u["smiles"], u["amount_mmol"] or 0)),
              "reagents": sorted((u.model_dump() for u in s.reagents), key=lambda u: (u["smiles"], u["amount_mmol"] or 0)),
              "conditions": s.conditions, "condition_inputs": None if s.condition_inputs is None else dict(s.condition_inputs),
              "product_amount_mmol": s.product_amount_mmol,
              "conditions_complete": s.conditions_complete,
              "operations": s.operations, "required_equipment": s.required_equipment}
             for s in route.steps]
    return {"target": route.target, "steps": sorted(steps, key=lambda s: s["product"])}


def route_fingerprint(route):
    return hashlib.sha256(json.dumps(_reviewable_route(route), sort_keys=True).encode()).hexdigest()


def review_queue(runs):
    records = {}
    for run in runs:
        episode = run["episode"]
        for route in episode["routes"]:
            if route["route_id"] not in episode["submitted_route_ids"]:
                continue
            fingerprint = route_fingerprint(route)
            records[fingerprint] = {"route_fingerprint": fingerprint, "route": _reviewable_route(route),
                                    "verdict": "unresolved", "reviewer_kind": None,
                                    "reviewer": None, "independent": False, "source_locators": []}
    return [records[key] for key in sorted(records)]


def _review_index(reviews):
    index = {}
    for record in reviews:
        kind = record.get("reviewer_kind")
        if kind not in {"human", "automated_source_audit"}:
            raise ValueError("Review must be human or an independent automated_source_audit, not an LLM critic")
        if not record.get("independent") or not record.get("reviewer"):
            raise ValueError("Review requires an identified independent evaluator")
        if record.get("verdict") not in {"accepted", "rejected", "unresolved"}:
            raise ValueError("Invalid review verdict")
        if record["verdict"] == "accepted" and not record.get("source_locators"):
            raise ValueError("Accepted review requires independently inspected evidence locations")
        key = record["route_fingerprint"]
        if key in index:
            raise ValueError("Conflicting or duplicate reviews require adjudication")
        index[key] = record
    return index


def evaluate_episode(episode, reviews):
    index = _review_index(reviews)
    routes = {r["route_id"]: r for r in episode["routes"]}
    assessments = {r["route_id"]: r for r in episode["assessments"]}
    ids = episode["submitted_route_ids"]
    reviewed, resolved, outcomes, kinds = [], [], [], []
    for route_id in ids:
        assessment = assessments[route_id]
        gates = (assessment["graph_valid"] and assessment["inventory_complete"]
                 and assessment["constraint_compliant"] and not assessment["acquisition_only"]
                 and assessment["quantity_status"] in {"complete", "not_requested"})
        record = index.get(route_fingerprint(routes[route_id]))
        known = record is not None and record["verdict"] != "unresolved"
        reviewed.append(record is not None)
        resolved.append(known)
        outcomes.append(False if not gates else (record["verdict"] == "accepted" if known else None))
        kinds.append(record["reviewer_kind"] if record else None)
    at_k = True if any(v is True for v in outcomes) else (None if any(v is None for v in outcomes) else False)
    return {"task_id": episode["task"]["task_id"], "submitted_routes": len(ids),
            "inventory_complete_top1": assessments[ids[0]]["inventory_complete"] if ids else False,
            "feasible_top1": outcomes[0] if outcomes else False, "feasible_at_k": at_k,
            "review_coverage": sum(reviewed) / len(ids) if ids else 0,
            "resolved_outcome_coverage": sum(resolved) / len(ids) if ids else 0,
            "review_kinds": kinds, "review_scope": "evidence-grounded assessment; not new experimental validation",
            "cost_top1": assessments[ids[0]]["cost"] if ids else None, "usage": episode["usage"]}


def check_split(training, testing):
    train_products = {canonical_smiles(r["target"]) for r in training}
    test_products = {canonical_smiles(r["target"]) for r in testing}
    train_groups = {r.get("source_family") for r in training} - {None, ""}
    test_groups = {r.get("source_family") for r in testing} - {None, ""}
    if train_products & test_products or train_groups & test_groups:
        raise ValueError("Training/test target or source-family leakage")
    return {"disjoint": True, "training_products": len(train_products), "test_products": len(test_products),
            "source_family_metadata_complete": all(r.get("source_family") for r in training + testing)}
