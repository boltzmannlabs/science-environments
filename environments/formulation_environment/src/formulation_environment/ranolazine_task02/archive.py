"""Verify immutable Task-02 evidence and arithmetic; never refit or invent data."""
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
import csv
import hashlib
import json
import math

NAME = "task-02-ranolazine-er-dissolution"


def _equal(actual, expected, label):
    if not math.isfinite(actual) or not math.isclose(actual, expected, abs_tol=1e-10, rel_tol=1e-10):
        raise ValueError("Metric mismatch: " + label)


def verify_contract(environment, contract):
    """Read-only hash, folder, split-count and saved-metric consistency checks.

    Recomputing macro averages from archived fold errors does not independently
    reproduce training, model selection or the underlying source transcription.
    """
    environment = Path(environment).resolve()
    for section, relative in contract["folders"].items():
        if not (environment / relative).is_dir():
            raise ValueError("Missing task directory: " + section)
    checked = []
    targets = {contract["input"]["path"]: contract["input"]["sha256"], **contract["artifacts"]}
    for relative, expected in targets.items():
        file = environment / relative
        observed = hashlib.sha256(file.read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError("Source hash mismatch: " + relative)
        checked.append({"path": relative, "sha256": observed})
    outputs = environment / contract["folders"]["results"]
    comparison = json.loads((outputs / "literature_model_comparison.json").read_text())
    if comparison["input_sha256"] != contract["input"]["sha256"]:
        raise ValueError("Comparison input identity mismatch")
    if set(comparison["groups"]) != set(contract["groups"]):
        raise ValueError("Unexpected literature groups")
    metric_checks = 0
    for group_id, expected_count in contract["groups"].items():
        group = comparison["groups"][group_id]
        if group["n_profiles"] != expected_count or len(group["folds"]) != expected_count:
            raise ValueError("Unexpected profile count: " + group_id)
        if {f["profile_id"] for f in group["folds"]} != set(group["profile_ids"]):
            raise ValueError("Fold identity mismatch: " + group_id)
        for fold in group["folds"]:
            if fold["n_train_profiles"] != expected_count - 1:
                raise ValueError("Unexpected training count")
        for model, metrics in group["macro_profile_metrics"].items():
            for metric, value in metrics.items():
                _equal(mean(f["models"][model][metric] for f in group["folds"]), value, group_id + model + metric)
                metric_checks += 1
        for policy, metrics in group["nested_model_selection_outer_metrics"].items():
            folds = group["nested_outer_folds"][policy]
            if len(folds) != expected_count:
                raise ValueError("Unexpected nested fold count")
            for metric in ("mae_pp", "rmse_pp", "bias_pp"):
                _equal(mean(f[metric] for f in folds), metrics[metric], group_id + policy + metric)
                metric_checks += 1
    with (outputs / "literature_model_comparison.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    expected_rows = sum(len(g["macro_profile_metrics"]) for g in comparison["groups"].values())
    if len(rows) != expected_rows:
        raise ValueError("CSV model count mismatch")
    for row in rows:
        metrics = comparison["groups"][row["group"]]["macro_profile_metrics"][row["model"]]
        for column, metric in [("macro_profile_MAE_pp", "mae_pp"), ("macro_profile_RMSE_pp", "rmse_pp"), ("macro_profile_bias_pp", "bias_pp")]:
            _equal(float(row[column]), metrics[metric], column)
            metric_checks += 1
    baseline = json.loads((outputs / "existing_lofo_rerun.json").read_text())
    if baseline["verifier_findings"] or baseline["status"] != "evaluated_descriptive_only":
        raise ValueError("Archived baseline verification failed")
    return {"status": "ARCHIVE_CONSISTENCY_VERIFIED", "scope": "saved_artifact_hashes_and_aggregate_arithmetic_only_not_scientific_reexecution", "checked_artifacts": checked, "metric_checks": metric_checks, "groups": contract["groups"], "candidate_lab_observations": 0, "new_candidate_recipe_predictions": 0, "product_validation": "NOT_EVALUATED"}


def run_task02(input_dir, output_dir):
    """Validate an archive into a new directory; never overwrite prior runs."""
    config = Path(input_dir).resolve()
    environment = config.parents[1]
    contract = json.loads((config / "contract.json").read_text())
    output = Path(output_dir).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory is not empty; use a new run directory")
    result = verify_contract(environment, contract)
    output.mkdir(parents=True, exist_ok=True)
    result["checked_utc"] = datetime.now(timezone.utc).isoformat()
    (output / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
