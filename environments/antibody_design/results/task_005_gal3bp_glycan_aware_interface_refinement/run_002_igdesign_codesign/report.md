# Gal-3BP — IgDesign candidate-evaluation results

Run: `run_002_igdesign_codesign`.

The completed IgDesign route produced a 97-candidate retained library and a matched three-candidate evaluation.

## Completed workflow

Local IgDesign generated 100 samples from the prepared reference-complex context. CDR, framework and sequence checks retained 97 unique candidates. The three selected candidates received matched AF2-Multimer evaluation, sequence-echo verification, Prodigy scoring, interface chemistry, simplified glycan analysis and five-model interface-persistence assessment.

## Candidate results

| Candidate | Rank-1 ipTM | Predicted ΔG kcal/mol ↓ | Simplified occlusion Å² | Glycan clashes | Contact persistence | Interface RMSD Å |
| --- | --- | --- | --- | --- | --- | --- |
| G3I-01 | 0.29 | -9.1 | 217.1 | 0 | 0/18 | 5.78–51.39 |
| G3I-02 | 0.29 | -8.4 | 220.6 | 0 | 0/22 | 33.32–50.39 |
| G3I-03 | 0.29 | -9.2 | 213.3 | 0 | 0/19 | 15.21–39.31 |

## Reference comparison and highlights

The matched reference has rank-1 ipTM **0.32** and predicted Prodigy energy **−9.2 kcal/mol**. **G3I-03** matches that energy and has the lowest modeled glycan occlusion in this run (**213.3 Å²**). All three evaluated candidates have rank-1 ipTM **0.29** and zero counted glycan clashes. **G3I-01** has 10 recorded hydrogen bonds, alongside nine for the reference.

The ensemble analysis records persistence **0/18**, **0/22** and **0/19**, with interface RMSD ranges spanning **5.78–51.39 Å** across the candidates. Sequence-echo verification confirms the heavy chain, light chain and antigen identities. The glycan and ensemble definitions match those used in the task's AntiBMPNN comparison route.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement/comparison.md).
