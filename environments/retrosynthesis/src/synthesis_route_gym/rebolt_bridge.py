"""Local, additive compatibility bridge for REBOLT's saved topN route trees.

Legacy display nodes and scores remain untouched. Deterministic checks establish
graph/inventory consistency only; citations and model yields do not prove synthesis.
"""

import hashlib
import json
import math
import re
from urllib.parse import urlparse

from .chemistry import canonical_smiles
from .condition_domain import condition_roles_match_step
from .schemas import MaterialUse, ReactionStep, RouteCandidate, Task
from .validation import assess_route

BRIDGE_VERSION = "1.0.0"
CONDITION_ROLES = ("aryl halide", "ligand", "additive", "base")


def _flag(node, name):
    value = node.get(name)
    if value is True or value == "True":
        return True
    if value is False or value == "False":
        return False
    raise ValueError(f"Node requires an explicit boolean {name}")


def _node(node):
    if not isinstance(node, dict) or not isinstance(node.get("smile"), str):
        raise ValueError("Node requires a molecule SMILES")
    children = node.get("children", [])
    if not isinstance(children, list) or any(not isinstance(c, dict) for c in children):
        raise ValueError("Node children must be a list of nodes")
    return canonical_smiles(node["smile"]), children


def _analogues(node):
    links = node.get("uspto_link", [])
    if isinstance(links, str):
        links = [links]
    if not isinstance(links, list):
        return ()
    return tuple({"source": link, "evidence_status": "retrieved_analogue_unverified"}
                 for link in links if isinstance(link, str)
                 and urlparse(link).scheme in {"https", "http"} and urlparse(link).netloc)


def _condition_data(node, reactants):
    inputs = node.get("condition_inputs")
    if inputs is None:
        return None, ()
    if not isinstance(inputs, dict) or any(role not in CONDITION_ROLES for role in inputs):
        raise ValueError("Condition inputs must use explicit supported role names")
    canonical = {role: canonical_smiles(value) for role, value in inputs.items()}
    if "aryl halide" in canonical and canonical["aryl halide"] not in reactants:
        raise ValueError("Condition aryl halide is absent from the reaction reactants")
    reagents = tuple(MaterialUse(smiles=s) for s in sorted(set(canonical.values()) - set(reactants)))
    return canonical, reagents


def _parse(node, ancestors=(), address="0"):
    """Collapse only an explicit, identity-matching molecule/reaction wrapper."""
    product, children = _node(node)
    if len(ancestors) >= 100:
        raise ValueError("Route exceeds the supported depth")
    if product in ancestors:
        raise ValueError("Route contains a molecular dependency cycle")
    stocked, reference = _flag(node, "building_block"), _flag(node, "reference")
    citations = _analogues(node)
    if stocked:
        if children or reference:
            raise ValueError("A building block must be a molecule leaf")
        return (), (), citations
    if not children:
        if reference:
            raise ValueError("A reaction display node requires reactants")
        return (), (product,), citations
    if not reference:
        if len(children) != 1 or not _flag(children[0], "reference"):
            raise ValueError("Ambiguous molecule node: expected one reaction display child")
        reaction = children[0]
        identity, children = _node(reaction)
        if identity != product or _flag(reaction, "building_block") or not children:
            raise ValueError("Reaction wrapper identity or reactants are inconsistent")
        citations += _analogues(reaction)
    else:
        reaction = node
    if any(_flag(child, "reference") for child in children):
        raise ValueError("A reaction must consume molecule nodes")
    reactants = tuple(_node(child)[0] for child in children)
    inputs, reagents = _condition_data(reaction, reactants)
    step = ReactionStep(step_id=f"step_{address}", product=product,
                        reactants=tuple(MaterialUse(smiles=s) for s in reactants),
                        reagents=reagents, condition_inputs=inputs,
                        source_tool="REBOLT", source_version="legacy_artifact_unspecified")
    subtrees = tuple(_parse(child, ancestors + (product,), f"{address}_{i}")
                     for i, child in enumerate(children))
    steps = (step,) + tuple(s for subtree in subtrees for s in subtree[0])
    unresolved = tuple(s for subtree in subtrees for s in subtree[1])
    return steps, unresolved, citations + tuple(s for subtree in subtrees for s in subtree[2])


def _unique_steps(steps):
    """Shared intermediates may reuse one identical producer, never two alternatives."""
    producers = {}
    for step in steps:
        signature = step.model_dump(mode="json", exclude={"step_id"})
        if step.product in producers and producers[step.product][0] != signature:
            raise ValueError("A molecule has conflicting reaction producers")
        producers = {**producers, **({step.product: (signature, step)} if step.product not in producers else {})}
    return tuple(pair[1] for pair in producers.values())


