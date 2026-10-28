import csv
import hashlib
import json

import pytest

from synthesis_route_gym.heldout_route_benchmark import (
    build_inventory_tasks, select_route_decisions, run_heldout_route_benchmark,
)
from synthesis_route_gym.ranking import ConditionRanker
from synthesis_route_gym.schemas import Task, RouteCandidate


def measured_fixture():
    records = []
    for substrate, product, value in [
        ("CCCl", "CCO", 10), ("CCCCl", "CCCO", 20),
        ("CCCCCl", "CCCCO", 30), ("CCl", "CO", 40),
        ("CBr", "CO", 50), ("CI", "CO", 60),
    ]:
        records.append({"aryl halide": substrate, "ligand": "P", "additive": "O", "base": "N",
                        "rxn": f"{substrate}.O.P.N>>{product}", "yield": value})
    return records


def constant_model():
    return {"schema_version": "condition-ranker.v1", "n_features": 512,
            "metadata": {"model_version": "test-fixture"},
            "trees": [{"left": [-1], "right": [-1], "feature": [-2], "threshold": [-2], "value": [50]}]}


def write_bundle(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    rows = measured_fixture()
    dataset = tmp_path / "data.csv"
    with dataset.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    model_file = model_dir / "condition_ranker.json"
    model_file.write_text(json.dumps(constant_model()))
    protocol = {"split": {"dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
                           "row_indices": {"train": [0, 1], "validation": [2], "test": [3, 4, 5]}}}
    (model_dir / "protocol.json").write_text(json.dumps(protocol))
    (model_dir / "evaluation.json").write_text(json.dumps({
        "model_sha256": hashlib.sha256(model_file.read_bytes()).hexdigest()}))
    return dataset, model_dir


def test_candidate_export_excludes_outcomes_and_is_unchanged_by_hidden_labels():
    rows = measured_fixture()[3:]
    pools = build_inventory_tasks(rows, row_indices=[3, 4, 5], source_version="fixture")
    altered = [{**r, "yield": 999 - r["yield"]} for r in rows]
    assert build_inventory_tasks(altered, row_indices=[3, 4, 5], source_version="fixture") == pools
    assert len(pools) == 3
    text = json.dumps(pools)
    assert "yield" not in text and "outcome" not in text
    for pool in pools:
        task = Task.model_validate(pool["task"])
        route = RouteCandidate.model_validate(pool["candidates"][0]["route"])
        assert len(route.steps) == 1
        assert route.steps[0].condition_inputs
        assert all(item.available_mmol is None for item in task.inventory)
        assert task.target_amount_mmol is None


def test_selectors_use_identical_inventory_gates_and_do_not_consume_hidden_yields():
    rows = measured_fixture()
    pools = build_inventory_tasks(rows[3:], row_indices=[3, 4, 5], source_version="fixture")
    model = ConditionRanker(constant_model())
    output = select_route_decisions(pools, rows[:2], model)
    assert output["arms"]["learned_yield_route_utility"][0]["top_1_route_ids"]
    assert "measured_yield" not in json.dumps(output)
    assert all(g["graph_valid"] and g["inventory_complete"] for g in output["candidate_gates"])
    broken = [{**pool, "task": {**pool["task"], "inventory": []}} for pool in pools]
    blocked = select_route_decisions(broken, rows[:2], model)
    for arm in blocked["arms"].values():
        assert all(not task["top_1_route_ids"] for task in arm)


def test_frozen_benchmark_produces_route_decisions_and_scoped_source_audit(tmp_path):
    dataset, model_dir = write_bundle(tmp_path)
    report = run_heldout_route_benchmark(dataset, model_dir, tmp_path / "results")
    assert report["target_task_count"] == 3
    assert report["heldout_product_family_count"] == 1
    assert report["multi_step_route_improvement_proven"] is False
    assert report["review"]["kind"] == "automated_source_record_audit"
    assert report["quantity_compliance_proven"] is False
    assert report["candidate_pool_origin"] == "recorded_reactions_not_retrosynthetic_search"
    assert (tmp_path / "results" / "decisions.json").exists()
    evaluated = json.loads((tmp_path / "results" / "evaluated_decisions.json").read_text())
    assert all(record["source_record_match"] for record in evaluated)
    assert all(record["recorded_yield_percent"] is not None for record in evaluated)


def test_data_or_model_drift_rejected_before_evaluation(tmp_path):
    dataset, model_dir = write_bundle(tmp_path)
    dataset.write_text(dataset.read_text() + "\n")
    with pytest.raises(ValueError, match="dataset checksum"):
        run_heldout_route_benchmark(dataset, model_dir, tmp_path / "out")
    dataset, model_dir = write_bundle(tmp_path / "other")
    (model_dir / "condition_ranker.json").write_text("{}")
    with pytest.raises(ValueError, match="model checksum"):
        run_heldout_route_benchmark(dataset, model_dir, tmp_path / "out")


def test_invalid_reaction_and_overlapping_split_fail_closed(tmp_path):
    row = measured_fixture()[0]
    with pytest.raises(ValueError):
        build_inventory_tasks([{**row, "rxn": "CCO"}], [0], "fixture")
    dataset, model_dir = write_bundle(tmp_path)
    protocol_path = model_dir / "protocol.json"
    protocol = json.loads(protocol_path.read_text())
    protocol["split"]["row_indices"]["train"] += [3]
    protocol_path.write_text(json.dumps(protocol))
    with pytest.raises(ValueError, match="overlap"):
        run_heldout_route_benchmark(dataset, model_dir, tmp_path / "out")
