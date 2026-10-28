"""Reproducible measured-yield training; final outcomes are evaluator-only."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
from rdkit import Chem, rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold
import sklearn
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .ranking import COMPONENTS, FEATURE_VERSION, MODEL_SCHEMA, condition_features, ConditionRanker

SEED = 20261027
MODEL_VERSION = "doyle-condition-ranker-0.1.0"
SOURCE = {
    "dataset": "GAUCHE DreherDoyle.csv",
    "url": "https://github.com/leojklarner/gauche/blob/main/gauche/datasets/reactions/DreherDoyle.csv",
    "paper_doi": "10.1126/science.aar5169",
    "paper_url": "https://doyle.chem.ucla.edu/wp-content/uploads/2020/07/43-Predicting-Reaction-Performance-in-C-N-Cross-Coupling-Using-Machine-Learning.pdf",
    "evidence_kind": "reported_high_throughput_measured_yield",
    "repository_license": "MIT",
    "license_url": "https://github.com/leojklarner/gauche/blob/main/LICENSE",
    "data_redistribution": "Raw data is not bundled; original experimental-data terms require review before redistribution.",
}


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def product_family(row: Mapping) -> str:
    reaction = row.get("rxn", "")
    parts = reaction.split(">")
    if len(parts) != 3 or not parts[-1]:
        raise ValueError("Reaction SMILES must include a product for grouped splitting")
    mol = Chem.MolFromSmiles(parts[-1])
    if mol is None:
        raise ValueError("Invalid product in grouped splitting")
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, isomericSmiles=True)


def grouped_split(rows: Sequence[Mapping], seed: int = SEED) -> dict[str, list[int]]:
    """Split by canonical product, keeping leaving-group variants together.

    The grouping and assignment inspect structures only. This is product-family
    isolation, not a claim of complete Murcko-scaffold isolation.
    """
    groups = [product_family(row) for row in rows]
    families = sorted(set(groups), key=lambda group: _digest([seed, group]))
    if len(families) < 5:
        raise ValueError("At least five distinct product families are required")
    n_holdout = max(1, len(families) // 5)
    assigned = {"test": set(families[:n_holdout]),
                "validation": set(families[n_holdout:2*n_holdout]),
                "train": set(families[2*n_holdout:])}
    return {name: [i for i, group in enumerate(groups) if group in assigned[name]]
            for name in ("train", "validation", "test")}


def export_forest(estimator, metadata: Mapping) -> dict:
    trees = [{
        "left": tree.tree_.children_left.tolist(),
        "right": tree.tree_.children_right.tolist(),
        "feature": tree.tree_.feature.tolist(),
        "threshold": tree.tree_.threshold.tolist(),
        "value": tree.tree_.value[:, 0, 0].tolist(),
    } for tree in estimator.estimators_]
    return {"schema_version": MODEL_SCHEMA, "feature_version": FEATURE_VERSION,
            "n_features": estimator.n_features_in_, "metadata": dict(metadata), "trees": trees}


def evaluate_selection(rows: Sequence[Mapping], predictions: Sequence[float], ks=(1, 5, 10)) -> dict:
    if len(rows) != len(predictions) or not rows:
        raise ValueError("Selection evaluation needs equal nonempty rows and predictions")
    if not np.all(np.isfinite(np.asarray(predictions, dtype=float))):
        raise ValueError("Predictions must be finite")
    grouped = defaultdict(list)
    for i, row in enumerate(rows):
        grouped[row["aryl halide"]].append(i)
    records = []
    for substrate, indices in sorted(grouped.items()):
        ordered = sorted(indices, key=lambda i: (
            -float(predictions[i]), _digest({c: rows[i].get(c) for c in COMPONENTS})))
        oracle = max(float(rows[i]["yield"]) for i in indices)
        record = {"substrate": substrate, "candidate_count": len(indices), "oracle_best_yield_percent": oracle}
        for k in ks:
            chosen = ordered[:k]
            selected = max(float(rows[i]["yield"]) for i in chosen)
            record[f"top_{k}_selected_best_yield_percent"] = selected
            record[f"top_{k}_simple_regret_percent"] = oracle - selected
            record[f"top_{k}_selected_row_indices"] = chosen
        records.append(record)
    result = {"substrate_count": len(records), "per_substrate": records,
              "metric_scope": "best measured yield after testing the selected k condition candidates"}
    for k in ks:
        result[f"top_{k}_mean_selected_yield_percent"] = float(np.mean(
            [r[f"top_{k}_selected_best_yield_percent"] for r in records]))
        result[f"top_{k}_mean_simple_regret_percent"] = float(np.mean(
            [r[f"top_{k}_simple_regret_percent"] for r in records]))
    return result


def _prediction_metrics(rows, predictions):
    actual = np.asarray([float(row["yield"]) for row in rows])
    return {"mae_yield_percent": float(mean_absolute_error(actual, predictions)),
            "rmse_yield_percent": float(np.sqrt(mean_squared_error(actual, predictions))),
            **evaluate_selection(rows, predictions)}


def _condition_mean_predictions(training_rows, evaluated_rows):
    groups = defaultdict(list)
    for row in training_rows:
        groups[tuple(row[c] for c in COMPONENTS[1:])].append(float(row["yield"]))
    mean = float(np.mean([float(r["yield"]) for r in training_rows]))
    return np.array([float(np.mean(groups[key])) if key in groups else mean
                     for key in (tuple(row[c] for c in COMPONENTS[1:]) for row in evaluated_rows)])


def _split_manifest(rows, splits):
    scaffold_sets = {}
    for name, indices in splits.items():
        scaffold_sets[name] = {MurckoScaffold.MurckoScaffoldSmiles(smiles=product_family(rows[i])) for i in indices}
    return {"seed": SEED, "group_by": "canonical_product_identity",
            "row_indices": splits,
            "product_families": {name: sorted({product_family(rows[i]) for i in indices})
                                 for name, indices in splits.items()},
            "substrates": {name: sorted({rows[i]["aryl halide"] for i in indices})
                           for name, indices in splits.items()},
            "scaffold_overlap_train_test": sorted(scaffold_sets["train"] & scaffold_sets["test"]),
            "is_scaffold_disjoint": not bool(scaffold_sets["train"] & scaffold_sets["test"])}


def train_and_evaluate(csv_path: str | Path, output_dir: str | Path) -> dict:
    """Train once, choose on validation only, then evaluate the frozen test set."""
    started = time.monotonic()
    source = Path(csv_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with source.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if any(not 0 <= float(row["yield"]) <= 100 for row in rows):
        raise ValueError("Measured yields must be finite percentages in [0, 100]")
    splits = grouped_split(rows)
    manifest = {**_split_manifest(rows, splits), "dataset_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "source": SOURCE, "row_count": len(rows)}
    configs = [{"n_estimators": 128, "max_depth": 18, "min_samples_leaf": leaf,
                "max_features": 1.0, "random_state": SEED, "n_jobs": 2} for leaf in (2, 8)]
    protocol = {"model_version": MODEL_VERSION, "split": manifest,
                "candidate_configs": configs, "selection_rule": "lowest validation top-1 regret, then validation MAE",
                "primary_metric": "test top-1 measured condition-selection regret versus training-condition mean",
                "test_tuning_allowed": False}
    # Persist protocol before fitting or evaluation, so the audit can inspect it.
    (output / "protocol.json").write_text(json.dumps(protocol, indent=2))
    partition = {name: [rows[i] for i in indices] for name, indices in splits.items()}
    x_train = condition_features(partition["train"])
    y_train = np.array([float(r["yield"]) for r in partition["train"]])
    x_validation = condition_features(partition["validation"])
    trials = []
    for config in configs:
        estimator = ExtraTreesRegressor(**config).fit(x_train, y_train)
        predictions = estimator.predict(x_validation)
        metrics = _prediction_metrics(partition["validation"], predictions)
        trials.append((metrics["top_1_mean_simple_regret_percent"], metrics["mae_yield_percent"],
                       estimator, predictions, config, metrics))
    winner = min(trials, key=lambda trial: trial[:2])
    _, _, estimator, validation_predictions, config, _ = winner
    residual = np.abs(np.asarray([float(r["yield"]) for r in partition["validation"]]) - validation_predictions)
    metadata = {"model_version": MODEL_VERSION, "dataset_sha256": manifest["dataset_sha256"],
                "validation_residual_q90": float(np.quantile(residual, 0.9, method="higher")),
                "training_component_smiles": {c: sorted({r[c] for r in partition["train"]}) for c in COMPONENTS},
                "training_row_count": len(y_train), "selected_config": config,
                "prediction_unit": "yield_percent", "source": SOURCE,
                "scope": "condition ranking in one measured C-N coupling dataset; not validated for multi-step synthesis"}
    artifact = export_forest(estimator, metadata)
    model_path = output / "condition_ranker.json"
    model_path.write_text(json.dumps(artifact, separators=(",", ":"), allow_nan=False))
    predictor = ConditionRanker.load(model_path)
    test_rows = partition["test"]
    predictions = np.asarray([r["predicted_yield_percent"] for r in predictor.predict(test_rows)])
    alternatives = {"new_model": predictions,
                    "training_condition_mean": _condition_mean_predictions(partition["train"], test_rows),
                    "training_global_mean": np.repeat(np.mean(y_train), len(test_rows))}
    metrics = {name: _prediction_metrics(test_rows, values) for name, values in alternatives.items()}
    improvement = (metrics["training_condition_mean"]["top_1_mean_simple_regret_percent"]
                   - metrics["new_model"]["top_1_mean_simple_regret_percent"])
    report = {"model_version": MODEL_VERSION, "created_at": datetime.now(timezone.utc).isoformat(),
              "data_manifest": manifest, "metrics": metrics,
              "validation_trials": [{"config": trial[4], "metrics": trial[5]} for trial in trials],
              "top_1_regret_improvement_percentage_points": improvement,
              "condition_decision_gate_passed": improvement > 0,
              "multi_step_route_improvement_proven": False,
              "independent_chemical_review_status": "pending",
              "limitations": ["Only one product family is in the final test set; substrate variants are correlated.",
                              "Product-family split is not necessarily Murcko-scaffold disjoint; overlap is reported.",
                              "Residual bands use the validation set also used for model selection; no coverage guarantee.",
                              "Ranking observed conditions does not establish route feasibility, impurity control, or scale-up success."],
              "runtime_seconds": time.monotonic() - started,
              "versions": {"python": platform.python_version(), "rdkit": rdBase.rdkitVersion,
                           "sklearn": sklearn.__version__, "numpy": np.__version__},
              "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest()}
    (output / "evaluation.json").write_text(json.dumps(report, indent=2, allow_nan=False))
    with (output / "heldout_predictions.jsonl").open("w") as handle:
        for i, row, prediction in zip(splits["test"], test_rows, predictions):
            record = {"dataset_row_index": i, "substrate": row["aryl halide"],
                      "measured_yield_percent": float(row["yield"]), "predicted_yield_percent": float(prediction),
                      "reaction_sha256": _digest(row["rxn"])}
            handle.write(json.dumps(record) + "\n")
    return report
