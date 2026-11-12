# Task 002 — PD-L1 Epitope-Targeted scFv Design

Source execution record: `../../../src/task_002_pdl1_epitope_targeted_scfv_design/runs/20261110_rf_antibody_boltz2/execution.md`

## Packaging scope

This report describes retained scientific artifacts only. No design, structure prediction, property prediction or scoring was rerun during normalization.

## Workflow distinction

Workflow A (`epitope_abgen -> AntiBMPNN -> Boltz2 -> Antibody_Prediction`) was selected during planning because it directly conditions design on PD-L1 hotspots I37, Y39, E41, R96 and M98. The `epitope_abgen` job returned no output after the retained polling window, so it has no downstream scientific artifacts.

Workflow B (`rfdiffusion_proteinmpnn -> local Boltz-2 -> interface analysis -> Antibody_Prediction`) was the completed fallback. It returned 20 generated candidates; 10 were evaluated locally with Boltz-2; five received Antibody_Prediction properties and were retained in the shortlist.

Workflow C (`agcdr_diff`) was not run because a pre-positioned antibody-antigen complex was unavailable.

## Candidate and result coverage

- Generated candidates: 20.
- Locally structure-evaluated candidates: 10.
- Candidates with property predictions: 5.
- Shortlist records: 5.
- Epitope-engaged recommendations: rf1_d5, rf1_d2, rf1_d3 and rf0_d5.
- Contrast control: rf0_d0, retained because it had high interface confidence but zero declared-hotspot engagement.
- `designed_sequences.fasta` contains the five candidates carried into the evaluation/shortlist. The complete generated inventory is retained in `candidates.csv` and `evidence/raw/`.

## Shortlist summary

| Candidate | Role | ipTM | Hotspots engaged | Reason |
|---|---|---:|---:|---|
| rf1_d5 | primary recommendation | 0.772 | 5/5 | Highest ipTM among all-hotspot candidates; low ipDE and favorable retained property values |
| rf1_d2 | selected | 0.714 | 5/5 | Strong interface confidence, five hotspots and low clashes |
| rf1_d3 | selected | 0.680 | 5/5 | Highest retained ESM thermal score among the shortlist and fewest clashes |
| rf0_d5 | selected | 0.551 | 5/5 | Five hotspots with conservative VL redesign |
| rf0_d0 | contrast control | 0.813 | 0/5 | High-confidence off-epitope mode; not an epitope-targeted recommendation |

## Benchmark and interpretation limits

The retained H5 reconstruction comparison reports 14.94 Å antibody Cα RMSD from local Boltz-2 versus the published Germinal generator value of 1.25 Å. These are different predictors and protocols. The published aggregate screening and enrichment metrics cannot be reproduced from the retained single-task artifacts. Prodigy, Boltz-2 confidence, thermal-stability and solubility values are computational predictions, not measurements.

The result package preserves the distinction between the design-selected but unsuccessful epitope-conditioned branch and the executed whole-surface fallback. No platform backend code is reconstructed locally.

## Artifacts

- Candidate inventory: `candidates.csv`
- Shortlist: `shortlist.csv`
- Evaluated sequences: `designed_sequences.fasta`
- Structures: `structures/`
- Machine-readable metrics: `metrics.json`
- Benchmark comparison: `benchmark_comparison.csv`
- Raw platform/local outputs: `evidence/raw/`
- Reference and mappings: `evidence/reference/`, `evidence/mappings/`
- Fresh packaging validation: `evidence/validation.json`
