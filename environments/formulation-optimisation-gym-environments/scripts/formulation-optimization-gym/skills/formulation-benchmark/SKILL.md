---
name: formulation-benchmark
description: Design and run leakage-audited formulation model evaluations and matched-budget A/B/C/D comparisons using eligible data. Use for exploratory or controlled-case validity, uncertainty and claim review.
---

# Formulation benchmark

Inspect `docs/evaluation_protocol.md`, `evaluation/holdout_benchmark.py`, predictor/uncertainty modules and [implementation plan](../../docs/implementation_plan.md) T08–T11. Current model is a scalar nearest-mixture baseline; its point-error function does not establish calibrated intervals. Small-sample code guards do not prove scientific adequacy.

## Eligibility and intended use

Choose controlled-case or exploratory literature track. Verify provenance/rights, endpoint/units, features, method/timepoint and processing scope. Keep recalls separate. Literature/graph records need the explicit exploratory path and original labels, never coercion to `measured`.

Declare the generalization question: replicate, formulation family, lot, study, site or method. Group related records, shared controls and duplicate publications accordingly. The same API does not make methods compatible.

For externally pretrained tools, record available training-data provenance and known/unknown overlap with the local holdout. A public-literature holdout may already be in a tool's training data. Unknown overlap is a limitation, not proof of independence; exclude affected results from claims of uncontaminated external generalization unless independence is established.

## Freeze before fitting

- Freeze dataset/source hashes, inclusions/exclusions, feature/target definitions, groups, seed/assignments and method strata.
- Have responsible reviewers prespecify independent sample support, meaningful error/improvement, interval coverage/width and applicability before final-test access. Do not invent product specifications or model targets.
- Separate development/calibration/untouched-test groups for interval claims, or document a reviewed alternative. Fit transforms/select models using development data only. Inadequate independence yields `not_evaluated` or `not_established`.
- Version training data, transforms, features, units, model/policy and domain. Missing required features stay unknown; predictions retain evidence labels and parent/model IDs.

## Compare appropriate arms

A = fixed zero-tool evidence-gap baseline; B = direct approved tools; C = same tools plus six bounded specialists; D = C plus evaluated model/policy. Freeze the same task/evidence permissions, criteria, versions, rubric and online budgets for applicable arms. Disclose D's offline training/compute separately. Final-test labels stay inaccessible to all arms.

A has no predictive output. Compare gap/provenance/unsupported-claim behavior where applicable; numeric prediction metrics are not applicable. Use a frozen predictive comparator for error comparisons. Unavailable B/C/D stay unevaluated, never simulated wins.

Measure errors with units/method/timepoint, calibrated coverage/width only if established, applicability/abstention, constraint violations, unsupported claims, source accuracy, attempts/failures, time and cost. Compare policy outcomes using independent measurements when available. Prespecify improvement analysis and include negative results.

## Verify and report

Test group overlap, changed manifests, holdout-fitted transforms, incompatible methods/units, inadequate calibration and unfair budgets. Independently audit splits/results. Tuning after test inspection requires a new untouched set for a fresh claim.

Report track, independent groups, manifests, models, all arm statuses, checks, metrics and limitations. Software tests and synthetic fixtures are not predictive evidence. Literature results cannot prove recall compliance; retrospective accuracy cannot establish prospective optimization. Preserve G3/G4/G5 distinctions.
