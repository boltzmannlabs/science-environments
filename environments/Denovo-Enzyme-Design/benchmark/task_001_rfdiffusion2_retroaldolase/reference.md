# Benchmark: retroaldolase active-site scaffold design

Task ID: `task_001_rfdiffusion2_retroaldolase`

## Published Results

Source: [Atom-level enzyme active site scaffolding using RFdiffusion2](https://doi.org/10.1038/s41592-025-02975-x). Primary article passages are retained with the Results raw evidence.

Workflow: catalytic theozyme → RFdiffusion2 scaffold generation → LigandMPNN sequence assignment → independent structure prediction and task-specific assessment.

| Published quantity | Value | Source and definition |
|---|---|---|
| AME catalytic-site recovery criterion | Heavy-atom RMSD<1.5Å | Results AME benchmark; fit catalytic N/CA/C, then evaluate catalytic-residue heavy atoms |
| Ligand short-contact definition | Distance<1.5Å | Results AME benchmark; retain the atom selection for each implementation |
| Backbone sampling per AME case |100 | Benchmark protocol, not the sample count for one sequence |
| Sequence assignment per AME backbone |8 | LigandMPNN benchmark protocol |
| Figure4a nearest-PDB structure |6SU3 | Paper's designed retroaldolase |
| Figure4a nearest-PDB TM-score |0.47 | Structural novelty example |
| Designed-retroaldolase kcat/KM |6.34±0.92M⁻¹s⁻¹ | Retroaldolase section; separate from motif-donor5AN7 |

## Evaluation Criteria

| Quantity | Comparison rule |
|---|---|
| Catalytic RMSD | Preserve alignment atoms,41-heavy-atom selection and cohort/sample denominator. Compare to the published numerical threshold; no per-example reference RMSD is invented. |
| Whole-chain RMSD | Fit corresponding120Cα atoms; report separately from catalytic-only alignment. |
| Sidechain RMSD | One globalCα fit followed by residue-specific sidechain residuals; preserve coupledTyr ring symmetry. |
| RMSF | Within-cohort population coordinate dispersion; keep different sequences and cohorts separate. |
| Ligand clearance | Distinguish design-backbone clearance from full protein/free-ligand heavy contacts. |
| Structural novelty | Retain database snapshot, retrieval scope, matching chain and both TM-score normalizations. |
| Sequence constraint | Verify catalytic identities and count nonmotif lysines directly from each sequence. |

## Saved workflow results

See [comparison.md](comparison.md) and [the results report](../../results/task_001_rfdiffusion2_retroaldolase/GLP1_p03_variable_s02/report.md).
