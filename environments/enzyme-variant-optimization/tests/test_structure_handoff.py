import json
from pathlib import Path
from types import SimpleNamespace
import zipfile

import pytest

from enzyme_research.connector import TrackedConnector
from enzyme_research.contracts import ResearchError
from enzyme_research.preparation import prepare_input
from enzyme_research.structures import coordinate_metadata, select_structure, sync_structures
from enzyme_research.workflow import WorkflowExecutor, load_workflow
from test_workflow_bridge import fixture_module

from enzyme_research.paths import bundled_workflow_source
WORKFLOW = bundled_workflow_source()


def pdb(sequence, *, chain="B", start=101, backbone=False, ligand=True, shift=0.0):
    from enzyme_workflow.artifacts import ONE_LETTER, SIDECHAINS
    names = {letter: name for name, letter in ONE_LETTER.items()}
    lines = []
    for position, aa in enumerate(sequence, start):
        residue = names[aa]
        atoms = ["CA"] if backbone else ["N", "CA", "C", "O", *SIDECHAINS[residue].split()]
        for offset, atom in enumerate(atoms):
            lines.append(f"ATOM  {len(lines)+1:5d} {atom:>4} {residue} {chain}{position:4d}    "
                         f"{(position-start)*3.8+offset*0.2+shift:8.3f}{0.0:8.3f}{0.0:8.3f}  1.00 20.00          {atom[0]:>2}")
    if ligand:
        lines.append(f"HETATM{len(lines)+1:5d} {'C':>4} ACT Z 501    {1.0:8.3f}{1.0:8.3f}{1.0:8.3f}  1.00 20.00           C")
    return "\n".join(lines) + "\nEND\n"


def cif_from_fixture_pdb(content):
    fields = ["group_PDB", "id", "label_atom_id", "label_comp_id", "label_asym_id", "label_seq_id",
              "Cartn_x", "Cartn_y", "Cartn_z", "auth_atom_id", "auth_comp_id", "auth_asym_id", "auth_seq_id",
              "label_alt_id", "pdbx_PDB_ins_code", "pdbx_PDB_model_num", "type_symbol", "occupancy", "B_iso_or_equiv"]
    lines = ["data_synthetic", "loop_", *("_atom_site." + field for field in fields)]
    for line in content.splitlines():
        if not line.startswith(("ATOM  ", "HETATM")): continue
        atom, residue, chain, number = line[12:16].strip(), line[17:20].strip(), line[21], line[22:26].strip()
        row = [line[:6].strip(), line[6:11].strip(), atom, residue, chain, number,
               *(line[i:i+8].strip() for i in (30, 38, 46)), atom, residue, chain, number, ".", "?", "1",
               line[76:78].strip(), line[54:60].strip(), line[60:66].strip()]
        lines.append(" ".join(row))
    return "\n".join(lines) + "\n#\n"


