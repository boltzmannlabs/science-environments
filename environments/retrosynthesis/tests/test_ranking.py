import json
import numpy as np
import pytest

from synthesis_route_gym.ranking import ConditionRanker, condition_features, rank_routes
from synthesis_route_gym.model_training import grouped_split, evaluate_selection, export_forest, train_and_evaluate
from synthesis_route_gym.condition_domain import condition_roles_match_step


def rows():
    return [
        {"aryl halide": s, "ligand": "P", "additive": "O", "base": "N", "rxn": f"{s}>>{p}", "yield": y}
        for s, p, y in [("ClC", "CO", 90), ("BrC", "CO", 70), ("ClCC", "CCO", 40),
                        ("BrCC", "CCO", 35), ("ClCCC", "CCCO", 20), ("BrCCC", "CCCO", 15),
                        ("ClCCCC", "CCCCO", 50), ("ClCCCCC", "CCCCCO", 80)]
    ]


def test_split_keeps_all_product_family_members_together_and_ignores_yields():
    data = rows()
    split = grouped_split(data, seed=20261027)
    changed = [{**row, "yield": 1000 - row["yield"]} for row in data]
    assert grouped_split(changed, seed=20261027) == split
    product_sets = [{data[i]["rxn"].split(">>")[1] for i in indices} for indices in split.values()]
    assert all(product_sets[i].isdisjoint(product_sets[j]) for i in range(3) for j in range(i))
    assert sorted(i for ids in split.values() for i in ids) == list(range(len(data)))


def test_features_ignore_labels_and_reject_bad_chemistry():
    row = rows()[0]
    assert np.array_equal(condition_features([row]), condition_features([{**row, "yield": -999}]))
    with pytest.raises(ValueError):
        condition_features([{**row, "ligand": "invalid molecule"}])


def test_exported_forest_predictions_match_and_safe_json_roundtrip(tmp_path):
    from sklearn.ensemble import ExtraTreesRegressor
    x = condition_features(rows())
    y = np.array([r["yield"] for r in rows()])
    estimator = ExtraTreesRegressor(n_estimators=5, max_depth=3, random_state=7, n_jobs=1).fit(x, y)
    artifact = export_forest(estimator, {"model_version": "test", "validation_residual_q90": 12.0})
    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps(artifact))
    predictor = ConditionRanker.load(model_path)
    result = predictor.predict(rows())
    assert np.allclose([r["predicted_yield_percent"] for r in result], estimator.predict(x))
    assert all(r["interval_kind"] == "validation_residual_band_not_coverage_guarantee" for r in result)
    assert all("success_probability" not in r for r in result)


def test_json_model_rejects_invalid_tree_and_unsupported_schema():
    with pytest.raises(ValueError):
        ConditionRanker({"schema_version": "unknown", "trees": []})
    malformed = {"schema_version": "condition-ranker.v1", "n_features": 512,
                 "metadata": {}, "trees": [{"left": [0], "right": [0], "feature": [0], "threshold": [0], "value": [1]}]}
    with pytest.raises(ValueError):
        ConditionRanker(malformed)


def test_selection_metric_uses_predictions_and_reports_regret():
    data = [
        {"aryl halide": "CCCl", "yield": 10},
        {"aryl halide": "CCCl", "yield": 90},
        {"aryl halide": "CCCCl", "yield": 50},
    ]
    result = evaluate_selection(data, [0.9, 0.1, 0.2], ks=(1, 2))
    assert result["top_1_mean_selected_yield_percent"] == 30
    assert result["top_1_mean_simple_regret_percent"] == 40
    assert result["top_2_mean_simple_regret_percent"] == 0


def test_generic_route_ranking_preserves_unknowns_and_hard_failures():
    routes = [
        {"route_id": "unknown", "steps": [{"predicted_yield": None}], "graph_valid": True, "inventory_complete": True},
        {"route_id": "supported", "steps": [{"predicted_yield": .8}], "graph_valid": True, "inventory_complete": True},
        {"route_id": "invalid", "steps": [{"predicted_yield": .99}], "graph_valid": False, "inventory_complete": True},
    ]
    output = rank_routes(routes)
    assert output[0]["route_id"] == "supported"
    assert output[-1]["eligible"] is False
    unknown = next(r for r in output if r["route_id"] == "unknown")
    assert unknown["bottleneck_predicted_yield"] is None
    assert unknown["unknown_step_count"] == 1
    assert all(r["score_kind"] == "heuristic_utility_not_success_probability" for r in output)


