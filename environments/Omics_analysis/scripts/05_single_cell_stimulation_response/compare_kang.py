#!/usr/bin/env python3
"""Compare an agent's DE results (single_cell_stimulation_response) with Kang et al. 2018 Supp Table 1.
Usage: python3 -I compare_kang.py DE_RESULTS.csv SUPP_TABLE1.xlsx SUMMARY.json REPORT.txt OUT.json
Only metrics with an obvious definition are computed; no weights, no pass/fail thresholds."""
import sys, json, hashlib, itertools, platform
import numpy as np, pandas as pd, openpyxl, scipy
from scipy.stats import pearsonr, spearmanr

de_path, t1_path, sum_path, rep_path, out_path = sys.argv[1:6]
MAP = {"CD14+ Monocytes": "cd14", "FCGR3A+ Monocytes": "cd16 mono", "B cells": "cd19", "Dendritic cells": "dc",
       "CD4 T cells": "cd4", "NK cells": "nk", "CD8 T cells": "cd8"}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

d = pd.read_csv(de_path)
wb = openpyxl.load_workbook(t1_path, read_only=True, data_only=True)
paper = {}
for ws in wb.worksheets:
    rows = [r for r in list(ws.iter_rows(values_only=True))[1:] if r[7] is not None]
    num = lambda v: float(v) if v not in (None, "", "NA") else float("nan")
    paper[ws.title] = pd.DataFrame({"gene": [str(r[7]) for r in rows], "baseMean": [num(r[1]) for r in rows],
                                    "lfc": [num(r[2]) for r in rows], "padj": [num(r[6]) for r in rows]}).set_index("gene")
summ = json.load(open(sum_path))

def agent_tbl(ct):
    a = d[d.cell_type == ct].set_index("gene")
    return a[a.adj_p_value.notna()]
sig = lambda a: a[(a.adj_p_value < 0.05) & (a.log2_fold_change.abs() > 1)]

per, tested_counts, agent_counts, paper_counts = {}, {}, {}, {}
for ct, sh in MAP.items():
    a, p = agent_tbl(ct), paper[sh]
    s = sig(a); tested = [g for g in p.index if g in a.index]; untested = [g for g in p.index if g not in a.index]
    same = [g for g in tested if g in s.index and np.sign(s.loc[g, "log2_fold_change"]) == np.sign(p.loc[g, "lfc"])]
    wrong = [g for g in tested if g in s.index and np.sign(s.loc[g, "log2_fold_change"]) != np.sign(p.loc[g, "lfc"])]
    x = p.loc[tested, "lfc"].to_numpy(); y = a.loc[tested, "log2_fold_change"].to_numpy()
    agent_only = [g for g in s.index if g not in p.index]
    ao = s.loc[agent_only]
    near = ((ao.log2_fold_change.abs() < 1.25) | (ao.adj_p_value > 0.01)).mean() if len(ao) else float("nan")
    per[ct] = {"paper_sheet": sh, "n_paper_genes": len(p), "n_paper_genes_tested": len(tested), "n_paper_genes_untested": len(untested),
        "n_agent_tested": len(a), "n_agent_significant": len(s),
        "n_same_direction_significant": len(same), "n_significant_wrong_direction": len(wrong),
        "n_tested_not_significant": len(tested) - len(same) - len(wrong),
        "coverage": round(len(tested) / len(p), 3), "agreement": round(len(same) / len(tested), 3),
        "sign_agreement": round(float((np.sign(x) == np.sign(y)).mean()), 3), "lfc_pearson": round(float(pearsonr(x, y)[0]), 3),
        "n_agent_only_significant": len(agent_only), "agent_only_near_cutoff_share": round(float(near), 3),
        "paper_baseMean_median_tested": round(float(p.loc[tested, "baseMean"].median()), 1),
        "paper_baseMean_median_untested": round(float(p.loc[untested, "baseMean"].median()), 1) if untested else None,
        "paper_abs_lfc_median_tested": round(float(p.loc[tested, "lfc"].abs().median()), 2),
        "paper_abs_lfc_median_untested": round(float(p.loc[untested, "lfc"].abs().median()), 2) if untested else None}
    tested_counts[ct] = len(tested); agent_counts[ct] = len(s); paper_counts[ct] = len(p)

