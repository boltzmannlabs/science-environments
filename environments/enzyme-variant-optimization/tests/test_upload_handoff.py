import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest

from enzyme_research.connector import TrackedConnector
from enzyme_research.contracts import ResearchError
from enzyme_research.preparation import prepare_input, upload_input
from enzyme_research.workflow import load_workflow

from enzyme_research.paths import bundled_workflow_source


@pytest.fixture
def handoff(store, task, tmp_path):
    task["allowed_jobs"] = ["Netsolp"]
    campaign = store.start(task, "base")
    catalogue = tmp_path / "catalogue"
    catalogue.mkdir()
    (catalogue / "tool-contracts.v1.json").write_text(json.dumps({"tools": {
        "Netsolp": {"job_name": "Netsolp", "status": "active", "execution_blocked": False}}}))
    load_workflow(bundled_workflow_source())

    class Remote:
        def __init__(self): self.calls, self.mode = [], "success"
        def call(self, name, args):
            self.calls.append((name, args))
            assert name == "boltzmann_upload"
            if self.mode == "timeout": raise TimeoutError("Outcome unknown")
            if self.mode == "blocked":
                return {"error": "Review required", "stage": "validation", "status": "approval_required"}
            return {"s3_path": "users/fixture/input.csv", "sha256": "0" * 64 if self.mode == "wrong_hash"
                    else hashlib.sha256(Path(args["local_path"]).read_bytes()).hexdigest()}

    remote = Remote()
    service = SimpleNamespace(store=store, settings={"catalogue_root": str(catalogue)},
                              connector=TrackedConnector(store, remote))
    prepared = prepare_input(service, campaign, "Netsolp", ["parent"])
    return service, campaign, prepared, remote


def test_verified_upload_returns_actual_file_reference_and_no_job(handoff):
    service, campaign, prepared, remote = handoff
    result = upload_input(service, campaign, prepared["input_id"], {"prediction_type": "S"})
    assert result["uploaded"] and result["jobs_submitted"] == 0
    assert result["experiment_data"] == {"prediction_type": "S", "input_path": "users/fixture/input.csv"}
    assert remote.calls[0][1]["job_name"] == "Netsolp"
    assert not any(c["tool"] == "boltzmann_submit" for c in service.store.status(campaign)["calls"])


def test_resume_reuses_upload_receipt_without_reupload(handoff):
    service, campaign, prepared, remote = handoff
    first = upload_input(service, campaign, prepared["input_id"])
    second = upload_input(service, campaign, prepared["input_id"])
    assert second["reused"] and first["call_id"] == second["call_id"]
    assert len(remote.calls) == 1
    assert len([e for e in service.store.status(campaign)["events"] if e["payload"]["event"] == "input_uploaded"]) == 1


def test_changed_input_rejected_before_upload(handoff):
    service, campaign, prepared, remote = handoff
    Path(prepared["path"]).write_text("corrupt")
    with pytest.raises(ResearchError): upload_input(service, campaign, prepared["input_id"])
    assert not remote.calls


def test_changed_contract_rejected_before_upload(handoff):
    service, campaign, prepared, remote = handoff
    path = Path(service.settings["catalogue_root"]) / "tool-contracts.v1.json"
    data = json.loads(path.read_bytes())
    data["tools"]["Netsolp"]["execution_blocked"] = True
    path.write_text(json.dumps(data))
    with pytest.raises(ResearchError): upload_input(service, campaign, prepared["input_id"])
    assert not remote.calls


def test_unknown_outcome_never_reuploads(handoff):
    service, campaign, prepared, remote = handoff
    remote.mode = "timeout"
    with pytest.raises(TimeoutError): upload_input(service, campaign, prepared["input_id"])
    with pytest.raises(ResearchError): upload_input(service, campaign, prepared["input_id"])
    assert len(remote.calls) == 1


def test_incorrect_receipt_hash_never_becomes_confirmed_upload(handoff):
    service, campaign, prepared, remote = handoff
    remote.mode = "wrong_hash"
    with pytest.raises(ResearchError): upload_input(service, campaign, prepared["input_id"])
    assert not any(e["payload"]["event"] == "input_uploaded" for e in service.store.status(campaign)["events"])


def test_validation_warning_is_not_claimed_uploaded(handoff):
    service, campaign, prepared, remote = handoff
    remote.mode = "blocked"
    result = upload_input(service, campaign, prepared["input_id"])
    assert not result["uploaded"] and result["status"] == "definite_failure"
    assert "allow_partial_validation" not in remote.calls[0][1]


def test_input_id_is_campaign_scoped(handoff, task):
    service, campaign, prepared, remote = handoff
    other = service.store.start(task, "base")
    with pytest.raises(ResearchError): upload_input(service, other, prepared["input_id"])
    assert not remote.calls


def test_upload_cannot_take_fabricated_storage_input(handoff):
    service, campaign, prepared, remote = handoff
    with pytest.raises(ResearchError): upload_input(service, campaign, prepared["input_id"], {"input_path": "users/guess.csv"})
    assert not remote.calls


def test_once_reservation_is_atomic_and_binds_arguments(store, campaign):
    args = {"job_name": "FixtureActivity"}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: store.reserve_call(campaign, "boltzmann_upload", args, operation_key="same-upload"), range(2)))
    assert len({result[0] for result in results}) == 1
    assert sorted(result[1] for result in results) == [False, True]
    with pytest.raises(ResearchError):
        store.reserve_call(campaign, "boltzmann_upload", {**args, "local_path": "/other"}, operation_key="same-upload")


def test_reserved_but_not_sent_upload_cannot_be_replayed(store, campaign):
    class NoCalls:
        def call(self, name, args): raise AssertionError("Cannot repeat a reserved operation")
    args = {"job_name": "FixtureActivity"}
    store.reserve_call(campaign, "boltzmann_upload", args, operation_key="reserved")
    with pytest.raises(ResearchError):
        TrackedConnector(store, NoCalls()).execute(campaign, "boltzmann_upload", args, operation_key="reserved")
