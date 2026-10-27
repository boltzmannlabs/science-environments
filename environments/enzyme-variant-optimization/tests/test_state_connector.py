import hashlib
import json
import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.connector import TrackedConnector, durable_result
from enzyme_research.store import Store


def candidate():
    return {"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}


def test_restart_and_duplicate_candidates(store, campaign):
    store.add_candidates(campaign, [candidate()])
    reopened = Store(store.root)
    assert len(reopened.status(campaign)["candidates"]) == 2
    with pytest.raises(ResearchError): reopened.add_candidates(campaign, [candidate()])


def test_parent_hash_checked(store, task):
    task["parent"]["structure"]["sha256"] = "0" * 64
    with pytest.raises(ResearchError): store.start(task, "base")


def test_events_tampering_detected(store, campaign):
    with store.connection() as db:
        db.execute("UPDATE events SET payload='{}'")
    with pytest.raises(ResearchError): store.status(campaign)


def test_candidate_budget(store, task):
    task["budget"]["max_unique_candidates"] = 1
    campaign = store.start(task, "base")
    store.add_candidates(campaign, [candidate()])
    with pytest.raises(ResearchError):
        store.add_candidates(campaign, [{"candidate_id": "c2", "parent_id": "parent", "sequence": "AGDAAAAAAA"}])


def test_unknown_parent(store, campaign):
    value = candidate(); value["parent_id"] = "unknown"
    with pytest.raises(ResearchError): store.add_candidates(campaign, [value])


class Stub:
    def __init__(self, result=None, error=False): self.result, self.error, self.calls = result, error, 0
    def call(self, name, args):
        self.calls += 1
        if self.error: raise TimeoutError("uncertain acceptance")
        return self.result


def test_unknown_submission_blocks_duplicate(store, campaign):
    remote = Stub(error=True)
    bridge = TrackedConnector(store, remote)
    args = {"job_name": "FixtureActivity", "experiment_name": "test", "experiment_data": {"input_path": "users/input.csv"}}
    with pytest.raises(TimeoutError): bridge.execute(campaign, "boltzmann_submit", args)
    assert store.status(campaign)["calls"][0]["status"] == "submit_unknown"
    with pytest.raises(ResearchError): bridge.execute(campaign, "boltzmann_submit", args)
    assert remote.calls == 1


def test_server_credit_calculation_500_is_not_proof_of_no_job(store, campaign):
    remote = Stub({"error": "Failed to calculate credits", "stage": "submit", "http_status": 500,
                   "status": "unknown", "authorization_required": False, "safe_to_retry": False})
    bridge = TrackedConnector(store, remote)
    first = bridge.execute(campaign, "boltzmann_submit", {
        "job_name": "FixtureActivity", "experiment_name": "synthetic-credit-failure", "experiment_data": {}})
    assert first["status"] == "submit_unknown"
    assert "doc_id" not in first["result"]
    with pytest.raises(ResearchError, match="reconciled or completed"):
        bridge.execute(campaign, "boltzmann_submit", {
            "job_name": "FixtureActivity", "experiment_name": "not-an-authorized-retry", "experiment_data": {}})
    assert remote.calls == 1 and not store.status(campaign)["observations"]


def test_accepted_not_completed(store, campaign):
    remote = Stub({"doc_id": "real-doc-id", "status": "accepted"})
    bridge = TrackedConnector(store, remote)
    result = bridge.execute(campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})
    assert result["status"] == "accepted"
    remote.result = {"status": "running"}
    bridge.poll(campaign, result["call_id"])
    assert store.status(campaign)["calls"][0]["status"] == "accepted"
    remote.result = {"status": "completed", "output": {"path": "users/result.zip", "download_link": "https://example.test/private"}}
    bridge.poll(campaign, result["call_id"])
    state = store.status(campaign)
    assert state["calls"][0]["status"] == "completed"
    assert "https://" not in json.dumps(state)


def test_unapproved_job_no_calls(store, campaign):
    remote = Stub({})
    with pytest.raises(ResearchError):
        TrackedConnector(store, remote).execute(campaign, "boltzmann_submit", {"job_name": "Unknown"})
    assert remote.calls == 0


def test_sending_cannot_replay(store, campaign):
    call = store.prepare_call(campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})
    store.call_transition(campaign, call, "sending")
    with pytest.raises(ResearchError): store.call_transition(campaign, call, "sending")
    with pytest.raises(ResearchError): store.prepare_call(campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})


def test_no_signed_urls_in_durable_result():
    result = durable_result({"output": [{"path": "users/a.zip", "download_link": "https://private/a?X-Goog-Signature=x"}]})
    assert result == {"output": [{"path": "users/a.zip"}]}


def test_observations_require_real_known_source(store, campaign):
    value = {"observation_id": "o1", "kind": "activity", "candidate_ids": ["parent"],
             "evidence_level": "synthetic_fixture", "metrics": {"score": 1.0}, "artifacts": [], "source_call_id": "missing"}
    with pytest.raises(ResearchError): store.add_observation(campaign, value)


def test_synthetic_forbidden_in_live(store, task):
    task["evidence_track"] = "computational"
    campaign = store.start(task, "base")
    with pytest.raises(ResearchError): store.prepare_call(campaign, "synthetic_observation", {})


def test_empty_candidates_fail(store, campaign):
    with pytest.raises(ResearchError): store.add_candidates(campaign, [])


def test_terminal_job_failure_is_not_left_running(store, campaign):
    remote = Stub({"doc_id": "job-id"})
    bridge = TrackedConnector(store, remote)
    result = bridge.execute(campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})
    remote.result = {"status": "failed", "error": "The tool failed"}
    bridge.poll(campaign, result["call_id"])
    assert store.status(campaign)["calls"][0]["status"] == "definite_failure"


def test_wrong_job_response_is_quarantined(store, campaign):
    result = TrackedConnector(store, Stub({"doc_id": "job-id", "job_name": "OtherJob"})).execute(
        campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})
    assert result["status"] == "submit_unknown"


def test_malformed_result_does_not_leave_send_replayable(store, campaign):
    with pytest.raises(ResearchError):
        TrackedConnector(store, Stub([])).execute(campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})
    assert store.status(campaign)["calls"][0]["status"] == "submit_unknown"


def test_output_not_yet_generated_keeps_the_original_accepted_job(store, campaign):
    remote = Stub({"doc_id": "original-job-id"})
    bridge = TrackedConnector(store, remote)
    submitted = bridge.execute(campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})
    remote.result = {"error": "Output Not Yet Generated", "http_status": 404, "status": "unknown"}
    bridge.poll(campaign, submitted["call_id"])
    state = store.status(campaign)
    assert state["calls"][0]["status"] == "accepted"
    assert state["calls"][0]["result"]["doc_id"] == "original-job-id"
    with pytest.raises(ResearchError): bridge.execute(campaign, "boltzmann_submit", {"job_name": "FixtureActivity"})
    remote.result = {"status": "completed"}
    bridge.poll(campaign, submitted["call_id"])
    assert store.status(campaign)["calls"][0]["status"] == "completed"
