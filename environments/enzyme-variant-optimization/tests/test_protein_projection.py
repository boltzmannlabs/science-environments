import hashlib

import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.protein_projection import project_protein_pdb
from enzyme_research.workflow import load_workflow
from test_structure_handoff import pdb, cif_from_fixture_pdb, WORKFLOW


@pytest.fixture
def cif():
    load_workflow(WORKFLOW)
    return cif_from_fixture_pdb(pdb("AGCAAAAAAA")).encode()


def test_projection_is_protein_only_and_preserves_sequence_numbering(cif):
    from enzyme_workflow.artifacts import inspect_structure
    output, audit = project_protein_pdb("complex.cif", cif)
    projected = inspect_structure("protein.pdb", output)
    original = inspect_structure("complex.cif", cif)
    assert projected["structural_sequence"] == original["structural_sequence"]
    assert projected["residues"] == original["residues"]
    assert "ligand" not in projected["capabilities"] and "all_atom" in projected["capabilities"]
    assert audit["removed_hetero_atoms"] == 1 and audit["atoms_added"] == 0
    assert audit["residues_renumbered"] is False and audit["ligands_preserved"] is False
    assert audit["source_member_sha256"] == hashlib.sha256(cif).hexdigest()
    assert audit["projected_pdb_sha256"] == hashlib.sha256(output).hexdigest()
    assert all(len(line) == 80 for line in output.decode().splitlines() if line.startswith("ATOM"))


def test_projection_is_deterministic(cif):
    assert project_protein_pdb("complex.cif", cif) == project_protein_pdb("complex.cif", cif)


def test_pdb_rounding_is_explicit_and_bounded(cif):
    # Change one x coordinate from an exactly representable to a finer value.
    text = cif.decode().replace("0.000", "0.0004", 1).encode()
    output, audit = project_protein_pdb("complex.cif", text)
    assert 0 < audit["max_coordinate_rounding_angstrom"] <= 0.00050000001


def test_missing_element_is_not_invented(cif):
    text = cif.decode().replace("_atom_site.type_symbol", "_atom_site.unused_element")
    with pytest.raises(ResearchError, match="elements"):
        project_protein_pdb("complex.cif", text.encode())


@pytest.mark.parametrize("old,new", [(" B 101 ", " B 10001 "), ("0.000", "100000.0"),
                                    ("1.00 20.00", "nan 20.00"), ("1.00 20.00", "1.00 -1.00")])
def test_unrepresentable_or_invalid_values_rejected(cif, old, new):
    text = cif.decode()
    assert old in text
    with pytest.raises(ResearchError): project_protein_pdb("complex.cif", text.replace(old, new).encode())


def test_backbone_is_not_filled_to_pass_projection():
    load_workflow(WORKFLOW)
    content = cif_from_fixture_pdb(pdb("AGCAAAAAAA", backbone=True)).encode()
    with pytest.raises(ResearchError, match="no missing atoms"):
        project_protein_pdb("backbone.cif", content)


def test_multi_model_cif_rejected(cif):
    lines = cif.decode().splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith("ATOM "))
    row = lines[first].split()
    row[-4] = "2"  # pdbx_PDB_model_num before element/occupancy/B.
    lines[first] = " ".join(row)
    with pytest.raises(ResearchError): project_protein_pdb("models.cif", "\n".join(lines).encode())


def test_pdb_file_is_not_passed_off_as_cif():
    with pytest.raises(ResearchError): project_protein_pdb("protein.pdb", pdb("AGCAAAAAAA").encode())