def test_training_writes_reproducible_split_and_independent_evaluation_bundle(tmp_path):
    import csv
    data = rows()
    source = tmp_path / "measured-fixture.csv"
    with source.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    output = tmp_path / "artifact"
    report = train_and_evaluate(source, output)
    protocol = json.loads((output / "protocol.json").read_text())
    saved = json.loads((output / "evaluation.json").read_text())
    assert saved["model_sha256"] == report["model_sha256"]
    assert protocol["test_tuning_allowed"] is False
    assert report["multi_step_route_improvement_proven"] is False
    assert report["independent_chemical_review_status"] == "pending"
    model = ConditionRanker.load(output / "condition_ranker.json")
    assert model.metadata["training_row_count"] == len(protocol["split"]["row_indices"]["train"])
    assert len((output / "heldout_predictions.jsonl").read_text().splitlines()) == len(protocol["split"]["row_indices"]["test"])


def test_empty_predictions_invalid_metrics_and_invalid_yield_fail_closed():
    with pytest.raises(ValueError):
        grouped_split(rows()[:3])
    with pytest.raises(ValueError):
        evaluate_selection([], [])
    with pytest.raises(ValueError):
        evaluate_selection(rows(), [float("nan")] * len(rows()))
    with pytest.raises(ValueError):
        rank_routes([{"route_id": "bad", "steps": [{"predicted_yield": 90}]}])


def constant_model(**metadata):
    return ConditionRanker({
        "schema_version": "condition-ranker.v1", "n_features": 512,
        "metadata": {"model_version": "fixture", **metadata},
        "trees": [{"left": [-1], "right": [-1], "feature": [-2],
                   "threshold": [-2.0], "value": [80.0]}],
    })


def coupling_step():
    roles = {
        "aryl halide": "CCc1ccc(Br)cc1",
        "ligand": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
        "additive": "Cc1cc(C)on1", "base": "CCN(CC)CC",
    }
    return {
        "product": "CCc1ccc(Nc2ccc(C)cc2)cc1",
        "reactants": [{"smiles": roles["aryl halide"]}, {"smiles": "Cc1ccc(N)cc1"}],
        "reagents": [{"smiles": roles[key]} for key in ("ligand", "additive", "base")] + [
            {"smiles": "O=S(=O)(O[Pd]1c2ccccc2-c2ccccc2N~1)C(F)(F)F"}],
        "conditions": ("operational details not established by this software fixture",),
        "condition_inputs": roles,
    }


def test_route_condition_model_requires_explicit_chemical_roles():
    model = constant_model()
    routes = [
        {"route_id": "prose", "steps": [{"conditions": ("ambient", "stirred")}],
         "graph_valid": True, "inventory_complete": True},
        {"route_id": "roles", "steps": [coupling_step()],
         "graph_valid": True, "inventory_complete": True},
        {"route_id": "incomplete", "steps": [{"condition_inputs": {"base": "N"}}],
         "graph_valid": True, "inventory_complete": True},
    ]
    output = {r["route_id"]: r for r in rank_routes(routes, condition_ranker=model)}
    assert output["prose"]["bottleneck_predicted_yield"] is None
    assert output["incomplete"]["bottleneck_predicted_yield"] is None
    assert output["roles"]["bottleneck_predicted_yield"] == .8
    assert output["prose"]["model_version"] is None
    assert output["roles"]["condition_model_applied_step_count"] == 1
    assert output["roles"]["route_utility_kind"] == "declared_surrogate_heuristic"


def test_legacy_conditions_mapping_remains_supported_but_explicit_inputs_take_precedence():
    step = coupling_step()
    good = step["condition_inputs"]
    legacy = {k: v for k, v in step.items() if k != "condition_inputs"}
    routes = [
        {"route_id": "legacy", "steps": [{**legacy, "conditions": good}]},
        {"route_id": "explicit_incomplete", "steps": [{**legacy, "conditions": good, "condition_inputs": {"base": "N"}}]},
    ]
    output = {r["route_id"]: r for r in rank_routes(routes, constant_model())}
    assert output["legacy"]["bottleneck_predicted_yield"] == .8
    assert output["explicit_incomplete"]["bottleneck_predicted_yield"] is None


