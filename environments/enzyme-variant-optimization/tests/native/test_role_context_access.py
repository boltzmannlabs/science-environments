import json
from types import SimpleNamespace

import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.model_roles import LiveDiscoveryRoles
from enzyme_research.service import ResearchService


class Audit:
    def __init__(self): self.events = []
    def record(self, event, **values): self.events.append((event, values))


def response(value):
    terminal = {"status": "completed", "model": "gpt-6.1-sol", "id": "response-fixture",
                "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(value)}]}]}
    return ("event: response.completed\ndata: " + json.dumps({"type": "response.completed", "response": terminal}) + "\n\n").encode()


def route(responses):
    queries, requests = [], []
    class Service:
        def read_context(self, campaign, **query):
            if campaign != "campaign" or set(query) - {"view", "record_id", "pointer", "offset", "limit", "snapshot_sha256"}:
                raise ResearchError("Read-only context fields only")
            queries.append(query)
            return {"items": [{"value": {"prediction": 0.25}}], "snapshot_sha256": "a" * 64}
    class Route:
        def __init__(self):
            self.audit = Audit()
            self.policy = SimpleNamespace(tools=(), campaign="campaign", service=Service())
            self.budget = SimpleNamespace(max_output_tokens_per_request=1536)
            self.requests = 0
        def forward(self, body):
            requests.append(json.loads(json.dumps(body)))
            self.requests += 1
            return response(responses.pop(0))
    return Route(), queries, requests


def test_role_reads_original_result_before_final_response():
    r, queries, requests = route([{"read_context": {"view": "observations", "record_id": "o1", "pointer": "/metrics/c1"}},
                                  {"score": 4, "critique": "Observed prediction is weak", "decision": "revise"}])
    roles = LiveDiscoveryRoles(r)
    result = roles.critique({"id": "hypothesis1"}, {"observations": [{"record_id": "o1"}]})
    assert result["decision"] == "revise" and roles.calls["critic"] == r.requests == 2
    assert queries == [{"view": "observations", "record_id": "o1", "pointer": "/metrics/c1"}]
    forwarded = json.loads(requests[1]["input"][0]["content"])
    assert forwarded["context_reads"][0]["result"]["items"][0]["value"]["prediction"] == 0.25
    assert all(body["tool_choice"] == "none" for body in requests)


def test_role_cannot_use_lookup_for_submission():
    r, queries, requests = route([{"read_context": {"action": "submit", "view": "calls"}}])
    with pytest.raises(ResearchError): LiveDiscoveryRoles(r).propose({})
    assert not queries and len(requests) == 1


def test_role_context_reads_are_bounded():
    query = {"read_context": {"view": "observations", "record_id": "o1"}}
    r, queries, requests = route([query, query, query])
    with pytest.raises(ResearchError, match="exceeded"):
        LiveDiscoveryRoles(r).propose({})
    assert len(queries) == 2 and len(requests) == 3


def test_context_service_denies_mutation_fields():
    service = object.__new__(ResearchService)
    with pytest.raises(ResearchError, match="only supported"):
        service.read_context("campaign", view="calls", action="submit")


def test_dedicated_critic_receives_the_native_contract_and_explicit_unsubmitted_repair_rules(store, campaign):
    from enzyme_research.context import compact_context
    from enzyme_research.native_policy import NativeResearchPolicy
    review = {"score": 6, "critique": "Review corrected inputs", "decision": "test"}
    r, queries, requests = route([review])
    policy = NativeResearchPolicy(SimpleNamespace(store=store), campaign, Audit())
    r.policy.tools = policy.tools
    context = compact_context(store.status(campaign), {})
    context["pre_submission_repair"] = {"round": 1, "reason": "Malformed input", "original_action": {}}
    assert LiveDiscoveryRoles(r).critique({"id": "h1"}, context) == review
    assert requests[0]["tools"] == list(policy.tools)
    assert json.loads(requests[0]["input"][0]["content"])["research_context"]["operation_contracts"] == context["operation_contracts"]
    assert "pre_submission_repair" in requests[0]["instructions"]
    assert "not a new scientific round" in requests[0]["instructions"]
    assert not queries
