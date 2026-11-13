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
out = {"sections": sections, "per_cell_type": per, "negative_control_mismatched_cell_types_mean_agreement": neg_mean,
 "ranking": rank, "top_genes": topchk, "megakaryocytes": mega, "table1_rules_observed": t1_rules,
 "report_checks_evidence": {"claims_checked": len(claims), "claims_confirmed": int(claims_ok), "counts_in_report_match_de_results": bool(tested_in_report)},
 "provenance": {"inputs_sha256": {"de_results.csv": sha(de_path), "supp_table1.xlsx": sha(t1_path), "summary.json": sha(sum_path), "analysis_report.txt": sha(rep_path)},
   "scorer": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "openpyxl": openpyxl.__version__}}}
json.dump(out, open(out_path, "w"), indent=2)
print(json.dumps({"sections": sections, "neg_control": neg_mean, "rank": {k: rank[k] for k in rank if "spearman" in k or "order" in k}, "top": topchk, "mega": mega, "report": out["report_checks_evidence"]}, indent=1))
for ct, v in per.items(): print(ct, {k: v[k] for k in ("n_paper_genes","n_paper_genes_tested","coverage","agreement","sign_agreement","lfc_pearson","n_agent_only_significant","agent_only_near_cutoff_share","paper_baseMean_median_tested","paper_baseMean_median_untested","paper_abs_lfc_median_tested","paper_abs_lfc_median_untested")})
print(t1_rules)
