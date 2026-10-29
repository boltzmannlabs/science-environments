"""Synthetic tree fixtures only: no private benchmark reference routes."""
import copy
import json

import pytest

from synthesis_route_gym.route_data import load_paroutes, parse_paroutes_record, load_stock
from synthesis_route_gym.schemas import RouteCandidate


def mol(smiles, *reactions, metadata=None):
    return {"type": "mol", "smiles": smiles, "children": list(reactions),
            **({"metadata": metadata} if metadata is not None else {})}


def rxn(*reactants, metadata=None):
    return {"type": "reaction", "children": list(reactants),
            **({"metadata": metadata} if metadata is not None else {})}


def simple():
    return mol("CCOC(C)=O", rxn(mol("CCO"), mol("CC(=O)O")))


def test_load_file_into_route_contract(tmp_path):
    path = tmp_path / "routes.json"
    path.write_text(json.dumps([simple()]))
    record = load_paroutes(path, "paroutes-v2-n1")[0]
    route = RouteCandidate.model_validate(record["reference_route"])
    assert route.target == record["target"]
    assert record["stock"] == ["CC(=O)O", "CCO"]
    assert record["step_count"] == 1
    assert record["reaction_keys"] == ["CC(=O)O.CCO>>CCOC(C)=O"]
    assert record["source_family"] == "unresolved:paroutes"
    assert record["source_identity_status"] == "unresolved"
    assert record["source_locator"] == "paroutes-v2-n1#/0"
    assert record["source_id"] == "paroutes-v2-n1"
    assert record["molecule_keys"] == [record["target"]]
    assert record["scaffold"] == ""
    assert not record["has_stereo"] and not record["convergent"]
    assert route.steps[0].predicted_yield is None
    assert route.steps[0].evidence_ids == ()


def test_determinism_order_invariance_and_no_mutation():
    first = simple()
    saved = copy.deepcopy(first)
    second = simple()
    second["children"][0]["children"].reverse()
    a = parse_paroutes_record(first, "paroutes-v2-n1", 0)
    b = parse_paroutes_record(second, "paroutes-v2-n1", 0)
    assert a == b
    assert first == saved
    assert parse_paroutes_record(first, "other-source", 4)["route_fingerprint"] == a["route_fingerprint"]
    assert parse_paroutes_record(first, "other-source", 4)["record_id"] != a["record_id"]


def test_stereo_and_atom_maps_are_handled():
    a = mol("C[C@H](O)C(=O)O", rxn(mol("C[C@H](O)C(=O)Cl"), mol("O")))
    b = mol("C[C@@H](O)C(=O)O", rxn(mol("C[C@@H](O)C(=O)Cl"), mol("O")))
    one = parse_paroutes_record(a, "fixture", 0)
    two = parse_paroutes_record(b, "fixture", 0)
    assert one["has_stereo"]
    assert one["route_fingerprint"] != two["route_fingerprint"]
    mapped = mol("[CH3:1][CH2:2][OH:3]", rxn(mol("CCCl"), mol("O")))
    assert parse_paroutes_record(mapped, "fixture", 0)["target"] == "CCO"


def test_convergent_route_and_scaffold():
    tree = mol("c1ccccc1OC", rxn(
        mol("c1ccccc1O", rxn(mol("c1ccccc1Cl"), mol("O"))),
        mol("CO", rxn(mol("CCl"), mol("O"))),
    ))
    row = parse_paroutes_record(tree, "fixture", 3)
    assert row["convergent"] and row["step_count"] == 3
    assert row["scaffold"] == "c1ccccc1"
    assert row["stock"] == ["CCl", "O", "Clc1ccccc1"] or set(row["stock"]) == {"CCl", "O", "Clc1ccccc1"}


def test_document_metadata_and_unresolved_grouping():
    tree = simple()
    tree["children"][0]["metadata"] = {"patent_id": "US12345A1"}
    row = parse_paroutes_record(tree, "n1", 0)
    assert row["source_family"] == "patent:US12345A1"
    assert row["source_identity_status"] == "resolved_document"
    assert row["source_documents"] == ["US12345A1"]
    assert parse_paroutes_record(simple(), "n5", 1)["source_family"] == "unresolved:paroutes"


