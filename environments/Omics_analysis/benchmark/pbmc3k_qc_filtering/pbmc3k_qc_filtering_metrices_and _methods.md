# pbmc3k_qc_filtering: reference and metrics

## Reference

The agent's output is compared with the results of the reference pipeline (using Scanpy 1.12.5, with a manual NK/CD8 split). Scores measure agreement with this reference, not correctness against an external truth. The reference has not been independently reviewed.

- Files in this folder:
  - `qc_reference.csv`: one row for each of the 2,700 input cells, with `qc_pass`, `predicted_doublet`, `cell_status` and `exclusion_reason`.
  - `task_spec.json`: the checks, ranges and parameters the scorer applies.
- Reference outcome: 2,638 cells pass QC and 43 predicted doublets are removed, leaving 2,595 retained cells. 105 cells are excluded in total, for three reasons: `high_mito_fraction` (57), `predicted_doublet` (43) and `high_gene_count` (5).
- Pipeline description, versions and parameters: see `research/pbmc3k/research-notes.md`. Dataset: see `research/pbmc3k/references.md`.

## How to score

Scoring uses the shared scorer in `scripts/pbmc3k_benchmark/` (see its README for the command). The reference files are in this folder.

## Output files read

- `cell_qc.csv` (required): columns `cell_id`, `status` (or `cell_status`) with values such as `retained` or `excluded`, and `exclusion_reason`. A run without this file scores 0.
- `run_manifest.json`: keys `input_cells`, `qc_passing_cells`, `doublets_removed`, `retained_cells` and `retained_genes`. If a number is missing from the manifest, the scorer looks for it in the agent's report text (`.txt` or `.md`).

## Metrics

| Item | What it measures | How it is calculated |
|---|---|---|
| `input_cells` | The agent reports the right number of input cells | 1 if the reported number is exactly 2,700, else 0 |
| `qc_passing_cells` | Cells passing QC, before doublet removal | 1 if between 2,400 and 2,690, else 0 |
| `retained_cells` | Cells kept at the end | 1 if between 2,400 and 2,690, else 0. Counted from `cell_qc.csv`. |
| `doublets_removed` | Predicted doublets removed | 1 if between 0 and 150, else 0 |
| `genes_after_filter` | Genes kept (manifest key `retained_genes`) | 1 if between 10,000 and 33,000, else 0 |
| `accounting` | Every input cell is listed in `cell_qc.csv` | Share of the 2,700 reference cells present in the file. Halved if any cell ID appears more than once. |
| `exclusion_reasons` | Each excluded cell has a stated reason | Share of excluded cells with a non-empty `exclusion_reason`. Not scored if no cells are excluded. |
| `manifest_consistent` | The manifest agrees with the table | 1 if `retained_cells` in the manifest equals the number of retained cells in `cell_qc.csv`, else 0. Not scored if the manifest has no `retained_cells`. |
| `excluded_f1` | Agreement on which cells were removed | F1 of the agent's excluded cells against the reference's 105 excluded cells, divided by 0.7 and capped at 1 |

**Overall score:** the unweighted mean of the items that could be scored. An item that cannot be found is reported as "not scored" and left out of the mean. `weight_scored` in the output shows how much of the rubric was scored.

The scorer also reports, for information only, excluded-set precision and recall and the F1 of the retained set.

## How the spec was made

- The ranges are deliberately tolerant. The public task description does not disclose the QC thresholds, so a reasonable analysis can keep a different number of cells. The reference sits inside every range (2,638 passing, 2,595 retained, 43 doublets).
- The value 0.7 for full credit on the excluded-set F1 means that an F1 of 0.7 or higher earns the full item. It was chosen by judgment.
- The ranges, the 0.7 and the choice of these metrics are chosen defaults. They have not been calibrated against repeated agent runs or an independent pipeline.
- This is the same QC check that the end-to-end task uses as one of its parts.

## Limits

- One dataset (PBMC3k, widely used in public tutorials), one reference run, and a curated baseline.
- The self-tests (`scripts/pbmc3k_benchmark/tests/`) show the scorer works on reference-derived and deliberately flawed outputs. They are not evidence about any agent.
