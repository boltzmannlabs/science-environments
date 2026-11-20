"""
Task 7 evaluator: end-to-end analysis of UPS1 spiked into yeast (Ramus et al. 2016, PXD001819),
three contrasts of increasing difficulty.

Truth (from the sample composition):
  * UPS1 protein groups ('_UPS' in Fasta headers): changed, true log2fc = log2(high/low amount)
  * yeast protein groups: unchanged
  Groups flagged by MaxQuant (reverse / potential contaminant / only identified by site) are not
  scored, so removing them is never penalised (two UPS1 proteins are flagged as contaminants).
  Recall denominator: unflagged UPS1 groups with >=2 valid LFQ values at the higher amount.

Per contrast (C1 25000 vs 2500, C2 5000 vs 500, C3 2500 vs 500):
  detection    UPS1 recall relative to the best reference pipeline (highest F1), x FDR score
  fdr          false-discovery proportion vs the larger of (stated threshold + chance tolerance)
               and (best reference's FDP + 0.05), since low-abundance contrasts cannot reach 5%
  fold_change  median UPS1 log2fc vs the best reference's error (real data compresses ratios),
               plus yeast median log2fc ~ 0
Overall: contrasts weighted C1 0.25 / C2 0.40 / C3 0.35, scaled to 0.85; cleaning 0.05; bookkeeping 0.10.

Usage:
  python evaluation.py --input <proteinGroups.txt> --results <results dir> --out metrics_summary.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reference_pipelines as rp  # noqa: E402

CONTRAST_WEIGHTS = {"C1": 0.25, "C2": 0.40, "C3": 0.35}
SECTION_WEIGHTS = {"detection": 0.5, "fdr": 0.3, "fold_change": 0.2}
TOP = {"contrasts": 0.85, "cleaning": 0.05, "bookkeeping": 0.10}
FDR_SLACK = 0.25
FC_TOL = 1.5


def to_bool(s):
    m = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
    return s.astype(str).str.strip().str.lower().map(m)


def evaluate(input_txt, results_dir):
    res = Path(results_dir)
    pg = pd.read_csv(input_txt, sep="\t", low_memory=False)
    fl = rp.flagged(pg)
    info = pg.set_index("Protein IDs")
    ups_map = pg.set_index("Protein IDs")["Fasta headers"].map(rp.is_ups)
    flag_map = pd.Series(fl.values, index=pg["Protein IDs"].values)
    report = {"gate": {"passed": False, "errors": []}, "contrasts": {}, "sections": {}}
    err = report["gate"]["errors"]

    # ---------- gate ----------
    dpath, jpath = res / "de_results.csv", res / "run_manifest.json"
    for p in (dpath, jpath):
        if not p.exists():
            err.append(f"missing file: {p.name}")
    if err:
        report["score"] = 0.0
        return report
    try:
        D = pd.read_csv(dpath); man = json.load(open(jpath))
    except Exception as e:
        err.append(f"parse error: {e}"); report["score"] = 0.0
        return report
    need = ["contrast", "protein_id", "log2fc", "p_value", "adj_p_value", "significant", "call_basis"]
    miss = [c for c in need if c not in D.columns]
    if miss:
        err.append(f"de_results.csv missing columns {miss}")
    if not err:
        D["protein_id"] = D["protein_id"].astype(str); D["contrast"] = D["contrast"].astype(str).str.strip()
        if set(D.contrast) - set(rp.CONTRASTS):
            err.append(f"unknown contrast labels {sorted(set(D.contrast) - set(rp.CONTRASTS))}")
        for c in rp.CONTRASTS:
            if c not in set(D.contrast):
                err.append(f"no rows for contrast {c}")
        if D.duplicated(["contrast", "protein_id"]).any():
            err.append("duplicate (contrast, protein_id) rows")
        bad = set(D.protein_id) - set(info.index)
        if bad:
            err.append(f"{len(bad)} protein_id values not found in the input 'Protein IDs'")
        D["call_basis"] = D["call_basis"].astype(str).str.strip()
        if set(D.call_basis) - {"test", "presence_absence"}:
            err.append("call_basis must be 'test' or 'presence_absence'")
    if not err:
        for c in ["log2fc", "p_value", "adj_p_value"]:
            D[c] = pd.to_numeric(D[c], errors="coerce")
            bad_na = D[c].isna() & (D.call_basis == "test")
            if bad_na.any():
                err.append(f"{c} missing in {int(bad_na.sum())} test-based rows")
        sig = to_bool(D["significant"])
        if sig.isna().any():
            err.append("column significant must contain only True/False")
        if ((D[["p_value", "adj_p_value"]] < 0) | (D[["p_value", "adj_p_value"]] > 1)).any().any():
            err.append("p-values outside [0, 1]")
    if not err:
        D["sig"] = sig.values.astype(bool)
        D["ups"] = ups_map.loc[D.protein_id].values
        D["flag"] = flag_map.loc[D.protein_id].values
        c1 = D[(D.contrast == "C1") & D.log2fc.notna()]
        sep = c1.loc[c1.ups, "log2fc"].median() - c1.loc[~c1.ups, "log2fc"].median()
        if not np.isfinite(sep) or sep < 0:
            err.append(f"C1 log2fc of UPS1 vs yeast is {sep:.2f}; expected positive (higher minus lower amount)")
    if err:
        report["score"] = 0.0
        return report
    report["gate"]["passed"] = True

    q = man.get("fdr_threshold")
    q_ok = isinstance(q, (int, float)) and not isinstance(q, bool) and 0 < q <= 0.1
    q_used = float(q) if q_ok else 0.05

    # ---------- per contrast ----------
    total = 0.0
    for cname, (hi, lo) in rp.CONTRASTS.items():
        Xh = np.log2(pg[rp.cols(hi)].replace(0, np.nan).astype(float))
        detectable = (~fl.values) & pg["Fasta headers"].map(rp.is_ups).values & (Xh.notna().sum(axis=1) >= 2).values
        n_ups = int(detectable.sum())
        A = D[(D.contrast == cname) & ~D.flag]
        tp, fp = int((A.sig & A.ups).sum()), int((A.sig & ~A.ups).sum())
        # references
        refs = {}
        for rname, kw in rp.REFERENCES.items():
            r = rp.run(pg, cname, **kw)
            u = ups_map.loc[r.protein_id].values
            rtp, rfp = int((r.significant.values & u).sum()), int((r.significant.values & ~u).sum())
            refs[rname] = {"tp": rtp, "fp": rfp, "recall": round(rtp / n_ups, 4), "fdp": round(rfp / max(rtp + rfp, 1), 4),
                           "median_ups_log2fc": round(float(np.nanmedian(r.log2fc[u])), 3) if np.isfinite(r.log2fc[u]).any() else None}
        for v in refs.values():
            prec = v["tp"] / max(v["tp"] + v["fp"], 1)
            v["f1"] = round(2 * prec * v["recall"] / (prec + v["recall"]), 4) if prec + v["recall"] else 0.0
        best_name = max(refs, key=lambda k: refs[k]["f1"])
        best_recall, best_fdp = refs[best_name]["recall"], refs[best_name]["fdp"]
        # integrity on test-based rows
        # integrity: agent p-values vs a reference test, after shifting the reference fold changes so its
        # yeast baseline matches the agent's (different but valid normalizations must not fail this check)
        st = rp.strict_test_stats(pg, cname)
        At = A[A.call_basis == "test"].set_index("protein_id")
        common = At.index.intersection(st.index)
        if len(common) > 50:
            a_y = At.loc[common][~ups_map.loc[common].values]["log2fc"].median()
            r_y = st.loc[common][st.loc[common, "yeast"].values]["fc"].median()
            t_shift = np.abs((st.loc[common, "fc"] + (a_y - r_y)) / st.loc[common, "se"])
            rho = float(spearmanr(-np.log10(At.loc[common, "p_value"].clip(lower=1e-300)), t_shift).statistic)
        else:
            rho = 1.0
        data_driven = rho >= 0.2
        # fdr
        n_called = max(tp + fp, 1); fdp = fp / n_called
        # allowed: chance tolerance at the stated threshold, or what the best reference achieves on this
        # contrast if that is worse (low-abundance contrasts cannot reach the nominal FDR)
        tol = max(q_used + 2 * np.sqrt(q_used * (1 - q_used) / n_called), best_fdp + 0.05)
        fdr_s = float(np.clip(1 - max(0.0, fdp - tol) / FDR_SLACK, 0, 1)) * float(data_driven)
        # detection
        recall = tp / n_ups if n_ups else 0.0
        det_raw = recall / best_recall if best_recall else 0.0
        det_s = float(np.clip(det_raw, 0, 1)) * fdr_s
        # fold change (finite rows only)
        F = A[A.log2fc.notna()]
        med_u = float(F.loc[F.ups, "log2fc"].median()) if F.ups.any() else np.nan
        med_y = float(F.loc[~F.ups, "log2fc"].median())
        ref_err = min(abs(v["median_ups_log2fc"] - rp.TRUE_FC[cname]) for v in refs.values() if v["median_ups_log2fc"] is not None)
        u_err = max(0.0, abs(med_u - rp.TRUE_FC[cname]) - ref_err) if np.isfinite(med_u) else FC_TOL
        fc_s = 0.7 * float(np.clip(1 - u_err / FC_TOL, 0, 1)) + 0.3 * float(np.clip(1 - abs(med_y) / 0.5, 0, 1))
        cs = SECTION_WEIGHTS["detection"] * det_s + SECTION_WEIGHTS["fdr"] * fdr_s + SECTION_WEIGHTS["fold_change"] * fc_s
        total += CONTRAST_WEIGHTS[cname] * cs
        report["contrasts"][cname] = {
            "comparison": f"{hi} vs {lo}", "score": round(cs, 4),
            "detection": {"score": round(det_s, 4), "ups_found": tp, "ups_detectable": n_ups, "recall": round(recall, 4),
                          "recall_relative_to_best_reference": round(det_raw, 4), "best_reference": best_name,
                          "ups_found_by_presence_absence": int((A.sig & A.ups & (A.call_basis == "presence_absence")).sum())},
            "fdr": {"score": round(fdr_s, 4), "false_calls_yeast": fp, "actual_false_discovery_proportion": round(fdp, 4),
                    "allowed_fdp_given_number_of_calls": round(float(tol), 4)},
            "fold_change": {"score": round(fc_s, 4), "ups_median_log2fc": round(med_u, 3) if np.isfinite(med_u) else None,
                            "true_log2fc": round(rp.TRUE_FC[cname], 3), "best_reference_error": round(ref_err, 3),
                            "yeast_median_log2fc (expected 0)": round(med_y, 3)},
            "p_values_data_driven": data_driven, "p_value_spearman_vs_reference": round(rho, 3),
            "reference_pipelines": refs}

    # ---------- cleaning ----------
    tested_flagged = int(D.flag.sum())
    clean_s = float(np.clip(1 - tested_flagged / max(int(fl.sum()) * 3, 1) * 3, 0, 1))
    report["sections"]["cleaning"] = {"score": round(clean_s, 4), "flagged_rows_assessed": tested_flagged}

    # ---------- bookkeeping ----------
    cut = man.get("fold_change_cutoff")
    cut = float(cut) if isinstance(cut, (int, float)) and not isinstance(cut, bool) else 0.0
    T = D[D.call_basis == "test"]
    exp_sig = (T.adj_p_value.values <= q_used + 1e-12) & (np.abs(T.log2fc.values) >= cut)
    ints = {"total_protein_groups": len(pg), "removed_reverse": int(pg["Reverse"].notna().sum()),
            "removed_contaminant": int(pg["Potential contaminant"].notna().sum()),
            "removed_only_identified_by_site": int(pg["Only identified by site"].notna().sum()),
            "protein_groups_after_cleaning": int((~fl).sum())}
    checks = {k: man.get(k) == v for k, v in ints.items()}
    pa, ns = man.get("proteins_assessed", {}), man.get("n_significant", {})
    checks["proteins_assessed"] = isinstance(pa, dict) and all(pa.get(c) == int((D.contrast == c).sum()) for c in rp.CONTRASTS)
    checks["n_significant"] = isinstance(ns, dict) and all(ns.get(c) == int((D.sig & (D.contrast == c)).sum()) for c in rp.CONTRASTS)
    checks["fdr_threshold_valid"] = q_ok
    checks["test_calls_match_cutoffs"] = bool((T.sig.values == exp_sig).all())
    strs = ["intensity_columns_used", "filtering_rule", "missing_value_strategy", "normalization_method",
            "test_method", "presence_absence_rule", "processing_order"]
    checks["method_strings_present"] = all(isinstance(man.get(k), str) and man.get(k).strip() for k in strs)
    report["sections"]["bookkeeping"] = {"score": round(sum(checks.values()) / len(checks), 4), "checks": checks,
                                         "expected": ints,
                                         "test_rows_inconsistent_with_cutoffs": int((T.sig.values != exp_sig).sum())}
    report["optional"] = {"analysis_report_present": (res / "analysis_report.txt").exists(),
                          **{f"manifest_{k}": man.get(k) for k in strs}}
    report["score"] = round(TOP["contrasts"] * total + TOP["cleaning"] * clean_s
                            + TOP["bookkeeping"] * report["sections"]["bookkeeping"]["score"], 4)
    report["weights"] = {"top": TOP, "contrasts": CONTRAST_WEIGHTS, "within_contrast": SECTION_WEIGHTS}
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--truth", default=None, help="not needed (truth comes from the input's FASTA headers)")
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args()
    rep = evaluate(a.input, a.results)
    out = json.dumps(rep, indent=2, default=str)
    if a.out:
        Path(a.out).write_text(out)
    print(out)


if __name__ == "__main__":
    main()
