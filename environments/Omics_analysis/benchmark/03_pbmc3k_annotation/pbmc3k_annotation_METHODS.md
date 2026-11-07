# pbmc3k_annotation: reference and metrics

## Reference

The agent's output is compared with the results of the reference pipeline (using Scanpy 1.12.5, with a manual NK/CD8 split). Scores measure agreement with this reference, not correctness against an external truth. 

- Files in this folder:
  - `gold_labels.csv`: one row for each of the 2,595 retained cells, with the reference group (`ref_group`), fine label (`gold_fine_label`), lineage (`gold_lineage`) and `confidence`.
  - `cluster_map.csv`: maps the neutral cluster IDs shown to the agent (0 to 9) to the reference groups.
  - `task_spec.json`: the weights, parameters and canonical marker genes.
- Agent input: a clustered dataset with 10 clusters whose IDs are shuffled and neutral. The clusters are the 10 reference groups.
- Reference groups (cells): classical monocytes 463, non-classical monocytes 158, naive/central-memory T (CD4-dominant) 1,184, GZMK+ CD8 effector-memory T 95, CD8 cytotoxic effector T 155, CD16+ NK 145, NK-like uncertain 22, B cells 326, dendritic cells 34, megakaryocytes/platelets 13.
- Low-confidence groups: `1,2` (NK-like, uncertain, 22 cells) and `1,3` (CD8 cytotoxic effector T, 155 cells).
- Pipeline description, versions and parameters: see `research/pbmc3k/research-notes.md`. Dataset: see `research/pbmc3k/references.md`.

## How to score

Scoring uses the shared scorer in `scripts/pbmc3k_benchmark/` (see its README for the command). The reference files are in this folder.

## Output files read

- `cluster_assignments.csv` (required): columns `cell_id` and `cell_type`. Optional: `cluster_id` and `annotation_status` (a value of `unresolved` marks a cell the agent chose not to label). A run without the file scores 0, as does a file without both required columns or whose cell IDs match fewer than 10 reference cells.
- `cluster_annotation.csv` (optional): columns `cluster_id` and `supporting_markers`.

## Metrics

Each agent label is first read as a lineage (T, NK, B, Monocyte, DC, Platelet, or Unknown/Other) by keyword rules in `graders/common.py`. Each cell then earns credit against its reference lineage:

- 1.0 if the lineage matches.
- 0.5 if the agent writes a combined T/NK label and the reference is T or NK.
- In the low-confidence groups: 0.5 for a T/NK mix-up, and 0.5 (`unresolved_partial_credit`) if the cell is left unresolved. Elsewhere, an unresolved cell earns 0.
- 0 otherwise.

| Item | Weight | What it measures | How it is calculated |
|---|---|---|---|
| `lineage_macro_recall` | 0.50 | The right lineage is named | Mean credit per reference lineage, averaged over the six lineages |
| `lineage_macro_precision` | 0.15 | Labels the agent applies are right | Mean credit among the cells the agent assigned to each lineage, averaged over the lineages it used |
| `subtype_credit` | 0.25 | The right subtype is named | Among cells with full lineage credit, 1 if the label contains the expected subtype keyword (for example naive, central-memory or CD4 for naive T; CD8, cytotoxic or effector for CD8 effector T; classical versus non-classical monocytes; CD16 or FCGR3A for CD16+ NK). Averaged over the reference fine groups. Groups with no subtype structure (B, DC, platelets, uncertain NK) get full credit. |
| `evidence` | 0.10 | The cited markers support the call | Share of clusters in `cluster_annotation.csv` whose `supporting_markers` include at least one canonical marker (listed in `task_spec.json`) for the cluster's reference lineage. Not scored if the file is absent. |

**Score:** the weighted mean of the items that could be scored. If `cluster_annotation.csv` is absent, the other weights are renormalized.

Reported for information only and not scored: per-lineage recall, macro F1, per-group subtype credit, the share of cells the agent resolved, and labels that could not be read as a lineage.

## How the spec was made

- Lineage recall carries most of the weight because naming the cell population is the core of the task. The weights (0.50, 0.15, 0.25, 0.10) were chosen by judgment and have not been calibrated.
- Leaving a genuinely ambiguous reference group unresolved earns partial credit (0.5), not full credit and not zero. The low-confidence groups are the two the reference pipeline itself could not resolve cleanly.
- The canonical marker lists per lineage are in `task_spec.json`.

## Limits

- Labels are read by keyword rules. A valid label with unusual wording may be reported as unparsed and earn no credit, so check the `unparsed_labels` field in the score.
- The reference is a curated baseline with two low-confidence groups, and PBMC3k is widely used in public tutorials.

