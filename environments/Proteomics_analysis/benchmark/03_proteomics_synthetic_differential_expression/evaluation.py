"""
Task 3 evaluator: differential expression.

Layers:
  1. gate         files, columns, 500 proteins, numeric p-values, log2fc on log2 scale with
                  sign = Treated - Control
  2. bookkeeping  significant matches the stated threshold (and FC cutoff), adj_p >= p,
                  manifest counts match the file
  3. detection    recall of truly changed proteins relative to a moderated t-test at the SAME
                  threshold, multiplied by the FDR score (power at controlled FDR)
  4. fdr          actual false-discovery proportion vs the stated threshold (must be <= 0.1)
  5. ranking      average precision of the p-value ranking, relative to the moderated reference
  6. effect       log2fc accuracy (relative to a plain mean difference) + direction of calls

Usage:
  python evaluation.py --input <protein_log2_normalized.csv> --results <results dir> \
                       --truth <folder with ground_truth.csv + meta.json> --out metrics_summary.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, special, stats
from sklearn.metrics import average_precision_score

WEIGHTS = {"detection": 0.30, "fdr": 0.25, "ranking": 0.15, "effect": 0.10, "bookkeeping": 0.20}
CTRL = ["Control_Rep1", "Control_Rep2", "Control_Rep3"]
TRT = ["Treated_Rep1", "Treated_Rep2", "Treated_Rep3"]
FDR_SLACK = 0.25   # an FDP this far above the stated threshold scores 0


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(q, 1)
    return out


def moderated_t(C, T):
    """limma-style empirical-Bayes moderated t-test (Smyth 2004), two groups, equal n."""
    nc, nt = C.shape[1], T.shape[1]
    d = nc + nt - 2
    s2 = (C.var(axis=1, ddof=1) * (nc - 1) + T.var(axis=1, ddof=1) * (nt - 1)) / d
    e = np.log(s2) - special.digamma(d / 2) + np.log(d / 2)
    v = e.var(ddof=1) - special.polygamma(1, d / 2)
    if v <= 0:
        s_post, df = np.full_like(s2, np.exp(e.mean())), 1e6
    else:
        d0 = 2 * optimize.brentq(lambda x: special.polygamma(1, x) - v, 1e-8, 1e8)
        s0 = np.exp(e.mean() + special.digamma(d0 / 2) - np.log(d0 / 2))
        s_post, df = (d0 * s0 + d * s2) / (d0 + d), d + d0
    t = (T.mean(axis=1) - C.mean(axis=1)) / np.sqrt(s_post * (1 / nc + 1 / nt))
    return 2 * stats.t.sf(np.abs(t), df)


def to_bool(s):
    m = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
    return s.astype(str).str.strip().str.lower().map(m)


def evaluate(input_csv, results_dir, truth_dir):
    res = Path(results_dir)
    X = pd.read_csv(input_csv, index_col=0)
    truth = pd.read_csv(Path(truth_dir) / "ground_truth.csv", index_col=0).loc[X.index]
    is_ch = truth["is_changed"].astype(bool).values
    true_fc = truth["true_log2fc"].values
    C, T = X[CTRL].values, X[TRT].values
    mean_diff = T.mean(axis=1) - C.mean(axis=1)
    report = {"gate": {"passed": False, "errors": []}, "sections": {}}
    err = report["gate"]["errors"]

    # ---------- 1. gate ----------
    dpath, jpath = res / "de_results.csv", res / "run_manifest.json"
    for p in (dpath, jpath):
        if not p.exists():
            err.append(f"missing file: {p.name}")
    if err:
        report["score"] = 0.0
        return report
    try:
        D = pd.read_csv(dpath)
        man = json.load(open(jpath))
    except Exception as e:
        err.append(f"parse error: {e}")
        report["score"] = 0.0
        return report
    need = ["protein_id", "log2fc", "p_value", "adj_p_value", "significant"]
    if [c for c in need if c not in D.columns]:
        err.append(f"de_results.csv missing columns {[c for c in need if c not in D.columns]}")
    elif not D["protein_id"].is_unique or set(D["protein_id"]) != set(X.index):
        err.append(f"de_results.csv must contain each of the {len(X)} input proteins exactly once")
    if not err:
        D = D.set_index("protein_id").loc[X.index]
        for c in ["log2fc", "p_value", "adj_p_value"]:
            D[c] = pd.to_numeric(D[c], errors="coerce")
            if D[c].isna().any():
                err.append(f"column {c} has {int(D[c].isna().sum())} missing/non-numeric values")
        sig = to_bool(D["significant"])
        if sig.isna().any():
            err.append("column significant must contain only True/False")
    if not err:
        for c in ["p_value", "adj_p_value"]:
            if ((D[c] < 0) | (D[c] > 1)).any():
                err.append(f"{c} has values outside [0, 1]")
        slope = float(np.polyfit(mean_diff, D["log2fc"].values, 1)[0])
        if slope < -0.5:
            err.append(f"log2fc sign is reversed (slope {slope:.2f}); expected Treated minus Control")
        elif not 0.8 <= slope <= 1.25:
            err.append(f"log2fc scale is {slope:.2f}x the log2 difference; check log base or units")
    if err:
        report["score"] = 0.0
        return report
    report["gate"]["passed"] = True
    sig = sig.values.astype(bool)
    p = D["p_value"].values
    adj = D["adj_p_value"].values
    fc = D["log2fc"].values

    # ---------- 2. bookkeeping ----------
    q = man.get("fdr_threshold")
    q_ok = isinstance(q, (int, float)) and not isinstance(q, bool) and 0 < q <= 0.1   # usual range 0.01-0.1
    q_used = float(q) if q_ok else 0.05
    cut = man.get("fold_change_cutoff")
    cut = float(cut) if isinstance(cut, (int, float)) and not isinstance(cut, bool) else 0.0
    expected_sig = (adj <= q_used + 1e-12) & (np.abs(fc) >= cut)
    ints = ["total_proteins", "n_significant", "n_up", "n_down"]
    checks = {
        "fdr_threshold_valid": q_ok,
        "significant_matches_threshold": bool((sig == expected_sig).all()),
        "adj_p_not_below_p": bool((adj >= p - 1e-9).all()),
        "total_proteins": man.get("total_proteins") == len(X),
        "n_significant": man.get("n_significant") == int(sig.sum()),
        "n_up": man.get("n_up") == int((sig & (fc > 0)).sum()),
        "n_down": man.get("n_down") == int((sig & (fc < 0)).sum()),
        "integer_types": all(isinstance(man.get(k), int) and not isinstance(man.get(k), bool) for k in ints),
    }
    report["sections"]["bookkeeping"] = {"score": round(sum(checks.values()) / len(checks), 4),
                                         "checks": checks,
                                         "rows_inconsistent_with_threshold": int((sig != expected_sig).sum())}

    # ---------- reference methods at the agent's threshold ----------
    ref_p = {"student_t": stats.ttest_ind(T, C, axis=1).pvalue,
             "welch_t": stats.ttest_ind(T, C, axis=1, equal_var=False).pvalue,
             "moderated_t": moderated_t(C, T)}

    def detect(s):
        tp = int((s & is_ch).sum()); fp = int((s & ~is_ch).sum()); fn = int((~s & is_ch).sum())
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        return {"tp": tp, "fp": fp, "fn": fn, "precision": round(prec, 4), "recall": round(rec, 4),
                "f1": round(f1, 4), "fdp": round(fp / (tp + fp), 4) if tp + fp else 0.0}

    refs = {k: {**detect(bh(v) <= q_used), "average_precision": round(average_precision_score(is_ch, -np.log10(v + 1e-300)), 4)}
            for k, v in ref_p.items()}
    best_ap = refs["moderated_t"]["average_precision"]
    ag = detect(sig)

    # ---------- 4. FDR control (computed first; detection depends on it) ----------
    fdp = ag["fdp"]
    n_called = max(int(sig.sum()), 1)
    # chance tolerance: with few calls the realised FDP fluctuates around the true FDR (~2 binomial SDs)
    tolerance = q_used + 2 * np.sqrt(q_used * (1 - q_used) / n_called)
    fdr_score = float(np.clip(1 - max(0.0, fdp - tolerance) / FDR_SLACK, 0, 1))
    report["sections"]["fdr"] = {
        "score": round(fdr_score, 4),
        "stated_threshold": q_used, "actual_false_discovery_proportion": fdp,
        "allowed_fdp_given_number_of_calls": round(float(tolerance), 4),
        "n_called": int(sig.sum()),
        "note": "penalises only exceeding the stated threshold; calling nothing scores 1 here but 0 on detection"}

    # ---------- 3. detection: power at controlled FDR ----------
    best_rec = refs["moderated_t"]["recall"]
    raw = ag["recall"] / best_rec if best_rec else 0.0
    report["sections"]["detection"] = {
        "score": round(float(np.clip(raw, 0, 1)) * fdr_score, 4),
        "recall_relative_to_moderated_t": round(raw, 4), "fdr_multiplier": round(fdr_score, 4), **ag,
        "true_changed": int(is_ch.sum()), "fdr_threshold_used": q_used,
        "note": "recall relative to a moderated t-test at your threshold, multiplied by the FDR score, "
                "so calls are credited only when false discoveries stay controlled"}

    # ---------- 5. ranking ----------
    ap_agent = float(average_precision_score(is_ch, -np.log10(np.clip(p, 1e-300, 1))))
    raw = ap_agent / best_ap if best_ap else 0.0
    report["sections"]["ranking"] = {"score": round(float(np.clip(raw, 0, 1)), 4),
                                     "unclipped_skill": round(raw, 4),
                                     "average_precision": round(ap_agent, 4)}

    # ---------- 6. effect sizes ----------
    rmse_agent = float(np.sqrt(np.mean((fc - true_fc) ** 2)))
    rmse_ref = float(np.sqrt(np.mean((mean_diff - true_fc) ** 2)))
    rmse_score = float(np.clip((2 * rmse_ref - rmse_agent) / rmse_ref, 0, 1))
    called_true = sig & is_ch
    direction = float((np.sign(fc[called_true]) == np.sign(true_fc[called_true])).mean()) if called_true.any() else None
    eff = rmse_score if direction is None else 0.5 * rmse_score + 0.5 * direction
    report["sections"]["effect"] = {"score": round(eff, 4), "log2fc_rmse": round(rmse_agent, 4),
                                    "reference_mean_difference_rmse": round(rmse_ref, 4),
                                    "direction_accuracy_on_true_calls": direction}

    report["reference_methods_at_your_threshold"] = refs
    rp = res / "analysis_report.txt"
    report["optional"] = {"analysis_report_present": rp.exists(),
                          "manifest_test_method": man.get("test_method"),
                          "manifest_multiple_testing_correction": man.get("multiple_testing_correction"),
                          "manifest_fold_change_cutoff": man.get("fold_change_cutoff")}
    report["score"] = round(sum(WEIGHTS[k] * report["sections"][k]["score"] for k in WEIGHTS), 4)
    report["weights"] = WEIGHTS
    return report


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
