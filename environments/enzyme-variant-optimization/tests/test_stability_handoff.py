import csv
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import zipfile

import pytest

from enzyme_research.connector import TrackedConnector
from enzyme_research.contracts import AMINO_ACIDS, ResearchError
from enzyme_research.preparation import prepare_input, upload_input
from enzyme_research.results import sync_metrics
from enzyme_research.stability import input_layout, lookup_single_mutation, match_candidates, parse_output, validate_context
from enzyme_research.workflow import WorkflowExecutor, load_workflow
from test_structure_handoff import pdb
from test_workflow_bridge import fixture_module

from enzyme_research.paths import bundled_workflow_source
WORKFLOW = bundled_workflow_source()


def table(layouts):
    rows = []
    for cid, layout in layouts.items():
        for p in layout["positions"]:
            for aa in sorted(AMINO_ACIDS):
                rows.append({"Model": "ThermoMPNN", "Dataset": cid, "ddG_pred": "-0.75",
                    "position": str(p["model_position"]), "wildtype": p["wildtype"], "mutation": aa,
                    # Upstream .strip('.pdb') changes "parent" to "arent".
                    "pdb": cid.strip(".pdb"), "chain": layout["chain"]})
    return rows


def write_csv(path, rows):
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, ["Model", "Dataset", "ddG_pred", "position", "wildtype", "mutation", "pdb", "chain"])
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(text.getvalue())
    return path


@pytest.fixture
def layout():
    load_workflow(WORKFLOW)
    return input_layout(pdb("AGAAAAAAAA", chain="A", start=101, ligand=False).encode(), "AGAAAAAAAA")


def test_actual_auth_number_is_not_model_index(layout, tmp_path):
    output = write_csv(tmp_path / "output.csv", list(reversed(table({"parent": layout}))))
    result = parse_output(output, {"parent": layout})["parent"]
    assert len(result["predictions"]) == 200
    first = result["predictions"][0]
    assert (first["model_position"], first["sequence_position"], first["residue_number"]) == (0, 1, 101)
    assert result["absolute_stability_or_Tm"] == "not_predicted"
    assert result["multi_mutation_aggregation"] == "unsupported"
    hit = lookup_single_mutation(result, "AGAAAAAAAA", "AGCAAAAAAA")
    assert hit["sequence_mutation"] == "A3C" and hit["residue_number"] == 103 and hit["ddG_pred"] == -0.75


def test_numbering_gap_gets_a_model_slot_not_a_sequence_residue(tmp_path):
    load_workflow(WORKFLOW)
    content = pdb("AGAAAAAAA", chain="A", start=102, ligand=False)
    first = pdb("A", chain="A", start=100, ligand=False).split("END")[0]
    current = input_layout((first + content).encode(), "AAGAAAAAAA")
    assert [p["model_position"] for p in current["positions"]] == [0, *range(2, 11)]
    output = write_csv(tmp_path / "gaps.csv", table({"parent": current}))
    assert len(parse_output(output, {"parent": current})["parent"]["predictions"]) == 200


@pytest.mark.parametrize("change", ["insertion", "missing_O", "out_of_order", "huge_gap", "mse", "alternate"])
def test_ambiguous_or_masked_input_is_rejected(change):
    load_workflow(WORKFLOW)
    lines = pdb("AGAAAAAAAA", chain="A", start=101, ligand=False).splitlines()
    if change == "insertion": lines[0] = lines[0][:26] + "A" + lines[0][27:]
    if change == "missing_O": lines = [line for line in lines if line[12:16].strip() != "O"]
    if change == "out_of_order": lines = [line[:22] + f"{202-int(line[22:26]):4d}" + line[26:] if line.startswith("ATOM") else line for line in lines]
    if change == "huge_gap": lines[-2] = lines[-2][:22] + "9999" + lines[-2][26:]
    if change == "mse": lines.append("HETATM    1   CA MSE A 111       0.000   0.000   0.000  1.00 20.00           C")
    if change == "alternate": lines[0] = lines[0][:16] + "A" + lines[0][17:]
    with pytest.raises(ValueError): input_layout(("\n".join(lines) + "\n").encode(), "AGAAAAAAAA")


@pytest.mark.parametrize("field,value", [("Dataset", "unknown"), ("Model", "Other"), ("chain", "B"),
    ("wildtype", "C"), ("mutation", "X"), ("position", "101"), ("position", "0.5"),
    ("position", "1e9999999"), ("position", "NaN"), ("ddG_pred", "inf"), ("ddG_pred", "oops")])
