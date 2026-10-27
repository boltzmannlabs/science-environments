import csv
import io
import json
from pathlib import Path
import zipfile

import pytest

from enzyme_research.connector import TrackedConnector
from enzyme_research.contracts import ResearchError, observation_record
from enzyme_research.service import ResearchService
from enzyme_research.workflow import WorkflowExecutor, load_workflow
from test_workflow_bridge import fixture_module, WORKFLOW
from test_structure_handoff import pdb


def quality_zip(path, labels, *, mode="validation"):
    from enzyme_workflow.artifacts import QUALITY_METRICS
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=["candidate_id", "status", *QUALITY_METRICS])
    writer.writeheader()
    for i, label in enumerate(labels):
        row = {key: 0 for key in QUALITY_METRICS}
        row.update(candidate_id=label, status="measured" if mode == "measurement_only" else "passed" if i == 0 else "rejected",
                   clashscore=5 if i == 0 else 20, ramachandran_favored_percent=100)
        writer.writerow(row)
    with zipfile.ZipFile(path, "w") as archive: archive.writestr("candidate_summary.csv", stream.getvalue())


@pytest.fixture
def pipeline(store, task, tmp_path):
    load_workflow(WORKFLOW)
    task["allowed_jobs"] = ["Boltz2", "OfflineFixture_mol_probity", "OfflineFixture_netsolp"]
    campaign = store.start(task, "base")
    store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    catalogue, bindings = fixture_module().fixture_catalogue(tmp_path)
    fold = tmp_path / "fold.zip"
    quality = tmp_path / "quality.zip"
    properties = tmp_path / "properties.csv"
    with zipfile.ZipFile(fold, "w") as archive:
        archive.writestr("pose_0.pdb", pdb("AGCAAAAAAA"))
        archive.writestr("pose_1.pdb", pdb("AGCAAAAAAA", shift=0.1))
    returned = {"Boltz2": fold, "OfflineFixture_mol_probity": quality, "OfflineFixture_netsolp": properties}
    submitted = []
    class Connector:
        def call(self, name, args):
            if name == "boltzmann_upload": return {"s3_path": "fixtures/" + Path(args["local_path"]).name}
            if name == "boltzmann_submit":
                submitted.append(args)
                return {"doc_id": "synthetic-" + args["job_name"], "job_name": args["job_name"]}
            if name == "boltzmann_status": return {"status": "completed", "download_link": "https://offline.invalid/" + args["job_name"]}
            if name == "boltzmann_download": return {"output_paths": [str(returned[args["download_url"].rsplit("/", 1)[-1]])], "errors": []}
            raise AssertionError(name)
    driver = WorkflowExecutor(store, WORKFLOW, catalogue, TrackedConnector(store, Connector()), bindings=bindings)
    service = object.__new__(ResearchService)
    service.store, service.workflow = store, driver
    spec = {"objective": "Synthetic fold/quality/sequence-property identity integration", "approved": True, "steps": [
        {"step_id": "fold", "tool": "boltz2", "experiment_name": "Synthetic two poses", "candidate_ids": ["c1"], "expected_count": 2,
         "inputs": {"Protein_Sequences": ["AGCAAAAAAA"], "SMILES": ["CCO"]}},
        {"step_id": "quality", "tool": "mol_probity", "experiment_name": "Synthetic pose quality", "depends_on": ["fold"],
         "inputs": {"input_path": {"from_step": "fold", "artifact": "structures", "upload_as": "zip"},
                    "execution_mode": "validation", "quality_thresholds": {"max_clashscore": 10}}},
        {"step_id": "property", "tool": "netsolp", "experiment_name": "Synthetic passed-pose property", "depends_on": ["quality"],
         "selection": "passed", "required_gates": ["quality"],
         "inputs": {"input_path": {"from_step": "quality", "artifact": "sequences", "upload_as": "csv"}}},
    ]}
    workflow = driver.start_segment(campaign, spec)["workflow_id"]

    def run(step, path, bindings):
        receipt = service.next(campaign, "submit", workflow_id=workflow, step_id=step)
        call = receipt["call_id"]
        response = service.next(campaign, "poll", workflow_id=workflow, step_id=step, submission_call_id=call)
        driver.download(campaign, workflow, step, response["result"]["download_link"], tmp_path)
        result = service.next(campaign, "ingest", workflow_id=workflow, step_id=step, submission_call_id=call,
                              local_path=str(path), bindings=bindings)
        return result, call
    folded, fold_call = run("fold", fold, {name: {"parent_ids": ["c1"]} for name in ("pose_0", "pose_1")})
    pose_ids = driver.harness.status(workflow)["state"]["steps"]["fold"]["candidate_ids"]
    quality_zip(quality, pose_ids)
    measured, quality_call = run("quality", quality, {wid: {"candidate_id": wid} for wid in pose_ids})
    return service, campaign, workflow, measured, quality_call, pose_ids, properties, run, submitted


