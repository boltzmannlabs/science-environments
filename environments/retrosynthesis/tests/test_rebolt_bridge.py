"""Compatibility tests: legacy route trees remain unchanged outside new annotations."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from synthesis_route_gym.rebolt_bridge import enrich_rebolt_paths
from synthesis_route_gym.chemistry import canonical_smiles
from synthesis_route_gym.schemas import InventoryItem, Task


def leaf(smiles, stocked=True):
    return {"smile": smiles, "building_block": str(stocked), "reference": "False", "children": []}


def reaction(product="CCOC(C)=O", reactants=None, **extra):
    children = reactants if reactants is not None else [leaf("CCO"), leaf("CC(=O)O")]
    node = {"smile": product, "building_block": "False", "reference": "True", "children": children, **extra}
    return {"smile": product, "building_block": "False", "reference": "False", "children": [node]}


def task(target="CCOC(C)=O", stock=("CCO", "CC(=O)O")):
    return Task(task_id="bridge-test", target=target, inventory=tuple(InventoryItem(smiles=s) for s in stock))


def bundle(node=None):
    return {"top7": {"path": node or reaction(), "idx": 7, "clusters": [2, 3],
                     "pathway_ranking_score": 12.3}, "clusters": {"top7": 2}}


def domain_fixture():
    roles = {"aryl halide": "BrC1=CC=C(C(F)(F)F)C=C1",
             "ligand": "CC(C)C(C=C(C(C)C)C=C1C(C)C)=C1C2=C(P(C(C)(C)C)C(C)(C)C)C(OC)=CC=C2OC",
             "additive": "C1(C2=CC=CC=C2)=CC=NO1", "base": "CC(C)(C)/N=C(N(C)C)/N(C)C"}
    reactants = (roles["aryl halide"], "Cc1ccc(N)cc1",
                 "O=S(=O)(O[Pd]1c2ccccc2-c2ccccc2N~1)C(F)(F)F")
    return roles, "Cc1ccc(Nc2ccc(C(F)(F)F)cc2)cc1", reactants


def test_wrapper_collapses_once_and_preserves_legacy_fields_without_mutation():
    paths = bundle()
    before = deepcopy(paths)
    enriched, report = enrich_rebolt_paths(paths, task())
    assert paths == before
    annotation = enriched["top7"]["synthesis_route_gym"]
    restored = {**enriched["top7"]}
    restored.pop("synthesis_route_gym")
    assert restored == before["top7"] and enriched["clusters"] == paths["clusters"]
    assert len(annotation["route"]["steps"]) == 1
    assert annotation["assessment"]["graph_valid"]
    assert annotation["assessment"]["inventory_complete"]
    assert annotation["assessment"]["solved"] is False
    assert report["parsed_route_count"] == 1


def test_declared_stock_cannot_override_actual_task_inventory():
    enriched, _ = enrich_rebolt_paths(bundle(), task(stock=("CCO",)))
    check = enriched["top7"]["synthesis_route_gym"]["assessment"]
    assert not check["inventory_complete"] and "CC(=O)O" in check["unstocked"]


def test_reference_true_and_retrieved_patents_do_not_establish_exact_evidence():
    node = reaction(uspto_link=["https://patents.google.com/patent/US0000000A1"],
                    usid=["US0000000A1_Example_1"], reaction_yield=85.0)
    enriched, _ = enrich_rebolt_paths(bundle(node), task())
    result = enriched["top7"]["synthesis_route_gym"]
    assert set(result["assessment"]["evidence_status"].values()) == {"predicted"}
    assert result["retrieved_analogues"][0]["evidence_status"] == "retrieved_analogue_unverified"
    assert result["route"]["steps"][0]["predicted_yield"] is None
    assert result["assessment"]["cost"]["total"] is None


def test_wrong_wrapper_product_is_parse_error_not_silent_reaction_change():
    node = reaction()
    node["children"][0]["smile"] = "CCO"
    enriched, report = enrich_rebolt_paths(bundle(node), task())
    annotation = enriched["top7"]["synthesis_route_gym"]
    assert annotation["status"] == "parse_error" and annotation["assessment"] is None
    assert report["parse_error_count"] == 1


def test_wrong_target_is_assessed_as_invalid():
    enriched, _ = enrich_rebolt_paths(bundle(), task(target="CCN"))
    assert not enriched["top7"]["synthesis_route_gym"]["assessment"]["graph_valid"]


def test_stock_leaf_with_children_and_nonmatching_stereo_are_rejected():
    bad = leaf("CCO")
    bad["children"] = [leaf("CO")]
    annotated, _ = enrich_rebolt_paths(bundle(reaction(reactants=[bad])), task())
    assert annotated["top7"]["synthesis_route_gym"]["status"] == "parse_error"
    node = reaction(product="C[C@H](O)F", reactants=[leaf("CC(O)F")])
    node["children"][0]["smile"] = "C[C@@H](O)F"
    annotated, _ = enrich_rebolt_paths(bundle(node), task(target="C[C@H](O)F"))
    assert annotated["top7"]["synthesis_route_gym"]["status"] == "parse_error"


def test_unresolved_nonstock_leaf_remains_required_material():
    enriched, _ = enrich_rebolt_paths(bundle(reaction(reactants=[leaf("CCO", False), leaf("CC(=O)O")])), task(stock=("CC(=O)O",)))
    annotation = enriched["top7"]["synthesis_route_gym"]
    assert annotation["unresolved_leaves"] == ["CCO"]
    assert annotation["assessment"]["unstocked"] == ["CCO"]


def test_zero_step_acquisition_is_not_synthesis():
    enriched, _ = enrich_rebolt_paths(bundle(leaf("CCO")), task(target="CCO", stock=("CCO",)))
    annotation = enriched["top7"]["synthesis_route_gym"]
    assert annotation["route"]["steps"] == []
    assert annotation["assessment"]["acquisition_only"]
    assert annotation["model_application"]["status"] == "not_applicable"


def test_cycle_and_ambiguous_reaction_children_fail_closed():
    cyclic = reaction(reactants=[reaction(product="CCO", reactants=[leaf("CCOC(C)=O", False)])])
    enriched, _ = enrich_rebolt_paths(bundle(cyclic), task())
    assert enriched["top7"]["synthesis_route_gym"]["status"] == "parse_error"
    ambiguous = reaction()
    ambiguous["children"] = [leaf("CCO"), leaf("CC(=O)O")]
    enriched, _ = enrich_rebolt_paths(bundle(ambiguous), task())
    assert enriched["top7"]["synthesis_route_gym"]["status"] == "parse_error"


def test_model_is_not_called_without_explicit_condition_roles():
    class ForbiddenModel:
        def predict(self, rows):
            raise AssertionError("Unsupported route reached condition model")
    enriched, _ = enrich_rebolt_paths(bundle(), task(), ForbiddenModel())
    assert enriched["top7"]["synthesis_route_gym"]["model_application"]["status"] == "insufficient_condition_inputs"


def test_supported_explicit_conditions_are_predicted_and_inventory_checked():
    class Model:
        def predict(self, rows):
            assert rows[0]["aryl halide"] == canonical_smiles("BrC1=CC=C(C(F)(F)F)C=C1")
            return [{"predicted_yield_percent": 60.0, "evidence_status": "predicted", "model_version": "fixture"}]
    inputs, target, reactants = domain_fixture()
    node = reaction(product=target, reactants=[leaf(s) for s in reactants], condition_inputs=inputs)
    enriched, _ = enrich_rebolt_paths(bundle(node), task(target=target, stock=reactants), Model())
    annotation = enriched["top7"]["synthesis_route_gym"]
    assert annotation["model_application"]["status"] == "applied"
    assert annotation["route"]["steps"][0]["predicted_yield"] == 0.6
    assert not annotation["assessment"]["inventory_complete"]
    assert set(annotation["assessment"]["unstocked"]) == {canonical_smiles(inputs[role]) for role in ("ligand", "additive", "base")}


def test_nonfinite_and_circular_input_is_rejected_without_mutation():
    paths = bundle()
    paths["top7"]["score"] = float("nan")
    with pytest.raises(ValueError):
        enrich_rebolt_paths(paths, task())
    circular = bundle()
    circular["loop"] = circular
    with pytest.raises(ValueError):
        enrich_rebolt_paths(circular, task())


def test_real_saved_scoring_artifact_roundtrip():
    root = Path(__file__).parents[1] / "examples" / "rebolt"
    if any(not (root / name).is_file() for name in ('saved_scoring_excerpt.json', 'task.json')):
        pytest.skip('Optional archived REBOLT scoring excerpt is not bundled in the source-only release')
    paths = json.loads((root / "saved_scoring_excerpt.json").read_text())
    supplied_task = Task.model_validate_json((root / "task.json").read_text())
    enriched, report = enrich_rebolt_paths(paths, supplied_task)
    assert report["parse_error_count"] == 0
    assert len(enriched["top1"]["synthesis_route_gym"]["route"]["steps"]) == 1
    assert len(enriched["top2"]["synthesis_route_gym"]["route"]["steps"]) == 2
    assert enriched["top0"]["synthesis_route_gym"]["assessment"]["acquisition_only"]
    for key, original in paths.items():
        assert {k: v for k, v in enriched[key].items() if k != "synthesis_route_gym"} == original


def test_route_order_unknown_metadata_and_malformed_entries_are_preserved():
    paths = {"top2": bundle()["top7"], "top10": 99, "top1": {"idx": 1}, "notes": ["unchanged"]}
    enriched, report = enrich_rebolt_paths(paths, task())
    assert list(enriched) == list(paths)
    assert enriched["top10"] == 99 and enriched["notes"] == ["unchanged"]
    assert report["parse_error_count"] == 2
    assert "top10" in report["unannotatable_entries"]


@pytest.mark.parametrize("change", [
    {"reference": "unknown"}, {"smile": None}, {"children": "not a list"},
])
def test_malformed_node_fields_fail_closed(change):
    node = {**reaction(), **change}
    enriched, _ = enrich_rebolt_paths(bundle(node), task())
    assert enriched["top7"]["synthesis_route_gym"]["status"] == "parse_error"


def test_missing_model_and_invalid_model_output_are_explicit():
    inputs, target, reactants = domain_fixture()
    paths = bundle(reaction(product=target, reactants=[leaf(s) for s in reactants], condition_inputs=inputs))
    enriched, _ = enrich_rebolt_paths(paths, task(target=target))
    assert enriched["top7"]["synthesis_route_gym"]["model_application"]["status"] == "model_unavailable"
    class BadModel:
        def predict(self, rows):
            return [{"predicted_yield_percent": 120}]
    enriched, _ = enrich_rebolt_paths(paths, task(target=target), BadModel())
    assert enriched["top7"]["synthesis_route_gym"]["model_application"]["status"] == "error"
    assert enriched["top7"]["synthesis_route_gym"]["route"]["steps"][0]["predicted_yield"] is None


def test_conflicting_duplicate_producers_are_rejected():
    node = reaction(reactants=[reaction(product="CCO", reactants=[leaf("CC")]),
                               reaction(product="CCO", reactants=[leaf("CO")])])
    enriched, _ = enrich_rebolt_paths(bundle(node), task())
    assert enriched["top7"]["synthesis_route_gym"]["status"] == "parse_error"


def test_identical_convergent_producers_are_deduplicated():
    branch = reaction(product="CCO", reactants=[leaf("CC")])
    node = reaction(reactants=[branch, deepcopy(branch)])
    enriched, _ = enrich_rebolt_paths(bundle(node), task())
    annotation = enriched["top7"]["synthesis_route_gym"]
    assert annotation["status"] == "ok" and len(annotation["route"]["steps"]) == 2


def test_invalid_condition_roles_and_substrate_do_not_reach_model():
    for inputs in ({"solvent": "O"}, {"aryl halide": "CCN"}, "unknown"):
        enriched, _ = enrich_rebolt_paths(bundle(reaction(condition_inputs=inputs)), task())
        assert enriched["top7"]["synthesis_route_gym"]["status"] == "parse_error"


def test_top_level_contract_requires_object_and_validated_task():
    with pytest.raises(ValueError):
        enrich_rebolt_paths([], task())
    with pytest.raises(ValueError):
        enrich_rebolt_paths(bundle(), {})


def test_explicit_condition_roles_do_not_authorize_unrelated_reaction_scoring():
    class ForbiddenModel:
        def predict(self, rows):
            raise AssertionError("An ester route must not use a C-N coupling model")
    inputs = {"aryl halide": "Brc1ccccc1", "ligand": "P", "additive": "O", "base": "N"}
    node = reaction(reactants=[leaf("Brc1ccccc1"), leaf("CCO")], condition_inputs=inputs)
    enriched, _ = enrich_rebolt_paths(bundle(node), task(), ForbiddenModel())
    annotation = enriched["top7"]["synthesis_route_gym"]
    assert annotation["model_application"]["status"] == "outside_model_domain"
    assert annotation["route"]["steps"][0]["predicted_yield"] is None
