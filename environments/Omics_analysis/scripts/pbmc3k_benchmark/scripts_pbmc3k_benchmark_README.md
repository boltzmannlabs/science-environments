# PBMC3k scorer

**Evaluator-only.** This folder holds the code that scores an agent's output on the PBMC3k tasks. The reference answers it reads are in `benchmark/`. Keep both folders out of the tested agent's workspace; the agent receives only `tasks/<task_id>/`.

## What is where

```
<environment>/
├── tasks/<task_id>/task.md        # what the agent receives
└── benchmark/
│   ├── <task_id>/                 # reference files, task_spec.json and METHODS.md for each task and benchmark_result.json
├── scripts/pbmc3k_benchmark/                # this folder
│   ├── score.py                   # entry point: reads <task_id>/task_spec.json and runs the graders
│   └── graders/                   # one module per kind of check (qc, normalization, clustering, markers, annotation, report)
└── results/<task_id>/             # the agent's report and the output files that were scored
```

## How scoring works

`score.py` is the single entry point. It reads the task's `task_spec.json`, which lists the graders to run with their weights and parameters, runs each grader on the agent's output folder, and writes the scores. The graders are shared: each task's spec picks the ones it needs. The end-to-end task uses all six.

| Task | Agent input | Required output | Graders | Graded on |
|---|---|---|---|---|
| `01_pbmc3k_qc_filtering` | raw 10x matrix | `cell_qc.csv`, `run_manifest.json` | `qc` | counts in ranges, accounting for every input cell, F1 of the excluded set, exclusion reasons |
| `02_pbmc3k_clustering` | normalized data | `cluster_assignments.csv` | `clustering` | lineage homogeneity (0.4), majority-label macro recall (0.5), valid assignments (0.1) |
| `03_pbmc3k_annotation` | clustered data with 10 neutral clusters | `cluster_assignments.csv`, optional `cluster_annotation.csv` | `annotation` | lineage recall (0.50), precision (0.15), subtype credit (0.25), cited-marker evidence (0.10) |
| `04_pbmc3k_celltype_annotation` | raw 10x matrix | `cluster_assignments.csv`, plus optional `cell_qc.csv`, manifest, `.h5ad`, markers and report | `qc`, `normalization`, `clustering`, `annotation`, `markers`, `report` | QC 0.20, normalization 0.15, clustering 0.20, annotation 0.25, markers 0.10, report 0.10 |

Each task's reference, metrics and calculations are described in `benchmark/<task_id>/METHODS.md`.

## Usage

Run from the environment folder:

```
python scripts/pbmc3k/score.py 03_pbmc3k_annotation results/03_pbmc3k_annotation --bench-dir benchmark --out benchmark/03_pbmc3k_annotation/benchmark_result.json

```
Replace the task name and folders to score the other tasks.
By default the scorer reads the reference files from `benchmark/`. To use another folder, pass `--bench-dir DIR` or set `PBMC_REF_DIR`. 

Requires Python 3, numpy, pandas and anndata (for the `.h5ad` checks).

## Design decisions

- **The reference is a curated baseline, not ground truth.** It is the run of the reference pipeline (Scanpy 1.12.5, scaled highly variable genes, CellTypist `Immune_All_Low`, seed 0) plus a manual split of one cluster into NK and CD8 T groups. Two groups, `1,2` and `1,3`, are low confidence. Scores measure agreement with this reference.
- **Stage tasks start from the reference's previous output,** so an earlier-stage mistake cannot lower a later stage's score. The annotation input uses the 10 reference groups with shuffled neutral cluster IDs.
- **Unresolved labels.** A label such as "Unresolved" or "Heterogeneous", or `annotation_status = unresolved`, earns partial credit (0.5) on low-confidence reference groups and 0 elsewhere. The share of resolved cells is reported separately.
- **The cluster count is informational.** Homogeneity and majority-label recall reward pure clusters and resolved small populations without penalizing defensible finer clusters. ARI and NMI are reported but not scored.
- **Tolerant ranges instead of exact thresholds,** because the public task descriptions do not disclose the thresholds.
- **Missing optional files are "not scored"** and the remaining weights are renormalized; `weight_scored` in the output shows how much of the rubric was scored. A missing required file scores 0.
- **Numbers come from `run_manifest.json` first,** and the report text is only a fallback.
- All weights, ranges and thresholds were chosen by judgment. They have not been calibrated against repeated agent runs or an independent pipeline.

## Known limits

- The report rubric is keyword-based and lenient. Use a person or a model to judge its depth.
- The marker check gives partial credit across related clusters, for example T subsets share CD3D and IL32, so shuffled cluster IDs still score about 0.4.
- Annotation labels are read by keyword rules in `graders/common.py`. Valid labels with unusual wording can go unparsed; the score reports them in `unparsed_labels`.

