from pathlib import Path
import sys

import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.context import compact_context, read_context
from enzyme_research.ligands import graph_coordinate_evidence, selector, verify_ligand
from enzyme_research.preparation import prepare_input
from enzyme_research.service import ResearchService
from enzyme_research.structures import select_structure, sync_structures
from test_structure_handoff import structure_job, pdb, cif_from_fixture_pdb, WORKFLOW

SELECTED = {"chain_id": "Z", "residue_number": 501, "component_id": "LIG"}


@pytest.fixture
def molecule():
    Chem = pytest.importorskip("rdkit.Chem", reason="Ligand graph checks require the optional chemistry extra")
    from enzyme_research.workflow import load_workflow
    load_workflow(WORKFLOW)
    def make(smiles="CCO", *, delta=0.0, dimension=True):
        mol = Chem.MolFromSmiles(smiles)
        conf = Chem.Conformer(mol.GetNumAtoms()); conf.Set3D(dimension)
        points = [(20 + i * 1.4 + delta, 1 + (i % 2) * .3, 2 + (i % 3) * .1 if dimension else 0.0) for i in range(mol.GetNumAtoms())]
        for i, p in enumerate(points): conf.SetAtomPosition(i, p)
        mol.AddConformer(conf)
        sdf = (Chem.MolToMolBlock(mol) + "\n$$$$\n").encode()
        protein = pdb("AGCAAAAAAA", ligand=False).split("END")[0]
        lines = []
        for i, atom in enumerate(mol.GetAtoms()):
            x, y, z = points[i]
            name = atom.GetSymbol().upper() + str(i + 1)
            lines.append(f"HETATM{1001+i:5d} {name:>4} LIG Z 501    {x:8.3f}{y:8.3f}{z:8.3f}  1.00 20.00          {atom.GetSymbol().upper():>2}")
        return (protein + "\n".join(lines) + "\nEND\n").encode(), sdf
    return make


@pytest.fixture
def ligand_job(structure_job, molecule):
    content, sdf = molecule()
    service, campaign, workflow, call, path = structure_job(poses=1, content_override=content.decode(), extras={"ligand.sdf": sdf})
    result = sync_structures(service, campaign, workflow, "fold", call)
    return service, campaign, result["structure_ids"][0], path


def test_graph_and_coordinates_not_names_establish_identity(molecule):
    content, sdf = molecule()
    result = graph_coordinate_evidence("pose.pdb", content, sdf, "OCC", SELECTED)
    assert result["canonical_isomeric_smiles"] == "CCO"
    assert result["heavy_atom_count"] == 3
    assert not result["assay_protonation_validated"] and not result["catalytic_geometry_validated"]
    assert [a["structure_atom_name"] for a in result["heavy_atom_mapping"]] == ["C1", "C2", "O3"]


def test_cif_coordinate_labels_have_the_same_verified_atom_mapping(molecule):
    content, sdf = molecule()
    cif = cif_from_fixture_pdb(content.decode()).encode()
    result = graph_coordinate_evidence("pose.cif", cif, sdf, "CCO", SELECTED)
    assert result["heavy_atom_count"] == 3


@pytest.mark.parametrize("smiles", ["COC", "CC[O-]", "CCN", "CCO.[Na+]", "not-smiles"])
def test_isomer_charge_element_and_salt_mismatches_rejected(molecule, smiles):
    content, sdf = molecule()
    with pytest.raises(ResearchError): graph_coordinate_evidence("pose.pdb", content, sdf, smiles, SELECTED)


def test_sdf_from_a_different_pose_does_not_unlock_coordinates(molecule):
    content, sdf = molecule()
    _, other = molecule(delta=2.0)
    with pytest.raises(ResearchError, match="correspondence"):
        graph_coordinate_evidence("pose.pdb", content, other, "CCO", SELECTED)


def test_stereochemistry_is_checked_from_the_actual_3d_conformer(molecule):
    from rdkit import Chem
    content, sdf = molecule("C[C@H](O)N")
    mol = Chem.MolFromMolBlock(sdf.decode().split("$$$$")[0], removeHs=False)
    Chem.AssignStereochemistryFrom3D(mol, replaceExistingTags=True)
    expected = Chem.MolToSmiles(mol, isomericSmiles=True)
    assert "@" in expected
    graph_coordinate_evidence("pose.pdb", content, sdf, expected, SELECTED)
    opposite = expected.replace("@@", "@") if "@@" in expected else expected.replace("@", "@@")
    with pytest.raises(ResearchError, match="stereochemistry"):
        graph_coordinate_evidence("pose.pdb", content, sdf, opposite, SELECTED)


