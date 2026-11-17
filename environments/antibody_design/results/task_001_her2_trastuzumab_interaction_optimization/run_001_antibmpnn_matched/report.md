# HER2 / trastuzumab — AntiBMPNN workflow results

Run: `run_001_antibmpnn_matched`.

Reference-guided CDR redesign generated a verified paired-candidate library and a matched eight-candidate structural evaluation.

## Methods and preparation

The workflow used the 1N8Z trastuzumab Fv and HER2 ectodomain construct. AntiBMPNN generated 40 samples; sequence checks verified the CDR edit mask, framework identity and chain lengths. Deduplication retained 38 paired candidates, and eight received matched Boltz2 and Prodigy evaluation alongside the reference.

Boltz2 produced separate HER2:VH and HER2:VL records. Reference and candidates used the same construct and prediction/scoring procedures. Evaluation included Prodigy energy estimates, CDR pLDDT, contact overlap and heavy-atom interface clashes below 2.2 Å.

## Reference and candidate results

Energy values are Prodigy predictions in kcal/mol; confidence values use the 0–1 scale.

| Candidate | CDR changes | VH ΔG ↓ | VL ΔG ↓ | VL ipTM ↑ | VH / VL CDR pLDDT | Residue-ID overlap | Clashes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REFERENCE | 0 | -10.2 | -8.7 | 0.3400 | 0.8169/0.8708 | 0.0% | 0 |
| T001-C001 | 8 | -10.2 | -8.7 | 0.7010 | 0.8291/0.8895 | 0.0% | 1 |
| T001-C002 | 9 | -11.2 | -9.5 | 0.7920 | 0.8299/0.9222 | 6.2% | 3 |
| T001-C003 | 7 | -10.3 | -8.7 | 0.7530 | 0.8284/0.9092 | 6.2% | 1 |
| T001-C004 | 7 | -8.9 | -9.7 | 0.7380 | 0.8514/0.9182 | 0.0% | 0 |
| T001-C005 | 9 | -8.0 | -9.6 | 0.7970 | 0.8425/0.9073 | 0.0% | 1 |
| T001-C006 | 7 | -11.4 | -9.5 | 0.7810 | 0.8849/0.9044 | 0.0% | 0 |
| T001-C007 | 10 | -10.2 | -10.1 | 0.5690 | 0.8378/0.8714 | 6.2% | 3 |
| T001-C008 | 6 | -10.6 | -9.6 | 0.8080 | 0.8159/0.9337 | 6.2% | 1 |

## Candidate highlights

**T001-C008** combines the highest VL ipTM (**0.8080**) and VL CDR pLDDT (**0.9337**) with predicted VH/VL energies of **−10.6/−9.6 kcal/mol**. **T001-C006** provides the lowest VH predicted energy (**−11.4 kcal/mol**) and zero counted clashes. **T001-C007** provides the lowest VL predicted energy (**−10.1 kcal/mol**), together with three counted clashes. The saved shortlist retains **T001-C005** as its first-ranked entry; these metric-specific highlights identify complementary numerical strengths.

All eight evaluated candidates exceed the reference VL ipTM of 0.3400, and six have lower VL predicted energy than the reference value of −8.7 kcal/mol.

## Reference comparison and metric definitions

The contact-overlap score is the intersection of recorded HER2 interface residue identifiers with the 16-residue 1N8Z crystal contact set, divided by 16. The delivered calculations retain the PDB crystal-contact identifiers and the model construct identifiers used in that calculation. Reported overlap spans 0–6.2%; the VH and VL prediction records retain their separate interface definitions.

The published reference reports Rosetta REF15 interaction energies in REU. The present candidate comparisons use matched local Boltz2 confidence and Prodigy energy estimates against the predicted trastuzumab reference, with each scoring definition and unit stated in its table.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization/comparison.md).
