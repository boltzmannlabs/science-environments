# Task - 01 benchmark

[Task](../../tasks/task-01-clarithromycin-ir-formulation-dissolution/README.md) · [Results](../../results/task-01-clarithromycin-ir-formulation-dissolution/README.md)

## Frozen objective and inputs

The [specification](specification.md) is the user-supplied benchmark; its bounds/defaults are design assumptions, not regulatory limits. [Contract](../../config/task-01-clarithromycin-ir-formulation-dissolution/contract.json) freezes 500 mg API and 800 mg finished mass. [Input snapshots](inputs/) contain 24 original design-only records and sixteen published profile records (one duplicated reference is excluded during evaluation).

R1 numeric means/SD are from different roughly 875 mg coated recipes with croscarmellose, starch/talc and a different coat. No exact eight-excipient experimental dataset was supplied. Source numeric transcription is not independent laboratory verification.

## Tracks and metrics

1. **Composition:** exact identities, dose, bounds, mass/core/coat and uniqueness.
2. **Published-curve analysis:** in-sample fit and descriptive f1/f2; no regulatory similarity decision.
3. **v2 diagnostics:** LOTO and forward30 mean RMSE/MAE in percentage points, MAPE in relative percent. Forward30 repeats the 30-minute LOTO fold, not independent evidence.
4. **Design:** expanded CP/PVP matrix rank; blank prospective measurements stay blank.
5. **Abstention:** candidate dissolution/stability/manufacturing/compatibility and external predictive validation remain unavailable.

[Expected computed metrics](expected_metrics.json) were exported from the actual v2 run and are regression references, not experimental targets. The source scientific protocol and constraints must not be tuned after seeing scores.

## Fair-comparison boundary

The reported 39.88% reduction compares **our capped Weibull against our free Weibull on withheld literature endpoints**. It does not compare a new tablet against the published product. Several overall errors worsened. No calibrated recipe intervals, whole-formulation holdout, independent-batch evidence, f2 pass, stability improvement or shelf-life claim is supported.

[References](../../../../research/clarithromycin-ir-formulation/references.md).
