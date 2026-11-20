"""
Task 1 evaluator: QC + log2 + imputation.

Layers:
  1. gate          files exist, schema valid, values on log2 scale (fail -> score 0)
  2. integrity     observed input cells equal log2(raw)
  3. bookkeeping   manifest consistent with files and input
  4. qc            spikes excluded (recall); adequately-measured proteins kept (coverage)
  5. imputation    RMSE on originally-missing cells, scored relative to reference methods
                   computed on the SAME retained rows (naive = 0, best reference = 1)

Usage:
  python evaluation.py --input tasks/task1/inputs/raw_protein_intensities.csv \
                       --results results --truth benchmark/task1 \
                       --out benchmark/task1/metrics_summary.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer

WEIGHTS = {"integrity": 0.15, "bookkeeping": 0.15, "qc": 0.25, "imputation": 0.45}
REASONS = {"excessive_missing_values", "no_valid_values"}
MIN_OBS_FOR_COVERAGE = 3   # proteins with >= 3/6 valid values should normally be retained


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def reference_imputations(log_in):
    """Standard methods applied to the agent's retained rows (log2 input with NaNs)."""
    col_med = log_in.fillna(log_in.median())
    row_mean = log_in.T.fillna(log_in.mean(axis=1)).T.fillna(log_in.median())
    knn = pd.DataFrame(KNNImputer(n_neighbors=5).fit_transform(log_in),
                       index=log_in.index, columns=log_in.columns)
    # Perseus-style down-shift: per sample, mean - 1.8 SD (deterministic centre of the draw)
    down = log_in.fillna(log_in.mean() - 1.8 * log_in.std())
    return {"column_median": col_med, "row_mean": row_mean, "knn_k5": knn, "downshift_1.8sd": down}


