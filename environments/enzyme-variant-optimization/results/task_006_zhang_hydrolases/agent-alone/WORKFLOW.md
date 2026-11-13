# Executed workflow

This record describes actual agent-alone execution. Original design work is paused; reference comparison is a separate completed assessment.

| Step | Agent operation and outcome | Records |
|---|---|---|
| parent preparation | Original supplementary WT sequences and stabilized M2/M5 backgrounds were frozen separately. Structures were prepared for WT Pythia scans. | [Step record](steps/01_parent_preparation/README.md) |
| pythia scoring | Pythia scanned cellulase WT and beta-glucanase WT; raw C/P components and summed negative log-likelihood scores are retained. | [Step record](steps/02_pythia_scoring/README.md) |
| esm scoring | ESM-2 scanned stabilized cellulase M2 and beta-glucanase M5. Same-variant publication comparisons retain those distinct backgrounds. | [Step record](steps/03_esm_scoring/README.md) |
| ranking | Primary convention leaders are T131D, M2+T257K, M30P and M5+P10D. Opposite-sign diagnostics E158C/G74P remain in the raw candidate records. | [Step record](steps/04_ranking/README.md) |

## Separate property assessments

Original selected sequences were subsequently assessed with shared temperature, pHPred and NetSolP predictors. Reconstructable reference variants were assessed without restarting the design runs. [Results](reference_comparison/README.md).

## Current outcome

Declared scoring execution completed; provenance review separately recorded.

Sequence identities: [sequences/](sequences/). Usage: [USAGE_AND_TIME.md](USAGE_AND_TIME.md).

## Additional open-source metric comparison

EvoEF1 calculates whole combined variants against a common WT for each enzyme. This supplies a matched folding-stability comparison for final published M5/M7 variants and our retained candidates, alongside the original Pythia/ESM comparisons. Undefined combined Pythia/ESM paper scores are not fabricated.

This is an operator-guided post-selection assessment, separate from the original agent-alone design execution. Exact sequence identities and original selections are unchanged. [Metric records](reference_comparison/open_source_metrics.csv).
