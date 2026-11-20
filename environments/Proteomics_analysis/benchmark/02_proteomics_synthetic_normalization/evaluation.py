"""
Task 2 evaluator: log2 + imputation + sample normalization.

All comparisons with the truth remove ONE global constant first (offset-invariant),
so centring on 0, aligning to the global median, etc. are all scored equally.

Layers:
  1. gate         files, schema, 250 rows, no NaN, log2 scale (checked by spread, not level)
  2. integrity    within each sample, observed values keep their order (Spearman >= 0.999)
  3. alignment    residual per-sample offset vs truth, relative to no normalization
  4. accuracy     offset-free RMSE on observed cells, relative to no normalization
  5. biology      Control-vs-Treated log2 fold changes preserved (systematic bias + distortion);
                  trap proteins reported separately
  6. imputation   RMSE on originally missing cells, relative to reference imputers
  7. bookkeeping  manifest consistent with files and input

Usage:
  python evaluation.py --input <raw_protein_intensities.csv> --results <results dir> \
                       --truth <folder with ground_truth_log2.csv + meta.json> --out metrics_summary.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import KNNImputer

WEIGHTS = {"alignment": 0.30, "biology": 0.25, "accuracy": 0.15,
           "integrity": 0.10, "imputation": 0.10, "bookkeeping": 0.10}
CTRL = ["Control_Rep1", "Control_Rep2", "Control_Rep3"]
TRT = ["Treated_Rep1", "Treated_Rep2", "Treated_Rep3"]
FC_BIAS_TOLERANCE = 1.0   # log2; a systematic fold-change bias this large scores 0


def rms(x):
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(x ** 2)))


def rel_score(agent_err, worst_err, best_err=0.0):
    if worst_err - best_err < 1e-12:
        return float(agent_err <= best_err + 1e-9)
    return float(np.clip((worst_err - agent_err) / (worst_err - best_err), 0, 1))


def finish(report):
    report["score"] = round(sum(WEIGHTS[k] * report["sections"].get(k, {}).get("score", 0.0)
                                for k in WEIGHTS), 4)
    report["weights"] = WEIGHTS
    return report


def evaluate(input_csv, results_dir, truth_dir):
    res = Path(results_dir)
    raw = pd.read_csv(input_csv, index_col=0)
    truth = pd.read_csv(Path(truth_dir) / "ground_truth_log2.csv", index_col=0).loc[raw.index]
    meta = json.load(open(Path(truth_dir) / "meta.json"))
    R = np.log2(raw)
    obs = R.notna()
    report = {"gate": {"passed": False, "errors": []}, "sections": {}}
    err = report["gate"]["errors"]

    # ---------- 1. gate ----------
    mpath, jpath = res / "normalized_matrix_log2.csv", res / "run_manifest.json"
    for p in (mpath, jpath):
        if not p.exists():
            err.append(f"missing file: {p.name}")
    if err:
        report["score"] = 0.0
        return report
    try:
        A = pd.read_csv(mpath, index_col=0)
        man = json.load(open(jpath))
    except Exception as e:
        err.append(f"parse error: {e}")
        report["score"] = 0.0
        return report
    if list(A.columns) != list(raw.columns):
        err.append(f"columns {list(A.columns)} != input columns {list(raw.columns)}")
    if not A.index.is_unique or set(A.index) != set(raw.index):
        err.append(f"matrix must contain each of the {len(raw)} input proteins exactly once")
    if not err and A.isna().values.any():
        err.append(f"matrix contains {int(A.isna().values.sum())} NaN cells")
    if not err:
        A = A.loc[raw.index]
        iqr = lambda d: d.quantile(0.75) - d.quantile(0.25)
        ratio = float((iqr(A) / iqr(truth)).median())
        if not 0.8 <= ratio <= 1.25:
            err.append(f"value spread is {ratio:.2f}x the expected log2 spread; "
                       "check log base (ln ~0.69x, log10 ~0.30x) or per-protein scaling")
    if err:
        report["score"] = 0.0
        return report
    report["gate"]["passed"] = True

    E = A - truth                                   # agent minus truth
    c = float(E.values[obs.values].mean())          # the one free global constant
    shift_none = (R - truth)                        # error of "no normalization"
    complete = obs.all(axis=1)
    fc = lambda M: M[TRT].mean(axis=1) - M[CTRL].mean(axis=1)
    fc_sd = float(fc(truth)[complete].std())

    def core_metrics(M):
        """Offset-free metrics for any normalized log2 matrix M (observed cells only)."""
        Em = M - truth
        cm = float(Em.values[obs.values].mean())
        d = np.array([np.median(Em[col][obs[col]]) for col in raw.columns])
        fe = (fc(M) - fc(truth))[complete]
        b = float(np.median(fe))
        return {"resid": d - d.mean(), "rmse": rms(Em.values[obs.values] - cm),
                "fc_bias": b, "fc_dist": rms(fe - b), "fc_err": fe}

    # reference methods applied to the KNN-imputed log2 input
    Rk = pd.DataFrame(KNNImputer(n_neighbors=5).fit_transform(R), index=R.index, columns=R.columns)
    ref_ref = np.sort(Rk.values, axis=0).mean(axis=1)
    ref_mats = {"median_centring": Rk - Rk.median(),
                "mean_centring": Rk - Rk.mean(),
                "quantile": Rk.rank(axis=0).apply(lambda col: np.interp(col, np.arange(1, len(ref_ref) + 1), ref_ref))}
    none = core_metrics(R.fillna(Rk))
    refs = {k: core_metrics(v) for k, v in ref_mats.items()}
    ag = core_metrics(A)
    # "best achievable" = best of the centring methods; quantile is reported for comparison only,
    # because it forces identical distributions and so looks perfectly "aligned" by construction.
    centring = [refs["median_centring"], refs["mean_centring"]]
    best = lambda key, f=lambda x: x: min(f(r[key]) for r in centring)
    ref_table = {k: {"rms_residual_offset": round(rms(r["resid"]), 4), "offset_free_rmse": round(r["rmse"], 4),
                     "fc_bias": round(r["fc_bias"], 4), "fc_distortion": round(r["fc_dist"], 4)}
                 for k, r in refs.items()}

    # ---------- 2. integrity ----------
    rhos = {}
    for col in raw.columns:
        m = obs[col]
        rhos[col] = float(spearmanr(A.loc[m, col], R.loc[m, col]).statistic)
    integ = float(np.mean([r >= 0.999 for r in rhos.values()]))
    const_shift = {col: float((A[col] - R[col])[obs[col]].std()) for col in raw.columns}
    report["sections"]["integrity"] = {
        "score": round(integ, 4), "spearman_vs_log2_input": {k: round(v, 5) for k, v in rhos.items()},
        "info_sd_of_per_sample_adjustment": {k: round(v, 4) for k, v in const_shift.items()},
        "info": "SD ~0 means a constant per-sample shift (median/mean centring); >0 means a shape-changing method (e.g. quantile)"}

    # Scores below: 0 = no normalization (or a fixed tolerance), 1 = best standard reference method.
    # ---------- 3. alignment ----------
    a_res = rms(ag["resid"])
    report["sections"]["alignment"] = {
        "score": round(rel_score(a_res, rms(none["resid"]), best("resid", rms)), 4),
        "rms_residual_offset": round(a_res, 4),
        "rms_offset_without_normalization": round(rms(none["resid"]), 4),
        "residual_sample_offsets_log2": dict(zip(raw.columns, np.round(ag["resid"], 3).tolist())),
        "sample_medians_after": A.median().round(3).to_dict()}

    # ---------- 4. accuracy ----------
    report["sections"]["accuracy"] = {
        "score": round(rel_score(ag["rmse"], none["rmse"], best("rmse")), 4),
        "offset_free_rmse_log2": round(ag["rmse"], 4),
        "rmse_without_normalization": round(none["rmse"], 4),
        "global_offset_removed": round(c, 3)}

    # ---------- 5. biology ----------
    bias_score = rel_score(abs(ag["fc_bias"]), FC_BIAS_TOLERANCE, best("fc_bias", abs))
    dist_score = rel_score(ag["fc_dist"], fc_sd, best("fc_dist"))
    trap = [t for t in meta["trap_ids"] if t in ag["fc_err"].index]
    report["sections"]["biology"] = {
        "score": round(0.5 * bias_score + 0.5 * dist_score, 4),
        "fold_change_bias_log2": round(ag["fc_bias"], 4),
        "fold_change_distortion_rms_log2": round(ag["fc_dist"], 4),
        "trap_protein_fc_error_log2": round(float(ag["fc_err"].loc[trap].mean()), 4) if trap else None,
        "note": "bias = systematic shift of all Treated-vs-Control ratios (e.g. total-sum normalization); "
                "distortion = protein-specific fold-change damage (e.g. quantile normalization on the trap proteins)"}
    report["reference_methods"] = ref_table

    # ---------- 6. imputation ----------
    miss = ~obs.values
    n_miss = int(miss.sum())
    if n_miss:
        agent_imp = rms(E.values[miss] - c)
        Rm = R - R.median()                       # reference imputers on median-centred input
        refs_frames = {
            "column_median": Rm.fillna(Rm.median()),
            "row_mean": Rm.T.fillna(Rm.mean(axis=1)).T,
            "knn_k5": pd.DataFrame(KNNImputer(n_neighbors=5).fit_transform(Rm), index=Rm.index, columns=Rm.columns)}
        refs = {}
        for k, F in refs_frames.items():
            Ef = F - truth
            refs[k] = rms(Ef.values[miss] - Ef.values[obs.values].mean())
        best = min(refs.values())
        report["sections"]["imputation"] = {
            "score": round(rel_score(agent_imp, refs["column_median"], best), 4),
            "n_scored_cells": n_miss, "agent_rmse_log2": round(agent_imp, 4),
            "reference_rmse_log2": {k: round(v, 4) for k, v in refs.items()}}
    else:
        report["sections"]["imputation"] = {"score": 1.0, "n_scored_cells": 0}

    # ---------- 7. bookkeeping ----------
    keys = ["total_input_proteins", "output_proteins", "imputed_value_cells"]
    checks = {
        "total_input_proteins": man.get("total_input_proteins") == len(raw),
        "output_proteins": man.get("output_proteins") == len(A),
        "imputed_value_cells": man.get("imputed_value_cells") == n_miss,
        "integer_types": all(isinstance(man.get(k), int) and not isinstance(man.get(k), bool) for k in keys)}
    report["sections"]["bookkeeping"] = {"score": round(sum(checks.values()) / len(checks), 4),
                                         "checks": checks, "expected_imputed_value_cells": n_miss}

    rp = res / "analysis_report.txt"
    report["optional"] = {"analysis_report_present": rp.exists(),
                          "manifest_normalization_method": man.get("normalization_method"),
                          "manifest_imputation_method": man.get("imputation_method"),
                          "manifest_processing_order": man.get("processing_order")}
    return finish(report)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--truth", required=True)
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args()
    rep = evaluate(a.input, a.results, a.truth)
    out = json.dumps(rep, indent=2, default=str)
    if a.out:
        Path(a.out).write_text(out)
    print(out)


if __name__ == "__main__":
    main()
