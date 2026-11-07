# pbmc3k_clustering: reference and metrics

## Reference

The agent's output is compared with the results of the reference pipeline (using Scanpy 1.12.5, with a manual NK/CD8 split). Scores measure agreement with this reference, not correctness against an external truth. 

- Files in this folder:
  - `gold_labels.csv`: one row for each of the 2,595 retained cells, with the reference group (`ref_group`), a fine label (`gold_fine_label`), a lineage (`gold_lineage`) and a `confidence` flag.
  - `task_spec.json`: the weights and parameters the scorer applies.
- Reference lineages: T 1,434 cells, Monocyte 621, B 326, NK 167, DC 34, Platelet 13.
- Agent input: this task starts from the reference's normalized data.
- Pipeline description, versions and parameters: see `research/pbmc3k/research-notes.md`. Dataset: see `research/pbmc3k/references.md`.

## How to score

Scoring uses the shared scorer in `scripts/pbmc3k_benchmark/` (see its README for the command). The reference files are in this folder.

## Output file read

`cluster_assignments.csv` (required) with columns `cell_id` and `cluster_id`. A run without the file scores 0, as does a file without both columns or whose cell IDs match fewer than 10 reference cells.

## Metrics

| Item | Weight | What it measures | How it is calculated |
|---|---|---|---|
| `valid_assignments` | 0.1 | Every reference cell is assigned once | Share of the 2,595 reference cells present in the file, halved if a cell ID repeats or a cluster ID is missing |
| `lineage_homogeneity` | 0.4 | Clusters do not mix lineages | Homogeneity of the reference lineages within the agent's clusters, 1 - H(lineage given cluster) / H(lineage). The value is rescaled: 0 at 0.5 or below, 1 at 0.95 or above, linear in between. |
| `lineage_majority_macro_recall` | 0.5 | Each lineage, including small ones, is resolved | Each cluster is labelled with its majority lineage, then the recall of each of the six lineages (T, NK, B, Monocyte, DC, Platelet) is averaged. Rescaled the same way (0.5 to 0.95). |

**Score:** the weighted mean of the three items.

Reported for information only and not scored: the number of clusters, the raw homogeneity and majority-recall values, and ARI and NMI against the lineages and against the fine reference groups.

## How the spec was made

- The cluster count is not scored. Homogeneity and majority-label recall reward pure clusters and resolved small populations without penalizing defensible finer clusters. ARI and NMI are reported but not scored, because they penalize finer clusters.
- The weights (0.1, 0.4, 0.5) and the rescaling limits (0.5 and 0.95) were chosen by judgment and have not been calibrated against repeated agent runs or an independent pipeline.
- The reference lineages come from the reference pipeline's labels (CellTypist `Immune_All_Low` plus a manual split of one cluster into NK and CD8 T cells). The two low-confidence groups are `1,2` and `1,3`.

## Limits

- One dataset (PBMC3k, widely used in public tutorials), one reference run, and a curated baseline.

