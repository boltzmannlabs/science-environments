# Local evidence-grounded route selection

This historical case study refers to task descriptions and research receipts retained in the original local workspace, including `examples/tasks/` and `artifacts/`. They are not bundled in this source release, and the recorded pilot is not a current-checkout benchmark result. Use the current [environment README](../README.md) for runnable examples and [validation status](../results/README.md) for current verification.

## What was tested

The [aspirin task](../examples/tasks/aspirin_001.md) compares fixed breadth-first
search with main Agent Scientist and a strategist/condition-scientist/critic
configuration. Every arm uses the same target, six-material inventory,
LocalRetro checkpoint and task resource caps. Both LLM arms use only the
configured main-profile model, recorded here as `gpt-6-sol`.

This is a familiar single-target pilot. It is separate from the frozen
measured-data test of the newly trained yield model. Neither experiment proves
general multi-step retrosynthetic improvement.

## Route decisions and individual review

The reviewer received blinded route structures and independently retrieved
source material, without generating-method labels or prediction scores.
Reviews ran in separate main-profile contexts. The
[university source](https://web.njit.edu/~mitra/green_chemistry/EXP_5.htm)
documents the salicylic-acid/acetic-anhydride transformation with phosphoric
acid. It does not establish every proposed alternative or supply yields for
our incompletely specified routes.

Across both recorded versions, all six distinct proposed routes received
[individual reviews](../artifacts/aspirin_comparison/reviews_by_fingerprint/).
Three records of the same acetylation, with different annotations, were accepted as source-supported transformations; three remained
unresolved. All have `lab_ready: false` and incomplete operating conditions.
Acceptance here is an automated source assessment, not human review,
experimental reproduction, or evidence from an independent model family.

| Latest arm | Submitted | Source-supported submitted transformations | Expansions | Elapsed | Recorded LLM tokens |
|---|---:|---|---:|---:|---:|
| Fixed workflow | 2 | Both unresolved | 12 | 90.04 s | 0 |
| Main Agent Scientist v2 | 1 | 1 accepted with incomplete conditions | 1 | 35.27 s | 31,728 |
| Specialists v2 | 0 | No submitted shortlist | 2 | 98.82 s | 98,624 |

The fixed proposal using acetic anhydride omitted the catalyst specified by
the inspected source. Its acetic-acid alternative also lacked supporting
evidence. These are unresolved evidence gaps, not claims that the reactions
are impossible. The main agent included the source-supported catalyst, but
quantities, conditions, measured yield and cost remain unknown.

The specialist configuration stopped at resource admission before its final
submission. It had a plausible intermediate proposal, so this failure does
not establish inferior chemical reasoning. It does establish that the tested
configuration failed to finish under the common caps. Specialists remain
experimental; the main agent is the default. Individual-role ablation gains
have not been demonstrated.

The [metrics](../artifacts/aspirin_comparison/metrics.json) retain unknown
outcomes as null. `review_coverage` includes an unresolved source review;
`resolved_outcome_coverage` counts only accepted/rejected outcomes. No submitted
route means failure to deliver a shortlist, not evidence that the target is
unsynthesizable. Equal allowances are not equal actual resource consumption.

Review overhead is separate: successful reviews used six model calls and
25,480 reported tokens across two sessions. Earlier review attempts hit the
native transport's 12-second idle timeout; their failures and diagnosis are
retained. A review-process-only 60-second idle allowance enabled completion
within the existing overall deadline without changing the main profile.

## New scientific model

The [condition model](../artifacts/model/README.md) was trained on 3,955 measured
reaction rows with a frozen product-family split. Its held-out test contains
790 rows, three substrate/inventory variants, and **one independent product
family**. The same supplied one-step candidates and route checks are used by
the learned predictor and training-condition-mean baseline.

Mean measured yield of the top-1 selection was **50.805% versus 49.844%**,
a gain of **0.961 percentage points**. The baseline won at top 5 and top 10.
This is a narrow retrospective selection gain; statistical significance,
unfamiliar-scaffold generalisation and multi-step discovery are unproven.
Thirty selected decision records, covering 22 unique source rows, were matched
back to measured source records. This source audit is not a new experiment.

The model's explicit domain check requires the declared substrate, partner,
precatalyst and correct C–N product transformation. It abstains from assigning
an aspirin yield. Agent-authored yield numbers cannot enter host ranking.

## Reproduce and inspect

Use the [README](../README.md) for local inference and the
[delivery guide](LOCAL_DELIVERY.md) for training and frozen evaluation commands.
The [tool audit](TOOL_AUDIT.md) distinguishes discovered capabilities from
actually executed adapters.

Recompute case metrics from existing reviews without an LLM call:

```sh
.venv/bin/synthesis-route-gym evaluate \
  --input artifacts/aspirin_comparison/evaluation_inputs.json \
  --reviews artifacts/aspirin_comparison/reviews.json \
  --output artifacts/reproduction/aspirin_metrics.json
```

The remaining scientific questions are broader held-out targets and seeds,
isolated specialist ablations, measured impurity accuracy, quantitative process
costs and biocatalytic operating evidence. The current executable paths retain
those unknowns rather than manufacturing success labels.
