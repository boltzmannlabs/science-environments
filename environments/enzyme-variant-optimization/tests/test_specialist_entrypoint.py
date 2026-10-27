import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.service import ResearchService


def test_nonfixture_service_cannot_inject_critic_scores(store, task):
    task["evidence_track"] = "computational"
    campaign = store.start(task, "specialist")
    service = object.__new__(ResearchService)
    service.store = store
    with pytest.raises(ResearchError, match="synthetic fixtures only"):
        service.next(campaign, "propose", proposals=[], critiques={})
    assert not store.status(campaign)["decisions"]


def test_base_arm_cannot_use_specialist(store, task):
    campaign = store.start(task, "base")
    service = object.__new__(ResearchService)
    service.store = store
    with pytest.raises(ResearchError, match="only in the specialist arm"):
        service.next(campaign, "investigate")


def test_valid_declined_review_returns_stop_without_creating_an_executable_plan(store, campaign, upstream):
    from test_discovery import proposal, critique
    class Roles:
        def propose(self, context): return proposal(context)
        def critique(self, candidate, context): return {**critique(candidate, context), "decision": "revise"}
    service = object.__new__(ResearchService)
    service.store = store
    service.settings = {"upstream_source": str(upstream)}
    service.model_context = lambda state: {"task": state["task"]}
    service.model_roles = Roles()
    result = service.next(campaign, "investigate")
    assert result["status"] == "hypothesis_review_declined"
    assert result["approved_for_execution"] is False
    assert store.status(campaign)["calls"] == []
    assert store.status(campaign)["decisions"] == []
