# Task 004 execution record

Run ID: `20261111_lcat_cdrh3_multworkflow`
Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`
Status: completed with documented failures and pending stages

## Target

5BV7 human LCAT (L4F/N5D) reference Fab complex. Native heavy-chain CDR-H3 is `AREGAAVRSFYYSYYGMDV`.

## Stages actually executed

| Stage | Status | Record |
|---|---|---|
| Reference PDB and VH/VL preparation | completed | `inputs/`, preparation code |
| AgCDR-Diff backbone generation | completed | 24 PDB backbones |
| AntiBMPNN sequence design | completed | 240 sequences, 10 per backbone |
| CDR_Generator/EvoDiff generation | completed | 24 HCDR3 sequences |
| AAR and CAAR scoring | completed | W1/W2 evidence JSON |
| CDR-H3 RMSD/TM scoring | completed | corrected W1 RMSD JSON; prior W5 metrics |
| Interface contacts/minimum distance | completed | native and W1 evidence |
| Developability metrics | completed | W2 sequence-level metrics |
| ProteinMPNN/Boltz2 comparison | completed in prior work | 20 designs, top 3 structures |
| IG-Design | failed | internal `KeyError: 'aa_regions'` |
| Epitope AbGen | pending/no output | no scientific artifact produced |
| Stability-Binding DDG | not run | no direct candidate score claimed |

## Key results

- W1 mean AAR: 0.0414; best AAR: 0.2105.
- W1 best loop-aligned RMSD: 7.448 Å; mean RMSD: 7.924 Å.
- W1 native interface: 352 heavy-atom contact pairs and 2.79 Å minimum distance.
- W1 generated interface: approximately 1 contact pair on average and 6.76 Å minimum distance on average; sample 9 retained 9 contact pairs.
- W2 best AAR: 0.2632; mean AAR: 0.1360.
- W5 best AAR/CAAR: 0.4737/0.5714; best framework-aligned RMSD: 6.456 Å for `task004_sample9`.

## Selection outcome

`task004_sample9` is the overall computational shortlist leader. `cdr_gen_9` is the best Boltzmann-platform sequence-only candidate. `agcdr_16` is the best Boltzmann-platform loop-RMSD candidate, but it is not interface-preserving. `agcdr_9` is retained as the best W1 interface contrast.

## Deviations and limitations

- W5 is a prior completed comparison workflow, not a duplicate submission in this run.
- W1 and W5 RMSD values use different alignment protocols.
- Remote Boltzmann submission payloads were not retained as local source code.
- Epitope detection was limited by the prepared-PDB result and is not used as a decisive binding claim.

## Result links

- Results report: `../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/report.md`.
- Candidate table: `../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/candidates.csv`.
- Benchmark comparison: `../../../../benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction/benchmark_comparison.csv`.

## Canonical scientific results

- [Scientific report](../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/report.md)
- [Candidate inventory](../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/candidates.csv)
- [Selection table](../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/shortlist.csv)

The source run and scientific results share run ID `20261111_lcat_cdrh3_multworkflow`.


## AbFlow benchmark reproduction

Completed a separate 60-case AbFlow RAbD H3 benchmark using the downloaded RAbD test set and the retained `paratope_centric_design.ckpt`. The run used Python 3.10.14, Biopython 1.79, PyTorch 2.6.0+cu124, batch size 1, one worker and the RTX 3090. AbFlow's own metric pipeline completed AAR, CAAR, RMSD, TM-score, structural lDDT and DockQ for all 60 cases with no OOM.

The reproduced aggregate is retained under the matching results evidence. Current task-004 ProteinMPNN+Boltz2 candidates were evaluated separately under the same structural metric implementations and are not relabeled as AbFlow-generated candidates.
