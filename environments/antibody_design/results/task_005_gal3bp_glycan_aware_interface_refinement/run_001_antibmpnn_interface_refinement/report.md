# Gal-3BP — AntiBMPNN interface-analysis results

Run: `run_001_antibmpnn_interface_refinement`.

The completed workflow delivers a verified candidate library, matched model scores, glycan-model measurements and ensemble interface statistics.

## Inputs and completed workflow

The prepared input combines the PDB 7KEW BDBV-43-derived Fv with the mature Gal-3BP construct. Reference prediction used Boltz2 and AF2-Multimer. AntiBMPNN generated 20 samples, deduplication retained 19 candidate sequences, and three received matched AF2-Multimer, Prodigy and interface evaluation. Sequence verification confirmed the downloaded candidate models against the submitted designs.

The analyses quantified heavy-atom contacts, hydrogen bonds, salt bridges, simplified glycan occlusion and interface consistency across five-model ensembles.

## Matched reference and candidate results

| Record | Rank-1 ipTM ↑ | Predicted ΔG kcal/mol ↓ | Heavy-atom contacts | H-bonds | Salt bridges |
| --- | --- | --- | --- | --- | --- |
| BDBV43_reference | 0.32 | -9.2 | 1387 | 9 | 0 |
| G3BPD-14 | 0.68 | -8.7 | 512 | 5 | 0 |
| G3BPD-04 | 0.66 | -8.7 | 608 | 5 | 0 |
| G3BPD-17 | 0.56 | -8.6 | 665 | 6 | 2 |

## Glycan and ensemble measurements

| Candidate | Simplified glycan occlusion Å² | Glycan clashes | Contact persistence | Interface RMSD range Å |
| --- | --- | --- | --- | --- |
| G3BPD-14 | 222.2 | 0 | 0/6 | 6.12–41.83 |
| G3BPD-04 | 217.2 | 0 | 0/7 | 6.22–45.30 |
| G3BPD-17 | 217.5 | 0 | 0/2 | 11.34–37.31 |

The simplified glycan model uses the stated BACK-region window and N344 context, with reference occlusion **245.3 Å²**. Persistence counts rank-1 Cα contact pairs retained in at least three of five models. The interface RMSD aligns the antigen before comparing the interface coordinates.

## Candidate highlights

**G3BPD-14** has the highest rank-1 ipTM (**0.68**), versus **0.32** for the reference. Candidate Prodigy energies are **−8.7/−8.7/−8.6 kcal/mol**, versus the reference **−9.2 kcal/mol**. All three candidates have zero counted glycan clashes and lower modeled occlusion than the reference. Ensemble analysis records zero rank-1 pairs retained in at least three of five models, with candidate interface RMSD spanning **6.12–45.30 Å**. The report presents each confidence, energy, occlusion and ensemble endpoint under its own definition.

The task comparison places this matched reference/candidate screen beside the completed IgDesign route. Published study measurements are documented separately with their study-specific constructs and sampling definitions in the benchmark reference.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement/comparison.md).