def test_invalid_grid_rows_fail_cleanly(layout, tmp_path, field, value):
    rows = table({"parent": layout})
    rows[0][field] = value
    output = write_csv(tmp_path / "bad.csv", rows)
    with pytest.raises(ResearchError): parse_output(output, {"parent": layout})


@pytest.mark.parametrize("alter", ["partial", "duplicate", "empty", "wrong_header"])
def test_partial_and_empty_output_never_succeed(layout, tmp_path, alter):
    rows = table({"parent": layout})
    if alter == "partial": rows.pop()
    if alter == "duplicate": rows.append(rows[0])
    if alter == "empty": rows = []
    output = write_csv(tmp_path / "bad.csv", rows)
    if alter == "wrong_header": output.write_text("sequence,prediction\nAAAA,-1\n")
    with pytest.raises(ValueError): parse_output(output, {"parent": layout})


def test_optional_blank_chain_matches_first_file_chain(layout):
    for data in ({}, {"chain": ""}, {"chain": "A"}, {"chain": None}): validate_context({"parent": layout}, data)
    for data in ({"chain": "B"}, {"chain": 1}, {"model_path": "placeholder.pt"}, {"model_path": {}}):
        with pytest.raises(ResearchError): validate_context({"parent": layout}, data)


def test_first_file_hetero_chain_is_not_silently_selected():
    load_workflow(WORKFLOW)
    content = pdb("AGAAAAAAAA", chain="A", start=101)
    lines = content.splitlines()
    content = "\n".join([lines[-2], *lines[:-2], "END"]) + "\n"
    current = input_layout(content.encode(), "AGAAAAAAAA")
    with pytest.raises(ResearchError): validate_context({"parent": current}, {})
    validate_context({"parent": current}, {"chain": "A"})


def test_no_absolute_parent_or_additive_multimutant_score(layout, tmp_path):
    output = write_csv(tmp_path / "grid.csv", table({"parent": layout}))
    matrix = parse_output(output, {"parent": layout})["parent"]
    for target in ("AGAAAAAAAA", "AGCCAAAAAA", "AGAAAAAAAAA"):
        with pytest.raises(ResearchError): lookup_single_mutation(matrix, "AGAAAAAAAA", target)
    with pytest.raises(ResearchError): lookup_single_mutation(matrix, "AGCAAAAAAA", "AGCCAAAAAA")


@pytest.fixture
def handoff(store, task, tmp_path):
    load_workflow(WORKFLOW)
    catalogue, bindings = fixture_module().fixture_catalogue(tmp_path)
    contract = catalogue / "tool-contracts.v1.json"
    data = json.loads(contract.read_bytes())
    data["tools"]["Thermal_MPNN"] = {"job_name": "Thermal_MPNN", "status": "active", "execution_blocked": False,
        "submission": {"wire_job_name": "Thermal_MPNN"}, "diagnostics": []}
    contract.write_text(json.dumps(data))
    task["allowed_jobs"] = ["Thermal_MPNN"]
    campaign = store.start(task, "base")
    output = tmp_path / "raw.zip"

    class Remote:
        def __init__(self): self.calls = []
        def call(self, name, args):
            self.calls.append((name, args))
            if name == "boltzmann_upload": return {"s3_path": "users/fixture/stability.zip",
                "sha256": hashlib.sha256(Path(args["local_path"]).read_bytes()).hexdigest()}
            if name == "boltzmann_submit": return {"job_name": "Thermal_MPNN", "doc_id": "synthetic-stability-job"}
            if name == "boltzmann_status": return {"status": "completed", "download_link": "https://offline.invalid/raw.zip"}
            if name == "boltzmann_download": return {"output_paths": [str(output)], "errors": []}
            raise AssertionError(name)

    remote = Remote()
    connector = TrackedConnector(store, remote)
    driver = WorkflowExecutor(store, WORKFLOW, catalogue, connector, bindings=bindings)
    service = SimpleNamespace(store=store, workflow=driver, connector=connector, settings={"catalogue_root": str(catalogue)})
    prepared = prepare_input(service, campaign, "Thermal_MPNN", ["parent"])
    grid = tmp_path / "ThermoMPNN_inference_parent.csv"
    write_csv(grid, table(prepared["stability_layouts"]))
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("results/" + grid.name, grid.read_bytes())
    uploaded = upload_input(service, campaign, prepared["input_id"], {"chain": "A"})
    spec = {"objective": "Synthetic complete ThermoMPNN handoff", "approved": True, "steps": [{
        "step_id": "stability", "tool": "thermompnn", "experiment_name": "Synthetic saturation matrix",
        "candidate_ids": ["parent"], "inputs": uploaded["experiment_data"]}]}
    workflow = driver.start_segment(campaign, spec)["workflow_id"]
    return service, campaign, workflow, prepared, output, remote