@pytest.mark.parametrize("tree", [
    {},
    {"left": [], "right": [], "feature": [], "threshold": [], "value": []},
    {"left": [-1], "right": [-1], "feature": [], "threshold": [-2], "value": [80]},
    {"left": [-1.0], "right": [-1], "feature": [-2], "threshold": [-2], "value": [80]},
    {"left": [-1], "right": [-1], "feature": [-2], "threshold": [-2], "value": [float("inf")]},
    {"left": [-1], "right": [-1], "feature": [-2], "threshold": [-2], "value": ["80"]},
])
def test_model_rejects_malformed_or_non_numeric_tree_data(tree):
    with pytest.raises(ValueError):
        ConditionRanker({"schema_version": "condition-ranker.v1", "n_features": 512, "trees": [tree]})


def test_model_rejects_incompatible_features_empty_ensemble_and_large_file(tmp_path):
    with pytest.raises(ValueError):
        ConditionRanker({"schema_version": "condition-ranker.v1", "n_features": 1, "trees": []})
    with pytest.raises(ValueError):
        ConditionRanker({"schema_version": "condition-ranker.v1", "n_features": 512, "trees": []})
    path = tmp_path / "oversize.json"
    with path.open("wb") as handle:
        handle.truncate(100_000_001)
    with pytest.raises(ValueError):
        ConditionRanker.load(path)


def test_prediction_empty_uncalibrated_and_missing_features():
    model = constant_model()
    assert model.predict([]) == []
    prediction = model.predict([rows()[0]])[0]
    assert prediction["lower_yield_percent"] is None
    assert prediction["upper_yield_percent"] is None
    with pytest.raises(ValueError):
        model.predict([{"ligand": "P"}])
    with pytest.raises(ValueError):
        model.predict([{**rows()[0], "ligand": ""}])
    with pytest.raises(ValueError):
        constant_model(validation_residual_q90=-1).predict([rows()[0]])


def test_unrelated_reaction_cannot_borrow_condition_model_scores():
    actual = coupling_step()
    ester = {**actual, "product": "CCOC(C)=O", "reactants": [{"smiles": "CCO"}, {"smiles": "CC(=O)O"}]}
    wrong_product = {**actual, "product": "CCOC(C)=O"}
    missing_structure = {"condition_inputs": actual["condition_inputs"]}
    for bad_step in (ester, wrong_product, missing_structure):
        assert not condition_roles_match_step(bad_step)
        ranked = rank_routes([{"route_id": "unrelated", "steps": [bad_step],
                               "graph_valid": True, "inventory_complete": True}], constant_model())[0]
        assert ranked["bottleneck_predicted_yield"] is None
        assert ranked["condition_model_applied_step_count"] == 0
        assert ranked["condition_model_refused_step_count"] == 1
        assert ranked["model_version"] is None


def test_condition_domain_checks_fixed_partner_catalyst_and_declared_roles():
    step = coupling_step()
    assert condition_roles_match_step(step)
    assert not condition_roles_match_step({**step, "reactants": step["reactants"][:1]})
    assert not condition_roles_match_step({**step, "reagents": step["reagents"][:-1]})
    assert not condition_roles_match_step({**step, "condition_inputs": {**step["condition_inputs"], "base": "N"}})
    assert not condition_roles_match_step({**step, "condition_inputs": {**step["condition_inputs"], "base": "bad smiles"}})


@pytest.mark.parametrize("quantity_status,acquisition_only,expected", [
    ("complete", False, True), ("not_requested", False, True),
    ("unknown", False, False), ("insufficient", False, False),
    ("complete", True, False), ("not_requested", True, False),
])
def test_route_eligibility_respects_quantity_and_acquisition(quantity_status, acquisition_only, expected):
    route = {"route_id": "route", "steps": [{"predicted_yield": .9}],
             "graph_valid": True, "inventory_complete": True, "constraint_compliant": True,
             "quantity_status": quantity_status, "acquisition_only": acquisition_only}
    assert rank_routes([route])[0]["eligible"] is expected
    assert not rank_routes([{**route, "steps": [], "acquisition_only": False}])[0]["eligible"]
