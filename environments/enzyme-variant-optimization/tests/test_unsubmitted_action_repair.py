"""Bounded local repair of a reviewed request before any execution exists."""
import copy
from types import SimpleNamespace

import pytest

from enzyme_research.contracts import ResearchError, digest
from enzyme_research.service import ResearchService
from test_discovery import proposal


def pending_service(store, campaign):
    action = proposal({})[0]["action"]
    action["experiment_data"] = {"input_path": "missing"}
    value = {"round": 1, "selected_id": "h1", "action": action,
             "hypotheses": [{"id": "h1", "claim": "Fixture test", "plan": "Fixture plan"}],
             "critiques": {"h1": {"score": 7, "critique": "Original review", "decision": "test"}}}
    store.save_decision(campaign, value)
    reviews = []
    class Roles:
        def critique(self, candidate, context):
            reviews.append((copy.deepcopy(candidate), copy.deepcopy(context)))
            return {"score": 6, "critique": "Reviewed corrected inputs without claiming a result", "decision": "test"}
    service = object.__new__(ResearchService)
    service.store = store
    service.model_context = lambda state: {"observations": state["observations"]}
    service.model_roles = Roles()
    return service, value, reviews


def test_unsubmitted_input_repair_is_critic_reviewed_same_round_and_preserves_original(store, campaign):
    service, before, reviews = pending_service(store, campaign)
    repaired = service.next(campaign, "repair_unsubmitted", experiment_data={"input_path": "corrected"},
                            reason="Correct malformed unsubmitted input")
    state = store.status(campaign)
    assert repaired["status"] == "pending_action_repaired" and repaired["scientific_jobs_submitted"] == 0
    assert state["calls"] == state["observations"] == []
    assert len(state["decisions"]) == 1 and state["decisions"][0]["status"] == "planned"
    after = state["decisions"][0]["value"]
    assert after["round"] == 1 and after["selected_id"] == "h1"
    assert after["action"] == {**before["action"], "experiment_data": {"input_path": "corrected"}}
    assert after["hypotheses"] == before["hypotheses"] and after["critiques"] == before["critiques"]
    assert reviews[0][0]["action"] == after["action"]
    assert reviews[0][1]["pre_submission_repair"]["original_action"] == before["action"]
    events = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "pending_action_repaired"]
    assert len(events) == 1 and events[0]["original_decision"] == before
    assert events[0]["repaired_decision_sha256"] == digest(after)
    # A malformed operation is not a completed scientific round.
    with pytest.raises(ResearchError, match="actual known observations"):
        service.next(campaign, "complete_decision", round=1, observation_ids=[])
    with pytest.raises(ResearchError, match="repair.*exhausted"):
        service.next(campaign, "repair_unsubmitted", experiment_data={"input_path": "third"}, reason="Again")
    assert len(reviews) == 1


@pytest.mark.parametrize("event,data", [
    ("workflow_segment_created", {"workflow_id": "existing"}),
    ("call_prepared", {"call_id": "ambiguous", "tool": "boltzmann_submit"}),
])
def test_repair_refuses_any_started_or_ambiguous_execution(store, campaign, event, data):
    service, before, reviews = pending_service(store, campaign)
    with store.transaction() as db:
        store.event(db, campaign, event, data)
    with pytest.raises(ResearchError, match="forbidden after"):
        service.next(campaign, "repair_unsubmitted", experiment_data={"input_path": "corrected"}, reason="Repair")
    assert not reviews and store.status(campaign)["decisions"][0]["value"] == before


@pytest.mark.parametrize("decision", ["revise", "stop"])
def test_critic_decline_leaves_pending_action_unchanged_and_consumes_single_attempt(store, campaign, decision):
    service, before, reviews = pending_service(store, campaign)
    service.model_roles.critique = lambda *args: {"score": 4, "critique": "Not executable", "decision": decision}
    with pytest.raises(ResearchError, match="did not approve"):
        service.next(campaign, "repair_unsubmitted", experiment_data={"input_path": "corrected"}, reason="Repair")
    assert store.status(campaign)["decisions"][0]["value"] == before
    declined = [e["payload"]["data"] for e in store.status(campaign)["events"] if e["payload"]["event"] == "pending_action_repair_declined"]
    assert len(declined) == 1 and declined[0]["review"]["decision"] == decision
    with pytest.raises(ResearchError, match="repair.*exhausted"):
        service.next(campaign, "repair_unsubmitted", experiment_data={"input_path": "other"}, reason="Again")
    assert store.status(campaign)["observations"] == []


def test_repair_does_not_allow_critic_to_change_identity_or_inputs(store, campaign):
    service, before, reviews = pending_service(store, campaign)
    def mutating_critic(candidate, context):
        candidate["action"]["job_name"] = "other-job"
        candidate["action"]["experiment_data"]["changed"] = True
        context["pre_submission_repair"]["original_action"]["job_name"] = "also-changed"
        return {"score": 7, "critique": "Test", "decision": "test"}
    service.model_roles.critique = mutating_critic
    service.next(campaign, "repair_unsubmitted", experiment_data={"input_path": "corrected"}, reason="Repair")
    value = store.status(campaign)["decisions"][0]["value"]
    assert value["action"] == {**before["action"], "experiment_data": {"input_path": "corrected"}}
    event = next(e["payload"]["data"] for e in store.status(campaign)["events"] if e["payload"]["event"] == "pending_action_repaired")
    assert event["original_decision"] == before
