import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.connector import NativeConnector, TrackedConnector
from enzyme_research.request_scope import validate_request_scope
from enzyme_research.workflow import WorkflowExecutor, load_workflow
from test_workflow_bridge import WORKFLOW, fixture_module


def test_inline_complex_matches_the_declared_candidate(store, campaign):
    state = store.status(campaign)
    validate_request_scope(state, "Boltz2", {"Protein_Sequences": ["AGAAAAAAAA"], "SMILES": ["CCO"]}, ["parent"])


@pytest.mark.parametrize("data", [
    {"Protein_Sequences": ["AGCAAAAAAA"], "SMILES": ["CCO"]},
    {"Protein_Sequences": ["AGAAAAAAAA", "AGCAAAAAAA"], "SMILES": ["CCO"]},
    {"Protein_Sequences": ["AGAAAAAAAA"], "SMILES": ["CCC"]},
    {"Protein_Sequences": ["AGAAAAAAAA"], "SMILES": ["CCO"], "DNA_Sequences": ["ACTG"]},
])
def test_inline_request_cannot_hide_changed_sequence_or_molecules(store, campaign, data):
    with pytest.raises(ResearchError): validate_request_scope(store.status(campaign), "Boltz2", data, ["parent"])


@pytest.mark.parametrize("count", ["0", "-1", "3.5", "1e5", "NaN", "999999999", 3, True, "１００"])
def test_invalid_or_expanding_allocation_rejected(store, campaign, count):
    with pytest.raises(ResearchError):
        validate_request_scope(store.status(campaign), "Solublempnn", {"num_seq": count}, ["parent"])


def test_actual_remaining_budget_is_checked(store, campaign):
    for cid, sequence in [("c1", "AGCAAAAAAA"), ("c2", "AGDAAAAAAA"), ("c3", "AGEAAAAAAA")]:
        store.add_candidates(campaign, [{"candidate_id": cid, "parent_id": "parent", "sequence": sequence}])
    state = store.status(campaign)
    validate_request_scope(state, "Solublempnn", {"num_seq": "3"}, ["parent"])
    with pytest.raises(ResearchError): validate_request_scope(state, "Solublempnn", {"num_seq": "4"}, ["parent"])
    with pytest.raises(ResearchError): validate_request_scope(state, "Solublempnn", {"num_seq": "2"}, ["parent", "c1"])


def test_live_generation_file_must_match_its_selected_candidate_receipt(store, task):
    task["evidence_track"] = "computational"
    campaign = store.start(task, "base")
    state = store.status(campaign)
    with pytest.raises(ResearchError):
        validate_request_scope(state, "Solublempnn", {"num_seq": "3", "input_path": "users/guessed.zip"}, ["parent"])
    with store.transaction() as db:
        store.event(db, campaign, "input_uploaded", {"job_name": "Solublempnn", "input_field": "input_path",
            "storage_path": "users/verified.zip", "candidate_ids": ["parent"]})
    validate_request_scope(store.status(campaign), "Solublempnn", {"num_seq": "3", "input_path": "users/verified.zip"}, ["parent"])


def test_synthetic_campaign_cannot_reach_the_real_connector(store, campaign):
    native = object.__new__(NativeConnector)
    with pytest.raises(ResearchError, match="Synthetic campaigns"):
        TrackedConnector(store, native).execute(campaign, "boltzmann_status", {"job_name": "FixtureActivity"})
    assert not store.status(campaign)["calls"]


@pytest.mark.parametrize("job,tool,data", [
    ("Boltz2", "boltz2", {"Protein_Sequences": ["AGCAAAAAAA"], "SMILES": ["CCO"]}),
    ("Solublempnn", "solublempnn", {"input_path": "fixtures/parent.zip", "num_seq": "7"}),
])
def test_invalid_scope_is_blocked_before_any_connector_request(tmp_path, store, task, job, tool, data):
    load_workflow(WORKFLOW)
    task["allowed_jobs"] = [job]
    campaign = store.start(task, "base")
    catalogue, bindings = fixture_module().fixture_catalogue(tmp_path)
    class NoCalls:
        def call(self, name, args): raise AssertionError("Invalid allocation must not reach the connector")
    driver = WorkflowExecutor(store, WORKFLOW, catalogue, TrackedConnector(store, NoCalls()), bindings=bindings)
    spec = {"objective": "Synthetic invalid-request allocation test", "approved": True,
            "initial_candidates": [{"candidate_id": "parent", "local_path": task["parent"]["structure"]["path"]}],
            "steps": [{"step_id": "invalid", "tool": tool, "candidate_ids": ["parent"],
                       "experiment_name": "Must not start a scientific request", "inputs": data}]}
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    with pytest.raises(ResearchError): driver.submit(campaign, workflow, "invalid")
    state = store.status(campaign)
    assert not state["calls"]
    rejected = [e["payload"]["data"] for e in state["events"] if e["payload"]["event"] == "request_scope_rejected"]
    assert len(rejected) == 1 and rejected[0]["scientific_request_started"] is False