@pytest.fixture
def structure_job(store, task, tmp_path):
    load_workflow(WORKFLOW)
    task["allowed_jobs"] = ["Boltz2", "OfflineFixture_mol_probity", "Placer", "Solublempnn", "Thermal_MPNN"]
    catalogue, bindings = fixture_module().fixture_catalogue(tmp_path)
    path = catalogue / "tool-contracts.v1.json"
    doc = json.loads(path.read_bytes())
    doc["tools"]["Thermal_MPNN"] = {"job_name": "Thermal_MPNN", "status": "active", "execution_blocked": False,
                                     "submission": {"wire_job_name": "Thermal_MPNN"}, "diagnostics": []}
    path.write_text(json.dumps(doc))
    campaign = store.start(task, "base")
    store.add_candidates(campaign, [{"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])
    counter = []

    def run(*, poses=2, backbone=False, format="pdb", content_override=None, extras=None):
        number = len(counter) + 1
        counter.append(number)
        output = tmp_path / f"predicted-{number}.zip"
        with zipfile.ZipFile(output, "w") as archive:
            for i in range(poses):
                content = content_override or pdb("AGCAAAAAAA", backbone=backbone, shift=i*0.1)
                archive.writestr(f"pose_{i}.{format}", content if format == "pdb" else cif_from_fixture_pdb(content))
            for member, content in (extras or {}).items(): archive.writestr(member, content)

        class Connector:
            def call(self, name, args):
                if name == "boltzmann_submit": return {"job_name": "Boltz2", "doc_id": f"synthetic-fold-{number}"}
                if name == "boltzmann_status": return {"status": "completed", "download_link": f"https://offline.invalid/predicted-{number}.zip"}
                if name == "boltzmann_download": return {"output_paths": [str(output)], "errors": []}
                raise AssertionError(name)

        connector = TrackedConnector(store, Connector())
        driver = WorkflowExecutor(store, WORKFLOW, catalogue, connector, bindings=bindings)
        specification = {"objective": "Synthetic coordinate identity and handoff", "approved": True, "steps": [{
            "step_id": "fold", "tool": "boltz2", "experiment_name": f"Synthetic fold {number}",
            "candidate_ids": ["c1"], "expected_count": poses,
            "inputs": {"Protein_Sequences": ["AGCAAAAAAA"], "SMILES": ["CCO"]}}]}
        workflow = driver.start_segment(campaign, specification)["workflow_id"]
        submitted = driver.submit(campaign, workflow, "fold")
        response = driver.poll(campaign, workflow, "fold", submitted["call_id"])
        driver.download(campaign, workflow, "fold", response["result"]["download_link"], tmp_path)
        driver.ingest(campaign, workflow, "fold", output,
                      bindings={f"pose_{i}": {"parent_ids": ["c1"]} for i in range(poses)})
        service = SimpleNamespace(store=store, workflow=driver, connector=connector, settings={"catalogue_root": str(catalogue)})
        return service, campaign, workflow, submitted["call_id"], output
    return run


def test_coordinates_attach_to_exact_sequence_without_new_variants(structure_job):
    service, campaign, workflow, call, output = structure_job()
    result = sync_structures(service, campaign, workflow, "fold", call)
    state = service.store.status(campaign)
    assert len(state["candidates"]) == 2 and len(state["structures"]) == 2
    assert set(r["candidate_id"] for r in state["structures"]) == {"c1"}
    assert result["observation"]["kind"] == "folding"
    assert state["structures"][0]["mapping"]["A2"] == {"chain_id": "B", "residue_number": 102, "insertion_code": ""}
    assert "all_atom" in state["structures"][0]["capabilities"]
    assert all(not r["quality_validated"] and not r["ligand_identity_verified"] for r in state["structures"])


def test_hetatm_is_not_automatically_the_task_substrate(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    sync_structures(service, campaign, workflow, "fold", call)
    record = select_structure(service, campaign, "c1")
    assert "ligand" in record["detected_capabilities"]
    assert "ligand" not in record["capabilities"] and "ligand_present_unverified" in record["capabilities"]


def test_multiple_poses_need_explicit_structure_version(structure_job):
    service, campaign, workflow, call, output = structure_job()
    result = sync_structures(service, campaign, workflow, "fold", call)
    with pytest.raises(ResearchError): select_structure(service, campaign, "c1")
    assert select_structure(service, campaign, "c1", result["structure_ids"][1])["artifact"]["member"] == "pose_1.pdb"


def test_structure_transfer_resumes_without_duplicate_versions(structure_job):
    service, campaign, workflow, call, output = structure_job()
    first = sync_structures(service, campaign, workflow, "fold", call)
    second = sync_structures(service, campaign, workflow, "fold", call)
    assert first == second and len(service.store.status(campaign)["structures"]) == 2
    assert len(service.store.status(campaign)["observations"]) == 1


def test_tampered_structure_artifact_cannot_be_used(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    sync_structures(service, campaign, workflow, "fold", call)
    record = service.store.status(campaign)["structures"][0]
    Path(record["artifact"]["path"]).write_bytes(b"corrupt")
    with pytest.raises(ResearchError): select_structure(service, campaign, "c1")
    with pytest.raises(ResearchError): sync_structures(service, campaign, workflow, "fold", call)


def test_unrelated_job_cannot_establish_structure_version(structure_job):
    service, campaign, workflow, call, output = structure_job()
    with pytest.raises(ResearchError): sync_structures(service, campaign, workflow, "fold", "wrong-call")
    assert not service.store.status(campaign)["structures"]


def test_backbone_never_becomes_all_atom(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1, backbone=True)
    sync_structures(service, campaign, workflow, "fold", call)
    version = select_structure(service, campaign, "c1")
    assert "all_atom" not in version["capabilities"] and "backbone_or_incomplete" in version["capabilities"]
    spec = {"objective": "Must not pass a missing side-chain gate", "approved": True, "steps": [{
        "step_id": "quality", "tool": "mol_probity", "candidate_ids": ["c1"], "experiment_name": "Synthetic missing atoms",
        "inputs": {"input_path": "fixtures/structure.zip", "execution_mode": "measurement_only"}}]}
    following = service.workflow.start_segment(campaign, spec)["workflow_id"]
    with pytest.raises(ValueError): service.workflow.prepare(campaign, following, "quality")


def test_verified_structure_reaches_quality_tool_with_mapping(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    result = sync_structures(service, campaign, workflow, "fold", call)
    spec = {"objective": "Synthetic folding-to-quality handoff", "approved": True, "steps": [{
        "step_id": "quality", "tool": "mol_probity", "candidate_ids": ["c1"], "experiment_name": "Synthetic quality input",
        "inputs": {"input_path": "fixtures/structure.zip", "execution_mode": "measurement_only"}}]}
    following = service.workflow.start_segment(campaign, spec, structure_ids={"c1": result["structure_ids"][0]})["workflow_id"]
    candidate = service.workflow.harness.status(following)["state"]["candidates"]["c1"]
    assert candidate["sequence"] == "AGCAAAAAAA" and "all_atom" in candidate["capabilities"]
    assert candidate["mapping"]["A2"]["residue_number"] == 102
    assert service.workflow.prepare(campaign, following, "quality")["status"] == "ready"


def test_generic_ligand_cannot_unlock_placer(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    sync_structures(service, campaign, workflow, "fold", call)
    with pytest.raises(ResearchError): prepare_input(service, campaign, "Placer", ["c1"])


def test_mutant_pdb_export_uses_actual_folded_coordinates(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    sync_structures(service, campaign, workflow, "fold", call)
    result = prepare_input(service, campaign, "Thermal_MPNN", ["c1"])
    with zipfile.ZipFile(result["path"]) as archive:
        assert archive.namelist() == ["c1.pdb"]
        content = archive.read("c1.pdb").decode()
    assert "CYS B 103" in content and "CYS A   3" not in content
    assert result["residue_mappings"]["c1"]["A2"]["residue_number"] == 102
    assert not result["uploaded"] and result["jobs_submitted"] == 0


def test_wrong_candidate_sequence_is_rejected(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    from enzyme_workflow.artifacts import inspect_structure
    state = service.store.status(campaign)
    candidate = next(c for c in state["candidates"] if c["candidate_id"] == "c1")
    parsed = inspect_structure("wrong.pdb", pdb("AGDAAAAAAA").encode())
    with pytest.raises(ResearchError): coordinate_metadata(parsed, state["task"], candidate)


def test_other_campaign_cannot_select_this_structure(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    result = sync_structures(service, campaign, workflow, "fold", call)
    other = service.store.start(service.store.status(campaign)["task"], "base")
    with pytest.raises(ResearchError): select_structure(service, other, "parent", result["structure_ids"][0])


def test_cif_coordinates_keep_their_format_and_correct_numbering(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1, format="cif")
    sync_structures(service, campaign, workflow, "fold", call)
    record = select_structure(service, campaign, "c1")
    assert record["artifact"]["member"] == "pose_0.cif"
    assert record["mapping"]["A2"]["residue_number"] == 102
    assert "all_atom" in record["capabilities"]
    prepared = prepare_input(service, campaign, "Thermal_MPNN", ["c1"])
    with zipfile.ZipFile(prepared["path"]) as archive:
        projected = archive.read("c1.pdb").decode()
    assert "CYS B 103" in projected and "HETATM" not in projected
    assert prepared["protein_projections"]["c1"]["removed_hetero_atoms"] == 1
    assert prepared["protein_projections"]["c1"]["residues_renumbered"] is False
    assert select_structure(service, campaign, "c1")["artifact"]["member"] == "pose_0.cif"


def test_coordinate_version_cannot_be_overwritten(structure_job):
    service, campaign, workflow, call, output = structure_job(poses=1)
    sync_structures(service, campaign, workflow, "fold", call)
    record = dict(service.store.status(campaign)["structures"][0])
    record["quality_validated"] = True
    with pytest.raises(ResearchError, match="immutable"):
        service.store.add_structure_version(campaign, record)
    assert service.store.status(campaign)["structures"][0]["quality_validated"] is False