def complete_remote(service, campaign, workflow, output, *, download=True):
    submitted = service.workflow.submit(campaign, workflow, "stability")
    response = service.workflow.poll(campaign, workflow, "stability", submitted["call_id"])
    if download: service.workflow.download(campaign, workflow, "stability", response["result"]["download_link"], output.parent)
    return submitted["call_id"]


def test_complete_original_receipts_matrix_and_resumable_observation(handoff):
    service, campaign, workflow, prepared, output, remote = handoff
    metadata = service.workflow.harness.registry["thermompnn"]
    assert metadata["backend_status"] == "active" and metadata["binding_source"] == "catalogue"
    call = complete_remote(service, campaign, workflow, output)
    result = service.workflow.ingest(campaign, workflow, "stability", output)
    assert result["candidate_ids"] == ["parent"]
    first = sync_metrics(service, campaign, workflow, "stability", call)
    assert sync_metrics(service, campaign, workflow, "stability", call) == first
    observation = first["observation"]
    assert observation["kind"] == "stability" and observation["evidence_level"] == "synthetic_fixture"
    sid = prepared["structure_ids"]["parent"]
    assert len(observation["metrics"]["parent"]["by_structure"][sid]["predictions"]) == 200
    assert observation["artifacts"][0]["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    with pytest.raises(ResearchError): sync_metrics(service, campaign, workflow, "stability", call, "activity")
    assert len([c for c in service.store.status(campaign)["calls"] if c["tool"] == "boltzmann_submit"]) == 1


def test_unreceipted_matrix_is_not_ingested(handoff):
    service, campaign, workflow, prepared, output, remote = handoff
    complete_remote(service, campaign, workflow, output, download=False)
    with pytest.raises(ResearchError): service.workflow.ingest(campaign, workflow, "stability", output)
    assert service.workflow.harness.status(workflow)["state"]["steps"]["stability"]["status"] == "remote_completed"


def test_changed_uploaded_structure_stops_before_scientific_submit(handoff):
    service, campaign, workflow, prepared, output, remote = handoff
    Path(prepared["path"]).write_bytes(b"changed")
    with pytest.raises(ResearchError): service.workflow.submit(campaign, workflow, "stability")
    assert not any(name == "boltzmann_submit" for name, _ in remote.calls)


def test_arbitrary_storage_reference_is_not_candidate_provenance(handoff):
    service, campaign, workflow, prepared, output, remote = handoff
    spec = service.workflow.harness.status(workflow)["spec"]
    spec["steps"][0]["inputs"]["zip_path"] = "users/someone/unrelated.zip"
    spec["steps"][0]["experiment_name"] = "Synthetic unrelated storage request"
    workflow = service.workflow.start_segment(campaign, spec)["workflow_id"]
    with pytest.raises(ResearchError): service.workflow.submit(campaign, workflow, "stability")
    assert not any(name == "boltzmann_submit" for name, _ in remote.calls)


def test_partial_result_rolls_back_workflow_status(handoff, tmp_path):
    service, campaign, workflow, prepared, output, remote = handoff
    rows = table(prepared["stability_layouts"])
    raw = write_csv(tmp_path / "partial.csv", rows[:-1]).read_bytes()
    with zipfile.ZipFile(output, "w") as archive: archive.writestr("partial.csv", raw)
    call = complete_remote(service, campaign, workflow, output)
    with pytest.raises(ResearchError): service.workflow.ingest(campaign, workflow, "stability", output)
    assert not service.store.status(campaign)["observations"]
    assert service.workflow.harness.status(workflow)["state"]["steps"]["stability"]["status"] == "remote_completed"


def complete_matrix(handoff):
    service, campaign, workflow, prepared, output, remote = handoff
    call = complete_remote(service, campaign, workflow, output)
    service.workflow.ingest(campaign, workflow, "stability", output)
    source = sync_metrics(service, campaign, workflow, "stability", call)["observation"]
    service.store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"},
        {"candidate_id": "c2", "parent_id": "parent", "sequence": "AGCCAAAAAA"}])
    return service, campaign, prepared["structure_ids"]["parent"], source