def test_actual_paroutes_id_format_and_partial_metadata():
    tree = simple()
    tree["children"][0]["metadata"] = {"ID": "US12345678A1;0042;1234"}
    row = parse_paroutes_record(tree, "n1", 0)
    assert row["source_keys"] == ["patent:US12345678A1"]
    assert row["patent_family_status"] == "unknown"
    assert row["reaction_source_locators"] == ["US12345678A1;0042;1234"]
    nested = mol("CCOC(C)=O", rxn(mol("CCO", rxn(mol("CCCl"), mol("O"))),
                                 mol("CC(=O)O"), metadata={"ID": "US12345678A1;1;1"}))
    row = parse_paroutes_record(nested, "n1", 0)
    assert row["source_keys"] == ["patent:US12345678A1", "unresolved:paroutes"]
    assert row["source_identity_status"] == "partial_documents"
    assert set(row["molecule_keys"]) == {"CCO", "CCOC(C)=O"}
    assert row["intermediate_keys"] == ["CCO"]


def test_unrecognized_id_is_not_invented_document():
    tree = simple()
    tree["children"][0]["metadata"] = {"ID": "reaction-42"}
    assert parse_paroutes_record(tree, "fixture", 0)["source_keys"] == ["unresolved:paroutes"]
    tree["children"][0]["metadata"] = {"patent_id": None}
    with pytest.raises(ValueError, match="identifier"):
        parse_paroutes_record(tree, "fixture", 0)


@pytest.mark.parametrize("document", ["USRE045108E1", "USH0002007H1"])
def test_nonstandard_patent_document_identity_is_preserved(document):
    tree = simple()
    tree["children"][0]["metadata"] = {"ID": document + ";0001;123"}
    row = parse_paroutes_record(tree, "fixture", 0)
    assert row["source_keys"] == ["patent:" + document]
    assert row["patent_family_status"] == "unknown"


@pytest.mark.parametrize("tree", [
    None, [], {}, {"type": "reaction", "children": []},
    mol("CCO"), mol("bad smiles", rxn(mol("O"))),
    mol("CCO", rxn()), mol("CCO", mol("O")),
    mol("CCO", rxn(mol("O")), rxn(mol("C"))),
    mol("CCO", rxn({"type": "reaction", "smiles": "O"})),
    {"type": "mol", "smiles": "CCO", "children": None},
    mol("CCO", rxn(mol("O")), metadata=[]),
])
def test_reject_malformed_without_echoing_structures(tree):
    with pytest.raises(ValueError) as exc:
        parse_paroutes_record(tree, "fixture", 0)
    assert "bad smiles" not in str(exc.value)


def test_reject_molecular_cycle_and_python_cycle():
    tree = mol("CCO", rxn(mol("CCO"), mol("O")))
    with pytest.raises(ValueError, match="cycle"):
        parse_paroutes_record(tree, "fixture", 0)
    cyclic = simple()
    cyclic["children"][0]["children"].append(cyclic)
    with pytest.raises(ValueError, match="cycle"):
        parse_paroutes_record(cyclic, "fixture", 0)


def test_reject_repeated_product_even_identical_expansion():
    branch = mol("CCO", rxn(mol("CCCl"), mol("O")))
    tree = mol("CCOCC", rxn(branch, copy.deepcopy(branch)))
    with pytest.raises(ValueError, match="repeated product"):
        parse_paroutes_record(tree, "fixture", 0)


def test_reject_leaf_product_ambiguity():
    tree = mol("CCOCC", rxn(mol("CCO"), mol("CCO", rxn(mol("CCCl"), mol("O")))))
    with pytest.raises(ValueError, match="leaf.*product"):
        parse_paroutes_record(tree, "fixture", 0)


def test_multiple_or_partial_documents_are_conservatively_unresolved():
    tree = mol("CCOC(C)=O", rxn(
        mol("CCO", rxn(mol("CCCl"), mol("O"), metadata={"patent_id": "US222"})),
        mol("CC(=O)O"), metadata={"patent_id": "US111"}))
    row = parse_paroutes_record(tree, "fixture", 0)
    assert row["source_family"] == "unresolved:paroutes"
    assert row["source_identity_status"] == "multiple_documents"
    assert row["source_documents"] == ["US111", "US222"]


def test_load_rejects_nonlist_invalid_json_and_reports_only_index(tmp_path):
    p = tmp_path / "routes.json"
    for contents in ['{}', '{broken', json.dumps([simple(), {}])]:
        p.write_text(contents)
        with pytest.raises(ValueError):
            load_paroutes(p, "fixture")


@pytest.mark.parametrize("source,index", [("", 0), ("a\n", 0), (None, 0), ("a", -1), ("a", True)])
def test_invalid_identifiers(source, index):
    with pytest.raises(ValueError):
        parse_paroutes_record(simple(), source, index)


def test_global_stock_is_loaded_separately(tmp_path):
    p = tmp_path / "stock.txt"
    p.write_text("OCC\nCCO\nO\n\n")
    assert load_stock(p) == ["CCO", "O"]
    p.write_text("CCO\nnot-a-molecule\n")
    with pytest.raises(ValueError, match="line 2"):
        load_stock(p)
