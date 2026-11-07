"""Marker-gene grader: expected canonical markers among each cluster's top positive genes."""
import numpy as np
import pandas as pd

from .common import clip01

ALIASES = {"cluster_id": ["cluster_id", "cluster", "group", "leiden"],
           "gene": ["gene", "names", "gene_name"],
           "score": ["score", "scores"],
           "logfoldchange": ["logfoldchange", "logfoldchanges", "log2fc", "avg_log2fc", "logfc"],
           "p_value_adj": ["p_value_adj", "pvals_adj", "p_val_adj", "padj", "fdr"]}


def load_markers(ctx):
    path = ctx.agent_dir / "cluster_markers.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    lower, rename = {c.lower(): c for c in df.columns}, {}
    for want, alts in ALIASES.items():
        hit = next((lower[a] for a in alts if a in lower), None)
        if hit:
            rename[hit] = want
    df = df.rename(columns=rename)
    if not {"cluster_id", "gene"} <= set(df.columns):
        return None
    df["cluster_id"] = df["cluster_id"].astype(str)
    for c in ("score", "logfoldchange", "p_value_adj"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def top_genes(d, n):
    if "logfoldchange" in d:
        d = d[d.logfoldchange > 0]
    if "p_value_adj" in d:
        d = d[d.p_value_adj < 0.05]
    key = "score" if "score" in d.columns else ("logfoldchange" if "logfoldchange" in d.columns else None)
    if key:
        d = d.sort_values(key, ascending=False)
    return list(dict.fromkeys(d.gene.astype(str)))[: n]


def grade(ctx, p):
    mk = load_markers(ctx)
    if mk is None:
        return (0.0 if p.get("required_file") else None), {
            "error": "cluster_markers.csv missing or lacks cluster_id/gene columns"}
    top = {cid: top_genes(d, p["top_n"]) for cid, d in mk.groupby("cluster_id")}
    n_rows = mk.groupby("cluster_id").size()
    per, wts, detail = {}, {}, {}
    if p["mode"] == "mapped":
        cmap = pd.read_csv(ctx.ref_dir / "cluster_map.csv", dtype=str)
        for r in cmap.itertuples(index=False):
            exp = set(p["expected"][r.ref_group])
            hits = sorted(exp & set(top.get(r.neutral_id, [])))
            per[r.neutral_id] = clip01(len(hits) / p["min_hits"])
            wts[r.neutral_id] = p["low_conf_weight"] if r.confidence == "low" else 1.0
            detail[r.neutral_id] = {"group": r.gold_fine_label, "hits": hits,
                                    "precision_at_k": round(len(hits) / p["top_n"], 3),
                                    "recall_at_k": round(len(hits) / len(exp), 3)}
        present = [c for c in cmap.neutral_id if c in top]
        fmt = [len(present) / len(cmap),
               float(np.mean([n_rows[c] >= p["min_rows_per_cluster"] for c in present])) if present else 0.0]
        hits_score = sum(per[k] * wts[k] for k in per) / sum(wts.values())
        score = (1 - p["format_weight"]) * hits_score + p["format_weight"] * float(np.mean(fmt))
        info = {"per_cluster": per, "detail": detail,
                "format": {"clusters_present": round(fmt[0], 3), "rows_per_cluster_ok": round(fmt[1], 3)}}
        return float(score), info
    # majority mode: each reference lineage needs a dedicated, mostly pure agent cluster
    a, gold = ctx.assignments(), ctx.gold()
    if a is None:
        return None, {"error": "cluster_assignments.csv needed to map clusters to lineages"}
    m = a.merge(gold, on="cell_id", how="inner").assign(cluster_id=lambda d: d.cluster_id.astype(str))
    maj = m.groupby("cluster_id").gold_lineage.agg(lambda s: s.value_counts().idxmax())
    pur = m.groupby("cluster_id").gold_lineage.agg(lambda s: s.value_counts(normalize=True).max())
    size = m.groupby("cluster_id").size()
    for lin, exp in p["expected"].items():
        cl = [c for c in maj.index if maj[c] == lin and pur[c] >= p["min_purity"]]
        if not cl:
            per[lin], detail[lin] = 0.0, "no dedicated cluster"
            continue
        vals = [clip01(len(set(exp) & set(top.get(c, []))) / p["min_hits"]) for c in cl]
        per[lin] = float(np.average(vals, weights=[size[c] for c in cl]))
        detail[lin] = {c: sorted(set(exp) & set(top.get(c, []))) for c in cl}
    return float(np.mean(list(per.values()))), {"per_lineage": per, "detail": detail}
