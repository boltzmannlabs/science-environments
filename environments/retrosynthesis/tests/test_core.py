import pytest
from pydantic import ValidationError
from synthesis_route_gym.chemistry import canonical_smiles
from synthesis_route_gym.schemas import (
    Budget, Constraints, EvidenceRecord, InventoryItem, MaterialUse,
    ReactionStep, RouteCandidate, Task,
)
from synthesis_route_gym.validation import assess_route


def make_step(step_id="ester", **kwargs):
    values = dict(step_id=step_id, product="CCOC(C)=O", reactants=(
        MaterialUse(smiles="CCO"), MaterialUse(smiles="CC(=O)O")),
        source_tool="test-fixture", source_version="1")
    return ReactionStep(**{**values, **kwargs})


def make_task(**kwargs):
    values = dict(task_id="ethyl-acetate", target="CCOC(C)=O", inventory=(
        InventoryItem(smiles="CCO"), InventoryItem(smiles="CC(=O)O")))
    return Task(**{**values, **kwargs})


def make_route(**kwargs):
    values = dict(route_id="r1", target="CCOC(C)=O", steps=(make_step(),))
    return RouteCandidate(**{**values, **kwargs})


def test_identity_preserves_stereo_and_removes_atom_maps():
    assert canonical_smiles("OCC") == canonical_smiles("[CH3:1][CH2:2][OH:3]")
    assert canonical_smiles("C[C@H](O)F") != canonical_smiles("C[C@@H](O)F")
    with pytest.raises(ValueError):
        canonical_smiles("this is not a molecule")


def test_unknown_yield_cost_and_evidence_are_not_success():
    result = assess_route(make_task(), make_route())
    assert result.graph_valid and result.inventory_complete
    assert result.cost.total is None
    assert result.evidence_status == {"ester": "predicted"}
    assert result.review_status == "pending" and not result.solved
    assert make_step().predicted_yield is None


def test_all_reactant_branches_and_reagents_must_be_available():
    task = make_task(inventory=(InventoryItem(smiles="CCO"),))
    assert not assess_route(task, make_route()).inventory_complete
    route = make_route(steps=(make_step(reagents=(MaterialUse(smiles="O"),)),))
    assert not assess_route(make_task(), route).inventory_complete


def test_cyclic_disconnected_and_wrong_target_routes_are_rejected():
    route = make_route(steps=(make_step(reactants=(MaterialUse(smiles="CCOC(C)=O"),)),))
    assert not assess_route(make_task(), route).graph_valid
    detached = make_step("unused", product="CCN", reactants=(MaterialUse(smiles="CN"),))
    assert not assess_route(make_task(), make_route(steps=(make_step(), detached))).graph_valid
    assert not assess_route(make_task(), make_route(target="CCO")).graph_valid


def test_inventory_exclusions_and_equipment_are_hard_gates():
    task = make_task(constraints=Constraints(forbidden_smiles=("CCO",)))
    assert not assess_route(task, make_route()).constraint_compliant
    route = make_route(steps=(make_step(required_equipment=("sealed_reactor",)),))
    assert not assess_route(make_task(), route).constraint_compliant


def test_quantity_is_aggregated_and_unknown_is_not_zero():
    task = make_task(target_amount_mmol=1, inventory=(
        InventoryItem(smiles="CCO", available_mmol=1),
        InventoryItem(smiles="CC(=O)O", available_mmol=2)))
    step = make_step(product_amount_mmol=1, reactants=(
        MaterialUse(smiles="CCO", amount_mmol=0.75),
        MaterialUse(smiles="CCO", amount_mmol=0.75),
        MaterialUse(smiles="CC(=O)O", amount_mmol=1)))
    assert assess_route(task, make_route(steps=(step,))).quantity_status == "insufficient"
    assert assess_route(task, make_route()).quantity_status == "unknown"


def test_exact_evidence_requires_verified_structure_match():
    analogue = EvidenceRecord(evidence_id="e1", kind="literature_analogue",
        source="https://example.org/paper", locator="Example 1", verified_by="curator",
        reactants=("CCO", "CC(=O)O"), product="CCOC(C)=O")
    step = make_step(evidence_ids=("e1",))
    task = make_task(evidence=(analogue,))
    assert assess_route(task, make_route(steps=(step,)), trusted_evidence=(analogue,)).evidence_status["ester"] == "literature_analogue"
    wrong = analogue.model_copy(update={"kind": "literature_exact", "product": "CCO"})
    assert assess_route(make_task(evidence=(wrong,)), make_route(steps=(step,)), trusted_evidence=(wrong,)).evidence_status["ester"] == "unresolved"
    exact = analogue.model_copy(update={"kind": "literature_exact"})
    result = assess_route(make_task(evidence=(exact,)), make_route(steps=(step,)), trusted_evidence=(exact,))
    assert result.evidence_status["ester"] == "literature_exact" and not result.solved
    assert assess_route(make_task(evidence=(exact,)), make_route(steps=(step,))).evidence_status["ester"] == "unresolved"
    with pytest.raises(TypeError):
        result.evidence_status["ester"] = "measured"


def test_acquisition_is_not_counted_as_synthesis():
    task = make_task(inventory=(InventoryItem(smiles="CCOC(C)=O"),))
    result = assess_route(task, make_route(steps=()))
    assert result.acquisition_only and not result.solved


def test_missing_atom_source_is_flagged():
    route = make_route(steps=(make_step(reactants=(MaterialUse(smiles="CC"),)),))
    result = assess_route(make_task(), route)
    assert any(f.code == "missing_element_source" for f in result.findings)
    assert not result.graph_valid


def test_declared_quantities_cannot_create_product_atoms():
    step = make_step(product_amount_mmol=1, reactants=(MaterialUse(smiles="CO", amount_mmol=1),))
    task = make_task(target_amount_mmol=1, inventory=(InventoryItem(smiles="CO", available_mmol=1),))
    result = assess_route(task, make_route(steps=(step,)))
    assert not result.graph_valid
    assert any(f.code == "element_amount_deficit" for f in result.findings)


def test_models_reject_unknown_fields_nonfinite_values_and_bad_limits():
    with pytest.raises(ValidationError):
        make_task(hidden_answer="cheat")
    with pytest.raises(ValidationError):
        Budget(max_actions=0)
    with pytest.raises(ValidationError):
        InventoryItem(smiles="CCO", available_mmol=float("nan"))
    with pytest.raises(ValidationError):
        make_step(predicted_yield=90)
    with pytest.raises(ValidationError):
        Constraints(forbidden_smarts=("[invalid",))
def test_condition_materials_cannot_bypass_inventory_exclusions_or_freezing():
    from synthesis_route_gym.schemas import Constraints, RouteCandidate
    payload = make_route().model_dump(mode="json")
    payload["steps"][0]["condition_inputs"] = {"aryl halide": "Brc1ccccc1", "ligand": "P", "additive": "O", "base": "N"}
    route = RouteCandidate.model_validate(payload)
    task = make_task(constraints=Constraints(forbidden_smiles=("P",)))
    result = assess_route(task, route)
    assert not result.inventory_complete
    assert not result.constraint_compliant
    assert not result.graph_valid
    assert "P" in result.unstocked
    with pytest.raises(TypeError):
        route.steps[0].condition_inputs["base"] = "CCC"
    assert route.model_dump(mode="json")["steps"][0]["condition_inputs"]["base"] == "N"

