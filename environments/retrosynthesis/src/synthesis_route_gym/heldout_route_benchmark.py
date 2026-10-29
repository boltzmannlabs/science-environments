"""Frozen one-step route-and-condition decisions against recorded outcomes.

Candidates are supplied by the held-out reaction records, so this experiment
tests selection, not retrosynthetic retrieval or multi-step planning. Measured
outcomes are exported only after both selectors have written their decisions.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from rdkit import Chem

from .chemistry import canonical_smiles
from .model_training import product_family, SOURCE
from .ranking import COMPONENTS, ConditionRanker, rank_routes
from .schemas import Constraints, InventoryItem, MaterialUse, ReactionStep, RouteCandidate, Task
from .validation import assess_route


def _hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def _parse_reaction(row: Mapping):
    parts = row["rxn"].split(">")
    if len(parts) != 3 or not parts[0] or not parts[-1]:
        raise ValueError("Candidate reaction needs reactants and product")
    components = tuple(canonical_smiles(s) for side in parts[:2] for s in side.split(".") if s)
    roles = {role: canonical_smiles(row[role]) for role in COMPONENTS}
    if not set(roles.values()).issubset(components):
        raise ValueError("Condition role structures do not match the recorded reaction inputs")
    declared_agents = set(roles[c] for c in COMPONENTS[1:])
    reagents = tuple(s for s in components if s in declared_agents
                     or any(atom.GetSymbol() == "Pd" for atom in Chem.MolFromSmiles(s).GetAtoms()))
    reactants = tuple(s for s in components if s not in reagents)
    if not reactants:
        raise ValueError("No atom-contributing reactants remain in the candidate")
    return reactants, reagents, canonical_smiles(parts[-1]), roles


def build_inventory_tasks(rows: Sequence[Mapping], row_indices: Sequence[int], source_version: str) -> list[dict]:
    """Public chemical candidate export. Yield/label fields are never read."""
    if len(rows) != len(row_indices):
        raise ValueError("Candidate row indices must match chemical records")
    grouped = defaultdict(list)
    for row, row_index in zip(rows, row_indices):
        reactants, reagents, target, roles = _parse_reaction(row)
        step = ReactionStep(
            step_id=f"record-{row_index}", product=target,
            reactants=tuple(MaterialUse(smiles=s) for s in reactants),
            reagents=tuple(MaterialUse(smiles=s) for s in reagents),
            source_tool="gauche_recorded_reaction", source_version=source_version,
            conditions=("Role structures supplied by the recorded reaction dataset; operational details unresolved",),
            condition_inputs=roles, conditions_complete=False)
        route = RouteCandidate(route_id=f"doyle-row-{row_index}", target=target, steps=(step,))
        grouped[roles["aryl halide"]].append({
            "dataset_row_index": row_index,
            "selection_tie_key": _hash({c: row[c] for c in COMPONENTS}),
            "route": route.model_dump(mode="json", exclude_none=True)})
    pools = []
    for number, (substrate, candidates) in enumerate(sorted(grouped.items()), start=1):
        targets = {candidate["route"]["target"] for candidate in candidates}
        if len(targets) != 1:
            raise ValueError("Each substrate task must have exactly one target product")
        stock = sorted({use["smiles"] for candidate in candidates
                        for step in candidate["route"]["steps"]
                        for use in step["reactants"] + step["reagents"]})
        task = Task(task_id=f"doyle-heldout-inventory-{number}", target=next(iter(targets)),
                    constraints=Constraints(max_steps=1),
                    inventory=tuple(InventoryItem(smiles=s, source="frozen candidate material inventory") for s in stock))
        pools.append({"task": task.model_dump(mode="json"), "substrate": substrate,
                      "inventory_scope": "structural availability; quantities and prices unknown",
                      "candidates": candidates})
    return pools


def _training_condition_means(training_rows):
    grouped = defaultdict(list)
    for row in training_rows:
        key = tuple(canonical_smiles(row[c]) for c in COMPONENTS[1:])
        value = float(row["yield"])
        if not np.isfinite(value) or not 0 <= value <= 100:
            raise ValueError("Training yields must be finite percentages")
        grouped[key].append(value)
    if not grouped:
        raise ValueError("Training-condition baseline requires training outcomes")
    return {key: float(np.mean(values)) for key, values in grouped.items()}, float(np.mean(
        [float(row["yield"]) for row in training_rows]))


def select_route_decisions(pools: Sequence[Mapping], training_rows: Sequence[Mapping], model: ConditionRanker) -> dict:
    """Both arms see identical public pools; only training outcomes are accepted."""
    means, default_mean = _training_condition_means(training_rows)
    arms = {"learned_yield_route_utility": [], "training_condition_mean_route_utility": []}
    gates = []
    for pool in pools:
        task = Task.model_validate(pool["task"])
        candidates = list(pool["candidates"])
        routes = [RouteCandidate.model_validate(candidate["route"]) for candidate in candidates]
        assessments = [assess_route(task, route) for route in routes]
        gates.extend({"task_id": task.task_id, **a.model_dump(mode="json")} for a in assessments)
        condition_rows = [dict(route.steps[0].condition_inputs) for route in routes]
        predicted = model.predict(condition_rows)
        estimates = {
            "learned_yield_route_utility": [item["predicted_yield_percent"] for item in predicted],
            "training_condition_mean_route_utility": [means.get(tuple(row[c] for c in COMPONENTS[1:]), default_mean)
                                                      for row in condition_rows],
        }
        for arm, values in estimates.items():
            records = [{"route_id": route.route_id, "steps": [{"predicted_yield": value / 100}],
                        "graph_valid": assessment.graph_valid, "inventory_complete": assessment.inventory_complete,
                        "constraint_compliant": assessment.constraint_compliant}
                       for route, value, assessment in zip(routes, values, assessments)]
            utilities = {record["route_id"]: record for record in rank_routes(records)}
            ordered = sorted(candidates, key=lambda candidate: (
                -utilities[candidate["route"]["route_id"]]["score"], candidate["selection_tie_key"]))
            eligible = [candidate for candidate in ordered if utilities[candidate["route"]["route_id"]]["eligible"]]
            ids = [candidate["route"]["route_id"] for candidate in eligible]
            arms[arm].append({
                "task_id": task.task_id, "candidate_count": len(candidates), "eligible_count": len(eligible),
                "candidate_pool_sha256": _hash(pool), "top_1_route_ids": ids[:1], "top_5_route_ids": ids[:5],
                "all_ranked_route_ids": ids, "route_utility_kind": "declared_surrogate_heuristic",
                "uses_learned_yield_model": arm == "learned_yield_route_utility",
            })
    return {"arms": arms, "candidate_gates": gates,
            "equal_candidate_pool": True, "hidden_test_labels_in_selector": False}


def _load_frozen_inputs(dataset: Path, model_dir: Path):
    protocol = json.loads((model_dir / "protocol.json").read_text())
    original = json.loads((model_dir / "evaluation.json").read_text())
    dataset_hash = hashlib.sha256(dataset.read_bytes()).hexdigest()
    model_path = model_dir / "condition_ranker.json"
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if dataset_hash != protocol["split"]["dataset_sha256"]:
        raise ValueError("Frozen dataset checksum mismatch")
    if model_hash != original["model_sha256"]:
        raise ValueError("Frozen model checksum mismatch")
    with dataset.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    splits = protocol["split"]["row_indices"]
    all_indices = [i for name in ("train", "validation", "test") for i in splits[name]]
    if len(set(all_indices)) != len(all_indices):
        raise ValueError("Frozen split has row overlap")
    if set(all_indices) != set(range(len(rows))):
        raise ValueError("Frozen split must cover dataset exactly")
    groups = {name: {product_family(rows[i]) for i in indices} for name, indices in splits.items()}
    if any(groups[a] & groups[b] for a, b in (("train", "test"), ("train", "validation"), ("validation", "test"))):
        raise ValueError("Frozen split has product-family overlap")
    return rows, splits, ConditionRanker.load(model_path), dataset_hash, model_hash


def _evaluate_decisions(pools, decisions, rows):
    evaluated, summaries = [], {}
    lookup = {candidate["route"]["route_id"]: candidate for pool in pools for candidate in pool["candidates"]}
    for arm, task_decisions in decisions["arms"].items():
        per_task = []
        for decision in task_decisions:
            pool = next(pool for pool in pools if pool["task"]["task_id"] == decision["task_id"])
            oracle = max(float(rows[c["dataset_row_index"]]["yield"]) for c in pool["candidates"])
            metrics = {"task_id": decision["task_id"], "oracle_best_recorded_yield_percent": oracle}
            for k in (1, 5):
                selected = decision[f"top_{k}_route_ids"]
                values = [float(rows[lookup[route_id]["dataset_row_index"]]["yield"]) for route_id in selected]
                best = max(values) if values else None
                metrics[f"top_{k}_best_recorded_yield_percent"] = best
                metrics[f"top_{k}_simple_regret_percent"] = None if best is None else oracle - best
            for route_id in decision["top_5_route_ids"]:
                candidate = lookup[route_id]
                row_index = candidate["dataset_row_index"]
                reactants, reagents, product, roles = _parse_reaction(rows[row_index])
                step = RouteCandidate.model_validate(candidate["route"]).steps[0]
                match = (step.product == product and tuple(u.smiles for u in step.reactants) == reactants
                         and tuple(u.smiles for u in step.reagents) == reagents and dict(step.condition_inputs) == roles)
                evaluated.append({"arm": arm, "task_id": decision["task_id"], "route_id": route_id,
                                  "recorded_yield_percent": float(rows[row_index]["yield"]),
                                  "source_record_match": match, "source_locator": f"DreherDoyle.csv data row {row_index + 1}",
                                  "evidence_kind": "reported_high_throughput_measured_yield",
                                  "source": SOURCE["url"], "quantity_compliance_proven": False})
            per_task.append(metrics)
        summaries[arm] = {"per_task": per_task}
        for k in (1, 5):
            values = [m[f"top_{k}_best_recorded_yield_percent"] for m in per_task]
            regrets = [m[f"top_{k}_simple_regret_percent"] for m in per_task]
            summaries[arm][f"top_{k}_mean_selected_yield_percent"] = None if None in values else float(np.mean(values))
            summaries[arm][f"top_{k}_mean_simple_regret_percent"] = None if None in regrets else float(np.mean(regrets))
    return evaluated, summaries


def run_heldout_route_benchmark(dataset: str | Path, model_dir: str | Path, output_dir: str | Path) -> dict:
    started = time.monotonic()
    rows, splits, model, dataset_hash, model_hash = _load_frozen_inputs(Path(dataset), Path(model_dir))
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    chemical_rows = [{key: rows[i][key] for key in (*COMPONENTS, "rxn")} for i in splits["test"]]
    pools = build_inventory_tasks(chemical_rows, splits["test"], dataset_hash[:16])
    _write(output / "candidate_pools.json", pools)
    decisions = select_route_decisions(pools, [rows[i] for i in splits["train"]], model)
    _write(output / "decisions.json", decisions)
    # The selectors have finished before any held-out measured yields are read.
    evaluated, metrics = _evaluate_decisions(pools, decisions, rows)
    _write(output / "evaluated_decisions.json", evaluated)
    learned = metrics["learned_yield_route_utility"]["top_1_mean_selected_yield_percent"]
    baseline = metrics["training_condition_mean_route_utility"]["top_1_mean_selected_yield_percent"]
    report = {
        "schema_version": "heldout-route-decisions.v1", "model_version": model.metadata.get("model_version"),
        "dataset_sha256": dataset_hash, "model_sha256": model_hash,
        "target_task_count": len(pools), "heldout_product_family_count": len({pool["task"]["target"] for pool in pools}),
        "candidate_count": sum(len(pool["candidates"]) for pool in pools),
        "candidate_pool_origin": "recorded_reactions_not_retrosynthetic_search",
        "evaluation_relationship": "same_frozen_test_reexpressed_through_route_contracts_not_new_independent_test",
        "selection_scope": "one-step route-and-condition selection on correlated substrate inventories",
        "equal_candidate_pool": True, "model_retrained_or_tuned": False,
        "metrics": metrics, "top_1_gain_percentage_points": None if learned is None or baseline is None else learned - baseline,
        "quantity_compliance_proven": False, "multi_step_route_improvement_proven": False,
        "review": {"kind": "automated_source_record_audit", "selected_record_matches": sum(e["source_record_match"] for e in evaluated),
                   "selected_records": len(evaluated), "human_review": False,
                   "unique_source_records": len({e["source_locator"] for e in evaluated}),
                   "scope": "Frozen-file checksum, molecular structures, role identities, inventory gates, and reported yield lookup"},
        "limitations": ["One held-out product family; three correlated halide inventories are not independent chemical families.",
                        "Known recorded candidates are supplied; no retrosynthetic discovery is tested.",
                        "Quantities, stoichiometry, operational conditions, cost and scale-up are unresolved.",
                        "Top-5 baseline can beat the new model; all signed differences are retained.",
                        "Automated source audit confirms record correspondence, not experimental reproduction or general feasibility."],
        "runtime_seconds": time.monotonic() - started,
    }
    _write(output / "summary.json", report)
    return report
