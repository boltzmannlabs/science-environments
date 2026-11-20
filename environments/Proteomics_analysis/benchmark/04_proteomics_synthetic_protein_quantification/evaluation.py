"""
Task 4 evaluator: peptide -> protein quantification.

Each protein's absolute level is arbitrary (peptide ionization is unknown), so all
comparisons use each protein's RELATIVE pattern across samples.

Layers:
  1. gate          files, schema, one row per protein with a unique peptide, no NaN,
                   log2 scale (fold-change slope vs truth ~1)
  2. profile       RMSE of row-centred protein profiles vs truth
  3. fold_change   RMSE of Treated-vs-Control log2 fold changes vs truth
  4. bookkeeping   manifest counts
  Profile and fold-change scores: 0 = summing all peptide intensities (incl. shared),
  1 = best robust reference (median polish / MaxLFQ-style on unique peptides).

Usage:
  python evaluation.py --input <peptide_intensities.csv> --results <results dir> \
                       --truth <folder with ground_truth_log2.csv + meta.json> --out metrics_summary.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quant_methods as qm  # noqa: E402

WEIGHTS = {"profile": 0.40, "fold_change": 0.35, "bookkeeping": 0.25}
SAMPLES = qm.SAMPLES
CTRL, TRT = SAMPLES[:3], SAMPLES[3:]


def profile_rmse(A, T):
    pa = A.sub(A.mean(axis=1), axis=0)
    pt = T.sub(T.mean(axis=1), axis=0)
    return float(np.sqrt(np.mean((pa.values - pt.values) ** 2)))


def fc(M):
    return M[TRT].mean(axis=1) - M[CTRL].mean(axis=1)


def rel(agent, worst, best):
    raw = (worst - agent) / (worst - best) if worst - best > 1e-12 else float(agent <= best)
    return float(np.clip(raw, 0, 1)), float(raw)


def evaluate(input_csv, results_dir, truth_dir):
    res = Path(results_dir)
    pep = pd.read_csv(input_csv)
    truth = pd.read_csv(Path(truth_dir) / "ground_truth_log2.csv", index_col=0)
    meta = json.load(open(Path(truth_dir) / "meta.json"))
    uniq = ~pep["Proteins"].astype(str).str.contains(";")
    expected = set(pep.loc[uniq, "Proteins"])
    report = {"gate": {"passed": False, "errors": []}, "sections": {}}
    err = report["gate"]["errors"]

    # ---------- 1. gate ----------
    mpath, jpath = res / "protein_matrix_log2.csv", res / "run_manifest.json"
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
    A.index = A.index.astype(str)
    if list(A.columns) != SAMPLES:
        err.append(f"columns {list(A.columns)} != {SAMPLES}")
    if not A.index.is_unique:
        err.append("duplicate protein IDs")
    combined = [i for i in A.index if ";" in i]
    if combined:
        err.append(f"{len(combined)} combined protein IDs (e.g. {combined[0]}); output single proteins only")
    missing, extra = expected - set(A.index), set(A.index) - expected
    if missing:
        err.append(f"{len(missing)} proteins with unique peptides are missing from the output")
    if extra and not combined:
        err.append(f"{len(extra)} unexpected protein IDs")
    if not err:
        A = A.loc[sorted(expected)]
        if A.isna().values.any():
            err.append(f"matrix contains {int(A.isna().values.sum())} NaN cells")
    if not err:
        T = truth.loc[A.index]
        big = (fc(T).abs() > 1.0)                      # clearly changed proteins
        slope = float(np.median(fc(A)[big] / fc(T)[big])) if big.sum() >= 5 else 1.0
        if not 0.8 <= slope <= 1.25:
            err.append(f"fold changes are {slope:.2f}x the true log2 scale; check log base "
                       "(ln ~0.69x, log10 ~0.30x) or per-protein scaling")
    if err:
        report["score"] = 0.0
        return report
    report["gate"]["passed"] = True

    # ---------- references ----------
    refs = {k: f(pep).loc[A.index] for k, f in qm.METHODS.items()}
    ref_prof = {k: profile_rmse(v, T) for k, v in refs.items()}
    ref_fc = {k: float(np.sqrt(np.mean((fc(v) - fc(T)) ** 2))) for k, v in refs.items()}
    robust = ["median_polish_unique", "maxlfq_like_unique"]

    # ---------- 2. profile ----------
    a_prof = profile_rmse(A, T)
    s, raw = rel(a_prof, ref_prof["sum_all_peptides"], min(ref_prof[k] for k in robust))
    report["sections"]["profile"] = {"score": round(s, 4), "unclipped_skill": round(raw, 4),
                                     "profile_rmse_log2": round(a_prof, 4)}

    # ---------- 3. fold change ----------
    fe = fc(A) - fc(T)
    a_fc = float(np.sqrt(np.mean(fe ** 2)))
    s, raw = rel(a_fc, ref_fc["sum_all_peptides"], min(ref_fc[k] for k in robust))
    # diagnostic: proteins affected by outlier peptides
    pep_idx = pep.set_index("Peptide_ID")
    out_prots = sorted({pep_idx.loc[x, "Proteins"] for x in meta["outlier_peptides"]
                        if x in pep_idx.index} & set(A.index))
    clean = sorted(set(A.index) - set(out_prots))
    report["sections"]["fold_change"] = {
        "score": round(s, 4), "unclipped_skill": round(raw, 4),
        "fc_rmse_log2": round(a_fc, 4), "fc_bias_log2": round(float(fe.median()), 4),
        "fc_rmse_on_proteins_with_outlier_peptides": round(float(np.sqrt(np.mean(fe[out_prots] ** 2))), 4),
        "fc_rmse_on_other_proteins": round(float(np.sqrt(np.mean(fe[clean] ** 2))), 4),
        "n_proteins_with_outlier_peptides": len(out_prots)}

    # ---------- 4. bookkeeping ----------
    ints = {"total_peptides": len(pep), "unique_peptides": int(uniq.sum()),
            "shared_peptides": int((~uniq).sum()), "quantified_proteins": len(A)}
    checks = {k: man.get(k) == v for k, v in ints.items()}
    checks["integer_types"] = all(isinstance(man.get(k), int) and not isinstance(man.get(k), bool) for k in ints)
    checks["method_strings_present"] = all(isinstance(man.get(k), str) and man.get(k).strip()
                                           for k in ["quantification_method", "shared_peptide_handling"])
    report["sections"]["bookkeeping"] = {"score": round(sum(checks.values()) / len(checks), 4),
                                         "checks": checks, "expected": ints}

    report["reference_methods"] = {k: {"profile_rmse": round(ref_prof[k], 4), "fc_rmse": round(ref_fc[k], 4)}
                                   for k in refs}
    rp = res / "analysis_report.txt"
    report["optional"] = {"analysis_report_present": rp.exists(),
                          "manifest_quantification_method": man.get("quantification_method"),
                          "manifest_shared_peptide_handling": man.get("shared_peptide_handling")}
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