mean = lambda k: round(float(np.mean([v[k] for v in per.values()])), 3)
sections = {"agreement_among_tested": mean("agreement"), "sign_agreement": mean("sign_agreement"), "lfc_pearson": mean("lfc_pearson"), "coverage": mean("coverage")}

# negative control: agent results for one cell type against the paper's list for a different cell type
neg = []
for ct, sh2 in itertools.product(MAP, MAP.values()):
    if MAP[ct] == sh2: continue
    a, p = agent_tbl(ct), paper[sh2]; s = sig(a); t = [g for g in p.index if g in a.index]
    ok = [g for g in t if g in s.index and np.sign(s.loc[g, "log2_fold_change"]) == np.sign(p.loc[g, "lfc"])]
    neg.append(len(ok) / len(t))
neg_mean = round(float(np.mean(neg)), 3)

# ranking
order = lambda dct: sorted(dct, key=lambda k: -dct[k])
rank = {"paper_counts": paper_counts, "agent_counts": agent_counts, "paper_genes_tested_by_agent": tested_counts,
    "spearman_agent_vs_paper_counts": round(float(spearmanr([paper_counts[c] for c in MAP], [agent_counts[c] for c in MAP])[0]), 3),
    "spearman_agent_vs_paper_genes_tested": round(float(spearmanr([tested_counts[c] for c in MAP], [agent_counts[c] for c in MAP])[0]), 3),
    "order_agent": order(agent_counts), "order_paper": order(paper_counts), "order_paper_genes_tested": order(tested_counts)}

# top genes (ranked by log2 fold change among significant genes in all_cells, as in the task)
inter = lambda g, sign: [c for c in MAP if g in paper[MAP[c]].index and np.sign(paper[MAP[c]].loc[g, "lfc"]) == sign]
topchk = {}
for key, sign in (("top_induced_genes", 1), ("top_repressed_genes", -1)):
    genes = summ[key]; topchk[key] = {"n_genes": len(genes), "in_paper_any_sheet_same_direction": sum(1 for g in genes if inter(g, sign)),
        "in_paper_any_sheet_opposite_direction": sum(1 for g in genes if inter(g, -sign) and not inter(g, sign))}

# report claim verification
claims = [("CD14+ Monocytes","CCL8",1),("CD14+ Monocytes","CXCL10",1),("CD14+ Monocytes","CXCL11",1),("CD14+ Monocytes","CLEC5A",-1),
 ("CD14+ Monocytes","VCAN",-1),("CD14+ Monocytes","MMP9",-1),("FCGR3A+ Monocytes","CCL8",1),("FCGR3A+ Monocytes","CLEC5A",-1),
 ("FCGR3A+ Monocytes","VCAN",-1),("B cells","IFIT1",1),("B cells","TNFSF10",1),("B cells","SPI1",-1),("CD8 T cells","FGFBP2",-1),
 ("Dendritic cells","CXCL10",1),("Dendritic cells","IL1R2",-1)]
claims += [(c, g, 1) for c in MAP for g in ("IFIT1", "IFIT3") if c in ("CD4 T cells", "CD8 T cells", "NK cells")]
claims += [(c, g, 1) for c in MAP for g in ("IFIT1", "IFIT3", "RSAD2") if c in ("CD14+ Monocytes","FCGR3A+ Monocytes","B cells","Dendritic cells")]
claims = list(dict.fromkeys(claims))
def okc(ct, g, sign):
    a = agent_tbl(ct)
    return g in a.index and a.loc[g, "adj_p_value"] < 0.05 and abs(a.loc[g, "log2_fold_change"]) > 1 and np.sign(a.loc[g, "log2_fold_change"]) == sign