def test_single_mutant_observation_retains_exact_basis_and_reuses_receipt(handoff):
    service, campaign, sid, source = complete_matrix(handoff)
    result = match_candidates(service, campaign, source["observation_id"], "parent", sid, ["c1"])
    assert match_candidates(service, campaign, source["observation_id"], "parent", sid, ["c1"]) == result
    observation = result["observation"]
    value = observation["metrics"]["c1"]
    assert value["basis_candidate_id"] == "parent" and value["basis_structure_id"] == sid
    assert value["sequence_mutation"] == "A3C" and value["ddG_pred"] == -0.75
    assert observation["source_call_id"] == source["source_call_id"]
    assert observation["artifacts"] == source["artifacts"]
    assert len(service.store.status(campaign)["observations"]) == 2


@pytest.mark.parametrize("targets", [["c1", "c2"], ["parent"], ["c1", "c1"], ["unknown"], []])
def test_unsupported_target_set_is_not_a_partial_success(handoff, targets):
    service, campaign, sid, source = complete_matrix(handoff)
    with pytest.raises(ResearchError): match_candidates(service, campaign, source["observation_id"], "parent", sid, targets)
    assert len(service.store.status(campaign)["observations"]) == 1


def test_score_cannot_be_taken_from_another_pose_or_changed_artifact(handoff):
    service, campaign, sid, source = complete_matrix(handoff)
    with pytest.raises(ResearchError): match_candidates(service, campaign, source["observation_id"], "parent", "other-pose", ["c1"])
    Path(source["artifacts"][0]["path"]).write_bytes(b"changed source")
    with pytest.raises(ResearchError): match_candidates(service, campaign, source["observation_id"], "parent", sid, ["c1"])


def test_multiple_input_tables_are_joined_by_dataset_not_file_order(layout, tmp_path):
    second = input_layout(pdb("AGCAAAAAAA", chain="B", start=205, ligand=False).encode(), "AGCAAAAAAA")
    layouts = {"parent": layout, "variant": second}
    output = tmp_path / "two.zip"
    with zipfile.ZipFile(output, "w") as archive:
        for cid in reversed(layouts):
            path = write_csv(tmp_path / (cid + ".csv"), table({cid: layouts[cid]}))
            archive.writestr("results/" + path.name, path.read_bytes())
    parsed = parse_output(output, layouts)
    assert parsed["variant"]["input_layout"]["chain"] == "B"
    assert parsed["variant"]["predictions"][0]["residue_number"] == 205
    with pytest.raises(ResearchError): parse_output(output, layouts, member="results/parent.csv")


def test_native_service_ingest_and_match_actions(handoff):
    from enzyme_research.service import ResearchService
    service, campaign, workflow, prepared, output, remote = handoff
    call = complete_remote(service, campaign, workflow, output)
    result = ResearchService.next(service, campaign, "ingest", workflow_id=workflow, step_id="stability",
                                  submission_call_id=call, local_path=str(output))
    source = result["observation"]
    assert source["kind"] == "stability"
    service.store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    scored = ResearchService.next(service, campaign, "match_stability", observation_id=source["observation_id"],
        basis_candidate_id="parent", structure_id=prepared["structure_ids"]["parent"], target_candidate_ids=["c1"])
    assert scored["observation"]["candidate_ids"] == ["c1"]


def test_oversized_matrix_is_refused_before_result_expansion(layout):
    layouts = {str(i): {**layout, "positions": layout["positions"] * 501} for i in range(2)}
    with pytest.raises(ResearchError): validate_context(layouts, {"chain": "A"})


@pytest.mark.parametrize("binding", [{"job_name": "Other"}, {"backend_status": "active"},
    {"contract_ref": {"path": "tool-contracts.v1.json", "entry": "Other"}}])
def test_stability_routing_cannot_be_replaced_with_an_unrelated_tool(handoff, binding):
    service, campaign, workflow, prepared, output, remote = handoff
    from enzyme_research.stability_workflow import catalogue_extension
    with pytest.raises(ResearchError): catalogue_extension(service.settings["catalogue_root"], {"thermompnn": binding})


def test_pending_canonical_tool_is_not_force_activated(handoff):
    service, campaign, workflow, prepared, output, remote = handoff
    contract = Path(service.settings["catalogue_root"]) / "tool-contracts.v1.json"
    value = json.loads(contract.read_bytes())
    value["tools"]["Thermal_MPNN"]["status"] = "pending"
    contract.write_text(json.dumps(value))
    other = contract.parent.parent / "other"
    other.mkdir()
    driver = WorkflowExecutor(service.store, WORKFLOW, contract.parent, service.connector,
                              bindings=fixture_module().fixture_catalogue(other)[1])
    assert driver.harness.registry["thermompnn"]["backend_status"] == "pending"
