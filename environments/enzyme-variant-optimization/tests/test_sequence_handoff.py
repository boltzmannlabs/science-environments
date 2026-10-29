import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from enzyme_research.connector import TrackedConnector
from enzyme_research.contracts import ResearchError
from enzyme_research.identity import sync_sequences
from enzyme_research.workflow import WorkflowExecutor
from test_workflow_bridge import fixture_module

from enzyme_research.paths import bundled_workflow_source
WORKFLOW = bundled_workflow_source()


@pytest.fixture
def sequence_job(store, task, tmp_path):
    task["allowed_jobs"] = ["Solublempnn", "OfflineFixture_netsolp"]
    campaign = store.start(task, "base")
    catalogue, bindings = fixture_module().fixture_catalogue(tmp_path)
    output = tmp_path / "designed.fasta"
    # One valid novel sequence, one catalytic change, one parent duplicate.
    output.write_text(">valid\nAGCAAAAAAA\n>catalytic_change\nAATAAAAAAA\n>parent_copy\nAGAAAAAAAA\n")

    class Connector:
        def call(self, name, args):
            if name == "boltzmann_upload": return {"s3_path": "fixtures/accepted_sequences.csv"}
            if name == "boltzmann_submit": return {"job_name": "Solublempnn", "doc_id": "synthetic-design-job"}
            if name == "boltzmann_status": return {"status": "completed", "download_link": "https://offline.invalid/design.fasta"}
            if name == "boltzmann_download": return {"output_paths": [str(output)], "errors": []}
            raise AssertionError(name)

    driver = WorkflowExecutor(store, WORKFLOW, catalogue, TrackedConnector(store, Connector()), bindings=bindings)
    spec = {"objective": "Synthetic sequence lineage check", "approved": True,
            "initial_candidates": [{"candidate_id": "parent", "local_path": task["parent"]["structure"]["path"]}],
            "steps": [{"step_id": "design", "tool": "solublempnn", "candidate_ids": ["parent"],
                       "experiment_name": "Synthetic design handoff", "expected_count": 3,
                       "inputs": {"input_path": "fixtures/parent.zip", "num_seq": "3"}},
                      {"step_id": "solubility", "tool": "netsolp", "depends_on": ["design"],
                       "experiment_name": "Synthetic accepted sequence screening",
                       "inputs": {"input_path": {"from_step": "design", "artifact": "sequences", "upload_as": "csv"}}}]}
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submission = driver.submit(campaign, workflow, "design")
    response = driver.poll(campaign, workflow, "design", submission["call_id"])
    driver.download(campaign, workflow, "design", response["result"]["download_link"], tmp_path)
    driver.ingest(campaign, workflow, "design", output,
                  bindings={label: {"parent_ids": ["parent"]} for label in ("valid", "catalytic_change", "parent_copy")})
    service = SimpleNamespace(store=store, workflow=driver)
    return service, campaign, workflow, submission["call_id"], output


def test_sequence_transfer_keeps_explicit_parent_and_rejections(sequence_job):
    service, campaign, workflow, call, output = sequence_job
    result = sync_sequences(service, campaign, workflow, "design", call)
    assert len(result["accepted_ids"]) == 1 and len(result["rejected"]) == 2
    candidate = next(c for c in service.store.status(campaign)["candidates"] if c["candidate_id"] == result["accepted_ids"][0])
    assert candidate["sequence"] == "AGCAAAAAAA" and candidate["parent_id"] == "parent"
    assert candidate["structure_status"] == "requires_new_structure"
    assert result["observation"]["kind"] == "sequence_design"
    assert "activity" not in result["observation"]["metrics"][candidate["candidate_id"]]


def test_sequence_transfer_restart_is_idempotent(sequence_job):
    service, campaign, workflow, call, output = sequence_job
    first = sync_sequences(service, campaign, workflow, "design", call)
    second = sync_sequences(service, campaign, workflow, "design", call)
    assert first == second
    assert len(service.store.status(campaign)["candidates"]) == 2
    assert len(service.store.status(campaign)["observations"]) == 1


def test_rejected_sequences_never_reenter_same_workflow(sequence_job):
    service, campaign, workflow, call, output = sequence_job
    result = sync_sequences(service, campaign, workflow, "design", call)
    assert service.workflow.prepare(campaign, workflow, "solubility")["status"] == "ready"
    state = service.workflow.harness.status(workflow)["state"]
    assert state["steps"]["design"]["candidate_ids"] == result["accepted_ids"]
    assert len(state["steps"]["design"]["raw_candidate_ids"]) == 3
    assert state["steps"]["solubility"]["input_candidate_ids"] == result["accepted_ids"]
    for rejection in result["rejected"]:
        cid = rejection["workflow_candidate_id"]
        assert state["candidates"][cid]["status"] == "rejected_by_research_identity"
        assert state["candidates"][cid]["gates"]["research_sequence_identity"] == "rejected"


def test_tampered_sequence_output_cannot_transfer(sequence_job):
    service, campaign, workflow, call, output = sequence_job
    current = service.workflow.harness.status(workflow)["state"]["steps"]["design"]
    Path(current["artifact_path"]).write_text(">fake\nAGFAAAAAAA\n")
    with pytest.raises(ResearchError): sync_sequences(service, campaign, workflow, "design", call)
    assert len(service.store.status(campaign)["candidates"]) == 1


def test_wrong_submission_cannot_transfer(sequence_job):
    service, campaign, workflow, call, output = sequence_job
    with pytest.raises(ResearchError): sync_sequences(service, campaign, workflow, "design", "missing-call")


def test_mutant_sequence_reaches_next_segment_without_parent_coordinates(sequence_job):
    service, campaign, workflow, call, output = sequence_job
    result = sync_sequences(service, campaign, workflow, "design", call)
    cid = result["accepted_ids"][0]
    spec = {"objective": "Synthetic next sequence step", "approved": True, "steps": [
        {"step_id": "follow", "tool": "netsolp", "candidate_ids": [cid],
         "experiment_name": "Synthetic follow-up cannot use missing structure", "inputs": {"input_path": "fixtures/input.zip"}}]}
    next_workflow = service.workflow.start_segment(campaign, spec)["workflow_id"]
    candidate = service.workflow.harness.status(next_workflow)["state"]["candidates"][cid]
    assert candidate["capabilities"] == ["sequence"] and "structure" not in candidate
    assert service.workflow.prepare(campaign, next_workflow, "follow")["status"] == "ready"


def test_parent_coordinates_cannot_be_assigned_to_mutant(sequence_job):
    service, campaign, workflow, call, output = sequence_job
    cid = sync_sequences(service, campaign, workflow, "design", call)["accepted_ids"][0]
    spec = {"objective": "Invalid coordinate reuse", "approved": True,
            "initial_candidates": [{"candidate_id": cid, "local_path": service.store.status(campaign)["task"]["parent"]["structure"]["path"]}],
            "steps": [{"step_id": "wrong", "tool": "solublempnn", "candidate_ids": [cid],
                       "experiment_name": "Must not submit", "inputs": {"input_path": "fixtures/input.zip"}}]}
    with pytest.raises(ResearchError): service.workflow.start_segment(campaign, spec)
