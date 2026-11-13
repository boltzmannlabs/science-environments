# Executed workflow

This record describes actual agent-alone execution. Original design work is paused; reference comparison is a separate completed assessment.

| Step | Agent operation and outcome | Records |
|---|---|---|
| parent preparation | The full 235-residue 3LCC construct consists of native227 plus LEHHHHHH. SAH and ethyl iodide define the requested reaction inputs. | [Step record](steps/01_parent_preparation/README.md) |
| variant generation | The failed mutagenesis route was replaced by SolubleMPNN. Its first12 records produced one unique V140A variant; the next8 produced A144S. Later ThermalMPNN landscapes expanded the candidate set. | [Step record](steps/02_variant_generation/README.md) |
| property screening | CatPred supplied the primary sequence/reaction prediction; Enzymes and NetSolP supplied property screens. ATH_R2_09 is the retained post-revision property candidate. | [Step record](steps/03_property_screening/README.md) |
| structure and chemical assessment | Boltz2, MolProbity and Placer outputs were inspected. A disconnected-reactant Boltz job failed; another route returned separate complexes. Native Placer crops required chemical-state review. | [Step record](steps/04_structure_and_chemical_assessment/README.md) |
| revision and re evaluation | Search positions and subsequent landscapes were revised after earlier measurements. Current chemical/function acceptance remains open; descriptive property comparison uses the exact retained sequence. | [Step record](steps/05_revision_and_re_evaluation/README.md) |

## Separate property assessments

Original selected sequences were subsequently assessed with shared temperature, pHPred and NetSolP predictors. Reconstructable reference variants were assessed without restarting the design runs. [Results](reference_comparison/README.md).

## Current outcome

Paused

Sequence identities: [sequences/](sequences/). Usage: [USAGE_AND_TIME.md](USAGE_AND_TIME.md).

## Additional open-source metric comparison

EvoEF1 folding comparisons for the reference and our retained candidate are complete. Reaction-site OpenMM/PySCF assessment is in progress; MD heating failures and corrected preparation are being diagnosed. Prepared-state quantum preflight is capability evidence only and is excluded from final comparison values.

This is an operator-guided post-selection assessment, separate from the original agent-alone design execution. Exact sequence identities and original selections are unchanged. [Metric records](reference_comparison/open_source_metrics.csv).
