"""Offline specialist execution core; synthetic candidates, no model calls."""
import copy
import hashlib
import json

import pytest

from enzyme_benchmark.cached_esm import CachedESMPredictor, pool_fingerprint
from enzyme_environment.policy import Audit, Policy, verify_audit
from enzyme_environment.research_loop import ResearchLoop


def fixture(tmp_path):
    rows = [{"candidate_id": f"X{i}", "mutation": f"A{i}C", "sequences": "A" * (i-1) + "C" + "A" * (10-i)}
            for i in range(1, 11)]
    raw = ("candidate_id,predicted_score,ensemble_score_std,model_count\n" +
           "".join(f"X{i},{i},0.1,5\n" for i in range(1, 11))).encode()
    predictor = CachedESMPredictor.from_bytes(raw, hashlib.sha256(raw).hexdigest(), rows, "A" * 10,
                                            expected_pool_fingerprint=pool_fingerprint(rows, "A" * 10))
    audit = Audit(tmp_path / "audit.jsonl")
    policy = Policy({"candidates": rows, "task": [], "train": [], "development": []},
                    tmp_path / "result", audit, predictor=predictor, max_unique_scores=10)
    return ResearchLoop(policy), audit


def proposal(context):
    return {"question": "Which candidates have larger predicted scores?", "claim": "Test the pinned predictor, not activity",
        "comparator": "Conventional prediction ranking", "alternative_explanation": "A larger score may not improve activity",
        "stop_condition": "End after two bounded tests", "revision_reason": "Use previous prediction feedback if present",
        "parent_id": context["parent_id"],
        "evidence_refs": [row["observation"]["observation_id"] for row in context["history"] if row["observation"]],
        "action": {"tool": "benchmark_score", "arguments": {"candidate_ids": ["X1", "X2"]}}}


def critique(proposal, context):
    return {"decision": "test", "reason": "Allowed prediction comparator, no measured activity claim",
            "objections": ["Predictor may be inaccurate"], "requested_revision": "Use actual returned scores in the next round"}


def test_real_action_observations_and_critique_reach_the_next_round(tmp_path):
    loop, audit = fixture(tmp_path)
    seen = []
    def propose(context):
        seen.append(copy.deepcopy(context))
        if len(seen) == 2:
            previous = context["history"][0]
            assert previous["observation"]["result"]["rows"][0] == {"candidate_id": "X1", "predicted_score": 1.0}
            assert previous["critique"]["objections"] == ["Predictor may be inaccurate"]
        return proposal(context)
    try:
        records = loop.run(propose, critique, question="Synthetic bounded test")
        assert len(records) == 2 and loop.policy.cache_hits == 2
        assert records[1]["parent_id"] == records[0]["record_id"]
        assert not any(row["scientific_improvement_established"] for row in records)
        records[0]["proposal"]["claim"] = "external mutation"
        assert loop.records[0]["proposal"]["claim"] != "external mutation"
        assert json.loads(loop.export_bytes())["independent_evaluator"] is False
        assert json.loads(loop.export_bytes())["status"] == "completed"
        with pytest.raises(ValueError, match="already closed"): loop.run(proposal, critique, question="Test")
        assert len(verify_audit(audit.path)) == 8
    finally: audit.close()


@pytest.mark.parametrize("problem", ["parent", "evidence", "tool", "extra", "unknown_id", "empty_claim", "path"])
def test_invalid_proposals_fail_before_scientific_action(tmp_path, problem):
    loop, audit = fixture(tmp_path)
    def bad(context):
        value = proposal(context)
        if problem == "parent": value["parent_id"] = "invented"
        if problem == "evidence": value["evidence_refs"] = ["fabricated"]
        if problem == "tool": value["action"]["tool"] = "boltzmann_submit"
        if problem == "extra": value["experimental_answer"] = 9
        if problem == "unknown_id": value["action"]["arguments"]["candidate_ids"] = ["unknown"]
        if problem == "empty_claim": value["claim"] = " "
        if problem == "path": value["action"]["arguments"]["path"] = "/operator/answers"
        return value
    try:
        with pytest.raises(ValueError): loop.run(bad, critique, question="Synthetic test")
        assert loop.policy.calls == 0 and loop.closed and loop.status == "failed"
        assert verify_audit(audit.path)[-1]["kind"] == "research_failed_closed"
    finally: audit.close()


@pytest.mark.parametrize("decision", ["revise", "stop"])
def test_unapproved_test_does_not_call_tools(tmp_path, decision):
    loop, audit = fixture(tmp_path)
    try:
        records = loop.run(proposal, lambda p,c: {**critique(p,c), "decision": decision}, question="Synthetic test")
        assert all(row["observation"] is None for row in records) and loop.policy.calls == 0
        assert len(records) == (1 if decision == "stop" else 2)
    finally: audit.close()


def test_bad_critic_and_exception_close_the_invocation(tmp_path):
    loop, audit = fixture(tmp_path)
    try:
        with pytest.raises(ValueError): loop.run(proposal, lambda p,c: {**critique(p,c), "activity_score": 1}, question="Synthetic test")
        assert loop.closed and loop.policy.calls == 0
        assert json.loads(loop.export_bytes())["status"] == "failed"
    finally: audit.close()


@pytest.mark.parametrize("rounds", [0, 4, True, "2"])
def test_round_limits_are_not_advisory(tmp_path, rounds):
    loop, audit = fixture(tmp_path)
    try:
        with pytest.raises(ValueError): ResearchLoop(loop.policy, max_rounds=rounds)
    finally: audit.close()


def test_existing_prediction_budget_remains_enforced(tmp_path):
    loop, audit = fixture(tmp_path)
    loop.policy.max_unique_scores = 1
    def propose(context):
        result = proposal(context)
        result["action"]["arguments"]["candidate_ids"] = ["X1" if context["round"] == 1 else "X2"]
        return result
    try:
        with pytest.raises(ValueError, match="budget"): loop.run(propose, critique, question="Synthetic test")
        assert len(loop.records) == 1 and loop.status == "failed"
        assert loop.policy.score_requests == 1 and len(loop.policy.prediction_cache) == 1
    finally: audit.close()
