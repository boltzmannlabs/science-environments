# Historical design results — qualified by later validation

The [independent audit](../20261111_ref15_benchmark_audit/report.md) found defects in the approximate structures and an edit-mask discrepancy. The historical scores and selections below remain archived observations; they do not validate improved binding or REF15 performance. Use the audit for the current interpretation.

# Task 001 — HER2: Trastuzumab Interaction Optimization — Report

## Run identity

- Task: `task_001_her2_trastuzumab_interaction_optimization`
- Run: `20261110_antibmpnn_her2_prodigy`
- Source execution record: `../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/execution.md`
- Source provenance: `../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/provenance.json`

## Design rationale

AntiBMPNN, structure-conditioned on the 1N8Z trastuzumab/HER2 complex, designed all six CDRs (H1/H2/H3 on VH and L1/L2/L3 on VL) while fixing the framework and required disulfides. The generated inventory contains 20 paired VH/VL variants. All 20 passed framework-integrity and disulfide-preservation checks. Five candidates were shortlisted using AntiBMPNN score and CDR-edit diversity.

The complete 20-candidate inventory is `candidates.csv`; only the five selected candidates appear in `shortlist.csv` and have binding/structure evaluation records.

## Matched-conditions evaluation

Reference and shortlisted candidates were evaluated on the same HER2 construct (1N8Z chain C) and preparation. For each shortlisted candidate, the 1N8Z backbone was kept fixed and designed CDR side chains were placed using approximate ideal geometry oriented by the original CA-to-CB direction. ProDIGy scored Fab chains A+B versus HER2 chain C. Antibody_Prediction supplied thermal-stability and solubility predictions.

## Supported improvements

- **AB_13** is the best computational candidate: ProDIGy ΔG −10.9 kcal/mol versus reference −9.9, predicted KD 9.4e−9 M versus 5.6e−8 M, 68 interface contacts, 27 clashes versus 26, and the highest ProtBert thermal-stability score (52.4).
- AB_20 and AB_05 maintain the reference ProDIGy prediction at −9.9 kcal/mol.
- AB_08 and AB_04 are slightly weaker than the reference under this fixed-pose approximation.

## Result artifacts

All paths below are relative to this run directory:

- `candidates.csv` — all 20 generated candidates, eligibility, selection and evaluation status.
- `shortlist.csv` — five selected candidates with rank, metrics and artifact paths.
- `designed_sequences.fasta` — shortlisted paired VH/VL sequences.
- `metrics.json` — machine-readable metrics for the reference and evaluated candidates.
- `benchmark_comparison.csv` — published REF15 controls and comparability decisions.
- `structures/` — reference plus five reconstructed candidate complexes.
- `evidence/prodigy_results.csv` — ProDIGy results.
- `evidence/property_predictions.csv` — Antibody_Prediction outputs.
- `evidence/reference/` — reference structure and retained Boltz2 confidence.
- `evidence/mappings/` — chain and design-scope mappings.
- `evidence/raw/` — retained raw generation/property/reconstruction outputs.
- `evidence/validation.json` — packaging validation.

## Benchmark and limitations

The published benchmark metric is REF15 (Rosetta REU). Rosetta was unavailable, so REF15 was not computed and was not fabricated. ProDIGy is a different contact-based metric in kcal/mol and is non-comparable to REF15. Its approximately 2.6 kcal/mol empirical error means the 1.0 kcal/mol AB_13 difference should be treated as directional rather than definitive.

Boltz2 reference VH–VL confidence was high (ipTM 0.955), while the reference VH–HER2 interface confidence was low (ipTM 0.245). Candidate Boltz2 signed downloads expired, so the candidate PDBs in this run are fixed-pose reconstructions, not completed Boltz2 candidate predictions. Full rotamer optimization was not run. Computational improvement does not establish experimental affinity or therapeutic activity.

## Source execution record

- [Execution record](../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/execution.md)
- [Execution provenance](../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/provenance.json)

Task: `task_001_her2_trastuzumab_interaction_optimization`. Run: `20261110_antibmpnn_her2_prodigy`.
