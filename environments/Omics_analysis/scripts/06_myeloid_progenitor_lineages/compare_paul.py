#!/usr/bin/env python3
"""Compare an agent's output for myeloid_progenitor_lineages with Paul et al. 2015 (Cell 163:1663).
Usage: python3 -I compare_paul.py CLUSTER_ASSIGNMENTS.csv CLUSTER_MARKERS.csv SUMMARY.json REPORT.txt PAUL_TABLE_S3.xlsx OUT.json
Only metrics with an obvious definition are computed; no weights, no pass/fail thresholds."""
import sys, re, json, hashlib, platform
import numpy as np, pandas as pd, openpyxl, scipy

ca_path, cm_path, sum_path, rep_path, s3_path, out_path = sys.argv[1:7]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

# --- what the paper reports (main text of Paul et al. 2015) -------------------------------------------
PAPER_FATE = {  # cluster -> fate, as stated in the main text
    **{k: "erythrocyte" for k in range(1, 8)}, 8: "megakaryocyte", 11: "dendritic cell", 13: "basophil",
    14: "monocyte", 15: "monocyte", 16: "neutrophil", 17: "neutrophil", 18: "eosinophil", 19: "NK-like (excluded by the paper)"}
PAPER_FATES = ["erythrocyte", "megakaryocyte", "monocyte", "dendritic cell", "neutrophil", "eosinophil", "basophil"]
# keyword rules to read an agent label as a paper fate (label with no fate keyword, or "mixed", is not scored)
def label_fates(label):
    l = label.lower()
    if "mixed" in l or "cycling" in l: return None
    if "t/nk" in l: return {"NK-like (excluded by the paper)"}
    if "megakaryocyte" in l: return {"megakaryocyte"}
    if "erythroid" in l: return {"erythrocyte"}
    if "granulocyte/monocyte" in l: return {"neutrophil", "monocyte", "eosinophil", "basophil"}
    if "neutrophil" in l or "granulocyte" in l: return {"neutrophil", "eosinophil", "basophil"}
    if "dendritic" in l: return {"dendritic cell"}
    if "monocyte" in l: return {"monocyte"}
    return None

# --- Table S3: mean expression of 3,461 genes in the paper's 19 clusters -------------------------------
wb = openpyxl.load_workbook(s3_path, read_only=True, data_only=True)
rows = list(wb.worksheets[0].iter_rows(values_only=True))
cl = list(range(1, 20))
S = pd.DataFrame([r[:20] for r in rows[1:] if r[0] is not None], columns=["gene"] + cl)
S[cl] = S[cl].apply(pd.to_numeric, errors="coerce")
sd = S[cl].std(axis=1).replace(0, np.nan)
Z = S[cl].sub(S[cl].mean(axis=1), axis=0).div(sd, axis=0)
Z.index = S.gene.astype(str)
tok = {}
for g in Z.index:
    for t in g.split(";"): tok.setdefault(t, g)
def lookup(gene):
    if gene in Z.index: return gene
    return next((tok[t] for t in gene.split(";") if t in tok), None)

ca = pd.read_csv(ca_path); cm = pd.read_csv(cm_path); summ = json.load(open(sum_path)); rep = open(rep_path).read()
labels = ca.drop_duplicates("cluster_id").set_index("cluster_id").cell_type.to_dict()
sizes = ca.groupby("cluster_id").size().to_dict()

# --- agent cluster -> paper cluster: mean z-score of the agent's marker genes in each paper cluster ------
M, per = {}, {}
for c, g in cm.groupby("cluster_id"):
    keys = [k for k in (lookup(x) for x in g.gene.astype(str)) if k]
    M[c] = Z.loc[keys].mean(axis=0, skipna=True) if keys else pd.Series(np.nan, index=cl)
    top = M[c].sort_values(ascending=False)
    fate = PAPER_FATE.get(int(top.index[0]))
    exp = label_fates(labels[c])
    per[int(c)] = {"agent_label": labels[c], "n_cells": int(sizes[c]), "n_markers": int(len(g)), "n_markers_in_paper_table": len(keys),
        "best_paper_cluster": int(top.index[0]), "best_paper_cluster_fate": fate or "early / unassigned in the paper",
        "best_score": round(float(top.iloc[0]), 2), "second_paper_cluster": int(top.index[1]), "second_score": round(float(top.iloc[1]), 2),
        "label_read_as": sorted(exp) if exp else None,
        "label_consistent_with_best_match": (fate in exp) if (exp and fate) else (False if exp else None)}
M = pd.DataFrame(M).T

