# Executed workflow

This record describes actual agent-alone execution. Original design work is paused; reference comparison is a separate completed assessment.

| Step | Agent operation and outcome | Records |
|---|---|---|
| parent preparation | Public 3TGL mature sequence (269 residues) was retained as the common parent. The exact laboratory starting construct was not established. | [Step record](steps/01_parent_preparation/README.md) |
| variant generation | Constrained generation produced the candidates recorded in candidate_history.csv. Parent identity and protected positions were carried through revision. | [Step record](steps/02_variant_generation/README.md) |
| property screening | Enzymes Tm and NetSolP predictions screened parent and variants. Full-precision measurements are retained in outputs.csv. | [Step record](steps/03_property_screening/README.md) |
| structure and chemical assessment | Folded models, MolProbity, docking and retained-pose geometry were assessed. Ligand preparation and output compatibility problems required additional assessment; see job status and measurement records. | [Step record](steps/04_structure_and_chemical_assessment/README.md) |
| revision and re evaluation | The agent revised sequences after reviewing earlier predictions, then re-evaluated them. RML_R2_02 and RML_R2_01 are retained for descriptive comparison; full functional qualification remains open. | [Step record](steps/05_revision_and_re_evaluation/README.md) |

## Separate property assessments

Original selected sequences were subsequently assessed with shared temperature, pHPred and NetSolP predictors. Reconstructable reference variants were assessed without restarting the design runs. [Results](reference_comparison/README.md).

## Current outcome

Paused

Sequence identities: [sequences/](sequences/). Usage: [USAGE_AND_TIME.md](USAGE_AND_TIME.md).

## Additional open-source metric comparison

Existing exact-sequence DDGun results were verified and reused; no new molecular calculation was submitted for this task. Parent comparisons remain the agreed basis.

This is an operator-guided post-selection assessment, separate from the original agent-alone design execution. Exact sequence identities and original selections are unchanged. [Metric records](reference_comparison/open_source_metrics.csv).
