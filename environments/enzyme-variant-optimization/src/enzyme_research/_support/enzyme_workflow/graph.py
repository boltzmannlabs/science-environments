"""Explicit dependency graphs and capability gates; never infer chemistry."""

from .common import WorkflowError, identifier, validate_data
from .contract_registry import validate_inputs

STAGES = {"generation", "sequence", "folding", "preparation", "geometry", "quality",
          "optimization", "properties", "docking", "pockets"}


def validate_plan(spec, registry):
    validate_data(spec)
    if not isinstance(spec, dict) or not isinstance(spec.get("objective"), str) or not spec["objective"].strip():
        raise WorkflowError("A nonempty scientific objective is required")
    if spec.get("approved") is not True:
        raise WorkflowError("Confirm the plan, experiment labels and execution budget with the user first")
    steps = spec.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
        raise WorkflowError("Plan needs 1–100 explicit steps")
    by_id = {}
    for step in steps:
        name = identifier(step.get("step_id"), "step_id")
        if name in by_id:
            raise WorkflowError("Duplicate step_id")
        tool = registry.get(step.get("tool"))
        if tool is None:
            raise WorkflowError(f"Unknown tool: {step.get('tool')}; add its audited contract first")
        if step.get("stage", tool["stage"]) not in STAGES:
            raise WorkflowError("Unsupported workflow stage")
        if not isinstance(step.get("experiment_name"), str) or not step["experiment_name"].strip():
            raise WorkflowError(f"{name}: explicitly confirmed experiment_name is required")
        if len(step["experiment_name"]) > 200:
            raise WorkflowError("Experiment name is too long")
        deps = step.get("depends_on", [])
        if not isinstance(deps, list) or len(set(deps)) != len(deps):
            raise WorkflowError("depends_on must be a list of unique step IDs")
        validate_inputs(tool, step.get("inputs", {}))
        if step.get("tool") == "catpred":
            from .catpred import validate_handoff
            validate_handoff(step.get("handoff"))
        count = step.get("expected_count")
        if count is not None and (type(count) is not int or not 1 <= count <= 10000):
            raise WorkflowError("expected_count must be a positive integer up to 10000")
        retry = step.get("max_retries", 0)
        if type(retry) is not int or not 0 <= retry <= 3:
            raise WorkflowError("max_retries must be an approved integer from 0 to 3")
        if step.get("selection", "all") not in {"all", "passed"}:
            raise WorkflowError("selection must be all or passed")
        gates = step.get("required_gates", [])
        if not isinstance(gates, list) or len(set(gates)) != len(gates):
            raise WorkflowError("required_gates must list unique step IDs")
        by_id[name] = step
    names = [step["experiment_name"] for step in steps]
    if len(set(names)) != len(names):
        raise WorkflowError("Each step needs a distinct experiment_name")
    visiting, done = set(), set()

    def visit(name):
        if name in visiting:
            raise WorkflowError("Workflow contains a dependency cycle")
        if name in done:
            return
        if name not in by_id:
            raise WorkflowError(f"Unknown dependency: {name}")
        visiting.add(name)
        step = by_id[name]
        for dep in step.get("depends_on", []):
            visit(dep)
        for gate in step.get("required_gates", []):
            if gate not in step.get("depends_on", []):
                raise WorkflowError("A required gate must be a direct dependency")
        for value in step["inputs"].values():
            if isinstance(value, dict) and set(value) == {"from_step", "artifact", "upload_as"}:
                if value["from_step"] not in step.get("depends_on", []):
                    raise WorkflowError("An artifact reference must name a direct dependency")
                identifier(value["artifact"], "artifact")
        visiting.remove(name)
        done.add(name)
    for name in by_id:
        visit(name)
    return by_id


def require_capabilities(step, tool, state):
    """Only an evaluated structure establishes structure capabilities."""
    selected = step.get("candidate_ids") or [cid for dep in step.get("depends_on", [])
        for cid in state["steps"][dep].get("candidate_ids", [])]
    selected = list(dict.fromkeys(selected))
    if any(cid not in state["candidates"] for cid in selected):
        raise WorkflowError("Selected candidate is unknown in this workflow")
    if step.get("depends_on"):
        allowed = {cid for dep in step["depends_on"] for cid in state["steps"][dep].get("candidate_ids", [])}
        if set(selected) - allowed:
            raise WorkflowError("Candidate selection must come from the declared direct dependencies")
    if step.get("selection") == "passed":
        selected = [cid for cid in selected if state["candidates"][cid].get("gates")
                    and all(v == "passed" for v in state["candidates"][cid]["gates"].values())]
    if step.get("depends_on") and not selected:
        raise WorkflowError("No candidates remain for this branch; do not submit an empty job")
    for cid in selected:
        if cid not in state["candidates"]:
            raise WorkflowError(f"Unknown candidate: {cid}")
        for gate in step.get("required_gates", []):
            if state["candidates"][cid].get("gates", {}).get(gate) != "passed":
                raise WorkflowError(f"Candidate {cid} did not pass required gate {gate}")
        missing = set(tool.get("requires", [])) - set(state["candidates"][cid]["capabilities"])
        if missing:
            raise WorkflowError(f"Candidate {cid} needs {sorted(missing)} before {step['tool']}")
    return selected
