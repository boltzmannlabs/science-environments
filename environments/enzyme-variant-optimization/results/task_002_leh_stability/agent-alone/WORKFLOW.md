# Executed workflow

This record describes actual agent-alone execution. Original design work is paused; reference comparison is a separate completed assessment.

| Step | Agent operation and outcome | Records |
|---|---|---|
| parent preparation | The native 149-residue 1NWW/Q9ZAG3 enzyme and biological dimer were used as the declared parent. | [Step record](steps/01_parent_preparation/README.md) |
| variant generation | Constrained sequence generation and later revisions are recorded in candidate_history.csv. | [Step record](steps/02_variant_generation/README.md) |
| property screening | Enzymes and NetSolP measured predicted temperature and solubility for parent and variants. | [Step record](steps/03_property_screening/README.md) |
| structure and chemical assessment | Boltz2, Vina, MolProbity and local chemical/geometry analyses assessed structures and ligand states. Dictionary compatibility and complete-state interpretation required recovery work. | [Step record](steps/04_structure_and_chemical_assessment/README.md) |
| revision and re evaluation | Results-driven sequence revisions were re-evaluated. LEH_R004 and LEH_R003 remain raw comparison candidates; the original structural acceptance requirement was not met. | [Step record](steps/05_revision_and_re_evaluation/README.md) |

## Separate property assessments

Original selected sequences were subsequently assessed with shared temperature, pHPred and NetSolP predictors. Reconstructable reference variants were assessed without restarting the design runs. [Results](reference_comparison/README.md).

## Current outcome

Paused

Sequence identities: [sequences/](sequences/). Usage: [USAGE_AND_TIME.md](USAGE_AND_TIME.md).
