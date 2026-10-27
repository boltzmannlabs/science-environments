import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.discovery import DiscoveryCoordinator
from test_discovery import proposal, critique


def observation(store, campaign, name, *, job="FixtureActivity", data=None):
    call = store.prepare_call(campaign, "synthetic_observation", {"job_name": job, "experiment_data": data or {}})
    store.call_transition(campaign, call, "sending")
    store.call_transition(campaign, call, "completed", {"synthetic_only": True})
    store.add_observation(campaign, {"observation_id": name, "kind": "activity", "candidate_ids": ["parent"],
                                    "evidence_level": "synthetic_fixture", "metrics": {"parent": {"fixture_score": 1}},
                                    "artifacts": [], "source_call_id": call})


def test_prior_observation_cannot_finish_a_new_investigation(store, campaign, upstream):
    observation(store, campaign, "old")
    DiscoveryCoordinator(store, upstream).advance(campaign, proposal, critique)
    with pytest.raises(ResearchError, match="new observations"):
        store.decision_observed(campaign, 1, ["old"])
    assert store.status(campaign)["decisions"][0]["status"] == "planned"


@pytest.mark.parametrize("job,data", [("FixtureStability", {}), ("FixtureActivity", {"different_settings": True})])
def test_unrelated_or_changed_job_cannot_finish_selected_action(store, campaign, upstream, job, data):
    DiscoveryCoordinator(store, upstream).advance(campaign, proposal, critique)
    observation(store, campaign, "other", job=job, data=data)
    with pytest.raises(ResearchError, match="selected scientific action"):
        store.decision_observed(campaign, 1, ["other"])


def test_new_matching_observation_finishes_once_and_records_source(store, campaign, upstream):
    DiscoveryCoordinator(store, upstream).advance(campaign, proposal, critique)
    observation(store, campaign, "matched")
    store.decision_observed(campaign, 1, ["matched"])
    state = store.status(campaign)
    assert state["decisions"][0]["status"] == "observed"
    event = next(e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "decision_observed")
    assert event["selected_action_observation_ids"] == ["matched"]
    with pytest.raises(ResearchError): store.decision_observed(campaign, 1, ["matched"])


@pytest.mark.parametrize("ids", [["matched", "matched"], [], [None], ["invented"]])
def test_bad_feedback_ids_are_cleanly_rejected(store, campaign, upstream, ids):
    DiscoveryCoordinator(store, upstream).advance(campaign, proposal, critique)
    observation(store, campaign, "matched")
    with pytest.raises(ResearchError): store.decision_observed(campaign, 1, ids)
