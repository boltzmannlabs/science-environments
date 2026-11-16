# myeloid_progenitor_lineages: reference and metrics

## Reference

The agent's clusters are compared with the clusters in Paul et al. 2015, *Cell* 163:1663-1677 (doi 10.1016/j.cell.2015.11.013), for the same dataset (GSE72857, mouse bone marrow myeloid progenitors, MARS-seq). The comparison measures agreement with the paper, not correctness against an external truth.

- Files in this folder:
  - `mmc2.xlsx`: Supplementary Table S3. Mean expression of 3,461 genes in each of the paper's 19 clusters (C1 to C19).
  - `benchmark_result.json`: the comparison for this run.
- What the paper reports: 2,730 cells in 19 clusters (0.3% to 13% of cells each) and 7 fates: erythrocyte (C1-C7), megakaryocyte (C8), dendritic cell (C11), basophil (C13), monocyte (C14-C15), neutrophil (C16-C17), eosinophil (C18). C9 and C10 are early myeloid clusters with no fate. C19 is a Ccl5+ NK-like population the paper excludes as mis-sorted. The paper's main claim is that unperturbed cells are primed toward single fates, with no progenitors of mixed lineage.
- Agent input: the public GEO series. The agent downloads the data itself.
- The paper's table is a reference, not ground truth.

## How to score

There are no weights, no overall score and no pass/fail. Each metric is reported on its own. `benchmark_result.json` is the direct output of `scripts/06_myeloid_progenitor_lineages/compare_paul.py` (command in the file header), run on the files in this folder and the agent's output files.

## Output files read

- `cluster_assignments.csv`: one row per cell, with `cluster_id` and `cell_type` (the agent's label).
- `cluster_markers.csv`: columns `cluster_id`, `gene`, `score`, `log2_fold_change`, `adj_p_value`.
- `summary.json`: cells in and retained, number of clusters, fates identified, cluster relationships, model.
- `Analysis report.txt`: checked for the marker genes it cites.

## Structure of `benchmark_result.json`

1. `paper_reported`: what the paper reports (cells, clusters, fates, cluster-to-fate map, the excluded cluster, the main claim).
2. `agent_reported`: what the agent reports (cells, clusters and labels, fates identified, cluster relationships, model).
3. `metrics`: how the agent's clusters compare with the paper's.
4. `notes`: how to read the metrics.
5. `provenance`: SHA256 of every input file and of the script, and the software versions used.

## Definitions

The paper has no per-cell cluster labels in its supplement, so cells cannot be compared one by one. The comparison uses Table S3 and the marker genes the agent reports.

**Matching an agent cluster to a paper cluster.** For each gene in Table S3, its mean expression across the 19 clusters is converted to a z-score (mean 0, standard deviation 1 across the 19). For an agent cluster, the score for a paper cluster is the mean z-score, in that paper cluster, of the agent cluster's marker genes that are found in Table S3. Genes are matched by exact symbol, otherwise by the first symbol of a multi-symbol name such as `Lyz1;Lyz2`. The paper cluster with the highest score is the `best_paper_cluster`. The second highest is also reported.

| Metric | What it measures | Calculation |
|---|---|---|
| `per_agent_cluster` | For each agent cluster, the best and second best paper cluster | best and second best paper cluster by mean marker z-score, with the scores and the number of markers found in Table S3 |
| `paper_fates_with_a_best_matching_agent_cluster` | How many of the paper's 7 fates the agent's clusters recover | number of paper fates that are the fate of the `best_paper_cluster` of at least one agent cluster |
| `agent_clusters_best_matching_each_fate` | Which agent clusters match each fate | list of agent clusters per fate |
| `labels_consistent_with_best_match` | Whether the agent's own label agrees with the match | agent clusters whose label names a fate and whose best-matching paper cluster has that fate ÷ agent clusters whose label names a fate |
| `per_paper_cluster` | For each paper cluster, the agent cluster that matches it best | highest mean z-score over agent clusters, with the score |
| `paper_clusters_that_are_the_best_match_of_an_agent_cluster` | Which paper clusters the agent's clusters land on | list |
| `report_marker_claims` | Whether the report's marker claims are in the marker table | for each cluster line in the report, the genes listed before the first semicolon that are in the vocabulary of Table S3 or the marker table, and the ones missing from that cluster's marker table |

**Reading labels as fates.** A label is read as a fate by keyword: megakaryocyte, erythroid (= erythrocyte), neutrophil or granulocyte (= neutrophil, eosinophil or basophil), granulocyte/monocyte (= any of those and monocyte), dendritic, monocyte, T/NK (= the paper's excluded C19). Labels with "mixed" or "cycling", or with no fate word, are not scored.

## How the spec was made

- The 19 paper clusters and the fate of each come from the paper's main text. Table S3 provides the expression profile of each cluster.
- Matching by mean z-score uses no threshold and no weight. A threshold on the score would have to be invented.
- Z-scores are taken across the paper's clusters, so a gene counts as a marker of a paper cluster only relative to the other 18.
- There are no weights and no pass/fail cutoffs, because none could be justified.

## Limits

- Cell-level agreement cannot be measured because the supplement has no per-cell labels.
- The agent has 12 clusters and the paper has 19, from different cell sets, QC and resolution. The counts are reported side by side and are not a metric.
- The mapping from agent cluster to paper cluster is this benchmark's own method, not the paper's. A different mapping could give different matches.
- The reading of labels as fates is a keyword rule and is a judgment.
- Table S3 has a `max_cluster` column that does not equal the cluster with the highest mean for most genes in the file, so it is not used.
- Marker scores are low in absolute terms for several clusters (best score 0.96 to 2.59), so second-best matches are close for some clusters. They are reported in `per_agent_cluster`.
- The report check only finds genes that are in the vocabulary of the two tables, and it ignores text after the first semicolon.
- One dataset, one run, and a single published reference.
