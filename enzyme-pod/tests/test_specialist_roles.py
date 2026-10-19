"""Mock-provider role checks, with actual host Policy dispatch; zero live calls."""
import hashlib
import json

import httpx
import pytest

from enzyme_benchmark.cached_esm import CachedESMPredictor, pool_fingerprint
from enzyme_benchmark.contracts import TaskContract
from enzyme_environment.transport import BenchmarkRoute, Budget
from enzyme_environment.connection import HostCredential
from enzyme_environment.policy import Audit, Policy
from enzyme_environment.roles import LiveResearchRoles
from enzyme_environment.research_loop import ResearchLoop


@pytest.fixture
def setup(tmp_path):
    rows = [{"candidate_id": f"X{i}", "mutation": f"A{i}C", "sequences": "A"*(i-1)+"C"+"A"*(10-i)} for i in range(1,11)]
    raw = ("candidate_id,predicted_score,ensemble_score_std,model_count\n" + "".join(f"X{i},{i},0.1,5\n" for i in range(1,11))).encode()
    p = CachedESMPredictor.from_bytes(raw, hashlib.sha256(raw).hexdigest(), rows, "A"*10,
                                    expected_pool_fingerprint=pool_fingerprint(rows,"A"*10))
    audit = Audit(tmp_path / "audit.jsonl")
    policy = Policy({"task": [], "candidates": rows, "train": [], "development": []}, tmp_path/"result", audit, predictor=p)
    task = TaskContract("synthetic", "Pick ten for a synthetic role test", "toy", "synthetic", "A"*10, 10, 10, 10)
    yield policy, task, rows
    audit.close()


def result_for(body):
    context = json.loads(body["input"][0]["content"])["research_context"]
    if body["text"]["format"]["name"] == "enzyme_proposal":
        return {"question": "Query the frozen prediction", "claim": "Predictions can be ranked, not treated as activity",
            "comparator": "Same conventional score source", "alternative_explanation": "Prediction can be wrong",
            "stop_condition": "Two bounded tests", "revision_reason": "Use actual earlier feedback",
            "parent_id": context["parent_id"], "evidence_refs": [r["observation"]["observation_id"] for r in context["history"] if r["observation"]],
            "action": {"tool": "benchmark_score", "arguments": {"candidate_ids": ["X1","X2"]}}}
    return {"decision": "test", "reason": "Valid limited prediction test", "objections": ["No activity proof"],
            "requested_revision": "Use actual tool observations in the revision"}


def provider(policy, transform=lambda x:x, *, requests=6):
    seen=[]
    def handle(req):
        body=json.loads(req.content)
        seen.append(body)
        value=transform(result_for(body))
        output=[{"type":"message","role":"assistant","content":[{"type":"output_text","text":json.dumps(value)}]}]
        if value == "tool": output=[{"type":"function_call","name":"benchmark_score","call_id":"call_unit","arguments":'{"candidate_ids":["X1"]}'}]
        response={"id":"unit","model":"gpt-6.1-sol","status":"completed","output":output,
                  "usage":{"input_tokens":5,"output_tokens":4,"total_tokens":9}}
        return httpx.Response(200,content=("data: "+json.dumps({"type":"response.completed","response":response})+"\n\n").encode())
    route=BenchmarkRoute(HostCredential("synthetic-secret-not-real",{}),policy,Budget(max_requests=requests),
        client_factory=lambda:httpx.AsyncClient(transport=httpx.MockTransport(handle),trust_env=False))
    return route,seen


def test_shared_ledger_real_tool_feedback_and_no_credentials_in_role_input(setup):
    policy,task,rows=setup
    route,seen=provider(policy)
    roles=LiveResearchRoles(route,task,rows)
    records=ResearchLoop(policy).run(roles.propose,roles.critique,question=task.objective)
    assert len(records)==2 and route.requests==4 and roles.calls==4 and roles.provider_attempts==4
    assert route.usage["total_tokens"]==36 and policy.score_requests==4 and policy.cache_hits==2
    context=json.loads(seen[2]["input"][0]["content"])["research_context"]
    assert context["history"][0]["observation"]["result"]["rows"][0]["predicted_score"]==1.0
    assert context["history"][0]["critique"]["objections"]==["No activity proof"]
    assert all(body["tool_choice"]=="none" and body["text"]["format"]["strict"] is True for body in seen)
    assert "synthetic-secret-not-real" not in json.dumps(seen) and not policy.submitted


@pytest.mark.parametrize("value", ["not-an-object", [], {"invalid":"output"}, "tool"])
def test_malformed_or_tool_role_output_not_executed_or_retried(setup,value):
    policy,task,rows=setup
    route,seen=provider(policy,lambda x:value)
    roles=LiveResearchRoles(route,task,rows)
    with pytest.raises(ValueError): ResearchLoop(policy).run(roles.propose,roles.critique,question=task.objective)
    assert len(seen)==1 and policy.calls==0 and roles.provider_attempts==1
    # A structurally valid object with wrong scientific fields is rejected by
    # the ResearchLoop; transport can have completed while that contract fails.
    if not isinstance(value,dict): assert route.failed


def test_role_and_coordinator_cannot_have_independent_request_budgets(setup):
    policy,task,rows=setup
    route,seen=provider(policy,requests=3)
    roles=LiveResearchRoles(route,task,rows)
    with pytest.raises(ValueError,match="no retry"):
        ResearchLoop(policy).run(roles.propose,roles.critique,question=task.objective)
    assert route.requests==3 and len(seen)==3 and route.failed and policy.score_requests==2 and roles.provider_attempts==3


def test_bad_candidate_context_or_output_budget_fails_without_request(setup):
    policy,task,rows=setup
    route,seen=provider(policy)
    with pytest.raises(ValueError): LiveResearchRoles(route,task,[{**rows[0],"experimental_score":9}]+rows[1:])
    with pytest.raises(ValueError): LiveResearchRoles(route,task,rows,max_output_tokens=True)
    with pytest.raises(ValueError): LiveResearchRoles(route,task,rows,max_output_tokens=1025)
    assert not seen
