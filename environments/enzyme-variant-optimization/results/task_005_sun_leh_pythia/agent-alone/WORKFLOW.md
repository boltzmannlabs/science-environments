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

## Additional open-source metric comparison

The original Pythia scan supplies matched P57A/D101V/T85V score comparisons. New DDGun predictions were completed for P57A and D101V; exact T85V output was reused. No scan or sequence generation was repeated.

This is an operator-guided post-selection assessment, separate from the original agent-alone design execution. Exact sequence identities and original selections are unchanged. [Metric records](reference_comparison/open_source_metrics.csv).
