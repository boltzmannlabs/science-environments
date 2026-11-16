# PD-1 — backbone-diversified candidate screening

Run: `run_002_agcdr_antibmpnn`.

The completed route produced 115 gate-passing paired candidates and a matched five-candidate prediction panel.

## Methods and selection

The workflow used the paper's paired-framework context and the PD-1 extracellular construct. AgCDR-Diff generated 20 backbones, followed by 160 AntiBMPNN sequence samples. Sequence and framework gates retained 115 unique paired candidates. Five CDR-diverse candidates were selected before structural scoring, with a minimum pairwise CDR Hamming distance of 32 across 60 positions.

Boltz2 evaluated the five candidates and H965 control as separate PD1:VH and PD1:VL records. Antibody_Prediction supplied thermal-stability, solubility and CDR assessments. Structural analysis quantified interface contacts and overlap with the PD-L1-binding surface.

## Candidate results

Thermal stability is the ESM model estimate in °C; solubility is the returned model score.

| Candidate | VH ipTM ↑ | VL ipTM ↑ | VH / VL contacts <5 Å | Surface-overlap residues | Predicted Tm °C | Solubility score |
| --- | --- | --- | --- | --- | --- | --- |
| PD1T3-019 | 0.9453 | 0.9163 | 75/67 | 26 | 79.0 | 1 |
| PD1T3-011 | 0.9404 | 0.6770 | 74/50 | 19 | 77.7 | 1 |
| PD1T3-054 | 0.8818 | 0.7890 | 60/69 | 23 | 69.6 | 1 |
| PD1T3-038 | 0.8716 | 0.8559 | 72/69 | 22 | 80.2 | 1 |
| PD1T3-069 | 0.7218 | 0.8334 | 54/51 | 16 | 68.3 | 1 |

## Matched H965 control

| Prediction record | H965 ipTM |
| --- | --- |
| PD1:VH | 0.8953 |
| PD1:VL | 0.7172 |

## Candidate highlights

**PD1T3-019** has VH/VL ipTM **0.9453/0.9163**, compared with H965 **0.8953/0.7172**, and 26 contacted residues on the declared PD-L1-binding surface. Two of five candidates exceed the VH control and four exceed the VL control. Follow-up Prodigy and ipSAE results for these same models are delivered in run_003_prodigy_ipsae_evaluation.

The published reference defines separate panel-level screening endpoints. This run's tables present candidate-level structural and property predictions, with H965 evaluated under the matched local procedure.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design/comparison.md).
