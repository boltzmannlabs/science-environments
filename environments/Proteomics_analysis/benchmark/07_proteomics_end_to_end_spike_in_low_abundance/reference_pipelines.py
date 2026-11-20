"""Reference pipelines for Task 7 (UPS1 spiked into yeast, Ramus et al. 2016, PXD001819)."""
import numpy as np
import pandas as pd
from scipy import optimize, special, stats

CONTRASTS = {"C1": ("25000amol", "2500amol"), "C2": ("5000amol", "500amol"), "C3": ("2500amol", "500amol")}
TRUE_FC = {k: float(np.log2(int(h[:-4]) / int(l[:-4]))) for k, (h, l) in CONTRASTS.items()}


def cols(amount):
    return [f"LFQ intensity {amount}_{i}" for i in (1, 2, 3)]


def is_ups(header):
    return isinstance(header, str) and "_UPS" in header


def flagged(pg):
    return pg["Reverse"].notna() | pg["Potential contaminant"].notna() | pg["Only identified by site"].notna()


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(q, 1)
    return out


def moderated_t(XL, XH, return_se=False):
    nl, nh = np.sum(~np.isnan(XL), 1), np.sum(~np.isnan(XH), 1)
    d = (nl + nh - 2).astype(float)
    ss = np.nansum((XL - np.nanmean(XL, 1, keepdims=True)) ** 2, 1) + np.nansum((XH - np.nanmean(XH, 1, keepdims=True)) ** 2, 1)
    s2 = np.maximum(ss / d, 1e-8)
    e = np.log(s2) - special.digamma(d / 2) + np.log(d / 2)
    v = np.mean((e - e.mean()) ** 2 * len(e) / (len(e) - 1) - special.polygamma(1, d / 2))
    if v <= 0:
        sp, df = np.full_like(s2, np.exp(e.mean())), np.full_like(d, 1e6)
    else:
        d0 = 2 * optimize.brentq(lambda x: special.polygamma(1, x) - v, 1e-8, 1e8)
        s0 = np.exp(e.mean() + special.digamma(d0 / 2) - np.log(d0 / 2))
        sp, df = (d0 * s0 + d * s2) / (d0 + d), d + d0
    fc = np.nanmean(XH, 1) - np.nanmean(XL, 1)
    se = np.sqrt(sp * (1 / nl + 1 / nh))
    if return_se:
        return fc, 2 * stats.t.sf(np.abs(fc / se), df), se, df
    return fc, 2 * stats.t.sf(np.abs(fc / se), df)


def run(pg, contrast, mode="strict", fc_cut=1.0, q=0.05, shift=2.5, width=0.1, seed=1, min_present=3):
    """mode: 'strict' (>=2 valid in both), 'strict_onoff' (+ presence/absence calls), 'impute' (down-shift)."""
    hi, lo = CONTRASTS[contrast]
    df = pg[~flagged(pg)]
    allc = [c for c in df.columns if c.startswith("LFQ intensity ")]
    XA = np.log2(df[allc].replace(0, np.nan).astype(float))
    yeast = ~df["Fasta headers"].map(is_ups).values
    XA = XA - XA[yeast].median()                             # anchor on the constant yeast background
    XA.index = df["Protein IDs"].values
    L, H = XA[cols(lo)].values.copy(), XA[cols(hi)].values.copy()
    nl, nh = (~np.isnan(L)).sum(1), (~np.isnan(H)).sum(1)
    ids = XA.index.values
    rows = []
    if mode == "impute":
        keep = (nl >= 2) | (nh >= 2)
        L, H, idk = L[keep], H[keep], ids[keep]
        rng = np.random.default_rng(seed)
        for M, cl in ((L, cols(lo)), (H, cols(hi))):
            for j, cn in enumerate(cl):
                mu, sd = np.nanmean(XA[cn]), np.nanstd(XA[cn]); m = np.isnan(M[:, j])
                M[m, j] = rng.normal(mu - shift * sd, width * sd, m.sum())
        fc, p = moderated_t(L, H); adj = bh(p)
        sig = (adj <= q) & (np.abs(fc) >= fc_cut)
        return pd.DataFrame({"protein_id": idk, "log2fc": fc, "p_value": p, "adj_p_value": adj,
                             "significant": sig, "call_basis": "test"})
    keep = (nl >= 2) & (nh >= 2)
    fc, p = moderated_t(L[keep], H[keep]); adj = bh(p)
    out = pd.DataFrame({"protein_id": ids[keep], "log2fc": fc, "p_value": p, "adj_p_value": adj,
                        "significant": (adj <= q) & (np.abs(fc) >= fc_cut), "call_basis": "test"})
    if mode == "strict_onoff":
        # two-sided: no assumption about direction; consistent detection in one group, none in the other
        on = ((nh >= min_present) & (nl == 0)) | ((nl >= min_present) & (nh == 0))
        out = pd.concat([out, pd.DataFrame({"protein_id": ids[on], "log2fc": np.nan, "p_value": np.nan,
                                            "adj_p_value": np.nan, "significant": True,
                                            "call_basis": "presence_absence"})], ignore_index=True)
    return out


REFERENCES = {"strict_no_fc_cutoff": dict(mode="strict", fc_cut=0.0),
              "strict_fc1": dict(mode="strict", fc_cut=1.0),
              "strict_fc1_plus_presence_absence": dict(mode="strict_onoff", fc_cut=1.0),
              "downshift_impute_fc1": dict(mode="impute", fc_cut=1.0)}


def strict_test_stats(pg, contrast):
    """Strict-filter moderated t on yeast-anchored data, returning fc, se, df per protein (for integrity checks)."""
    hi, lo = CONTRASTS[contrast]
    df = pg[~flagged(pg)]
    allc = [c for c in df.columns if c.startswith("LFQ intensity ")]
    XA = np.log2(df[allc].replace(0, np.nan).astype(float))
    yeast = ~df["Fasta headers"].map(is_ups).values
    XA = XA - XA[yeast].median(); XA.index = df["Protein IDs"].values
    L, H = XA[cols(lo)].values, XA[cols(hi)].values
    keep = ((~np.isnan(L)).sum(1) >= 2) & ((~np.isnan(H)).sum(1) >= 2)
    fc, p, se, dfree = moderated_t(L[keep], H[keep], return_se=True)
    return pd.DataFrame({"fc": fc, "se": se, "df": dfree, "yeast": yeast[keep]}, index=XA.index[keep])
