# melanoma_tumor_ecosystem: reference and metrics

## Reference

The agent's output is compared with the tables of Tirosh et al. 2016, *Science* 352:189-196, for the same dataset (GSE72056, 4,645 cells from 19 metastatic melanoma tumors, Smart-seq2). The comparison measures agreement with the paper, not correctness against an external truth.

- Files in this folder (NIHMS791837 supplementary tables):
  - `Table_S2.xlsx`: number of cells of each type in each tumor (T-cells, B-cells, macrophages, endothelial cells, CAFs, NK cells, melanoma, unclassified).
  - `Table_S3.xlsx`: cell-type-specific genes for six types (T-cells 38 genes, B-cells 31, macrophages 92, endothelial cells 95, CAFs 88, melanoma 47).
  - `Table_S7.xlsx`: the 100 genes of the MITF program.
  - `Table_S8.xlsx`: the 100 genes of the AXL program.
  - `benchmark_result.json`: the comparison for this run.
- What the paper reports (from its text): malignant cells cluster by tumor, and non-malignant cells cluster by cell type. Malignant cells vary in cell cycle (13.5% cycling on average across tumors), and in MITF-high and AXL-high programs.
- Agent input: the public GEO series. The agent downloads the data itself and must not use the annotation rows of the table (malignant call, cell-type codes).
- Table S2 states a total of 4,645 cells, but its category counts sum to 4,644. The comparison uses the category counts.

## How to score

Each task has one score: the equal-weight mean of a few items, each between 0 and 1 (see Score). There are no weights and no pass/fail. All other metrics are reported on their own. `benchmark_result.json` is the direct output of `scripts/melanoma/compare_melanoma.py` (command in the file header), run on the files in this folder and the agent's output files.

## Output files read

- `cell_annotations.csv`: `cell_id`, `tumor_id`, `cell_type`, `malignant_call`.
- `cell_type_counts.csv`: `tumor_id`, `cell_type`, `n_cells`.
- `cell_type_markers.csv`: `cell_type`, `gene`, `score`, `log2_fold_change`, `adj_p_value`.
- `malignant_programs.csv`: `program`, `gene`, `score`.
- `summary.json`: cell counts, cell types found, data used, model.
- `Analysis report.txt` and `umap.png` are not read by the script.

## Structure of `benchmark_result.json`

1. `reference`: the paper and tables used.
2. `paper_reported`: what the paper reports (cells, patients, counts by category, gene list sizes, claims).
3. `agent_reported`: what the agent reports (cells, cell types found, data used, model, programs).
4. `metrics`: how the agent's output compares with the paper.
5. `score`: the score, its items and a sensitivity check (see Score).
6. `notes`: how to read the metrics.
7. `reference_table_check`: the total stated in Table S2 against the sum of its counts.
8. `provenance`: SHA256 of every input file and of the script, and the software versions used.

## Definitions

Agent cell types are matched to Table S2 columns as follows: T cell = T-cells, B cell = B-cells, macrophage = macrophages, endothelial cell = endothelial cells, fibroblast = CAFs, NK cell = NK cells, malignant = melanoma, unresolved = unclassified. Plasma cells and dendritic cells have no counterpart and are listed as agent-only. Tumors are matched by number (Mel53 = 53).

| Metric | What it measures | Calculation |
|---|---|---|
| `paper_total`, `agent_total` | Size of each category | cells in the category over all tumors |
| `pearson_across_19_tumors`, `spearman_across_19_tumors` | Whether the agent distributes a cell type across tumors like the paper | correlation over the 19 tumors of the agent's count and the paper's count for the category |
| `category_overlap.share_of_cells` | Upper bound on cell-by-cell agreement | for each tumor and category, the smaller of the two counts, summed, ÷ cells in Table S2 |
| `malignant_per_tumor` | Malignant cells per tumor | paper melanoma count and agent malignant count for each tumor |
| `agent_top20_in_paper_list`, `agent_top50_in_paper_list` | Whether the agent's top markers are in the paper's list | number of the agent's top 20 or top 50 markers that are in the Table S3 list for the type |
| `paper_genes_found_share` | How much of the paper's list the agent lists | Table S3 genes in the agent's marker list for the type (60 genes) ÷ size of the Table S3 list |
| `mitf_genes_in_program`, `axl_genes_in_program` | Which paper program each agent program resembles | agent program genes (100 listed) that are in Table S7 or Table S8 |
| `agent_file_consistency` | Whether the agent's files agree | summary counts, counts CSV and annotations compared with each other |

Table S3 has no list for NK cells, plasma cells, dendritic cells or unresolved cells, so their markers are not compared.

## Score

The score is the plain mean of the items below. Each item is a number from 0 to 1 and every item counts the same, because no weighting could be justified.

| Item | Calculation |
|---|---|
| `category_overlap` | `category_overlap.share_of_cells` |
| `count_correlation` | the mean of `pearson_across_19_tumors` over the seven cell types that have a paper counterpart (unclassified is left out because its definition differs) |
| `top20_marker_share` | the mean over the six cell types with a Table S3 list of the share of the agent's top 20 markers that are in the list |
| `program_overlap` | the mean of two shares: the most MITF genes in any one agent program ÷ 100, and the most AXL genes in any one agent program ÷ 100 |

`program_overlap` is low for any agent, because the two paper lists have 100 specific genes each. Not in the score and still reported in `metrics`: the per-type totals, `paper_genes_found_share`, the markers of types without a paper list and the file consistency checks.

For this run: `category_overlap` 0.8902, `count_correlation` 0.9619, `top20_marker_share` 0.6917, `program_overlap` 0.225. Score 0.6922.

`sensitivity` in the JSON scores the same run with each item counted twice in turn and reports the lowest and highest result (0.5987 to 0.7461 for this run). This shows how much the score depends on the choice of equal weights. The score is for this task only and should not be averaged with other tasks.

## How the spec was made

- The paper's tables give counts, gene lists and programs, not labels for single cells. The comparison therefore uses counts, overlaps and correlations.
- `category_overlap` is an upper bound, because it counts cells that could have the same category, not cells shown to have it.
- Correlations are reported per cell type and not averaged, because the types differ greatly in size.
- The score uses equal weights, because no weighting could be justified, and there are no pass/fail cutoffs.

## Limits

- There are no per-cell reference labels. GSE72056 has annotation rows that the task tells the agent not to use. They could be used as a per-cell reference but were not available for this comparison.
- The paper's categories do not match the agent's exactly. The paper has 511 unclassified cells and the agent has 89 unresolved cells, and the agent adds plasma cells and dendritic cells.
- Table S3 lists are short and were chosen by the paper's method. The agent's lists are its top 60 Wilcoxon markers, so the overlap shares depend on both list lengths.
- Table S5 (cell cycle genes) was not available, so the agent's `cell_cycle` program is not compared. The agent's other programs are compared only with the MITF and AXL gene sets.
- The paper's statement that malignant cells group by tumor and non-malignant cells by cell type is not tested, because no report or embedding was compared.
- One dataset, one run, and a single published reference.