@pytest.mark.parametrize("kind", ["empty", "corrupt", "multiple", "2d", "missing_atom", "altloc", "occupancy", "unknown_residue", "element"])
def test_invalid_or_ambiguous_molecular_evidence_rejected(molecule, kind):
    content, sdf = molecule()
    selected = SELECTED
    if kind == "empty": sdf = b""
    if kind == "corrupt": sdf = b"broken molecule"
    if kind == "multiple": sdf += sdf
    if kind == "2d": content, sdf = molecule(dimension=False)
    if kind == "missing_atom": content = b"\n".join(l for l in content.splitlines() if b"O3 LIG" not in l)
    if kind == "altloc": content = content.replace(b" O3 LIG", b" O3ALIG")
    if kind == "occupancy": content = content.replace(b"  1.00 20.00", b"  0.50 20.00")
    if kind == "unknown_residue": selected = {**SELECTED, "residue_number": 502}
    if kind == "element": content = content.replace(b"           O\n", b"           N\n")
    with pytest.raises(ResearchError): graph_coordinate_evidence("pose.pdb", content, sdf, "CCO", selected)


@pytest.mark.parametrize("value", [None, {}, {**SELECTED, "residue_number": True}, {**SELECTED, "extra": "claim"}, {**SELECTED, "component_id": ""}])
def test_ligand_selectors_need_explicit_exact_labels(value):
    with pytest.raises(ResearchError): selector(value)


def test_immutable_receipt_enables_only_matching_structure_and_resumes(ligand_job):
    service, campaign, sid, path = ligand_job
    before = select_structure(service, campaign, "c1", sid)
    assert "ligand" not in before["capabilities"]
    first = verify_ligand(service, campaign, "c1", sid, "ligand.sdf", SELECTED)
    assert verify_ligand(service, campaign, "c1", sid, "ligand.sdf", SELECTED) == first
    state = service.store.status(campaign)
    assert len([e for e in state["events"] if e["payload"]["event"] == "ligand_identity_verified"]) == 1
    assert "ligand" not in state["structures"][0]["capabilities"] # original coordinates remain immutable
    checked = select_structure(service, campaign, "c1", sid)
    assert checked["ligand_identity_verified"] and "ligand" in checked["capabilities"]
    assert checked["artifact"] == before["artifact"]
    prepared = prepare_input(service, campaign, "Placer", ["c1"], structure_ids={"c1": sid})
    assert prepared["structure_ids"] == {"c1": sid} and not prepared["uploaded"]
    assert prepared["ligand_verifications"]["c1"]["ligand_selector"]["component_id"] == "LIG"
    context = compact_context(state, {})
    assert context["context_access"]["views"]["ligand_verifications"]["count"] == 1
    page = read_context(state, {}, view="ligand_verifications")
    assert page["items"][0]["value"]["structure_id"] == sid
    assert len([c for c in state["calls"] if c["tool"] == "boltzmann_submit"]) == 1


def test_external_or_absent_sdf_and_wrong_candidate_rejected(ligand_job):
    service, campaign, sid, path = ligand_job
    for member in ("other.sdf", "/tmp/ligand.sdf", "../ligand.sdf", "pose_0.pdb"):
        with pytest.raises(ResearchError): verify_ligand(service, campaign, "c1", sid, member, SELECTED)
    with pytest.raises(ResearchError): verify_ligand(service, campaign, "parent", sid, "ligand.sdf", SELECTED)
    with pytest.raises(ResearchError): verify_ligand(service, campaign, "c1", None, "ligand.sdf", SELECTED)


def test_tampering_invalidates_former_ligand_gate(ligand_job):
    service, campaign, sid, path = ligand_job
    verify_ligand(service, campaign, "c1", sid, "ligand.sdf", SELECTED)
    Path(select_structure(service, campaign, "c1", sid)["artifact"]["path"]).write_bytes(b"changed artifact")
    with pytest.raises(ResearchError): select_structure(service, campaign, "c1", sid)


def test_missing_chemistry_dependency_is_an_explicit_gate(molecule, monkeypatch):
    content, sdf = molecule()
    monkeypatch.setitem(sys.modules, "rdkit", None)
    with pytest.raises(ResearchError, match="optional RDKit"):
        graph_coordinate_evidence("pose.pdb", content, sdf, "CCO", SELECTED)


def test_service_cannot_accept_a_model_supplied_verification_claim(ligand_job):
    service, campaign, sid, path = ligand_job
    real = ResearchService.__new__(ResearchService); real.store = service.store
    with pytest.raises(ResearchError, match="takes only"):
        real.next(campaign, "verify_ligand", candidate_id="c1", structure_id=sid,
                  sdf_member="ligand.sdf", ligand_selector=SELECTED, ligand_identity_verified=True)


