"""Reference end-to-end pipelines for E1 (MaxLFQ HeLa + E. coli benchmark, PXD000279)."""
import numpy as np
import pandas as pd
from scipy import optimize, special, stats

L = ["LFQ intensity L1", "LFQ intensity L2", "LFQ intensity L3"]
H = ["LFQ intensity H1", "LFQ intensity H2", "LFQ intensity H3"]


def species_of(header):
    if not isinstance(header, str) or not header.strip():
        return "unknown"
    s = set()
    for part in [p for p in header.split(";") if p.strip()]:
        if "_ECOLI" in part or "Escherichia" in part:
            s.add("ECOLI")
        elif "_HUMAN" in part or "Homo sapiens" in part:
            s.add("HUMAN")
        else:
            s.add("other")
    return s.pop() if len(s) == 1 else "mixed"


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(q, 1)
    return out


def moderated_t(XL, XH):
    """limma-style moderated t allowing missing values (per-protein residual df)."""
    nl, nh = np.sum(~np.isnan(XL), 1), np.sum(~np.isnan(XH), 1)
    d = (nl + nh - 2).astype(float)
    ssl = np.nansum((XL - np.nanmean(XL, 1, keepdims=True)) ** 2, 1)
    ssh = np.nansum((XH - np.nanmean(XH, 1, keepdims=True)) ** 2, 1)
    s2 = (ssl + ssh) / d
    e = np.log(s2) - special.digamma(d / 2) + np.log(d / 2)
    v = np.mean((e - e.mean()) ** 2 * len(e) / (len(e) - 1) - special.polygamma(1, d / 2))
    if v <= 0:
        d0, s0 = np.inf, np.exp(e.mean())
        sp = np.full_like(s2, s0); df = np.full_like(d, 1e6)
    else:
        d0 = 2 * optimize.brentq(lambda x: special.polygamma(1, x) - v, 1e-8, 1e8)
        s0 = np.exp(e.mean() + special.digamma(d0 / 2) - np.log(d0 / 2))
        sp = (d0 * s0 + d * s2) / (d0 + d); df = d + d0
    fc = np.nanmean(XH, 1) - np.nanmean(XL, 1)
    t = fc / np.sqrt(sp * (1 / nl + 1 / nh))
    return fc, 2 * stats.t.sf(np.abs(t), df)


def run(pg, normalization="none", test="moderated", min_valid=2):
    df = pg[pg["Reverse"].isna() & pg["Contaminant"].isna() & pg["Only identified by site"].isna()].copy()
    X = np.log2(df[L + H].replace(0, np.nan).astype(float))
    X.index = df["Protein IDs"].values
    keep = (X[L].notna().sum(1) >= min_valid) & (X[H].notna().sum(1) >= min_valid)
    X = X[keep]
    if normalization == "median_all":
        X = X - X.median() + X.median().mean()
    elif normalization == "median_human":
        hum = pg.set_index("Protein IDs").loc[X.index, "Fasta headers"].map(species_of) == "HUMAN"
        X = X - X[hum.values].median() + X[hum.values].median().mean()
    XL, XH = X[L].values, X[H].values
    if test == "moderated":
        fc, p = moderated_t(XL, XH)
    else:
        fc = np.nanmean(XH, 1) - np.nanmean(XL, 1)
        p = stats.ttest_ind(XH, XL, axis=1, equal_var=(test == "student"), nan_policy="omit").pvalue
        p = np.asarray(p, float)
    return pd.DataFrame({"protein_id": X.index, "log2fc": fc, "p_value": p, "adj_p_value": bh(p)})
