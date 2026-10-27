"""Prepare actual source bytes for single-structure tools without remote calls."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from enzyme_research.connector import TrackedConnector
from enzyme_research.contracts import ResearchError
from enzyme_research.paths import bundled_workflow_source
from enzyme_research.preparation import prepare_input, upload_input
from enzyme_research.request_scope import validate_request_scope
from enzyme_research.workflow import load_workflow
from test_structure_handoff import cif_from_fixture_pdb

JOBS = ("enzycontrol", "deepallo", "Enzyme_RFD3")


@pytest.fixture
def single_input(store, task, tmp_path, request):
    load_workflow(bundled_workflow_source())
    options = getattr(request, "param", {})
    source = Path(task["parent"]["structure"]["path"])
    content = source.read_text()
    if options.get("backbone"):
        content = "\n".join(line for line in content.splitlines() if line[12:16].strip() == "CA") + "\nEND\n"
    else:
        content = content.replace("END\n", "HETATM 1001   C1 LIG Z 501       1.000   1.000   1.000  1.00 20.00           C\nEND\n")
    extension = options.get("format", "pdb")
    if extension != "pdb":
        content = cif_from_fixture_pdb(content)
        source = source.with_suffix("." + extension)
    source.write_text(content)
    task["parent"]["structure"] = {"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    task["allowed_jobs"] = list(JOBS)
    task["evidence_track"] = options.get("evidence_track", "synthetic")
    campaign = store.start(task, "base")
    catalogue = tmp_path / "catalogue"
    catalogue.mkdir()
    (catalogue / "tool-contracts.v1.json").write_text(json.dumps({"tools": {
        job: {"job_name": job, "status": "active", "execution_blocked": False} for job in JOBS}}))
    return SimpleNamespace(store=store, settings={"catalogue_root": str(catalogue)}), campaign, source


@pytest.mark.parametrize("job,field", [("enzycontrol", "pdb_path"), ("deepallo", "input_path"), ("Enzyme_RFD3", "input_path")])
def test_single_pdb_preserves_sequence_ligand_and_author_labels(single_input, job, field):
    service, campaign, source = single_input
    result = prepare_input(service, campaign, job, ["parent"])
    assert result["input_field"] == field
    assert Path(result["path"]).suffix == ".pdb"
    assert Path(result["path"]).read_bytes() == source.read_bytes()
    assert result["residue_mappings"]["parent"]["A2"]["residue_number"] == 2
    assert result["structure_ids"]["parent"].startswith("supplied-")
    assert result["jobs_submitted"] == 0 and service.store.status(campaign)["calls"] == []
    assert prepare_input(service, campaign, job, ["parent"]) == result


@pytest.mark.parametrize("single_input", [{"format": "cif"}], indirect=True)
def test_rfd3_cif_is_not_renamed_or_stripped(single_input):
    service, campaign, source = single_input
    result = prepare_input(service, campaign, "Enzyme_RFD3", ["parent"])
    assert Path(result["path"]).suffix == ".cif"
    assert Path(result["path"]).read_bytes() == source.read_bytes()


@pytest.mark.parametrize("single_input", [{"format": "cif"}], indirect=True)
@pytest.mark.parametrize("job", ["enzycontrol", "deepallo"])
def test_pdb_only_tools_do_not_silently_convert_complexes(single_input, job):
    service, campaign, _ = single_input
    with pytest.raises(ResearchError, match="requires .pdb coordinates"):
        prepare_input(service, campaign, job, ["parent"])
    assert not service.store.status(campaign)["calls"]


@pytest.mark.parametrize("single_input", [{"format": "mmcif"}], indirect=True)
def test_rfd3_rejects_an_unsupported_storage_suffix(single_input):
    service, campaign, _ = single_input
    with pytest.raises(ResearchError, match="requires .cif, .pdb"):
        prepare_input(service, campaign, "Enzyme_RFD3", ["parent"])


@pytest.mark.parametrize("job", JOBS)
def test_multiple_candidates_cannot_be_sent_as_one_complex(single_input, job):
    service, campaign, _ = single_input
    service.store.add_candidates(campaign, [{"candidate_id": "child", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    with pytest.raises(ResearchError, match="one candidate structure"):
        prepare_input(service, campaign, job, ["parent", "child"])


@pytest.mark.parametrize("single_input", [{"backbone": True}], indirect=True)
def test_deepallo_still_requires_all_atom_coordinates(single_input):
    service, campaign, _ = single_input
    with pytest.raises(ResearchError, match="all_atom"):
        prepare_input(service, campaign, "deepallo", ["parent"])


@pytest.mark.parametrize("job", JOBS)
def test_upload_returns_the_correct_file_field(single_input, job):
    service, campaign, _ = single_input
    prepared = prepare_input(service, campaign, job, ["parent"])
    calls = []
    class Connector:
        def call(self, name, args):
            calls.append((name, args))
            assert name == "boltzmann_upload"
            return {"s3_path": "users/fixture/structure.pdb", "sha256": hashlib.sha256(Path(args["local_path"]).read_bytes()).hexdigest()}
    service.connector = TrackedConnector(service.store, Connector())
    result = upload_input(service, campaign, prepared["input_id"], {"seed": 123})
    assert result["experiment_data"][prepared["input_field"]] == "users/fixture/structure.pdb"
    assert result["experiment_data"]["seed"] == 123
    assert len(calls) == 1 and result["jobs_submitted"] == 0


@pytest.mark.parametrize("job", JOBS)
def test_changed_parent_coordinates_are_rejected(single_input, job):
    service, campaign, source = single_input
    source.write_text(source.read_text() + "REMARK changed\n")
    with pytest.raises(ResearchError, match="Frozen parent structure changed"):
        prepare_input(service, campaign, job, ["parent"])


@pytest.mark.parametrize("job", ["enzycontrol", "Enzyme_RFD3"])
@pytest.mark.parametrize("count", [0, -1, True, "2", 7])
def test_scaffold_count_respects_candidate_budget(store, campaign, job, count):
    with pytest.raises(ResearchError, match="remaining candidate allocation"):
        validate_request_scope(store.status(campaign), job, {"n_samples": count, "smiles": "CCO"}, ["parent"])


@pytest.mark.parametrize("job", ["enzycontrol", "Enzyme_RFD3"])
def test_scaffold_default_is_one_candidate(store, campaign, job):
    validate_request_scope(store.status(campaign), job, {"smiles": "CCO"}, ["parent"])


def test_scaffold_substrate_cannot_change_silently(store, campaign):
    with pytest.raises(ResearchError, match="declared substrate"):
        validate_request_scope(store.status(campaign), "enzycontrol", {"smiles": "CCN"}, ["parent"])


@pytest.mark.parametrize("job,field", [("enzycontrol", "pdb_path"), ("Enzyme_RFD3", "input_path")])
@pytest.mark.parametrize("single_input", [{"evidence_track": "computational"}], indirect=True)
def test_live_scaffold_request_needs_its_own_upload(single_input, job, field):
    service, campaign, _ = single_input
    data = {field: "users/fixture/structure.pdb", "n_samples": 1, "smiles": "CCO"}
    with pytest.raises(ResearchError, match="prepared/uploaded"):
        validate_request_scope(service.store.status(campaign), job, data, ["parent"])
    with service.store.transaction() as db:
        service.store.event(db, campaign, "input_uploaded", {"job_name": job, "input_field": field,
            "storage_path": data[field], "candidate_ids": ["parent"]})
    validate_request_scope(service.store.status(campaign), job, data, ["parent"])
