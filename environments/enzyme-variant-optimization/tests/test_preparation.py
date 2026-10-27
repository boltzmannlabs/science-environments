import csv
import json
from pathlib import Path
from types import SimpleNamespace
import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.preparation import prepare_input
from enzyme_research.workflow import load_workflow

from enzyme_research.paths import bundled_workflow_source


@pytest.fixture
def prepared(store, task, tmp_path):
    jobs = ["Cat_Pred", "Netsolp", "Protein_Structure_Prediction", "Solublempnn", "Thermal_MPNN", "Boltz2"]
    task["allowed_jobs"] = jobs
    campaign = store.start(task, "base")
    catalogue = tmp_path / "catalogue"
    catalogue.mkdir()
    (catalogue / "tool-contracts.v1.json").write_text(json.dumps({"tools": {
        name: {"job_name": name, "status": "active", "execution_blocked": False, "synthetic_fixture": True} for name in jobs}}))
    load_workflow(bundled_workflow_source())
    return SimpleNamespace(store=store, settings={"catalogue_root": str(catalogue)}), campaign


@pytest.mark.parametrize("job,field,headers", [("Cat_Pred", "input_path", ["Seq_id", "Sequences", "SMILES"]),
    ("Netsolp", "input_path", ["Sequence_ID", "Sequences"]), ("Protein_Structure_Prediction", "input_csv", ["seq_id", "sequences"])])
def test_labelled_csv_and_no_submission(prepared, job, field, headers):
    service, campaign = prepared
    result = prepare_input(service, campaign, job, ["parent"])
    assert result["input_field"] == field and result["jobs_submitted"] == 0
    with Path(result["path"]).open(newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == headers
        row = list(reader)[0]
        assert row["sequences" if job == "Protein_Structure_Prediction" else "Sequences"] == "AGAAAAAAAA"
        if job == "Cat_Pred":
            assert row["SMILES"] == "CCO"
    assert not service.store.status(campaign)["calls"]


def test_no_reordering_guess(prepared):
    service, campaign = prepared
    service.store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    result = prepare_input(service, campaign, "Cat_Pred", ["c1", "parent"])
    with Path(result["path"]).open(newline="") as handle:
        assert [r["Seq_id"] for r in csv.DictReader(handle)] == ["c1", "parent"]


def test_tampered_prepared_file_fails(prepared):
    service, campaign = prepared
    result = prepare_input(service, campaign, "Netsolp", ["parent"])
    Path(result["path"]).write_text("corrupt")
    with pytest.raises(ResearchError): prepare_input(service, campaign, "Netsolp", ["parent"])


def test_cannot_send_multiple_candidates_as_boltz_complex(prepared):
    service, campaign = prepared
    service.store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    with pytest.raises(ResearchError): prepare_input(service, campaign, "Boltz2", ["parent", "c1"])


def test_boltz_preparation_explicitly_supplies_empty_nonprotein_chains(prepared):
    service, campaign = prepared
    result = prepare_input(service, campaign, "Boltz2", ["parent"])
    assert result["experiment_data"] == {"Protein_Sequences": ["AGAAAAAAAA"],
        "DNA_Sequences": [], "RNA_Sequences": [], "SMILES": ["CCO"]}
    assert result["jobs_submitted"] == 0
    assert service.store.status(campaign)["calls"] == []


@pytest.mark.parametrize("ids", [[], ["unknown"], ["parent", "parent"]])
def test_invalid_candidate_selection(prepared, ids):
    service, campaign = prepared
    with pytest.raises(ResearchError): prepare_input(service, campaign, "Cat_Pred", ids)


def test_unknown_job_fails(prepared):
    service, campaign = prepared
    with pytest.raises(ResearchError): prepare_input(service, campaign, "Unapproved", ["parent"])


def test_zip_preparation_reproducible(prepared):
    service, campaign = prepared
    first = prepare_input(service, campaign, "Solublempnn", ["parent"])
    second = prepare_input(service, campaign, "Solublempnn", ["parent"])
    assert first["sha256"] == second["sha256"]


def test_no_parent_structure_reuse_for_mutant(prepared):
    service, campaign = prepared
    service.store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    with pytest.raises(ResearchError): prepare_input(service, campaign, "Thermal_MPNN", ["c1"])