def evaluate(input_csv, results_dir, truth_dir):
    res = Path(results_dir)
    raw = pd.read_csv(input_csv, index_col=0)
    truth = pd.read_csv(Path(truth_dir) / "ground_truth_log2.csv", index_col=0)
    meta = json.load(open(Path(truth_dir) / "meta.json"))
    spikes = set(meta["spike_ids"])
    log_raw = np.log2(raw)
    report = {"gate": {"passed": False, "errors": []}, "sections": {}}
    err = report["gate"]["errors"]

    # ---------- 1. gate ----------
    files = {k: res / k for k in ["imputed_matrix_log2.csv", "protein_qc.csv", "run_manifest.json"]}
    for k, p in files.items():
        if not p.exists():
            err.append(f"missing file: {k}")
    if err:
        report["score"] = 0.0
        return report
    try:
        mat = pd.read_csv(files["imputed_matrix_log2.csv"], index_col=0)
        qc = pd.read_csv(files["protein_qc.csv"], dtype=str, keep_default_na=False)
        man = json.load(open(files["run_manifest.json"]))
    except Exception as e:  # unreadable files
        err.append(f"parse error: {e}")
        report["score"] = 0.0
        return report

    if list(mat.columns) != list(raw.columns):
        err.append(f"matrix columns {list(mat.columns)} != input columns {list(raw.columns)}")
    if mat.isna().values.any():
        err.append(f"matrix contains {int(mat.isna().values.sum())} NaN cells")
    if not mat.index.is_unique:
        err.append("duplicate protein IDs in matrix")
    unknown = set(mat.index) - set(raw.index)
    if unknown:
        err.append(f"{len(unknown)} matrix IDs not in input")
    med = float(np.nanmedian(mat.values)) if mat.size else float("nan")
    lo_ok, hi_ok = np.nanmedian(log_raw.values) - 2, np.nanmedian(log_raw.values) + 2
    if not (lo_ok <= med <= hi_ok):
        err.append(f"matrix median {med:.2f} not on log2 scale (expected ~{np.nanmedian(log_raw.values):.1f}); "
                   "check log base / pseudocount / extra normalisation")
    need = {"protein_id", "status", "exclusion_reason"}
    if not need.issubset(qc.columns):
        err.append(f"protein_qc.csv missing columns {need - set(qc.columns)}")
    elif set(qc["protein_id"]) != set(raw.index) or len(qc) != len(raw):
        err.append(f"protein_qc.csv must list each of the {len(raw)} input IDs exactly once")
    if err:
        report["score"] = 0.0
        return report
    report["gate"]["passed"] = True
    qc = qc.set_index("protein_id")
    retained = set(qc.index[qc["status"] == "retained"])
    excluded = set(qc.index[qc["status"] == "excluded"])

    # ---------- 2. integrity ----------
    lr = log_raw.loc[mat.index]
    obs = lr.notna().values
    diff = np.abs(mat.values[obs] - lr.values[obs])
    altered = int((diff > 1e-6).sum())
    integrity = 1.0 - altered / max(int(obs.sum()), 1)
    report["sections"]["integrity"] = {"score": round(integrity, 4), "observed_cells": int(obs.sum()),
                                       "altered_cells": altered, "max_abs_diff": float(diff.max())}

    # ---------- 3. bookkeeping ----------
    n_missing_in_matrix = int(lr.isna().values.sum())
    checks = {
        "status_values_valid": set(qc["status"]) <= {"retained", "excluded"},
        "reasons_valid": bool((qc.loc[list(excluded), "exclusion_reason"].isin(REASONS)).all()
                              and (qc.loc[list(retained), "exclusion_reason"] == "").all()),
        "qc_retained_matches_matrix": retained == set(mat.index),
        "total_input_proteins": man.get("total_input_proteins") == len(raw),
        "retained_proteins": man.get("retained_proteins") == len(mat),
        "excluded_proteins": man.get("excluded_proteins") == len(excluded),
        "imputed_value_cells": man.get("imputed_value_cells") == n_missing_in_matrix,
        "integer_types": all(isinstance(man.get(k), int) and not isinstance(man.get(k), bool)
                             for k in ["total_input_proteins", "retained_proteins",
                                       "excluded_proteins", "imputed_value_cells"]),
    }
    report["sections"]["bookkeeping"] = {"score": round(sum(checks.values()) / len(checks), 4),
                                         "checks": checks,
                                         "expected_imputed_value_cells": n_missing_in_matrix}

    # ---------- 4. qc ----------
    n_obs = raw.notna().sum(axis=1)
    should_keep = set(n_obs[(n_obs >= MIN_OBS_FOR_COVERAGE)].index) - spikes
    spike_recall = len(spikes & excluded) / len(spikes)
    coverage = len(should_keep & retained) / len(should_keep)
    report["sections"]["qc"] = {"score": round(0.5 * spike_recall + 0.5 * coverage, 4),
                                "spike_exclusion_recall": round(spike_recall, 4),
                                "coverage_of_well_measured": round(coverage, 4),
                                "retained": len(retained), "excluded": len(excluded),
                                "spikes_retained": sorted(spikes & retained)}

    # ---------- 5. imputation ----------
    rows = [p for p in mat.index if p in truth.index]
    miss = lr.loc[rows].isna()
    t = truth.loc[rows].values[miss.values]
    if miss.values.sum() == 0:
        report["sections"]["imputation"] = {"score": 0.0, "note": "no imputed cells to score",
                                            "n_scored_cells": 0, "agent_rmse_log2": None}
        report["score"] = round(sum(WEIGHTS[k] * report["sections"][k]["score"] for k in WEIGHTS), 4)
        report["weights"] = WEIGHTS
        return report
    agent_vals = mat.loc[rows].values[miss.values]
    agent_rmse = rmse(agent_vals, t)
    ref_frames = reference_imputations(lr.loc[rows])
    refs = {k: rmse(v.loc[rows].values[miss.values], t) for k, v in ref_frames.items()}
    ref_bias = {k: round(float(np.mean(v.loc[rows].values[miss.values] - t)), 4)
                for k, v in ref_frames.items()}
    naive, best = refs["column_median"], min(refs.values())
    if naive - best < 1e-9:
        imp_score, note = float(agent_rmse <= naive), "references indistinguishable"
    else:
        raw_skill = (naive - agent_rmse) / (naive - best)
        imp_score, note = float(np.clip(raw_skill, 0, 1)), f"unclipped skill {raw_skill:.3f}"
    report["sections"]["imputation"] = {
        "score": round(imp_score, 4), "note": note, "n_scored_cells": int(miss.values.sum()),
        "agent_rmse_log2": round(agent_rmse, 4),
        "agent_bias_log2": round(float(np.mean(agent_vals - t)), 4),
        "reference_rmse_log2": {k: round(v, 4) for k, v in refs.items()},
        "reference_bias_log2": ref_bias,
        "legacy_score_1_over_1_plus_rmse": round(1 / (1 + agent_rmse), 4)}

    # ---------- optional report (recorded, not scored) ----------
    rp = res / "analysis_report.txt"
    report["optional"] = {"analysis_report_present": rp.exists(),
                          "analysis_report_chars": len(rp.read_text()) if rp.exists() else 0,
                          "manifest_filter_rule": man.get("filter_rule"),
                          "manifest_imputation_method": man.get("imputation_method")}

    report["score"] = round(sum(WEIGHTS[k] * report["sections"][k]["score"] for k in WEIGHTS), 4)
    report["weights"] = WEIGHTS
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--truth", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rep = evaluate(a.input, a.results, a.truth)
    out = json.dumps(rep, indent=2, default=str)
    if a.out:
        Path(a.out).write_text(out)
    print(out)


if __name__ == "__main__":
    main()
