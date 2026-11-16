#!/usr/bin/env python3
"""Compare an agent's output for melanoma_tumor_ecosystem with Tirosh et al. 2016 (Science 352:189; GSE72056).
Usage: python3 -I compare_melanoma.py CELL_ANNOTATIONS.csv CELL_TYPE_COUNTS.csv CELL_TYPE_MARKERS.csv MALIGNANT_PROGRAMS.csv SUMMARY.json S2.xlsx S3.xlsx S7.xlsx S8.xlsx OUT.json
S2 = cells per type per tumor, S3 = cell-type-specific genes, S7 = MITF program, S8 = AXL program (NIHMS791837 supplements).
No weights, no overall score, no pass/fail."""
import sys, json, hashlib, platform
import numpy as np, pandas as pd, openpyxl, scipy
from scipy.stats import pearsonr, spearmanr

ann_p, cnt_p, mk_p, pg_p, sum_p, s2_p, s3_p, s7_p, s8_p, out_p = sys.argv[1:11]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
clean = lambda x: None if x is None else str(x).strip().strip("'").strip()

# agent label -> Table S2 column. plasma cell and dendritic cell have no counterpart in the paper's table.
MAP = {"T cell": "T-cells", "B cell": "B-cells", "macrophage": "Mcrophages", "endothelial cell": "Endothelial cells",
       "fibroblast": "CAFs", "NK cell": "NK cells", "malignant": "Melanoma", "unresolved": "unclassified"}
S3MAP = {"T cell": "T-cells", "B cell": "B-cells", "macrophage": "Macrophages", "endothelial cell": "Endothelial cells",
         "fibroblast": "CAFs", "malignant": "melanoma"}

ann = pd.read_csv(ann_p, dtype={"tumor_id": str}); cnt = pd.read_csv(cnt_p, dtype={"tumor_id": str})
mk = pd.read_csv(mk_p); pg = pd.read_csv(pg_p); summ = json.load(open(sum_p))

# ---- Table S2 ----
rows = list(openpyxl.load_workbook(s2_p, read_only=True).worksheets[0].iter_rows(values_only=True))
cols = [c for c in rows[2][1:] if c != "Total"]
S2 = pd.DataFrame([r[1:1 + len(cols)] for r in rows[4:] if r[0] and str(r[0]).startswith("Mel")], columns=cols,
                  index=[str(r[0])[3:] for r in rows[4:] if r[0] and str(r[0]).startswith("Mel")]).astype(int)
paper_total = {c: int(v) for c, v in zip(cols, rows[3][1:])}
s2_check = {'total_stated_in_table': int(rows[3][len(cols) + 1]), 'sum_of_category_counts': int(S2.values.sum()), 'all_tumors_row_category_sum': int(sum(rows[3][1:len(cols) + 1]))}

# agent counts per tumor and S2 category
A = ann.assign(cat=ann.cell_type.map(MAP)).dropna(subset=["cat"])
agent_tab = pd.crosstab(A.tumor_id, A.cat).reindex(index=S2.index, columns=cols, fill_value=0)
agent_only = ann[~ann.cell_type.isin(MAP)].cell_type.value_counts().to_dict()

per_type = {}
for lab, c in MAP.items():
    a, p = agent_tab[c].values, S2[c].values
    per_type[lab] = {"paper_category": c, "paper_total": int(p.sum()), "agent_total": int(a.sum()),
        "pearson_across_19_tumors": round(float(pearsonr(a, p)[0]), 3) if a.std() and p.std() else None,
        "spearman_across_19_tumors": round(float(spearmanr(a, p)[0]), 3) if a.std() and p.std() else None}
same_cat = int(np.minimum(agent_tab.values, S2[cols].values).sum())
overlap = {"cells_in_both_tables": int(S2.values.sum()), "sum_over_tumors_and_categories_of_min_of_two_counts": same_cat,
           "share_of_cells": round(same_cat / int(S2.values.sum()), 4),
           "agent_only_cell_types": {k: int(v) for k, v in agent_only.items()}}
malignant_per_tumor = {t: {"paper_melanoma": int(S2.loc[t, "Melanoma"]), "agent_malignant": int(agent_tab.loc[t, "Melanoma"])} for t in S2.index}

# ---- Table S3 markers ----
r3 = list(openpyxl.load_workbook(s3_p, read_only=True).worksheets[0].iter_rows(values_only=True))
hdr = r3[4]; S3 = {h: [clean(r[i]) for r in r3[5:] if clean(r[i])] for i, h in enumerate(hdr)}
markers = {}
for lab, p in S3MAP.items():
    g = mk[mk.cell_type == lab].gene.tolist(); P = set(S3[p])
    markers[lab] = {"paper_list": p, "paper_list_size": len(P), "agent_markers_listed": len(g),
        "agent_top20_in_paper_list": int(sum(x in P for x in g[:20])), "agent_top50_in_paper_list": int(sum(x in P for x in g[:50])),
        "paper_genes_found_in_agent_list": int(len(P & set(g))), "paper_genes_found_share": round(len(P & set(g)) / len(P), 3)}
no_counterpart = [t for t in mk.cell_type.unique() if t not in S3MAP]

