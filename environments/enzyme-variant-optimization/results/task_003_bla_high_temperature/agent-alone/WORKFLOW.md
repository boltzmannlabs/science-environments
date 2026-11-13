# Executed workflow

This record describes actual agent-alone execution. Original design work is paused; reference comparison is a separate completed assessment.

| Step | Agent operation and outcome | Records |
|---|---|---|
| parent preparation | The declared mature BLA parent is WP_061576039.1 residues30–512. Its 483-residue identity is retained in parent.fasta. | [Step record](steps/01_parent_preparation/README.md) |
| variant generation | The first mutagenesis route failed during model-weight retrieval. SolubleMPNN generated six unique initial variants from12 draws; a later revision generated two additional variants. | [Step record](steps/02_variant_generation/README.md) |
| property screening | Enzymes temperature predictions screened the complete sequences. The retained descriptive leader is BLA_R2_001. | [Step record](steps/03_property_screening/README.md) |
| structure and chemical assessment | Predicted structures, docking, MolProbity and subsequent local parent-component preparation were attempted. The latest partial-state export completed; matched parent/candidate complex assessment remains open. | [Step record](steps/04_structure_and_chemical_assessment/README.md) |
| revision and re evaluation | The actual second-round variants were re-scored. No fully qualified improved finalist was sealed; the report presents the retained raw leader. | [Step record](steps/05_revision_and_re_evaluation/README.md) |

## Separate property assessments

Original selected sequences were subsequently assessed with shared temperature, pHPred and NetSolP predictors. Reconstructable reference variants were assessed without restarting the design runs. [Results](reference_comparison/README.md).

## Current outcome

Paused

Sequence identities: [sequences/](sequences/). Usage: [USAGE_AND_TIME.md](USAGE_AND_TIME.md).
