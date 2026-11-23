"""Annotation grader: lineage recall/precision/F1, subtype credit, unresolved handling, evidence."""
import numpy as np
import pandas as pd

from .common import LINEAGES, clip01, parse_lineage, subtype_credit


def _credit(al, gl, low, partial):
    if al == gl:
        return 1.0
    if al == "T/NK" and gl in ("T", "NK"):
        return 0.5
    if low and al in ("T", "NK", "T/NK") and gl in ("T", "NK"):
        return 0.5  # T/NK confusion inside the low-confidence reference groups
    if low and al == "Unknown":
        return partial  # leaving an ambiguous reference group unresolved is acceptable
    return 0.0


def grade(ctx, p):
    a, gold = ctx.assignments(), ctx.gold()
    if a is None or not {"cell_id", "cell_type"} <= set(a.columns):
        return (0.0 if p.get("required_file") else None), {
            "error": "cluster_assignments.csv needs columns cell_id and cell_type"}
    m = a.merge(gold, on="cell_id", how="inner")
    if len(m) < 10:
        return 0.0, {"error": "cell identifiers do not match the reference cells"}
    lin = m.cell_type.map(parse_lineage)
    if "annotation_status" in m.columns:
        lin = lin.where(m.annotation_status.astype(str).str.strip().str.lower() != "unresolved", "Unknown")
    m["agent_lineage"] = lin
    low = (m.confidence == "low").to_numpy()
    m["credit"] = [_credit(al, gl, lw, p["unresolved_partial_credit"])
                   for al, gl, lw in zip(m.agent_lineage, m.gold_lineage, low)]
    m["sub"] = [subtype_credit(f, t) if c == 1.0 else 0.0 for f, t, c in zip(m.gold_fine_label, m.cell_type, m.credit)]
    recall = m.groupby("gold_lineage").credit.mean().reindex(LINEAGES).fillna(0.0)
    pred = m[m.agent_lineage.isin(LINEAGES)].groupby("agent_lineage").credit.mean()
    precision = float(pred.mean()) if len(pred) else 0.0
    f1 = [(2 * pred.get(L, 0.0) * recall[L] / (pred.get(L, 0.0) + recall[L])) if pred.get(L, 0.0) + recall[L] else 0.0
          for L in LINEAGES]
    sub_by_group = m.groupby("gold_fine_label")["sub"].mean()
    items = {"lineage_macro_recall": float(recall.mean()), "lineage_macro_precision": precision,
             "subtype_credit": float(sub_by_group.mean()), "evidence": None}
    ev_path = ctx.agent_dir / "cluster_annotation.csv"
    if ev_path.exists():
        ev = pd.read_csv(ev_path, dtype=str)
        if {"cluster_id", "supporting_markers"} <= set(ev.columns):
            mm = m.assign(cluster_id=m.cluster_id.astype(str))
            true_lin = mm.groupby("cluster_id").gold_lineage.agg(lambda s: s.value_counts().idxmax())
            ok = []
            for r in ev.itertuples(index=False):
                genes = {g.strip() for g in str(r.supporting_markers).replace(",", ";").split(";") if g.strip()}
                lin_t = true_lin.get(str(r.cluster_id))
                ok.append(1.0 if lin_t and genes & set(p["canonical"].get(lin_t, [])) else 0.0)
            items["evidence"] = float(np.mean(ok)) if ok else None
    w = {k: p["weights"][k] for k, v in items.items() if v is not None}
    score = sum(w[k] * items[k] for k in w) / sum(w.values())
    info = {"items": items, "per_lineage_recall": {k: round(float(v), 3) for k, v in recall.items()},
            "macro_f1": round(float(np.mean(f1)), 3),
            "per_group_subtype": {k: round(float(v), 3) for k, v in sub_by_group.items()},
            "coverage_resolved": round(float((m.agent_lineage != "Unknown").mean()), 3),
            "unparsed_labels": sorted(set(m.loc[m.agent_lineage == "Other", "cell_type"]))}
    return float(score), info