def test_different_poses_keep_separate_quality_results(pipeline):
    service, campaign, workflow, measured, call, ids, properties, run, submitted = pipeline
    observation = measured["observation"]
    assert observation["candidate_ids"] == ["c1"]
    assert observation["kind"] == "quality"
    scope = observation["coordinate_scope"]
    assert len(scope["structure_candidates"]) == 2
    assert set(scope["outcomes"].values()) == {"passed", "rejected"}
    assert len(observation["metrics"]["c1"]["by_structure"]) == 2
    assessments = service.store.status(campaign)["structure_assessments"]
    assert len(assessments) == 2 and {r["outcome"] for r in assessments} == {"passed", "rejected"}
    # Coordinate registration itself never becomes an unconditional pass.
    assert all(record["quality_validated"] is False for record in service.store.status(campaign)["structures"])


def test_rejected_pose_does_not_reappear_in_downstream_property_job(pipeline):
    service, campaign, workflow, measured, call, ids, properties, run, submitted = pipeline
    properties.write_text("seq_id,solubility\n" + ids[0] + ",0.8\n")
    result, property_call = run("property", properties, {ids[0]: {"candidate_id": ids[0]}})
    state = service.workflow.harness.status(workflow)["state"]
    assert state["steps"]["property"]["input_candidate_ids"] == [ids[0]]
    assert result["observation"]["candidate_ids"] == ["c1"]
    assert result["observation"]["kind"] == "solubility"
    assert result["observation"]["metrics"]["c1"]["solubility"] == "0.8"
    assert len(submitted) == 3


def test_metric_transfer_restarts_without_duplicate_observations(pipeline):
    service, campaign, workflow, measured, call, *_ = pipeline
    before = len(service.store.status(campaign)["observations"])
    result = service.next(campaign, "sync_metrics", workflow_id=workflow, step_id="quality", submission_call_id=call)
    assert result["observation"] == measured["observation"]
    assert len(service.store.status(campaign)["observations"]) == before


def test_coordinate_scope_cannot_invent_a_passing_other_pose(pipeline):
    service, campaign, workflow, measured, call, *_ = pipeline
    value = json.loads(json.dumps(measured["observation"]))
    sid = next(iter(value["coordinate_scope"]["structure_candidates"]))
    fake = "structure-unknown"
    value["coordinate_scope"]["structure_candidates"][fake] = value["coordinate_scope"]["structure_candidates"].pop(sid)
    value["coordinate_scope"]["outcomes"][fake] = value["coordinate_scope"]["outcomes"].pop(sid)
    value["metrics"]["c1"]["by_structure"][fake] = value["metrics"]["c1"]["by_structure"].pop(sid)
    value["observation_id"] = "fake-scoped-observation"
    with pytest.raises(ResearchError): service.store.add_observation(campaign, value)


def test_wrong_original_job_cannot_sync_quality_metrics(pipeline):
    service, campaign, workflow, measured, call, *_ = pipeline
    with pytest.raises(ResearchError):
        service.next(campaign, "sync_metrics", workflow_id=workflow, step_id="quality", submission_call_id="wrong-job")


def test_measurement_mode_cannot_claim_a_validation_pass(pipeline):
    service, campaign, workflow, measured, call, *_ = pipeline
    value = json.loads(json.dumps(measured["observation"]))
    value["coordinate_scope"]["execution_mode"] = "measurement_only"
    with pytest.raises(ResearchError): observation_record(value)


def test_scoped_measurement_cannot_overwrite_recorded_outcome(pipeline):
    service, campaign, workflow, measured, call, *_ = pipeline
    value = json.loads(json.dumps(measured["observation"]))
    sid = next(sid for sid, outcome in value["coordinate_scope"]["outcomes"].items() if outcome == "rejected")
    value["coordinate_scope"]["outcomes"][sid] = "passed"
    with pytest.raises(ResearchError, match="immutable"):
        service.store.add_observation(campaign, value)


@pytest.mark.parametrize("bad", [[], {}, None, 1])
def test_coordinate_candidate_type_has_clean_validation_error(pipeline, bad):
    service, campaign, workflow, measured, call, *_ = pipeline
    value = json.loads(json.dumps(measured["observation"]))
    sid = next(iter(value["coordinate_scope"]["structure_candidates"]))
    value["coordinate_scope"]["structure_candidates"][sid] = bad
    with pytest.raises(ResearchError, match="coordinate candidate_id"):
        observation_record(value)
