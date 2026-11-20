"""
E1 evaluator: end-to-end LFQ analysis of the MaxLFQ HeLa + E. coli benchmark (PXD000279,
Cox et al. 2014, Mol Cell Proteomics).

Ground truth comes from the sample composition, not from a published result:
  * human protein groups:  equal amount in H and L   -> true log2fc = 0, should NOT be called
  * E. coli protein groups: 3x more in H than in L    -> true log2fc = log2(3) = 1.585, SHOULD be called
  * groups mixing both species are excluded from scoring.
Species is read from the FASTA headers in proteinGroups.txt.

Sections (weights in WEIGHTS):
  gate         files/columns, IDs from the input, numeric values, log2fc direction and scale,
               fold changes consistent with the measured intensities
  cleaning     no reverse / contaminant / only-identified-by-site groups among tested proteins
  detection    E. coli recall (denominator: E. coli groups quantifiable with >=2 valid values per
               condition) relative to the best reference pipeline, x FDR multiplier
  fdr          actual false-discovery proportion vs stated threshold (chance tolerance)
  ranking      recall at 98% precision of the p-value ranking, relative to the published 72%
  fold_change  human median log2fc ~0 (normalization) and E. coli - human separation ~1.585
  bookkeeping  manifest counts and consistency of `significant` with stated cutoffs
Calls are only credited if the p-values are data-driven (see integrity check).

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

WEIGHTS = {"cleaning": 0.10, "detection": 0.25, "fdr": 0.20, "ranking": 0.15,
           "fold_change": 0.15, "bookkeeping": 0.15}
TRUE_FC = float(np.log2(3))
PAPER_RECALL_AT_98 = 0.72      # Cox et al. 2014: 72% of E. coli proteins at 98% precision (Welch t)
PAPER_RECALL_AT_95 = 0.88
FDR_SLACK = 0.25
FC_TOL = 1.0


def to_bool(s):
    m = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
    return s.astype(str).str.strip().str.lower().map(m)


def recall_at_precision(p, is_pos, n_pos_total, level):
    o = np.argsort(p, kind="stable")
    e = is_pos[o]
    prec = np.cumsum(e) / np.arange(1, len(e) + 1)
    rec = np.cumsum(e) / n_pos_total
    ok = prec >= level
    return float(rec[ok].max()) if ok.any() else 0.0


def evaluate(input_txt, results_dir):
    res = Path(results_dir)
    pg = pd.read_csv(input_txt, sep="\t", low_memory=False)
    pg["species"] = pg["Fasta headers"].map(rp.species_of)
    flagged = pg["Reverse"].notna() | pg["Contaminant"].notna() | pg["Only identified by site"].notna()
    info = pg.set_index("Protein IDs")
    X = np.log2(pg[rp.L + rp.H].replace(0, np.nan).astype(float))
    X.index = pg["Protein IDs"].values
    quantifiable = (~flagged.values) & (X[rp.L].notna().sum(1) >= 2).values & (X[rp.H].notna().sum(1) >= 2).values
    n_ecoli_ref = int(((pg["species"] == "ECOLI").values & quantifiable).sum())

    report = {"gate": {"passed": False, "errors": []}, "sections": {}}
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
        D = pd.read_csv(dpath)
        man = json.load(open(jpath))
    except Exception as e:
        err.append(f"parse error: {e}")
        report["score"] = 0.0
        return report
    need = ["protein_id", "log2fc", "p_value", "adj_p_value", "significant"]
    miss = [c for c in need if c not in D.columns]
    if miss:
        err.append(f"de_results.csv missing columns {miss}")
    else:
        D["protein_id"] = D["protein_id"].astype(str)
        if not D["protein_id"].is_unique:
            err.append("duplicate protein_id rows")
        unknown = set(D["protein_id"]) - set(info.index)
        if unknown:
            err.append(f"{len(unknown)} protein_id values are not 'Protein IDs' from the input (e.g. {sorted(unknown)[0][:60]})")
    if not err:
        for c in ["log2fc", "p_value", "adj_p_value"]:
            D[c] = pd.to_numeric(D[c], errors="coerce")
            if D[c].isna().any():
                err.append(f"column {c} has {int(D[c].isna().sum())} missing/non-numeric values")
        sig = to_bool(D["significant"])
        if sig.isna().any():
            err.append("column significant must contain only True/False")
    if not err:
        if ((D[["p_value", "adj_p_value"]] < 0) | (D[["p_value", "adj_p_value"]] > 1)).any().any():
            err.append("p-values outside [0, 1]")
        D["species"] = info.loc[D["protein_id"], "species"].values
        sep = D.loc[D.species == "ECOLI", "log2fc"].median() - D.loc[D.species == "HUMAN", "log2fc"].median()
        if not np.isfinite(sep):
            err.append("no human and E. coli proteins among tested proteins")
        elif sep < -0.5:
            err.append(f"log2fc sign appears reversed (E. coli - human median = {sep:.2f}); expected H minus L")
        elif not 0.6 <= sep / TRUE_FC <= 1.6:
            err.append(f"log2fc scale off ({sep:.2f} vs expected ~{TRUE_FC:.2f}); check log base")
        # fold changes must follow the measured data (LFQ or raw intensities)
        cands = {}
        for name, cols_l, cols_h in [("LFQ intensity", rp.L, rp.H),
                                     ("Intensity", [c.replace("LFQ intensity", "Intensity") for c in rp.L],
                                      [c.replace("LFQ intensity", "Intensity") for c in rp.H])]:
            M = np.log2(info.loc[D["protein_id"], cols_l + cols_h].replace(0, np.nan).astype(float))
            dfc = M[cols_h].mean(1).values - M[cols_l].mean(1).values
            ok = np.isfinite(dfc)
            cands[name] = float(spearmanr(D["log2fc"].values[ok], dfc[ok]).statistic) if ok.sum() > 10 else 0.0
        report["gate"]["fold_change_vs_measured_spearman"] = {k: round(v, 3) for k, v in cands.items()}
        if not err and max(cands.values()) < 0.7:
            err.append("log2fc values do not follow the measured intensities (Spearman < 0.7)")
    if err:
        report["score"] = 0.0
        return report
    report["gate"]["passed"] = True
    sig = sig.values.astype(bool)
    D["sig"] = sig
    S = D[D.species.isin(["HUMAN", "ECOLI"])].copy()
    is_e = (S.species == "ECOLI").values

    # ---------- integrity: are p-values data-driven? ----------
    offset = float(S.loc[~is_e, "log2fc"].median())
    ref = rp.run(pg, "median_human", "moderated").set_index("protein_id")
    common = S["protein_id"][S["protein_id"].isin(ref.index)]
    rho_p = float(spearmanr(S.set_index("protein_id").loc[common, "p_value"], ref.loc[common, "p_value"]).statistic) if len(common) > 50 else 0.0
    within = []
    for sp_name in ["HUMAN", "ECOLI"]:
        sub = S[S.species == sp_name]
        within.append(sub["p_value"].nunique() / max(len(sub), 1))
    data_driven = rho_p >= 0.3 and min(within) > 0.2
    report["integrity"] = {"p_value_spearman_vs_reference": round(rho_p, 3),
                           "distinct_p_value_fraction_by_species": [round(w, 3) for w in within],
                           "p_values_data_driven": data_driven,
                           "note": "if false, detection, FDR and ranking are scored 0 (calls not derived from the data)"}

    # ---------- cleaning ----------
    idx = pd.Index(pg["Protein IDs"]).get_indexer(D["protein_id"])
    tested_flagged = int(flagged.values[idx].sum())
    # denominator: flagged groups that a pipeline WITHOUT cleaning would have tested (>=2 valid per condition)
    flagged_quantifiable = int((flagged.values & (X[rp.L].notna().sum(1) >= 2).values
                                & (X[rp.H].notna().sum(1) >= 2).values).sum())
    clean_s = float(np.clip(1 - tested_flagged / max(flagged_quantifiable, 1), 0, 1))
    report["sections"]["cleaning"] = {"score": round(clean_s, 4), "flagged_groups_tested": tested_flagged,
                                      "flagged_groups_with_enough_data": flagged_quantifiable,
                                      "tested_by_flag": {k: int(pg[k].notna().values[idx].sum())
                                                         for k in ["Reverse", "Contaminant", "Only identified by site"]}}

    # ---------- references ----------
    refs = {}
    for norm in ["none", "median_all", "median_human"]:
        r = rp.run(pg, norm, "moderated")
        r["species"] = info.loc[r["protein_id"], "species"].values
        r = r[r.species.isin(["HUMAN", "ECOLI"])]
        e = (r.species == "ECOLI").values
        for cut in [0.0, 1.0]:
            s = (r.adj_p_value.values <= 0.05) & (np.abs(r.log2fc.values) >= cut)
            tp, fp = int((s & e).sum()), int((s & ~e).sum())
            refs[f"{norm}_moderated_fc{cut:g}"] = {"tp": tp, "fp": fp, "recall": round(tp / n_ecoli_ref, 4),
                                                   "fdp": round(fp / max(tp + fp, 1), 4)}
        refs[f"{norm}_moderated_fc0"]["recall_at_98pct_precision"] = round(
            recall_at_precision(r.p_value.values, e, n_ecoli_ref, 0.98), 4)
    best_recall = max(v["recall"] for v in refs.values() if v["fdp"] <= 0.1)

    # ---------- fdr ----------
    q = man.get("fdr_threshold")
    q_ok = isinstance(q, (int, float)) and not isinstance(q, bool) and 0 < q <= 0.1
    q_used = float(q) if q_ok else 0.05
    tp, fp = int((S.sig.values & is_e).sum()), int((S.sig.values & ~is_e).sum())
    n_called = max(tp + fp, 1)
    fdp = fp / n_called
    tol = q_used + 2 * np.sqrt(q_used * (1 - q_used) / n_called)
    fdr_score = float(np.clip(1 - max(0.0, fdp - tol) / FDR_SLACK, 0, 1)) * float(data_driven)
    report["sections"]["fdr"] = {"score": round(fdr_score, 4), "stated_threshold": q_used,
                                 "actual_false_discovery_proportion": round(fdp, 4),
                                 "allowed_fdp_given_number_of_calls": round(float(tol), 4),
                                 "true_calls_ecoli": tp, "false_calls_human": fp}

    # ---------- detection ----------
    recall = tp / n_ecoli_ref
    raw = recall / best_recall if best_recall else 0.0
    det = float(np.clip(raw, 0, 1)) * fdr_score * float(data_driven)
    report["sections"]["detection"] = {"score": round(det, 4), "recall": round(recall, 4),
                                       "recall_relative_to_best_reference": round(raw, 4),
                                       "fdr_multiplier": round(fdr_score, 4),
                                       "ecoli_groups_quantifiable": n_ecoli_ref,
                                       "ecoli_groups_tested": int(is_e.sum()),
                                       "human_groups_tested": int((~is_e).sum())}

    # ---------- ranking (comparable to the paper) ----------
    r98 = recall_at_precision(S.p_value.values, is_e, n_ecoli_ref, 0.98)
    r95 = recall_at_precision(S.p_value.values, is_e, n_ecoli_ref, 0.95)
    rank_raw = r98 / PAPER_RECALL_AT_98
    report["sections"]["ranking"] = {"score": round(float(np.clip(rank_raw, 0, 1)) * float(data_driven), 4),
                                     "unclipped_skill": round(rank_raw, 4),
                                     "recall_at_98pct_precision": round(r98, 4),
                                     "recall_at_95pct_precision": round(r95, 4),
                                     "published_recall_at_98pct": PAPER_RECALL_AT_98,
                                     "published_recall_at_95pct": PAPER_RECALL_AT_95}

    # ---------- fold changes ----------
    med_h = float(S.loc[~is_e, "log2fc"].median())
    med_e = float(S.loc[is_e, "log2fc"].median())
    sep = med_e - med_h
    # the best achievable on real data is not exactly 0 / 1.585; errors up to the expert reference's are free
    rh = rp.run(pg, "median_human", "moderated")
    rh_sp = info.loc[rh["protein_id"], "species"].values
    ref_med_h = float(np.median(rh.log2fc[rh_sp == "HUMAN"]))
    ref_sep = float(np.median(rh.log2fc[rh_sp == "ECOLI"])) - ref_med_h
    norm_err = max(0.0, abs(med_h) - abs(ref_med_h))
    sep_err = max(0.0, abs(sep - TRUE_FC) - abs(ref_sep - TRUE_FC))
    norm_s = float(np.clip(1 - norm_err / FC_TOL, 0, 1))
    sep_s = float(np.clip(1 - sep_err / FC_TOL, 0, 1))
    report["sections"]["fold_change"] = {
        "score": round(0.5 * norm_s + 0.5 * sep_s, 4),
        "reference_human_median": round(ref_med_h, 4), "reference_separation": round(ref_sep, 4),
        "human_median_log2fc (expected 0)": round(med_h, 4),
        "ecoli_median_log2fc (expected 1.585)": round(med_e, 4),
        "ecoli_minus_human (expected 1.585)": round(sep, 4),
        "human_log2fc_iqr": round(float(np.subtract(*np.percentile(S.loc[~is_e, "log2fc"], [75, 25]))), 4),
        "ecoli_log2fc_iqr": round(float(np.subtract(*np.percentile(S.loc[is_e, "log2fc"], [75, 25]))), 4)}

    # ---------- bookkeeping ----------
    cut = man.get("fold_change_cutoff")
    cut = float(cut) if isinstance(cut, (int, float)) and not isinstance(cut, bool) else 0.0
    expected_sig = (D["adj_p_value"].values <= q_used + 1e-12) & (np.abs(D["log2fc"].values) >= cut)
    ints = {"total_protein_groups": len(pg), "removed_reverse": int(pg["Reverse"].notna().sum()),
            "removed_contaminant": int(pg["Contaminant"].notna().sum()),
            "removed_only_identified_by_site": int(pg["Only identified by site"].notna().sum()),
            "protein_groups_after_cleaning": int((~flagged).sum()),
            "proteins_tested": len(D), "n_significant": int(sig.sum())}
    checks = {k: man.get(k) == v for k, v in ints.items()}
    checks["fdr_threshold_valid"] = q_ok
    checks["significant_matches_cutoffs"] = bool((sig == expected_sig).all())
    checks["adj_p_not_below_p"] = bool((D["adj_p_value"] >= D["p_value"] - 1e-9).all())
    strs = ["intensity_columns_used", "filtering_rule", "normalization_method", "imputation_method",
            "test_method", "processing_order"]
    checks["method_strings_present"] = all(isinstance(man.get(k), str) and man.get(k).strip() for k in strs)
    report["sections"]["bookkeeping"] = {"score": round(sum(checks.values()) / len(checks), 4),
                                         "checks": checks, "expected": ints,
                                         "rows_inconsistent_with_cutoffs": int((sig != expected_sig).sum())}

    report["reference_pipelines"] = refs
    rpth = res / "analysis_report.txt"
    report["optional"] = {"analysis_report_present": rpth.exists(),
                          **{f"manifest_{k}": man.get(k) for k in strs}}
    report["score"] = round(sum(WEIGHTS[k] * report["sections"][k]["score"] for k in WEIGHTS), 4)
    report["weights"] = WEIGHTS
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--truth", default=None, help="not needed for E1 (truth comes from the input's species)")
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args()
    rep = evaluate(a.input, a.results)
    out = json.dumps(rep, indent=2, default=str)
    if a.out:
        Path(a.out).write_text(out)
    print(out)


if __name__ == "__main__":
    main()
