"""Clustering grader: partition quality against the reference lineages.

The cluster count is informational only. Homogeneity and majority-label recall reward clusters that
are pure and that resolve small populations, without penalizing defensible finer clusters.
ARI/NMI are reported for information only (they penalize finer clusters).
"""
from .common import ari_nmi, clip01, homogeneity, majority_macro_recall


def grade(ctx, p):
    a, gold = ctx.assignments(), ctx.gold()
    if a is None:
        return (0.0 if p.get("required_file") else None), {"error": "missing required file: cluster_assignments.csv"}
    if not {"cell_id", "cluster_id"} <= set(a.columns):
        return 0.0, {"error": "cluster_assignments.csv needs columns cell_id and cluster_id"}
    m = a.merge(gold, on="cell_id", how="inner")
    if len(m) < 10:
        return 0.0, {"error": "cell identifiers do not match the reference cells"}
    bad = a.cell_id.duplicated().any() or a.cluster_id.isna().any()
    valid = len(set(m.cell_id)) / len(gold) * (0.5 if bad else 1.0)
    h = homogeneity(m.gold_lineage, m.cluster_id)
    r = majority_macro_recall(m.gold_lineage, m.cluster_id)
    ari, nmi = ari_nmi(m.cluster_id, m.gold_lineage)
    ari_f, nmi_f = ari_nmi(m.cluster_id, m.ref_group)
    def scaled(v, cfg):
        return clip01((v - cfg["floor"]) / (cfg["full"] - cfg["floor"]))

    items = {"valid_assignments": clip01(valid),
             "lineage_homogeneity": scaled(h, p["homogeneity"]),
             "lineage_majority_macro_recall": scaled(r, p["majority_recall"])}
    w = p["weights"]
    score = sum(w[k] * items[k] for k in items) / sum(w[k] for k in items)
    info = {"items": items, "n_clusters_info": int(a.cluster_id.nunique()),
            "homogeneity": round(h, 3), "majority_macro_recall": round(r, 3),
            "ARI_lineage_info": round(ari, 3), "NMI_lineage_info": round(nmi, 3),
            "ARI_fine_groups_info": round(ari_f, 3), "NMI_fine_groups_info": round(nmi_f, 3)}
    return float(score), info
