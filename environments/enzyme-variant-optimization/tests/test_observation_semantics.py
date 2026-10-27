import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.service import ResearchService
from test_workflow_bridge import executor


def ready_service(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submitted = driver.submit(campaign, workflow, "property")
    response = driver.poll(campaign, workflow, "property", submitted["call_id"])
    driver.download(campaign, workflow, "property", response["result"]["download_link"], tmp_path)
    service = object.__new__(ResearchService)
    service.store, service.workflow = store, driver
    args = {"workflow_id": workflow, "step_id": "property", "submission_call_id": submitted["call_id"],
            "local_path": str(output), "bindings": {"parent": {"candidate_id": "parent"}}}
    return service, campaign, args


def test_solubility_cannot_be_mislabeled_as_activity(tmp_path, store, task):
    service, campaign, args = ready_service(tmp_path, store, task)
    with pytest.raises(ResearchError, match="scientific capability: solubility"):
        service.next(campaign, "ingest", **args, kind="activity")
    assert service.workflow.harness.status(args["workflow_id"])["state"]["steps"]["property"]["status"] == "remote_completed"
    assert not store.status(campaign)["observations"]


def test_known_tool_observation_kind_is_derived_not_guessed(tmp_path, store, task):
    service, campaign, args = ready_service(tmp_path, store, task)
    result = service.next(campaign, "ingest", **args)
    assert result["observation"]["kind"] == "solubility"
    assert result["observation"]["metrics"]["parent"]["solubility"] == "0.8"


def regenerated_service(tmp_path, store, task):
    campaign, driver, spec, output = executor(tmp_path, store, task)
    sequence = task["parent"]["sequence"]
    output.write_text("Sequence_ID,Sequence,predicted_solubility\nseq_1," + sequence + ",0.54\n")
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    submitted = driver.submit(campaign, workflow, "property")
    response = driver.poll(campaign, workflow, "property", submitted["call_id"])
    driver.download(campaign, workflow, "property", response["result"]["download_link"], tmp_path)
    service = object.__new__(ResearchService)
    service.store, service.workflow = store, driver
    return service, campaign, {"workflow_id": workflow, "step_id": "property",
        "submission_call_id": submitted["call_id"], "local_path": str(output)}


def test_realistic_regenerated_netsolp_id_is_bound_before_observation(tmp_path, store, task):
    service, campaign, args = regenerated_service(tmp_path, store, task)
    result = service.next(campaign, "ingest", **args)
    assert result["candidate_ids"] == ["parent"]
    assert result["observation"]["metrics"]["parent"]["predicted_solubility"] == "0.54"
    assert result["observation"]["metrics"]["parent"]["Sequence_ID"] == "seq_1"


def test_supplied_binding_cannot_override_report_sequence_identity(tmp_path, store, task):
    service, campaign, args = regenerated_service(tmp_path, store, task)
    with pytest.raises(ResearchError, match="contradict verified"):
        service.next(campaign, "ingest", **args, bindings={"seq_1": {"candidate_id": "made_up"}})
    assert not store.status(campaign)["observations"]
