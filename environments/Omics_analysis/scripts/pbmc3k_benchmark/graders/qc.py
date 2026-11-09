"""Normalization / HVG grader (reads the agent's .h5ad)."""
import numpy as np

from .common import clip01


def _dense(x):
    return x.toarray() if hasattr(x, "toarray") else np.asarray(x)


def _lognorm_constant(mat, tol, min_fraction):
    """True if expm1(values) sum to one constant per cell (any target sum)."""
    x = _dense(mat[:300]).astype(float)
    if not np.isfinite(x).all() or x.min() < 0:
        return False
    sums = np.expm1(x).sum(axis=1)
    med = float(np.median(sums))
    return med > 0 and float((np.abs(sums - med) / med <= tol).mean()) >= min_fraction


def grade(ctx, p):
    try:
        import anndata as ad
    except ImportError:
        return None, {"error": "anndata not installed; normalization checks skipped"}
    path = next((ctx.agent_dir / n for n in p["h5ad_names"] if (ctx.agent_dir / n).exists()), None)
    if path is None:
        found = sorted(ctx.agent_dir.glob("*.h5ad"))
        path = found[0] if found else None
    if path is None:
        return (0.0 if p.get("required_file") else None), {"error": "no .h5ad file found"}
    try:
        a = ad.read_h5ad(path)
    except Exception as exc:
        return 0.0, {"error": f"unreadable h5ad: {type(exc).__name__}: {exc}"}
    gold_ids = set(ctx.gold().cell_id)
    items, info = {}, {"file": path.name, "n_obs": int(a.n_obs), "n_vars": int(a.n_vars)}
    cov = len(set(a.obs_names) & gold_ids) / len(gold_ids)
    items["cells_present"] = clip01(cov / p["cell_coverage_min"])
    items["genes_kept"] = clip01((a.n_vars / p["n_genes_input"]) / p["min_gene_fraction"])
    has_counts = "counts" in a.layers
    if has_counts:
        x = _dense(a.layers["counts"][:300]).astype(float)
        items["counts_layer_integer"] = 1.0 if (np.isfinite(x).all() and np.allclose(x, np.rint(x))) else 0.0
        med = float(np.median(np.asarray(a.layers["counts"].sum(axis=1)).ravel()))
        rel = abs(med - p["counts_median_total"]) / p["counts_median_total"]
        info["counts_median_rel_diff"] = round(rel, 4)
        items["counts_preserved"] = 1.0 if rel <= p["counts_median_tol"] else 0.0
    else:
        items["counts_layer_integer"] = 0.0
        items["counts_preserved"] = 0.0
    lm = p["lognorm"]
    mats = [("X", a.X)] + ([("raw.X", a.raw.X)] if a.raw is not None else [])
    where = next((n for n, m in mats if _lognorm_constant(m, lm["tolerance"], lm["min_fraction_cells"])), None)
    items["log_normalized_constant_target"] = 1.0 if where else 0.0
    info["normalized_matrix_in"] = where
    if "highly_variable" in a.var.columns:
        h = set(a.var_names[a.var["highly_variable"].to_numpy(bool)])
        lo, hi = p["n_hvgs_range"]
        items["n_hvgs_in_range"] = 1.0 if lo <= len(h) <= hi else 0.0
        items["top10_hvgs_present"] = sum(g in h for g in p["top10"]) / len(p["top10"])
        ref_hvg = set((ctx.ref_dir / "hvg_reference.txt").read_text().split())
        rec = len(h & ref_hvg) / len(ref_hvg)
        info["n_hvgs"], info["hvg_ref_recall"] = len(h), round(rec, 3)
        items["hvg_ref_recall"] = clip01(rec / p["hvg_ref_recall_min"])
    else:
        items.update({"n_hvgs_in_range": 0.0, "top10_hvgs_present": 0.0, "hvg_ref_recall": 0.0})
        info["warning"] = "var['highly_variable'] missing"
    info["items"] = items
    return float(np.mean(list(items.values()))), info
