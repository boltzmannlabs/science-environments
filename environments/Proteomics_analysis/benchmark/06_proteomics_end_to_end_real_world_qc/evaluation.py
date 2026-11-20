"""
Task 6 evaluator: end-to-end analysis of the MaxLFQ HeLa + E. coli benchmark with planted
sample-level faults (see build_task6.py / faults.json).

Truth:
  * proteins: human -> unchanged (log2fc 0); E. coli -> 3x higher in H (log2fc 1.585)
  * samples:  L3 is really H, H3 is really L (swap); L4 duplicates L1; H4 is a failed run

Sections:
  fault_handling  from manifest `samples_used` / `samples_excluded`:
                    duplicate  - L1 and L4 not both used
                    failed run - H4 not used
                    swap       - L3 used as H and H3 used as L (1); both dropped (0.5); otherwise 0
                  minus 0.15 per good sample (L2, H1, H2, or the L1/L4 pair) left unused
  detection / fdr / ranking / fold_change   as in Task 5, against species truth; references are
                  computed on the clean design reconstructed from the faulted file
  bookkeeping     manifest counts and consistency

Usage:
  python evaluation.py --input <faulted proteinGroups.txt> --results <results dir> \
                       --truth <folder with faults.json> --out metrics_summary.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference_pipelines as rp  # noqa: E402  (copy of the Task 5 helper)

WEIGHTS = {"fault_handling": 0.35, "detection": 0.20, "fdr": 0.15, "ranking": 0.10,
           "fold_change": 0.10, "bookkeeping": 0.10}
SAMPLES = ["L1", "L2", "L3", "L4", "H1", "H2", "H3", "H4"]
TRUE_FC = float(np.log2(3))
PAPER_R98 = 0.72
FDR_SLACK = 0.25
FC_TOL = 1.0


def to_bool(s):
    m = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
    return s.astype(str).str.strip().str.lower().map(m)


def recall_at_precision(p, is_pos, n_pos, level):
    o = np.argsort(p, kind="stable"); e = is_pos[o]
    prec = np.cumsum(e) / np.arange(1, len(e) + 1); rec = np.cumsum(e) / n_pos
    ok = prec >= level
    return float(rec[ok].max()) if ok.any() else 0.0


def pipeline(pg, L, H, normalization="median_human", fc_cut=1.0, q=0.05, min_valid=2):
    """Expert reference: clean -> log2 LFQ -> filter -> normalize on human -> moderated t."""
    df = pg[pg["Reverse"].isna() & pg["Contaminant"].isna() & pg["Only identified by site"].isna()]
    cols = [f"LFQ intensity {s}" for s in L + H]
    X = np.log2(df[cols].replace(0, np.nan).astype(float)); X.index = df["Protein IDs"].values
    Lc, Hc = cols[:len(L)], cols[len(L):]
    X = X[(X[Lc].notna().sum(axis=1) >= min(min_valid, len(L))) & (X[Hc].notna().sum(axis=1) >= min(min_valid, len(H)))]
    if normalization == "median_human":
        hum = (df.set_index("Protein IDs").loc[X.index, "Fasta headers"].map(rp.species_of) == "HUMAN").values
        X = X - X[hum].median() + X[hum].median().mean()
    fc, p = rp.moderated_t(X[Lc].values, X[Hc].values)
    adj = rp.bh(p)
    return pd.DataFrame({"protein_id": X.index, "log2fc": fc, "p_value": p, "adj_p_value": adj,
                         "significant": (adj <= q) & (np.abs(fc) >= fc_cut)})


def evaluate(input_txt, results_dir, truth_dir):
    res = Path(results_dir)
    pg = pd.read_csv(input_txt, sep="\t", low_memory=False)
    faults = json.load(open(Path(truth_dir) / "faults.json"))
    true_cond = faults["true_condition"]
    pg["species"] = pg["Fasta headers"].map(rp.species_of)
    info = pg.set_index("Protein IDs")
    flagged = pg["Reverse"].notna() | pg["Contaminant"].notna() | pg["Only identified by site"].notna()
    good_L, good_H = ["L1", "L2", "H3"], ["H1", "H2", "L3"]          # true design (by input labels)
    Xc = np.log2(pg[[f"LFQ intensity {s}" for s in good_L + good_H]].replace(0, np.nan).astype(float))
    quant = (~flagged.values) & (Xc.iloc[:, :3].notna().sum(axis=1) >= 2).values & (Xc.iloc[:, 3:].notna().sum(axis=1) >= 2).values
    n_ecoli = int(((pg.species == "ECOLI").values & quant).sum())

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
        D = pd.read_csv(dpath); man = json.load(open(jpath))
    except Exception as e:
        err.append(f"parse error: {e}"); report["score"] = 0.0
        return report
    need = ["protein_id", "log2fc", "p_value", "adj_p_value", "significant"]
    if [c for c in need if c not in D.columns]:
        err.append(f"de_results.csv missing columns {[c for c in need if c not in D.columns]}")
    else:
        D["protein_id"] = D["protein_id"].astype(str)
        if not D["protein_id"].is_unique:
            err.append("duplicate protein_id rows")
        bad = set(D["protein_id"]) - set(info.index)
        if bad:
            err.append(f"{len(bad)} protein_id values not found in the input 'Protein IDs'")
    su = man.get("samples_used")
    if not (isinstance(su, dict) and set(su) == {"L", "H"} and all(isinstance(v, list) for v in su.values())):
        err.append('manifest samples_used must be {"L": [...], "H": [...]}')
    else:
        used = su["L"] + su["H"]
        if set(used) - set(SAMPLES) or len(used) != len(set(used)):
            err.append(f"samples_used must list distinct sample names from {SAMPLES}")
        if len(su["L"]) < 2 or len(su["H"]) < 2:
            err.append("each condition needs at least 2 samples in samples_used")
    if not err:
        for c in ["log2fc", "p_value", "adj_p_value"]:
            D[c] = pd.to_numeric(D[c], errors="coerce")
            if D[c].isna().any():
                err.append(f"column {c} has missing/non-numeric values")
        sig = to_bool(D["significant"])
        if sig.isna().any():
            err.append("column significant must contain only True/False")
    if not err:
        D["species"] = info.loc[D["protein_id"], "species"].values
        sep = D.loc[D.species == "ECOLI", "log2fc"].median() - D.loc[D.species == "HUMAN", "log2fc"].median()
        if not np.isfinite(sep):
            err.append("no human and E. coli proteins among tested proteins")
        elif sep < -0.5:
            err.append(f"log2fc sign appears reversed (E. coli - human = {sep:.2f}); expected H minus L")
        elif sep > 1.6 * TRUE_FC:
            err.append(f"log2fc scale off ({sep:.2f} vs ~{TRUE_FC:.2f}); check log base")
    if err:
        report["score"] = 0.0
        return report
    report["gate"]["passed"] = True
    D["sig"] = sig.values.astype(bool)

    # ---------- fault handling ----------
    UL, UH = set(su["L"]), set(su["H"])
    used = UL | UH
    dup_ok = not ({"L1", "L4"} <= used)
    failed_ok = "H4" not in used
    if "L3" in UH and "H3" in UL:
        swap = 1.0
    elif "L3" not in used and "H3" not in used:
        swap = 0.5
    else:
        swap = 0.0
    wrong_side = sorted(s for s in used if true_cond[s] != ("L" if s in UL else "H"))
    lost = [s for s in ["L2", "H1", "H2"] if s not in used] + ([] if ({"L1", "L4"} & used) else ["L1/L4"])
    fh = float(np.clip(np.mean([float(dup_ok), float(failed_ok), swap]) - 0.15 * len(lost), 0, 1))
    notes = man.get("sample_qc_notes", {})
    report["sections"]["fault_handling"] = {
        "score": round(fh, 4),
        "duplicate_L4_handled": dup_ok, "failed_run_H4_excluded": failed_ok,
        "swap_L3_H3": {1.0: "corrected (relabelled)", 0.5: "both excluded", 0.0: "not handled"}[swap],
        "samples_in_wrong_condition": wrong_side, "good_samples_not_used": lost,
        "samples_used": su, "samples_excluded": man.get("samples_excluded"),
        "notes_given_for": sorted(notes) if isinstance(notes, dict) else None}

    # ---------- references on the true (reconstructed) design ----------
    S = D[D.species.isin(["HUMAN", "ECOLI"])]
    is_e = (S.species == "ECOLI").values
    ref = pipeline(pg, good_L, good_H)
    ref["species"] = info.loc[ref.protein_id, "species"].values
    ref = ref[ref.species.isin(["HUMAN", "ECOLI"])]
    re_ = (ref.species == "ECOLI").values
    ref_recall = float((ref.significant.values & re_).sum() / n_ecoli)
    ref_med_h = float(ref.log2fc[~re_].median()); ref_sep = float(ref.log2fc[re_].median()) - ref_med_h
    blind = pipeline(pg, ["L1", "L2", "L3", "L4"], ["H1", "H2", "H3", "H4"])
    blind["species"] = info.loc[blind.protein_id, "species"].values
    blind = blind[blind.species.isin(["HUMAN", "ECOLI"])]
    be = (blind.species == "ECOLI").values

    # ---------- integrity ----------
    common = S.protein_id[S.protein_id.isin(ref.protein_id)]
    rho = float(spearmanr(S.set_index("protein_id").loc[common, "p_value"],
                          ref.set_index("protein_id").loc[common, "p_value"]).statistic) if len(common) > 50 else 0.0
    distinct = min(S[S.species == sp_]["p_value"].nunique() / max((S.species == sp_).sum(), 1) for sp_ in ["HUMAN", "ECOLI"])
    data_driven = rho >= 0.2 and distinct > 0.2
    report["integrity"] = {"p_value_spearman_vs_reference": round(rho, 3), "p_values_data_driven": data_driven}

    # ---------- fdr ----------
    q = man.get("fdr_threshold")
    q_ok = isinstance(q, (int, float)) and not isinstance(q, bool) and 0 < q <= 0.1
    q_used = float(q) if q_ok else 0.05
    tp, fp = int((S.sig.values & is_e).sum()), int((S.sig.values & ~is_e).sum())
    n_called = max(tp + fp, 1); fdp = fp / n_called
    tol = q_used + 2 * np.sqrt(q_used * (1 - q_used) / n_called)
    fdr_s = float(np.clip(1 - max(0.0, fdp - tol) / FDR_SLACK, 0, 1)) * float(data_driven)
    report["sections"]["fdr"] = {"score": round(fdr_s, 4), "stated_threshold": q_used,
                                 "actual_false_discovery_proportion": round(fdp, 4),
                                 "allowed_fdp_given_number_of_calls": round(float(tol), 4),
                                 "true_calls_ecoli": tp, "false_calls_human": fp}

    # ---------- detection ----------
    recall = tp / n_ecoli
    raw = recall / ref_recall if ref_recall else 0.0
    report["sections"]["detection"] = {"score": round(float(np.clip(raw, 0, 1)) * fdr_s, 4), "recall": round(recall, 4),
                                       "recall_relative_to_clean_reference": round(raw, 4),
                                       "ecoli_groups_quantifiable": n_ecoli}

    # ---------- ranking ----------
    r98 = recall_at_precision(S.p_value.values, is_e, n_ecoli, 0.98)
    report["sections"]["ranking"] = {"score": round(float(np.clip(r98 / PAPER_R98, 0, 1)) * float(data_driven), 4),
                                     "recall_at_98pct_precision": round(r98, 4), "published_recall_at_98pct": PAPER_R98}

    # ---------- fold changes ----------
    med_h = float(S.log2fc[~is_e].median()); sep = float(S.log2fc[is_e].median()) - med_h
    ne = max(0.0, abs(med_h) - abs(ref_med_h)); se = max(0.0, abs(sep - TRUE_FC) - abs(ref_sep - TRUE_FC))
    report["sections"]["fold_change"] = {
        "score": round(0.5 * float(np.clip(1 - ne / FC_TOL, 0, 1)) + 0.5 * float(np.clip(1 - se / FC_TOL, 0, 1)), 4),
        "human_median_log2fc (expected 0)": round(med_h, 4),
        "ecoli_minus_human (expected ~1.585)": round(sep, 4),
        "reference_separation": round(ref_sep, 4)}

    # ---------- bookkeeping ----------
    cut = man.get("fold_change_cutoff")
    cut = float(cut) if isinstance(cut, (int, float)) and not isinstance(cut, bool) else 0.0
    exp_sig = (D.adj_p_value.values <= q_used + 1e-12) & (np.abs(D.log2fc.values) >= cut)
    ints = {"total_protein_groups": len(pg), "removed_reverse": int(pg["Reverse"].notna().sum()),
            "removed_contaminant": int(pg["Contaminant"].notna().sum()),
            "removed_only_identified_by_site": int(pg["Only identified by site"].notna().sum()),
            "protein_groups_after_cleaning": int((~flagged).sum()),
            "proteins_tested": len(D), "n_significant": int(D.sig.sum())}
    checks = {k: man.get(k) == v for k, v in ints.items()}
    checks["fdr_threshold_valid"] = q_ok
    checks["significant_matches_cutoffs"] = bool((D.sig.values == exp_sig).all())
    excl = man.get("samples_excluded")
    checks["samples_excluded_consistent"] = isinstance(excl, list) and set(excl) == set(SAMPLES) - used
    checks["qc_notes_for_changed_samples"] = isinstance(notes, dict) and set(excl or []) | set(
        s for s in used if s[0] != ("L" if s in UL else "H")) <= set(notes)
    checks["flagged_rows_not_tested"] = int(flagged.values[pd.Index(pg["Protein IDs"]).get_indexer(D.protein_id)].sum()) == 0
    report["sections"]["bookkeeping"] = {"score": round(sum(checks.values()) / len(checks), 4),
                                         "checks": checks, "expected": ints}

    report["reference_pipelines"] = {
        "clean_design_expert": {"recall": round(ref_recall, 4),
                                "fdp": round(float((ref.significant & ~re_).sum() / max(ref.significant.sum(), 1)), 4)},
        "blind_all_8_samples_as_labelled": {
            "recall": round(float((blind.significant.values & be).sum() / n_ecoli), 4),
            "fdp": round(float((blind.significant.values & ~be).sum() / max(blind.significant.sum(), 1)), 4),
            "recall_at_98pct_precision": round(recall_at_precision(blind.p_value.values, be, n_ecoli, 0.98), 4)}}
    report["optional"] = {"analysis_report_present": (res / "analysis_report.txt").exists(),
                          "sample_qc_notes": notes}
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
