import json
import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.demo import demo
from enzyme_research.discovery import DiscoveryCoordinator, UPSTREAM_REVISION


def proposal(context):
    return [{"claim": "Check activity", "plan": "Run a permitted predictor", "alternatives": ["Prediction may not reflect experiment"],
        "revision_reason": "Initial test", "evidence_refs": [], "action": {"kind": "activity", "job_name": "FixtureActivity",
        "experiment_data": {}, "candidate_ids": ["parent"]}}]


def critique(candidate, context):
    return {"score": 7, "critique": "Explicit bounded computational test", "decision": "test"}


def test_actual_upstream_and_feedback(tmp_path, upstream):
    result = demo(tmp_path / "demo", upstream)
    assert result["success"] and result["actual_upstream_code_executed"]
    assert result["upstream_revision"] == UPSTREAM_REVISION
    assert result["observations_used_for_revision"] == ["observation-1"]
    assert result["real_model_requests"] == result["scientific_platform_jobs"] == 0
    replay = list((tmp_path / "demo" / "state").glob("*/discovery_rsi_episodes.jsonl"))
    assert len(replay) == 1
    episodes = [json.loads(line) for line in replay[0].read_text().splitlines()]
    assert len(episodes) == 2
    assert episodes[1]["candidates"][0]["parents"] == [episodes[0]["selected_id"]]


def test_pending_decision_cannot_revise(store, campaign, upstream):
    coordinator = DiscoveryCoordinator(store, upstream)
    coordinator.advance(campaign, proposal, critique)
    with pytest.raises(ResearchError): coordinator.advance(campaign, proposal, critique)


def test_fabricated_evidence(store, campaign, upstream):
    def bad(context):
        values = proposal(context); values[0]["evidence_refs"] = ["imaginary-result"]; return values
    with pytest.raises(ResearchError): DiscoveryCoordinator(store, upstream).advance(campaign, bad, critique)
    assert not store.status(campaign)["decisions"]


@pytest.mark.parametrize("score", [float("nan"), float("inf"), -1, 11, True])
def test_bad_critic_scores(store, campaign, upstream, score):
    def bad(c, context): return {**critique(c, context), "score": score}
    with pytest.raises(ResearchError): DiscoveryCoordinator(store, upstream).advance(campaign, proposal, bad)


def test_stop_does_not_submit(store, campaign, upstream):
    def stop(c, context): return {**critique(c, context), "decision": "stop"}
    with pytest.raises(ResearchError): DiscoveryCoordinator(store, upstream).advance(campaign, proposal, stop)
    assert not store.status(campaign)["calls"]
    state = store.status(campaign)
    assert state["decisions"] == []
    reviews = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "hypothesis_review_declined"]
    assert len(reviews) == 1 and reviews[0]["approved_for_execution"] is False
    assert reviews[0]["critiques"]["round-1-hypothesis-1"]["decision"] == "stop"
    assert reviews[0]["proposed_actions"]["round-1-hypothesis-1"]["action"]["job_name"] == "FixtureActivity"
    assert (store.root / campaign / "discovery_rsi_episodes.jsonl").is_file()


def test_base_does_not_get_specialist(store, task, upstream):
    campaign = store.start(task, "base")
    with pytest.raises(ResearchError): DiscoveryCoordinator(store, upstream).advance(campaign, proposal, critique)


def test_critic_receives_exact_action_without_mutating_selected_request(store, campaign, upstream):
    seen = []
    def review(candidate, context):
        seen.append(candidate["action"])
        candidate["action"]["experiment_data"]["changed_in_critic"] = True
        return critique(candidate, context)
    result = DiscoveryCoordinator(store, upstream).advance(campaign, proposal, review)
    assert seen[0]["job_name"] == "FixtureActivity"
    assert result["action"]["experiment_data"] == {}


@pytest.mark.parametrize("field,value,message", [
    ("kind", "not_a_capability", "kind is outside"),
    ("job_name", "not_a_job", "job_name is outside"),
    ("experiment_data", None, "experiment_data must be an object"),
])
def test_invalid_action_diagnoses_the_specific_contract_field(store, campaign, upstream, field, value, message):
    def bad(context):
        result = proposal(context)
        result[0]["action"][field] = value
        return result
    with pytest.raises(ResearchError, match=message):
        DiscoveryCoordinator(store, upstream).advance(campaign, bad, critique)
