# single_cell_stimulation_response: reference and metrics

## Reference

The agent's output is compared with the differential expression results published in Kang et al. 2018, *Nature Biotechnology* (PMID 29227470), for the same dataset (GSE96583, control versus 6-hour IFN-beta PBMCs). The comparison measures agreement with the paper, not correctness against an external truth.

- Files in this folder:
  - `NIHMS921103-supplement-supp_table1.xlsx`: Supplementary Table 1 of the paper, 8 sheets, one per cell type. Each row is a gene the paper called differentially expressed (DESeq2, absolute log2 fold change above 1, baseMean above 1).
  - `benchmark_result.json`: the comparison for this run.
- Paper sheets and number of genes: CD14+ monocytes 2,251; FCGR3A+ monocytes 1,221; B cells 583; dendritic cells 581; CD4 T cells 537; NK cells 351; CD8 T cells 248; megakaryocytes 107. The union over the 8 sheets is 3,055 unique genes.
- Agent input: the public GEO series. The agent downloads the data itself.
- The paper's table is a reference, not ground truth. Its `padj` column reaches 0.05 to 0.14 and has NA values, so it was not filtered at DESeq2 BH padj < 0.05.

## How to score

There are no weights, no overall score and no pass/fail. Each metric is reported on its own. `benchmark_result.json` is the direct output of `scripts/05_single_cell_stimulation_response/compare_kang.py` (command in the file header), run on the files in this folder and the agent's `de_results.csv`, `summary.json` and report.

## Output files read

- `de_results.csv` (required): columns `gene`, `cell_type`, `log2_fold_change`, `p_value`, `adj_p_value`.
- `summary.json`: significant gene counts and the 20 top induced and repressed genes.
- `Analysis report.txt` (optional): checked for the claims it makes.

## Structure of `benchmark_result.json`

1. `paper_reported`: what the paper reports (genes per cell type, megakaryocytes, unique genes).
2. `agent_reported`: what the agent reports (comparisons run, significant genes and genes tested per cell type, top genes, data used, model).
3. `metrics`: how the agent's results compare with the paper, per cell type and as the mean of the seven cell types analyzed by both.
4. `notes`: how to read the metrics.
5. `reference_table_check`: for each paper sheet, the smallest absolute log2 fold change and baseMean, the largest `padj` and the number of NA `padj` values, which show how the paper's table was filtered.
6. `provenance`: SHA256 of every input file and of the script, and the software versions used.

## Definitions

Cell types are matched as follows: CD14+ Monocytes = `cd14`, FCGR3A+ Monocytes = `cd16 mono`, B cells = `cd19`, Dendritic cells = `dc`, CD4 T cells = `cd4`, NK cells = `nk`, CD8 T cells = `cd8`. The agent's `all_cells` comparison has no counterpart in the paper. Genes are matched by exact symbol. Log2 fold change is stimulated relative to control in both analyses.

For each cell type:

- **Paper set:** all genes in the matching sheet.
- **Agent set:** genes in `de_results.csv` for that cell type with `adj_p_value` < 0.05 and absolute `log2_fold_change` > 1.
- **Tested:** paper genes that have a non-missing `adj_p_value` for that cell type in the agent's table.

| Metric | What it measures | Calculation |
|---|---|---|
| `coverage` | How much of the paper's list the agent tested | tested ÷ paper set |
| `agreement` | Whether the agent reproduces the paper's calls on genes both tested | tested paper genes that are in the agent set with the same sign as the paper ÷ tested |
| `n_significant_wrong_direction` | Contradictions | tested paper genes in the agent set with the opposite sign |
| `n_tested_not_significant` | Genes tested but not called | tested minus same-direction minus wrong-direction |
| `sign_agreement` | Direction of change, ignoring significance | share of tested paper genes whose log2 fold change has the same sign in both analyses |
| `lfc_pearson` | Size of change | Pearson correlation of log2 fold changes over tested paper genes |
| `n_agent_only_significant` | Calls the paper does not have | agent set minus paper set |
| `agent_only_near_cutoff_share` | Whether those extra calls are borderline | share of agent-only genes with absolute log2 fold change < 1.25 or `adj_p_value` > 0.01 |
| `paper_baseMean_median_tested` / `_untested` | Why genes were not tested | median paper baseMean of tested and untested paper genes |
| `agent_significant_to_paper_genes_ratio` | Size of the two lists | agent set size ÷ paper set size. A count ratio only. It does not show that the genes agree. |

**Mean of the seven cell types:** the unweighted mean of the per-cell-type values of `coverage`, `agreement`, `sign_agreement` and `lfc_pearson`.

Other items in `metrics`:

- **`negative_control_mean_agreement_mismatched_cell_types`:** `agreement` computed when the agent's result for one cell type is compared with the paper's sheet for a different cell type (all 42 mismatched pairs, mean). It shows how much agreement a comparison gets from the response shared across cell types.
- **`cell_type_ranking_spearman`:** Spearman correlation across the seven cell types between the agent's counts of significant genes and the paper's counts, and between the agent's counts and the number of paper genes the agent tested.
- **`top_20_genes`:** how many of the agent's `top_induced_genes` and `top_repressed_genes` are in any paper sheet in the same direction.
- **`megakaryocytes_in_all_cells_table`:** the agent ran no megakaryocyte comparison. This counts how many of the paper's 107 megakaryocyte genes appear in the agent's `all_cells` results and are significant in the same direction.
- **`report`:** the number of claims in the report that were checked against `de_results.csv` and `summary.json`, and whether the counts it states match.

## How the spec was made

- Coverage and agreement are reported separately and not combined. Coverage depends mainly on the agent's low-expression filter, and agreement depends on the calls on genes both tested. A combined number would hide which one moved.
- The 1.25 and 0.01 values in `agent_only_near_cutoff_share` are chosen to show how many extra calls are close to the cutoffs. They are not thresholds for a score.
- There are no weights and no pass/fail cutoffs, because none could be justified.

## Limits

- The paper's analysis is a different pipeline (different QC, doublet handling and filtering), so the comparison cannot separate real disagreement from method differences.
- A paper gene the agent did not test counts against coverage only, not against agreement. The agent's filter (at least 10 UMIs in at least 4 pseudobulk samples) is stricter than the paper's baseMean > 1 cutoff.
- The megakaryocyte genes are not part of the seven-cell-type metrics.
- The report says that 313 cells in the stimulated well have a conflicting condition label in the metadata, and that the well accession was used. The effect on the comparison is not tested.
- One dataset, one run, and a single published reference.