scored = [v for v in per.values() if v["label_consistent_with_best_match"] is not None]
fates_matched = {f: sorted(c for c, v in per.items() if v["best_paper_cluster_fate"] == f) for f in PAPER_FATES}
paper_side = {k: {"fate": PAPER_FATE.get(k, "early / unassigned"), "best_agent_cluster": int(M[k].idxmax()), "best_score": round(float(M[k].max()), 2)} for k in cl}

# --- report vs marker table: genes the report cites for a cluster that are absent from that cluster's marker table
vocab = set(tok) | {t for g in cm.gene.astype(str) for t in g.split(";")}
marker_tokens = {c: {t for g in grp.gene.astype(str) for t in g.split(";")} for c, grp in cm.groupby("cluster_id")}
cited, absent = 0, []
for line in rep.splitlines():
    m = re.match(r"^(\d+): (.*)$", line.strip())
    if not m or int(m.group(1)) not in marker_tokens: continue
    c = int(m.group(1)); body = m.group(2).split(";", 1)[0]  # genes are listed before the first semicolon; later text is commentary
    genes = {t.strip(".,;:()") for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-\.]*", body)} & vocab
    for g in sorted(genes):
        cited += 1
        if g not in marker_tokens[c]: absent.append({"cluster": c, "gene": g})

out = {
 "task_id": "myeloid_progenitor_lineages",
 "reference": {"paper": "Paul et al. 2015, Cell 163:1663-1677 (doi 10.1016/j.cell.2015.11.013)", "dataset": "GSE72857", "tables": "Supplementary Table S3 (mean expression of 3,461 genes in 19 clusters); Table S2 (batches)"},
 "paper_reported": {
   "cells_clustered": 2730, "clusters": 19, "differential_genes": 3461, "cluster_frequency_range": "0.3% to 13%",
   "fates": PAPER_FATES, "cluster_fate_map (from the main text)": {str(k): v for k, v in PAPER_FATE.items()},
   "excluded_cluster": "C19, Ccl5+ NK-like cells (mis-sorted)",
   "main_claim": "cells are transcriptionally primed toward single fates; no progenitors of mixed lineages in unperturbed cells"},
 "agent_reported": {
   "cells_input": summ.get("cells_input"), "cells_retained": summ.get("cells_retained"), "n_clusters": summ.get("n_clusters"),
   "fates_identified": summ.get("fates_identified"), "clusters": {str(c): {"label": labels[c], "n_cells": int(sizes[c])} for c in sorted(labels)},
   "cluster_relationships": summ.get("cluster_relationships"), "model": summ.get("model")},
 "metrics": {
   "fates": {"paper_fates": len(PAPER_FATES),
             "paper_fates_with_a_best_matching_agent_cluster": sum(1 for f in PAPER_FATES if fates_matched[f]),
             "agent_clusters_best_matching_each_fate": fates_matched},
   "per_agent_cluster": {str(c): per[c] for c in sorted(per)},
   "labels_consistent_with_best_match": {"consistent": sum(1 for v in scored if v["label_consistent_with_best_match"]), "scored_labels": len(scored)},
   "per_paper_cluster": {str(k): v for k, v in paper_side.items()},
   "paper_clusters_that_are_the_best_match_of_an_agent_cluster": sorted({v["best_paper_cluster"] for v in per.values()}),
   "report_marker_claims": {"genes_cited_per_cluster_and_recognized": cited, "cited_but_absent_from_that_cluster_marker_table": absent}},
 "notes": [
   "The paper's supplement has no per-cell cluster labels, so cells cannot be compared one by one. The comparison is at the level of clusters, marker genes and fates.",
   "The agent's 12 clusters and the paper's 19 clusters come from different cell sets and resolutions, so cluster counts are reported side by side and not compared.",
   "best_paper_cluster is the paper cluster with the highest mean z-score of the agent cluster's marker genes in Table S3. This mapping is this benchmark's own method, not the paper's.",
   "A label is scored only if it names a fate. Labels with 'mixed', 'cycling' or no fate word are not scored. The paper does not report C19 as a fate, so a T/NK label matching C19 counts as consistent.",
   "No agent cluster has eosinophil (paper C18) or basophil (paper C13) as its best match. The agent's summary lists neither fate."],
 "provenance": {"inputs_sha256": {"cluster_assignments.csv": sha(ca_path), "cluster_markers.csv": sha(cm_path), "summary.json": sha(sum_path),
                 "analysis_report.txt": sha(rep_path), "paul_table_s3.xlsx": sha(s3_path)},
   "script_sha256": sha(__file__),
   "scorer": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "openpyxl": openpyxl.__version__}}}
json.dump(out, open(out_path, "w"), indent=2)
print(json.dumps({"fates": out["metrics"]["fates"], "consistent": out["metrics"]["labels_consistent_with_best_match"],
                  "report_marker_claims": out["metrics"]["report_marker_claims"]}, indent=1))
