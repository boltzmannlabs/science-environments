"""Reference protein-quantification methods (used by the evaluator and mock tests)."""
import numpy as np
import pandas as pd

SAMPLES = ["Control_Rep1", "Control_Rep2", "Control_Rep3",
           "Treated_Rep1", "Treated_Rep2", "Treated_Rep3"]


def _groups(pep, unique_only=True):
    df = pep.copy()
    if unique_only:
        df = df[~df["Proteins"].str.contains(";")]
        return {p: np.log2(g[SAMPLES].values) for p, g in df.groupby("Proteins")}
    df = df.assign(Proteins=df["Proteins"].str.split(";")).explode("Proteins")
    return {p: np.log2(g[SAMPLES].values) for p, g in df.groupby("Proteins")}


def _frame(d):
    return pd.DataFrame.from_dict(d, orient="index", columns=SAMPLES).rename_axis("protein_id").sort_index()


def sum_intensity(pep, unique_only=True):
    return _frame({p: np.log2(np.nansum(2 ** L, axis=0)) for p, L in _groups(pep, unique_only).items()})


def mean_log(pep):
    return _frame({p: np.nanmean(L, axis=0) for p, L in _groups(pep).items()})


def top3(pep):
    out = {}
    for p, L in _groups(pep).items():
        top = np.argsort(-np.nanmean(L, axis=1))[:3]
        out[p] = np.log2(np.nanmean(2 ** L[top], axis=0))
    return _frame(out)


def median_polish(pep, n_iter=20):
    out = {}
    for p, L in _groups(pep).items():
        R = L.copy(); col = np.zeros(L.shape[1]); overall = 0.0
        for _ in range(n_iter):
            r = np.nanmedian(R, axis=1); r = np.where(np.isnan(r), 0, r)
            R = R - r[:, None]
            c = np.nanmedian(R, axis=0); c = np.where(np.isnan(c), 0, c)
            R = R - c[None, :]; col += c
            m = np.median(col); col -= m; overall += m
        out[p] = overall + col + np.nanmedian(np.nanmean(L, axis=1))   # level ~ typical peptide
    return _frame(out)


def maxlfq(pep):
    """MaxLFQ-style: median pairwise log-ratios over shared peptides, solved by least squares."""
    out = {}
    for p, L in _groups(pep).items():
        n = L.shape[1]; A, b = [], []
        for i in range(n):
            for j in range(i + 1, n):
                ok = ~np.isnan(L[:, i]) & ~np.isnan(L[:, j])
                if ok.sum() >= 1:
                    row = np.zeros(n); row[i], row[j] = 1, -1
                    A.append(row); b.append(np.median(L[ok, i] - L[ok, j]))
        A.append(np.ones(n)); b.append(0.0)
        x = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)[0]
        out[p] = x + np.nanmedian(np.nanmax(L, axis=0))
    return _frame(out)


METHODS = {"sum_all_peptides": lambda p: sum_intensity(p, unique_only=False),
           "sum_unique": sum_intensity, "mean_log_unique": mean_log, "top3_unique": top3,
           "median_polish_unique": median_polish, "maxlfq_like_unique": maxlfq}
