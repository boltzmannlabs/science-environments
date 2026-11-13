# Executed workflow

This record describes actual agent-alone execution. Original design work is paused; reference comparison is a separate completed assessment.

| Step | Agent operation and outcome | Records |
|---|---|---|
| parent preparation | The native149-residue LEH sequence and 1NWW coordinates were prepared for structure-conditioned scoring. | [Step record](steps/01_parent_preparation/README.md) |
| pythia scoring | Pythia scanned2755 coordinate-mapped substitutions. C/P component scores, their sum and mean sensitivity are retained separately. | [Step record](steps/02_pythia_scoring/README.md) |
| ranking | The summed-score cutoff <−2 selected33 mutations. D101V and T85V are the retained score leaders. D101V changes catalytic Asp101; ranking does not establish retained function. | [Step record](steps/03_ranking/README.md) |

## Separate property assessments

Original selected sequences were subsequently assessed with shared temperature, pHPred and NetSolP predictors. Reconstructable reference variants were assessed without restarting the design runs. [Results](reference_comparison/README.md).

## Current outcome

Declared scoring execution completed; provenance review separately recorded.

Sequence identities: [sequences/](sequences/). Usage: [USAGE_AND_TIME.md](USAGE_AND_TIME.md).