claims_ok = sum(okc(*c) for c in claims)
rep = open(rep_path).read()
tested_in_report = all(f"'{ct}': {len(agent_tbl(ct))}" in rep for ct in MAP) and f"'all_cells': {len(agent_tbl('all_cells'))}" in rep

# megakaryocyte genes (outside the score)
pm = paper["megakaryocyte"]; aa = agent_tbl("all_cells")
mega = {"n_paper_genes": len(pm), "in_agent_all_cells_table": int(sum(g in aa.index for g in pm.index)),
        "significant_same_direction_in_all_cells": int(sum(g in aa.index and abs(aa.loc[g,"log2_fold_change"])>1 and aa.loc[g,"adj_p_value"]<0.05 and np.sign(aa.loc[g,"log2_fold_change"])==np.sign(pm.loc[g,"lfc"]) for g in pm.index))}

t1_rules = {k: {"min_abs_lfc": round(float(v.lfc.abs().min()), 3), "max_padj": float(v.padj.max()), "n_padj_NA": int(v.padj.isna().sum()), "min_baseMean": round(float(v.baseMean.min()), 2)} for k, v in paper.items()}
keys = ["n_paper_genes_tested", "coverage", "n_same_direction_significant", "n_significant_wrong_direction", "n_tested_not_significant", "agreement",
        "sign_agreement", "lfc_pearson", "n_agent_only_significant", "agent_only_near_cutoff_share", "paper_baseMean_median_tested", "paper_baseMean_median_untested"]
dd = summ.get("data_used", {})
out = {
 "task_id": "single_cell_stimulation_response",
 "reference": {"paper": "Kang et al. 2018, Nat Biotechnol (PMID 29227470)", "dataset": "GSE96583", "table": "Supplementary Table 1"},
 "paper_reported": {
   "source": "Supplementary Table 1, one sheet per cell type; every row is a gene called by DESeq2 with abs(log2FC) > 1 and baseMean > 1",
   "genes_per_cell_type": {ct: len(paper[sh]) for ct, sh in MAP.items()},
   "megakaryocyte_genes": len(paper["megakaryocyte"]),
   "unique_genes_all_8_sheets": len(set().union(*[set(v.index) for v in paper.values()]))},
 "agent_reported": {
   "comparisons": summ.get("cell_types_analyzed"),
   "significant_genes_per_cell_type (adj_p<0.05 and abs_log2fc>1)": summ.get("n_significant_per_cell_type"),
   "genes_tested_per_cell_type": {ct: len(agent_tbl(ct)) for ct in MAP},
   "megakaryocytes": "not tested (see the agent's report)",
   "top_induced_genes": summ.get("top_induced_genes"), "top_repressed_genes": summ.get("top_repressed_genes"),
   "data_used": {"wells": dd.get("accessions"), "labels_used": dd.get("labels_used"), "cells_with_conflicting_condition_label": dd.get("metadata_stim_mismatches")},
   "model": summ.get("model")},
 "metrics": {
   "per_cell_type": {ct: {**{k: per[ct][k] for k in keys}, "agent_significant_to_paper_genes_ratio": round(per[ct]["n_agent_significant"] / per[ct]["n_paper_genes"], 3)} for ct in MAP},
   "all_seven_cell_types_mean": {"coverage": sections["coverage"], "agreement": sections["agreement_among_tested"], "sign_agreement": sections["sign_agreement"], "lfc_pearson": sections["lfc_pearson"]},
   "negative_control_mean_agreement_mismatched_cell_types": neg_mean,
   "cell_type_ranking_spearman": {"on_raw_counts": rank["spearman_agent_vs_paper_counts"], "paper_genes_tested_only": rank["spearman_agent_vs_paper_genes_tested"]},
   "top_20_genes": {"induced_found_in_paper_same_direction": f"{topchk['top_induced_genes']['in_paper_any_sheet_same_direction']} of {topchk['top_induced_genes']['n_genes']}",
                    "repressed_found_in_paper_same_direction": f"{topchk['top_repressed_genes']['in_paper_any_sheet_same_direction']} of {topchk['top_repressed_genes']['n_genes']}",
                    "found_in_paper_opposite_direction": topchk["top_induced_genes"]["in_paper_any_sheet_opposite_direction"] + topchk["top_repressed_genes"]["in_paper_any_sheet_opposite_direction"]},
   "megakaryocytes_in_all_cells_table": {"paper_genes": mega["n_paper_genes"], "present_in_agent_all_cells": mega["in_agent_all_cells_table"],
        "significant_same_direction": mega["significant_same_direction_in_all_cells"], "note": "the agent ran no megakaryocyte comparison; this uses its all_cells test"},
   "report": {"claims_checked": len(claims), "claims_confirmed": int(claims_ok), "counts_in_report_match_de_results": bool(tested_in_report)}},
 "notes": [
   "Coverage and agreement are reported separately and are not combined. There are no weights and no pass/fail flags.",
   "Coverage is limited by the agent's expression filter: compare paper_baseMean_median_tested with paper_baseMean_median_untested.",
   "Counts of significant genes are not a measure of agreement; use the coverage and agreement metrics.",
   "The paper's table is a reference, not ground truth: its padj column reaches 0.05 to 0.14 and has NA values, so it was not filtered at BH padj < 0.05.",
   "Megakaryocytes: no agent comparison, so they are outside the seven-cell-type metrics."],
 "reference_table_check": t1_rules,
 "provenance": {"inputs_sha256": {"de_results.csv": sha(de_path), "supp_table1.xlsx": sha(t1_path), "summary.json": sha(sum_path), "analysis_report.txt": sha(rep_path)},
   "script_sha256": sha(__file__),
   "scorer": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "openpyxl": openpyxl.__version__}}}

