# pbmc3k_celltype_annotation: reference and metrics

## Reference

The agent's output is compared with the results of the reference pipeline (run using Scanpy 1.12.5, with a manual NK/CD8 split). Scores measure agreement with this reference, not correctness against an external truth. The reference has not been independently reviewed.

- Files in this folder:
  - `qc_reference.csv`: one row for each of the 2,700 input cells, with `qc_pass`, `predicted_doublet`, `cell_status` and `exclusion_reason`.
  - `gold_labels.csv`: one row for each of the 2,595 retained cells, with the reference group, fine label, lineage and `confidence`.
  - `hvg_reference.txt`: the highly variable genes of the reference run.
  - `task_spec.json`: the sections, weights, parameters and canonical marker genes.
- Reference outcome: 2,638 cells pass QC, 43 predicted doublets are removed and 2,595 cells are retained. Lineages: T 1,434, Monocyte 621, B 326, NK 167, DC 34, Platelet 13.
- Agent input: the raw 10x matrix. The agent runs the whole analysis from there.
- Pipeline description, versions and parameters: see `research/pbmc3k/research-notes.md`. Dataset: see `research/pbmc3k/references.md`.

## How to score

Scoring uses the shared scorer in `scripts/pbmc3k_benchmark/` (see its README for the command). The reference files are in this folder.

## Sections and weights

| Section | Weight | Reads |
|---|---|---|
| QC | 0.20 | `cell_qc.csv`, `run_manifest.json` |
| Normalization | 0.15 | the agent's `.h5ad` file |
| Clustering | 0.20 | `cluster_assignments.csv` |
| Annotation | 0.25 | `cluster_assignments.csv`, `cluster_annotation.csv` |
| Markers | 0.10 | `cluster_markers.csv`, `cluster_assignments.csv` |
| Report | 0.10 | the agent's report (`.txt` or `.md`), `run_manifest.json` |

**Overall score:** the weighted mean of the sections that could be scored. A section whose optional file is missing is reported as "not scored" and the other weights are renormalized. `weight_scored` in the output shows how much of the rubric was scored.

## Metrics by section

**QC** (same as `pbmc3k_qc_filtering`): the counts `input_cells` (exactly 2,700), `qc_passing_cells` (2,400 to 2,690), `retained_cells` (2,400 to 2,690), `doublets_removed` (0 to 150) and `genes_after_filter` (10,000 to 33,000), each scored 1 inside its range and 0 outside; `accounting` (share of input cells listed in `cell_qc.csv`); `exclusion_reasons` (share of excluded cells with a reason); `manifest_consistent`; and `excluded_f1` (F1 of the agent's excluded cells against the reference's, divided by 0.7 and capped at 1). If `cell_qc.csv` is absent, the scorer falls back to the cell IDs in `cluster_assignments.csv`.

**Normalization** (reads the agent's `.h5ad`; looks for `pbmc3k_normalized.h5ad` or `pbmc3k_processed.h5ad`, else any `.h5ad`; not scored if there is none). The score is the mean of these items, each between 0 and 1:
- `cells_present`: share of reference cells in the file, divided by 0.9 and capped at 1.
- `genes_kept`: the share of the 13,714 input genes kept, divided by 0.6 and capped at 1.
- `counts_layer_integer`: the `counts` layer holds integers.
- `counts_preserved`: the median total counts per cell is within 10% of 2,209.
- `log_normalized_constant_target`: in at least 95% of the first 300 cells the values, once back-transformed, sum to one constant within 1%. Any target sum is accepted.
- `n_hvgs_in_range`: between 500 and 6,000 highly variable genes.
- `top10_hvgs_present`: share of the reference's top 10 highly variable genes that the agent flagged.
- `hvg_ref_recall`: recall of the reference's highly variable genes, divided by 0.6 and capped at 1.

**Clustering:** same as `pbmc3k_clustering`. Valid assignments (0.1), lineage homogeneity (0.4) and majority-label macro recall (0.5), the last two rescaled between 0.5 and 0.95.

**Annotation:** same as `pbmc3k_annotation`. Lineage macro recall (0.50), macro precision (0.15), subtype credit (0.25) and cited-marker evidence (0.10, if `cluster_annotation.csv` is present).

**Markers** (reads `cluster_markers.csv` with `cluster_id` and `gene`, optionally `score`, a log fold change and an adjusted p-value). Each cluster's top 25 genes are the positive, significant genes (adjusted p below 0.05) ranked by score. For each reference lineage, the scorer finds the agent's clusters whose majority lineage it is and whose purity is at least 0.5. Each such cluster earns min(1, canonical markers among its top 25 divided by 2), and these are averaged weighted by cluster size. A lineage with no such cluster earns 0. The section score is the mean over the six lineages.

**Report** (keyword-based and lenient). The score is the mean of these items, each 1 if present: QC thresholds stated, doublet handling stated, normalization stated, highly variable gene method stated, clustering method stated, uncertainty stated, predictions described as not independently validated, plus a marker-gene item (at least 8 distinct canonical markers cited, scaled to 1) and `records_reproducibility_info` (the share of seed, parameters and software versions recorded in `run_manifest.json`). Not scored if no report is found.

## How the spec was made

- The section weights (0.20, 0.15, 0.20, 0.25, 0.10, 0.10) put the most weight on the final biological result (annotation) and the least on the markers and report, and were chosen by judgment, not calibrated.
- The stage sections reuse the same graders as the stage tasks, with the same ranges and weights, so scores can be compared across tasks.
- All thresholds, ranges and the choice of metrics are chosen defaults. They have not been calibrated against repeated agent runs or an independent pipeline.

## Open item

In the current spec, `required_file` is `null` for every section, so a missing file means "not scored" for that section, not 0. The task description asks for `cell_qc.csv`. To make it mandatory for QC, set `"required_file": "cell_qc.csv"` in the QC section of `task_spec.json`.

## Limits

- The report rubric is keyword-based and lenient.
- The marker check gives partial credit across related clusters, so shuffled cluster IDs still score about 0.4.
- One dataset (PBMC3k, widely used in public tutorials), one reference run, and a curated baseline.