def test_oversized_advertised_graph_is_refused_before_loading_rdkit(monkeypatch):
    monkeypatch.setitem(sys.modules, "rdkit", None)
    payload = b"title\nprogram\ncomment\n  0  0  0     0  0            999 V3000\nM  V30 COUNTS 999999999 0 0 0 0\n"
    with pytest.raises(ResearchError, match="graph counts exceed"):
        graph_coordinate_evidence("pose.pdb", b"", payload, "CCO", SELECTED)


def test_explicit_external_pdb_connectivity_cannot_be_hidden_by_an_sdf(molecule):
    content, sdf = molecule()
    for connection in (b"CONECT 1001    1\n", b"CONECT    1 1001\n"):
        with pytest.raises(ResearchError, match="explicit external"):
            graph_coordinate_evidence("pose.pdb", content + connection, sdf, "CCO", SELECTED)


@pytest.mark.parametrize("kind,component,rejected", [("covale", "LIG", True), ("metalc", "LIG", True),
    ("hydrog", "LIG", False), ("disulf", "CYS", False)])
def test_cif_links_distinguish_substrate_links_from_protein_or_hbond_records(molecule, kind, component, rejected):
    content, sdf = molecule()
    cif = cif_from_fixture_pdb(content.decode()).encode()
    fields = ["conn_type_id", "ptnr1_auth_comp_id", "ptnr1_auth_asym_id", "ptnr1_auth_seq_id",
              "ptnr2_auth_comp_id", "ptnr2_auth_asym_id", "ptnr2_auth_seq_id"]
    cif += ("loop_\n" + "\n".join("_struct_conn." + f for f in fields) + "\n" +
            f"{kind} {component} Z 501 CYS B 103\n#\n").encode()
    if rejected:
        with pytest.raises(ResearchError, match="explicit external"):
            graph_coordinate_evidence("pose.cif", cif, sdf, "CCO", SELECTED)
    else:
        assert graph_coordinate_evidence("pose.cif", cif, sdf, "CCO", SELECTED)["heavy_atom_count"] == 3


def test_cif_label_author_chain_difference_does_not_hide_a_link(molecule):
    content, sdf = molecule()
    cif = cif_from_fixture_pdb(content.decode()).encode().replace(b" LIG Z 501 . ? 1", b" LIG X 501 . ? 1")
    fields = ["conn_type_id", "ptnr1_label_comp_id", "ptnr1_label_asym_id", "ptnr1_label_seq_id",
              "ptnr2_label_comp_id", "ptnr2_label_asym_id", "ptnr2_label_seq_id"]
    cif += ("loop_\n" + "\n".join("_struct_conn." + f for f in fields) + "\ncovale LIG Z 501 CYS B 103\n#\n").encode()
    with pytest.raises(ResearchError, match="explicit external"):
        graph_coordinate_evidence("pose.cif", cif, sdf, "CCO", {**SELECTED, "chain_id": "X"})


def test_same_compound_file_cannot_authorize_another_campaign(ligand_job):
    service, campaign, sid, path = ligand_job
    other = service.store.start(service.store.status(campaign)["task"], "base")
    with pytest.raises(ResearchError): verify_ligand(service, other, "parent", sid, "ligand.sdf", SELECTED)


def test_native_policy_calls_the_host_verifier_not_a_supplied_claim(ligand_job):
    from enzyme_research.native_policy import NativeResearchPolicy
    from test_native_policy import Audit
    service, campaign, sid, path = ligand_job
    real = ResearchService.__new__(ResearchService)
    real.store, real.workflow, real.settings = service.store, service.workflow, service.settings
    native = NativeResearchPolicy(real, campaign, Audit())
    result = native.tool("enzyme_research_next", {"campaign_id": campaign, "action": "verify_ligand",
        "values": {"candidate_id": "c1", "structure_id": sid, "sdf_member": "ligand.sdf", "ligand_selector": SELECTED}})
    assert result["research_step_finished"] and result["result"]["ligand_identity_verified"]
    assert result["result"]["scientific_jobs_submitted"] == 0


def test_joined_report_keeps_ligand_receipt_and_current_integrity(ligand_job, tmp_path):
    from enzyme_research.reporting import build_report, read_report, export_report
    service, campaign, sid, path = ligand_job
    verify_ligand(service, campaign, "c1", sid, "ligand.sdf", SELECTED)
    report = build_report(service.store, campaign)
    row = report["ligand_verification_records"][0]
    assert row["coordinate_artifact_verified_now"]
    assert read_report(report, view="ligand_verifications")["items"][0]["value"] == row
    export_report(report, tmp_path / "ligand-evidence")
    assert (tmp_path / "ligand-evidence/ligand_verifications.json").is_file()
    Path(select_structure(service, campaign, "c1", sid)["artifact"]["path"]).write_bytes(b"changed artifact")
    assert not build_report(service.store, campaign)["ligand_verification_records"][0]["coordinate_artifact_verified_now"]
