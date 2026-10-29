import importlib.util
from pathlib import Path

import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.connector import TrackedConnector
from enzyme_research.workflow import WorkflowExecutor

from enzyme_research.paths import bundled_workflow_source
WORKFLOW = bundled_workflow_source()


def fixture_module():
    spec = importlib.util.spec_from_file_location("workflow_replay_fixture", WORKFLOW / "examples/offline_replay.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def executor(tmp_path, store, task):
    from enzyme_research.workflow import load_workflow
    load_workflow(WORKFLOW)
    module = fixture_module()
    catalogue, bindings = module.fixture_catalogue(tmp_path)
    task["allowed_jobs"] = ["OfflineFixture_netsolp"]
    campaign = store.start(task, "base")
    output = tmp_path / "actual_output.csv"
    output.write_text("seq_id,solubility\nparent,0.8\n")
    class Connector:
        def call(self, name, args):
            if name == "boltzmann_submit": return {"job_name": "OfflineFixture_netsolp", "doc_id": "synthetic-job-id"}
            if name == "boltzmann_status": return {"status": "completed", "download_link": "https://offline.invalid/result.csv"}
            if name == "boltzmann_download": return {"output_paths": [str(output)], "errors": []}
            raise AssertionError(name)
    driver = WorkflowExecutor(store, WORKFLOW, catalogue, TrackedConnector(store, Connector()), bindings=bindings)
    structure = Path(task["parent"]["structure"]["path"])
    spec = {"objective": "Synthetic integration of the existing executor", "approved": True,
            "initial_candidates": [{"candidate_id": "parent", "local_path": str(structure)}],
            "steps": [{"step_id": "property", "tool": "netsolp", "candidate_ids": ["parent"],
                       "experiment_name": "Synthetic workflow bridge", "inputs": {"input_path": "fixtures/input.csv"}}]}
    return campaign, driver, spec, output


def test_existing_workflow_receipts_and_parsers(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submitted = driver.submit(campaign, workflow, "property")
    assert submitted["status"] == "accepted"
    result = driver.poll(campaign, workflow, "property", submitted["call_id"])
    assert driver.harness.status(workflow)["state"]["steps"]["property"]["status"] == "remote_completed"
    driver.download(campaign, workflow, "property", result["result"]["download_link"], tmp_path)
    ingested = driver.ingest(campaign, workflow, "property", output, bindings={"parent": {"candidate_id": "parent"}})
    assert ingested["status"] == "complete"
    assert driver.harness.status(workflow)["state"]["candidates"]["parent"]["metrics"]["property"]["solubility"] == "0.8"


def test_unreceipted_file_cannot_be_ingested(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submitted = driver.submit(campaign, workflow, "property")
    driver.poll(campaign, workflow, "property", submitted["call_id"])
    with pytest.raises(ValueError): driver.ingest(campaign, workflow, "property", output, bindings={"parent": {"candidate_id": "parent"}})


def test_cross_campaign_segment_denied(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    other = store.start(task, "base")
    with pytest.raises(ResearchError): driver.submit(other, workflow, "property")


def test_unrelated_download_link_is_denied_before_network(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submitted = driver.submit(campaign, workflow, "property")
    driver.poll(campaign, workflow, "property", submitted["call_id"])
    before = len(store.status(campaign)["calls"])
    with pytest.raises(ResearchError):
        driver.download(campaign, workflow, "property", "https://unrelated.invalid/private", tmp_path)
    assert len(store.status(campaign)["calls"]) == before


def test_native_list_link_is_receipted_and_downloaded_without_source_patch(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    original = driver.connector.connector.call
    def call(name, args):
        if name == "boltzmann_status":
            return {"status": "Success", "OutputData": {"output_path": {
                "path": "users/fixture/result.csv", "download_link": ["https://offline.invalid/result.csv"]}}}
        return original(name, args)
    driver.connector.connector.call = call
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submitted = driver.submit(campaign, workflow, "property")
    result = driver.download_current(campaign, workflow, "property", submitted["call_id"], tmp_path)
    assert result["result"]["output_paths"] == [str(output)]
    ingested = driver.ingest(campaign, workflow, "property", output, bindings={"parent": {"candidate_id": "parent"}})
    assert ingested["status"] == "complete"
    assert all("download_link" not in str(c.get("result")) for c in store.status(campaign)["calls"])


@pytest.mark.parametrize("links", [["https://offline.invalid/result.csv", "https://offline.invalid/other.csv"], [], [123], {"url": "https://offline.invalid/result.csv"}])
def test_ambiguous_or_malformed_link_lists_never_download(tmp_path, store, task, links):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    original = driver.connector.connector.call
    def call(name, args):
        if name == "boltzmann_status":
            return {"status": "completed", "download_link": links}
        if name == "boltzmann_download":
            raise AssertionError("No ambiguous or malformed result may be downloaded")
        return original(name, args)
    driver.connector.connector.call = call
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submitted = driver.submit(campaign, workflow, "property")
    with pytest.raises(ResearchError):
        driver.download_current(campaign, workflow, "property", submitted["call_id"], tmp_path)


def test_known_preflight_block_is_not_an_ambiguous_remote_job(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    class ValidationBlocked:
        def call(self, name, args):
            return {"error": "Review required", "stage": "validation", "status": "approval_required", "safe_to_retry": False}
    driver.connector.connector = ValidationBlocked()
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    result = driver.submit(campaign, workflow, "property")
    assert result["status"] == "definite_failure" and result["result"]["safe_to_retry"] is False
    current = driver.harness.status(workflow)["state"]["steps"]["property"]
    assert current["status"] == "failed" and "doc_id" not in current
    with pytest.raises(ValueError): driver.submit(campaign, workflow, "property")