# ---- score: unweighted mean of a few 0-to-1 items; no weights, no pass/fail ----
def make_score(items):
    names = list(items); vals = [min(1.0, max(0.0, float(items[n]))) for n in names]
    eq = sum(vals) / len(vals); sens = {}
    for i, n in enumerate(names):
        w = [2.0 if j == i else 1.0 for j in range(len(names))]
        sens["double_weight_on_" + n] = round(sum(a * b for a, b in zip(w, vals)) / sum(w), 4)
    allv = [eq] + list(sens.values())
    return {"rule": "equal-weight mean of the items below, each between 0 and 1. No weights and no pass/fail. Other checks stay in metrics.",
            "items": {n: round(v, 4) for n, v in zip(names, vals)}, "score": round(eq, 4),
            "sensitivity": sens, "sensitivity_range": [round(min(allv), 4), round(max(allv), 4)]}

_m = out["metrics"]; _t = _m["top_20_genes"]
_top = lambda s: int(s.split(" of ")[0]) / int(s.split(" of ")[1])
_score = make_score({"agreement": _m["all_seven_cell_types_mean"]["agreement"], "coverage": _m["all_seven_cell_types_mean"]["coverage"],
    "fold_change_correlation": _m["all_seven_cell_types_mean"]["lfc_pearson"],
    "top_20_genes_found": (_top(_t["induced_found_in_paper_same_direction"]) + _top(_t["repressed_found_in_paper_same_direction"])) / 2})

out = {k2: v2 for k, v in out.items() for k2, v2 in ([(k, v), ("score", _score)] if k == "metrics" else [(k, v)])}

json.dump(out, open(out_path, "w"), indent=2)
print(json.dumps({"sections": sections, "neg_control": neg_mean, "top": topchk, "mega": mega, "report": out["metrics"]["report"]}, indent=1))
for ct, v in per.items(): print(ct, {k: v[k] for k in ("n_paper_genes","n_paper_genes_tested","coverage","agreement","sign_agreement","lfc_pearson","n_agent_only_significant","agent_only_near_cutoff_share","paper_baseMean_median_tested","paper_baseMean_median_untested","paper_abs_lfc_median_tested","paper_abs_lfc_median_untested")})
print(t1_rules)