def _apply_model(route, model):
    complete = tuple(s for s in route.steps if s.condition_inputs is not None
                     and all(role in s.condition_inputs for role in CONDITION_ROLES))
    if not route.steps:
        return route, {"status": "not_applicable", "predictions": []}
    if not complete:
        return route, {"status": "insufficient_condition_inputs", "predictions": [],
                       "reason": "Legacy route fields do not specify all required condition roles"}
    supported = tuple(step for step in complete if condition_roles_match_step(step.model_dump(mode="json")))
    if not supported:
        return route, {"status": "outside_model_domain", "predictions": [],
                       "reason": "Declared reaction and materials do not match the supported screening domain"}
    complete = supported
    if model is None:
        return route, {"status": "model_unavailable", "predictions": []}
    try:
        predictions = model.predict([dict(s.condition_inputs) for s in complete])
        if not isinstance(predictions, list) or len(predictions) != len(complete):
            raise ValueError("Invalid model prediction count")
        values = tuple(float(p["predicted_yield_percent"]) for p in predictions)
        if any(not math.isfinite(v) or not 0 <= v <= 100 for v in values):
            raise ValueError("Invalid model yield")
        predictions = json.loads(json.dumps(predictions, allow_nan=False))
    except Exception:
        return route, {"status": "error", "predictions": [], "reason": "Condition model could not supply valid predictions"}
    yields = {step.step_id: value / 100 for step, value in zip(complete, values)}
    updated = route.model_copy(update={"steps": tuple(
        step.model_copy(update={"predicted_yield": yields[step.step_id]}) if step.step_id in yields else step
        for step in route.steps)})
    return updated, {"status": "applied" if len(complete) == len(route.steps) else "partially_applied",
                     "scope": "condition_yield_proxy_only_not_route_feasibility",
                     "predictions": [{"step_id": step.step_id, **prediction, "evidence_status": "predicted"}
                                     for step, prediction in zip(complete, predictions)],
                     "unsupported_steps": [s.step_id for s in route.steps if s.step_id not in yields]}


def _annotate(key, entry, task, condition_ranker):
    common = {"schema_version": "1.0", "bridge_version": BRIDGE_VERSION,
              "chemical_review_status": "pending",
              "limitations": ["Graph and inventory consistency do not establish reaction feasibility",
                              "Legacy scores, yields, flags and citations are unverified source metadata",
                              "Amounts, conditions, equipment and costs remain unknown unless supplied explicitly"]}
    try:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), dict):
            raise ValueError("Route entry requires a path root")
        steps, unresolved, citations = _parse(entry["path"])
        route = RouteCandidate(route_id=f"rebolt_{key}", target=_node(entry["path"])[0], steps=_unique_steps(steps))
        route, model_application = _apply_model(route, condition_ranker)
        assessment = assess_route(task, route)
        unique_citations = {citation["source"]: citation for citation in citations}
        return {**common, "status": "ok", "route": route.model_dump(mode="json"),
                "assessment": assessment.model_dump(mode="json"),
                "unresolved_leaves": sorted(set(unresolved)),
                "retrieved_analogues": list(unique_citations.values()),
                "model_application": model_application, "parse_findings": []}
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        return {**common, "status": "parse_error", "route": None, "assessment": None,
                "model_application": {"status": "not_applicable", "predictions": []},
                "retrieved_analogues": [], "unresolved_leaves": [],
                "parse_findings": [{"code": "invalid_legacy_tree", "message": str(exc)}]}


def enrich_rebolt_paths(paths, task: Task, condition_ranker=None):
    """Return ``(enriched_paths, report)``; perform no IO, network or input mutation.

    Only topN entries receive additive ``synthesis_route_gym`` annotations. The
    task's inventory is authoritative. No source citations are trusted implicitly.
    Re-running replaces the bridge annotation while preserving all legacy fields.
    """
    if not isinstance(paths, dict):
        raise ValueError("REBOLT paths must be a JSON object")
    if not isinstance(task, Task):
        raise ValueError("A validated Task is required")
    try:
        serialized = json.dumps(paths, allow_nan=False)
        copied = json.loads(serialized)
    except (ValueError, TypeError, RecursionError) as exc:
        raise ValueError("REBOLT artifact must contain finite, acyclic JSON values") from exc
    keys = tuple(key for key in copied if re.fullmatch(r"top\d+", key))
    annotations = {key: _annotate(key, copied[key], task, condition_ranker) for key in keys}
    # An invalid scalar route entry cannot accept an additive field. Report it
    # separately while retaining its original value exactly.
    enriched = {key: {**value, "synthesis_route_gym": annotations[key]}
                if key in annotations and isinstance(value, dict) else value for key, value in copied.items()}
    report = {"schema_version": "1.0", "bridge_version": BRIDGE_VERSION,
              "source_sha256": hashlib.sha256(serialized.encode()).hexdigest(),
              "task_id": task.task_id, "route_count": len(keys),
              "parsed_route_count": sum(a["status"] == "ok" for a in annotations.values()),
              "parse_error_count": sum(a["status"] == "parse_error" for a in annotations.values()),
              "route_status": {key: a["status"] for key, a in annotations.items()},
              "unannotatable_entries": {key: annotations[key] for key in keys if not isinstance(copied[key], dict)},
              "scientific_claim": "Compatibility and deterministic consistency checks only; chemical review pending"}
    return enriched, report
