"""Offline scoring against evaluator-owned records; never exposed as an agent tool."""
from .assessment import assess, budget_warnings, eligible
from .contracts import CANDIDATE, OBSERVATION, S, array, obj, validate, validate_task
from .core import digest


REFERENCE = obj({"schema_version": {"type": "integer", "const": 1}, "task_digest": S,
                 "source_version": S, "provenance": S, "candidates": array(CANDIDATE),
                 "observations": array(OBSERVATION)},
                ("schema_version", "task_digest", "source_version", "provenance", "candidates", "observations"))


def evaluate(frozen, reference, expected_digest):
    """expected_digest must come from a receipt retained outside the tested agent."""
    validate(reference, REFERENCE)
    snapshot = frozen["snapshot"]
    actual = digest(snapshot)
    if actual != frozen["digest"] or actual != expected_digest:
        raise ValueError("frozen submission differs from the retained receipt")
    task = snapshot["task"]
    validate_task(task)
    if digest(task) != reference["task_digest"] or snapshot["task_digest"] != reference["task_digest"]:
        raise ValueError("reference belongs to a different task snapshot")
    protocol = task.get("evaluation", {})
    if protocol.get("source_version") != reference["source_version"]:
        raise ValueError("reference source version differs from preregistered evaluation")
    if not protocol.get("objectives"):
        raise ValueError("task must preregister final-evaluation objectives")
    expected_kind = {"heldout_measurement": "experimental", "different_predictor": "predicted", "synthetic": "synthetic"}.get(protocol["kind"])
    for rule in protocol["objectives"]:
        if expected_kind and rule.get("kind") != expected_kind:
            raise ValueError("final objective evidence kind does not support the evaluation claim")
        if protocol["kind"] == "different_predictor":
            search_evidence = task.get("objectives", []) + task.get("constraints", []) + snapshot["observations"]
            same = [r for r in search_evidence if (r.get("method"), r.get("method_version"))
                    == (rule.get("method"), rule.get("method_version"))]
            if same:
                raise ValueError("final predictor is also used during search; transfer claim unsupported")
    candidates = {c["id"]: c for c in snapshot["candidates"]}
    refs = {c["id"]: c for c in reference["candidates"]}
    if len(refs) != len(reference["candidates"]):
        raise ValueError("duplicate reference candidate IDs")
    ids = [o["id"] for o in reference["observations"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate reference observation IDs")
    selected = snapshot["submission"]["candidate_ids"]
    if not selected or len(selected) != len(set(selected)) or not set(selected) <= candidates.keys():
        raise ValueError("invalid frozen candidate selection")
    for cid in candidates.keys() & refs.keys():
        if any(candidates[cid][k] != refs[cid][k] for k in ("representation", "form_id")):
            raise ValueError(f"reference molecular identity differs for {cid}")
    for obs in reference["observations"]:
        if obs["candidate_id"] not in refs or obs["form_id"] != refs[obs["candidate_id"]]["form_id"]:
            raise ValueError("reference observation has unmatched molecular identity")
    assessment_task = {**task, "objectives": protocol["objectives"], "constraints": protocol.get("constraints", [])}
    comparisons, constraints = assess(assessment_task, candidates, reference["observations"])
    warnings = budget_warnings(task, snapshot["usage"])
    over = any(w["category"] == "violation" for w in warnings)
    incomplete_resources = (not task.get("budgets") or any(w["code"] == "usage_incomplete" for w in warnings)
                            or bool(snapshot["unresolved_usage_commitments"]))
    forbidden_actions = [a["id"] for a in snapshot["actions"]
                         if ("allowed_jobs" in task and a["job"] not in task["allowed_jobs"])
                         or any(eligible(cid, task) == "fail" for cid in a["candidate_ids"])]
    results = []
    for cid in selected:
        objectives = [r for r in comparisons if r["candidate_id"] == cid]
        restrictions = [r for r in constraints if r["candidate_id"] == cid]
        eligibility = eligible(cid, task)
        if over or forbidden_actions or any(r["status"] == "fail" for r in restrictions):
            eligibility = "fail"
        elif (incomplete_resources or any(r["status"] == "unresolved" for r in restrictions)) and eligibility != "fail":
            eligibility = "unresolved"
        results.append({"candidate_id": cid, "eligibility": eligibility, "objectives": objectives,
                        "constraints": restrictions,
                        "all_objectives_met": None if any(r["status"] == "unresolved" for r in objectives)
                        else all(r["status"] == "pass" for r in objectives)})
    claims = {"synthetic": "Artificial software fixture only; no chemical performance evidence.",
              "search_score": "Performance on the search scoring objective; not independent confirmation.",
              "different_predictor": "Computational transfer; independence and model/data overlap require review.",
              "heldout_measurement": "Retrospective measured-endpoint comparison, conditional on assay compatibility and actual evaluator isolation."}
    return {"schema_version": 1, "submission_digest": actual, "task_digest": digest(task),
            "reference_digest": digest(reference), "reference_provenance": reference["provenance"],
            "results": results, "resource_warnings": warnings, "forbidden_action_ids": forbidden_actions,
            "resource_coverage": snapshot["coverage"], "claim": claims[protocol["kind"]],
            "isolation_verified": False,
            "limitations": ["A checksum binds a receipt; it does not establish trustworthy provenance or access isolation.",
                            "Run the evaluator outside the tested agent's readable filesystem and tools.",
                            "If final feedback is used for tuning, classify further work as development.",
                            "Unknown/unrecorded consumption prevents a claim of equal total work."]}