# ---- Tables S7 / S8 programs ----
prog = lambda f: [x for x in (clean(r[0]) for r in openpyxl.load_workbook(f, read_only=True).worksheets[0].iter_rows(values_only=True))][4:]
MITF = [x for x in prog(s7_p) if x]; AXL = [x for x in prog(s8_p) if x]
programs = {}
for k, g in pg.groupby("program", sort=False):
    s = set(g.gene)
    programs[k] = {"genes_listed": len(s), "mitf_genes_in_program": len(s & set(MITF)), "axl_genes_in_program": len(s & set(AXL))}
best_mitf = max(programs, key=lambda k: programs[k]["mitf_genes_in_program"]); best_axl = max(programs, key=lambda k: programs[k]["axl_genes_in_program"])

# ---- the agent's files against each other ----
vc = ann.cell_type.value_counts()
consistency = {"cell_ids_unique": bool(ann.cell_id.is_unique), "rows_equal_cells_retained": len(ann) == summ["cells_retained"],
    "cells_input_equals_retained": summ["cells_input"] == summ["cells_retained"],
    "cell_types_found_equals_annotations": {k: int(vc.get(k, 0)) == v for k, v in summ["cell_types_found"].items()},
    "n_malignant_matches": int((ann.malignant_call == "malignant").sum()) == summ["n_malignant"],
    "n_nonmalignant_matches": int((ann.malignant_call == "non-malignant").sum()) == summ["n_nonmalignant"],
    "counts_csv_sum_equals_annotations": int(cnt.n_cells.sum()) == len(ann),
    "counts_csv_matches_annotations": bool((cnt.set_index(["tumor_id", "cell_type"]).n_cells ==
        ann.groupby(["tumor_id", "cell_type"]).size().rename("n_cells").reindex(cnt.set_index(["tumor_id", "cell_type"]).index)).all()),
    "unresolved_cells": int((ann.malignant_call == "unresolved").sum())}

out = {"task_id": "melanoma_tumor_ecosystem",
 "reference": {"paper": "Tirosh et al. 2016, Science 352:189-196", "dataset": "GSE72056",
   "tables": "Table S2 (cells per type per tumor), S3 (cell-type-specific genes), S7 (MITF program), S8 (AXL program)"},
 "paper_reported": {"cells": 4645, "patients": 19, "cell_counts_by_category": paper_total,
   "cell_type_specific_gene_list_sizes": {k: len(v) for k, v in S3.items()}, "mitf_program_genes": len(MITF), "axl_program_genes": len(AXL),
   "claims": ["Malignant cells cluster by tumor; non-malignant cells cluster by cell type.",
              "Malignant cells vary in cell cycle (13.5% cycling on average across tumors), and in MITF-high and AXL-high programs."]},
 "agent_reported": {"cells_input": summ["cells_input"], "cells_retained": summ["cells_retained"], "cell_types_found": summ["cell_types_found"],
   "n_malignant": summ["n_malignant"], "n_nonmalignant": summ["n_nonmalignant"], "data_used": summ["data_used"], "model": summ["model"],
   "programs": {k: int((pg.program == k).sum()) for k in pg.program.unique()}},
 "metrics": {"cell_counts": {"per_cell_type": per_type, "category_overlap": overlap, "malignant_per_tumor": malignant_per_tumor},
   "markers_vs_table_s3": {"per_cell_type": markers, "agent_cell_types_without_a_paper_list": no_counterpart},
   "programs_vs_tables_s7_s8": {"per_agent_program": programs, "program_with_most_mitf_genes": best_mitf, "program_with_most_axl_genes": best_axl},
   "agent_file_consistency": consistency},
 "notes": ["The comparison is at the level of counts, gene lists and programs. No per-cell reference labels were used.",
   "The paper's categories include 'unclassified' (511 cells). The agent's 'unresolved' (89) is not the same thing, and the agent split out plasma cells and dendritic cells, which the paper's table does not have.",
   "category_overlap is an upper bound on cell-by-cell agreement: it counts cells that could have the same category in the same tumor, not cells shown to have it.",
   "Table S3 lists are short and were selected by the paper's own method. The agent's lists are its top 60 Wilcoxon markers, so the overlap shares depend on both list lengths.",
   "Table S2 states a total of 4,645 cells, but its category counts sum to 4,644 (see reference_table_check). The comparison uses the category counts.",
   "Table S5 (cell cycle genes) was not available, so the agent's cell_cycle program is not compared. The paper reports cell cycle as a program."],
 "reference_table_check": {"table_s2": s2_check},
 "provenance": {"inputs_sha256": {"cell_annotations.csv": sha(ann_p), "cell_type_counts.csv": sha(cnt_p), "cell_type_markers.csv": sha(mk_p),
     "malignant_programs.csv": sha(pg_p), "summary.json": sha(sum_p), "table_s2.xlsx": sha(s2_p), "table_s3.xlsx": sha(s3_p),
     "table_s7.xlsx": sha(s7_p), "table_s8.xlsx": sha(s8_p)}, "script_sha256": sha(__file__),
   "scorer": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "openpyxl": openpyxl.__version__}}}
json.dump(out, open(out_p, "w"), indent=2)
print(json.dumps({"per_type": per_type, "overlap": overlap, "markers": markers, "programs": programs, "consistency": consistency}, indent=1))
