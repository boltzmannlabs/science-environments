"""Offline canonical input regressions; no model or scientific service calls."""
import csv
import hashlib
from itertools import islice, product
import json
from pathlib import Path
from types import SimpleNamespace
import zipfile

import pytest

from enzyme_research.contracts import ResearchError, digest
from enzyme_research.ligands import verify_ligand
from enzyme_research.preparation import prepare_input
from enzyme_research.structures import coordinate_metadata
from enzyme_research.workflow import load_workflow
from test_ligand_identity import molecule
from test_structure_handoff import cif_from_fixture_pdb


from enzyme_research.paths import bundled_workflow_source
JOBS = ["Cat_Pred", "Netsolp", "Mol_Probity", "Catalytic_Geometry"]


@pytest.fixture
def canonical_preparation(store, task, tmp_path, request):
    load_workflow(bundled_workflow_source())
    options = getattr(request, "param", {})
    source = Path(task["parent"]["structure"]["path"])
    content = source.read_text()
    if options.get("backbone"):
        content = "\n".join(line for line in content.splitlines()
                            if line.startswith("ATOM  ") and line[12:16].strip() == "CA") + "\nEND\n"
    if options.get("ligand"):
        content = content.replace("END\n", "HETATM 1001   C1 LIG Z 501       1.000   1.000   1.000  1.00 20.00           C\nEND\n")
    extension = options.get("format", "pdb")
    if extension != "pdb":
        content = cif_from_fixture_pdb(content)
        source = source.with_suffix("." + extension)
    source.write_text(content)
    task["parent"]["structure"] = {"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    task["allowed_jobs"] = JOBS.copy()
    task["budget"]["max_unique_candidates"] = 59
    task["substrate"]["smiles"] = options.get("smiles", "[NH3+][C@@H](Cc1ccccc1)C(=O)[O-]")
    campaign = store.start(task, "base")
    catalogue = tmp_path / "catalogue"
    catalogue.mkdir()
    # Only the active-contract gate is needed by this local preparation seam.
    (catalogue / "tool-contracts.v1.json").write_text(json.dumps({"tools": {
        job: {"job_name": job, "status": "active", "execution_blocked": False,
              "synthetic_fixture": True} for job in JOBS}}))
    return SimpleNamespace(store=store, settings={"catalogue_root": str(catalogue)}), campaign


def library_with_parent(service, campaign):
    """Sixty distinct parser-fixture sequences, never experimental data."""
    sequences = ("AG" + "".join(pair) + "AAAAAA"
                 for pair in product("ACDEFGHIKLMNPQRSTVWY", repeat=2)
                 if pair != ("A", "A"))
    variants = [{"candidate_id": f"variant_{number}", "parent_id": "parent", "sequence": sequence}
                for number, sequence in enumerate(islice(sequences, 59), 1)]
    service.store.add_candidates(campaign, variants)
    # Deliberately do not sort candidate IDs or put the parent first.
    return [item["candidate_id"] for item in reversed(variants)] + ["parent"]


def test_catpred_default_uses_canonical_headers_and_exact_sixty_pairs(canonical_preparation):
    service, campaign = canonical_preparation
    candidate_ids = library_with_parent(service, campaign)
    before = service.store.status(campaign)
    candidates = {item["candidate_id"]: item for item in before["candidates"]}
    prepared = prepare_input(service, campaign, "Cat_Pred", candidate_ids)
    with Path(prepared["path"]).open(newline="") as handle:
        reader = csv.reader(handle)
        assert next(reader) == ["Seq_id", "Sequences", "SMILES"]
        rows = list(reader)
    assert len(rows) == 60
    assert rows == [[cid, candidates[cid]["sequence"], before["task"]["substrate"]["smiles"]]
                    for cid in candidate_ids]
    assert prepared["input_field"] == "input_path"
    assert prepared["candidate_ids"] == candidate_ids
    assert not prepared["uploaded"] and prepared["jobs_submitted"] == 0
    assert prepare_input(service, campaign, "Cat_Pred", candidate_ids) == prepared
    after = service.store.status(campaign)
    assert after["candidates"] == before["candidates"]
    assert after["task"] == before["task"]
    assert after["calls"] == []


@pytest.mark.parametrize("canonical_preparation", [{"format": fmt} for fmt in ("pdb", "cif", "mmcif")], indirect=True)
def test_molprobity_canonical_job_preserves_selected_all_atom_coordinates(canonical_preparation):
    service, campaign = canonical_preparation
    state = service.store.status(campaign)
    source = state["task"]["parent"]["structure"]
    path = Path(source["path"])
    content = path.read_bytes()
    structure_id = "supplied-" + source["sha256"][:20]
    prepared = prepare_input(service, campaign, "Mol_Probity", ["parent"],
                             structure_ids={"parent": structure_id})
    assert prepared["job_name"] == "Mol_Probity" and prepared["input_field"] == "input_path"
    assert prepared["structure_ids"] == {"parent": structure_id}
    assert prepared["residue_mappings"] == {"parent": {"A2": {
        "chain_id": "A", "residue_number": 2, "insertion_code": ""}}}
    with zipfile.ZipFile(prepared["path"]) as archive:
        assert archive.namelist() == ["parent" + path.suffix]
        assert archive.read("parent" + path.suffix) == content
    assert path.read_bytes() == content
    assert "protein_projections" not in prepared and "experiment_data" not in prepared
    assert not prepared["uploaded"] and prepared["jobs_submitted"] == 0
    assert prepare_input(service, campaign, "Mol_Probity", ["parent"],
                         structure_ids={"parent": structure_id}) == prepared
    assert service.store.status(campaign)["calls"] == []


@pytest.mark.parametrize("format", ["pdb", "cif", "mmcif"])
def test_geometry_canonical_job_preserves_verified_coordinates_without_inventing_context(
        canonical_preparation, molecule, tmp_path, format):
    service, campaign = canonical_preparation
    # The molecule fixture is CCO; use its matching isomeric graph, not the
    # different case/stereochemistry-preservation substrate of the CSV tests.
    task = service.store.status(campaign)["task"]
    task["substrate"]["smiles"] = "CCO"
    task["allowed_jobs"].append("SyntheticFixtureOnly")
    campaign = service.store.start(task, "base")
    service.store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    content, sdf = molecule()
    if format != "pdb":
        content = cif_from_fixture_pdb(content.decode()).encode()
    member = "pose." + format
    artifact = tmp_path / "explicitly_synthetic_complex.zip"
    with zipfile.ZipFile(artifact, "w") as archive:
        archive.writestr(member, content)
        archive.writestr("ligand.sdf", sdf)
    # Local provenance fixture only: no connector is constructed or invoked.
    call = service.store.prepare_call(campaign, "boltzmann_submit", {
        "job_name": "SyntheticFixtureOnly", "experiment_data": {"synthetic_fixture": True}})
    service.store.call_transition(campaign, call, "sending")
    service.store.call_transition(campaign, call, "completed", {"synthetic_fixture": True})
    state = service.store.status(campaign)
    candidate = next(item for item in state["candidates"] if item["candidate_id"] == "c1")
    from enzyme_workflow.artifacts import inspect_structure
    record = {"structure_id": "synthetic-complex", "candidate_id": "c1",
              "sequence_sha256": candidate["sequence_sha256"],
              "artifact": {"path": str(artifact), "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                           "member": member, "member_sha256": hashlib.sha256(content).hexdigest()},
              "source": {"source_call_id": call},
              **coordinate_metadata(inspect_structure(member, content), task, candidate)}
    service.store.add_structure_version(campaign, record)
    verify_ligand(service, campaign, "c1", record["structure_id"], "ligand.sdf",
                  {"chain_id": "Z", "residue_number": 501, "component_id": "LIG"})
    before = service.store.status(campaign)
    prepared = prepare_input(service, campaign, "Catalytic_Geometry", ["c1"],
                             structure_ids={"c1": record["structure_id"]})
    assert prepared["job_name"] == "Catalytic_Geometry" and prepared["input_field"] == "input_path"
    assert prepared["contract_sha256"] == digest(json.loads(
        (Path(service.settings["catalogue_root"]) / "tool-contracts.v1.json").read_bytes())["tools"]["Catalytic_Geometry"])
    assert prepared["structure_ids"] == {"c1": record["structure_id"]}
    assert prepared["residue_mappings"] == {"c1": record["mapping"]}
    assert prepared["ligand_verifications"]["c1"]["structure_id"] == record["structure_id"]
    with zipfile.ZipFile(prepared["path"]) as archive:
        assert archive.namelist() == ["c1." + format]
        assert archive.read("c1." + format) == content
    assert not {"reaction_template", "template_binding", "mapping_path", "experiment_data"} & prepared.keys()
    assert not prepared["uploaded"] and prepared["jobs_submitted"] == 0
    assert service.store.status(campaign)["calls"] == before["calls"]


def test_netsolp_default_uses_only_its_canonical_sequence_columns(canonical_preparation):
    service, campaign = canonical_preparation
    candidate_ids = library_with_parent(service, campaign)
    state = service.store.status(campaign)
    candidates = {item["candidate_id"]: item for item in state["candidates"]}
    prepared = prepare_input(service, campaign, "Netsolp", candidate_ids)
    with Path(prepared["path"]).open(newline="") as handle:
        reader = csv.reader(handle)
        assert next(reader) == ["Sequence_ID", "Sequences"]
        rows = list(reader)
    assert len(rows) == 60
    assert rows == [[cid, candidates[cid]["sequence"]] for cid in candidate_ids]
    assert prepared["input_field"] == "input_path"
    assert prepare_input(service, campaign, "Netsolp", candidate_ids) == prepared
    assert service.store.status(campaign)["calls"] == []


def test_catpred_new_layout_does_not_reuse_or_rewrite_legacy_cache(canonical_preparation):
    service, campaign = canonical_preparation
    state = service.store.status(campaign)
    entry = json.loads((Path(service.settings["catalogue_root"]) / "tool-contracts.v1.json").read_bytes())["tools"]["Cat_Pred"]
    old_id = digest({"job_name": "Cat_Pred", "candidate_ids": ["parent"],
                     "sequence_sha256": [state["candidates"][0]["sequence_sha256"]],
                     "substrate": state["task"]["substrate"], "structure_ids": {}, "contract_sha256": digest(entry)})
    old_path = service.store.root / campaign / "inputs" / (old_id + ".csv")
    old_path.parent.mkdir(parents=True)
    original = ("seq_id,sequences,smiles\r\nparent,AGAAAAAAAA," + state["task"]["substrate"]["smiles"] + "\r\n").encode()
    old_path.write_bytes(original)
    prepared = prepare_input(service, campaign, "Cat_Pred", ["parent"])
    assert prepared["input_id"] != old_id and Path(prepared["path"]) != old_path
    assert old_path.read_bytes() == original


@pytest.mark.parametrize("canonical_preparation", [{"smiles": "C C"}], indirect=True)
def test_catpred_canonical_serialization_keeps_existing_pair_validation(canonical_preparation):
    service, campaign = canonical_preparation
    from enzyme_workflow.common import WorkflowError
    with pytest.raises(WorkflowError, match="without whitespace"):
        prepare_input(service, campaign, "Cat_Pred", ["parent"])
    state = service.store.status(campaign)
    assert not any(event["payload"]["event"] == "input_prepared" for event in state["events"])
    assert state["calls"] == []


@pytest.mark.parametrize("canonical_preparation", [{"backbone": True}], indirect=True)
@pytest.mark.parametrize("job", ["Mol_Probity", "Catalytic_Geometry"])
def test_canonical_structural_jobs_reject_incomplete_atoms(canonical_preparation, job):
    service, campaign = canonical_preparation
    with pytest.raises(ResearchError, match="need .*all_atom"):
        prepare_input(service, campaign, job, ["parent"])
    assert service.store.status(campaign)["calls"] == []


@pytest.mark.parametrize("canonical_preparation", [{}, {"ligand": True}], indirect=True)
def test_geometry_needs_verified_substrate_not_merely_a_detected_ligand(canonical_preparation):
    service, campaign = canonical_preparation
    with pytest.raises(ResearchError, match="need ligand"):
        prepare_input(service, campaign, "Catalytic_Geometry", ["parent"])
    assert service.store.status(campaign)["calls"] == []


@pytest.mark.parametrize("job", ["Mol_Probity", "Catalytic_Geometry"])
def test_canonical_structural_jobs_do_not_reuse_parent_coordinates_for_variants(canonical_preparation, job):
    service, campaign = canonical_preparation
    service.store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    with pytest.raises(ResearchError, match="zero or multiple"):
        prepare_input(service, campaign, job, ["c1"])


@pytest.mark.parametrize("job", ["Cat_Pred", "Netsolp", "Mol_Probity"])
def test_canonical_prepared_artifact_tampering_is_rejected_without_rewrite(canonical_preparation, job):
    service, campaign = canonical_preparation
    prepared = prepare_input(service, campaign, job, ["parent"])
    path = Path(prepared["path"])
    path.write_bytes(b"tampered")
    with pytest.raises(ResearchError, match="changed or conflicts"):
        prepare_input(service, campaign, job, ["parent"])
    assert path.read_bytes() == b"tampered"


@pytest.mark.parametrize("job", ["Mol_Probity", "Catalytic_Geometry"])
def test_canonical_structural_jobs_still_check_frozen_coordinate_integrity(canonical_preparation, job):
    service, campaign = canonical_preparation
    path = Path(service.store.status(campaign)["task"]["parent"]["structure"]["path"])
    path.write_bytes(b"tampered")
    with pytest.raises(ResearchError, match="Frozen parent structure changed"):
        prepare_input(service, campaign, job, ["parent"])
