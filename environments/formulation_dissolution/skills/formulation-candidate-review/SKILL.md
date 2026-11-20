---
name: formulation-candidate-review
description: Review authorized ranolazine candidates for composition, dose, process, compatibility and stability eligibility before prediction or ranking in formulation-optimization-gym.
---

# Formulation candidate review

Read the selected episode, `tools/mixture_validator.py`, relevant `agents/` contracts and [implementation plan](../../docs/implementation_plan.md) T03/T06/T10. Review supplied evidence; do not invent a replacement formula or default manufacturing settings.

## Inputs

Require verified inventory, actual or explicitly proposed candidate identity, amounts/grades/units, dose/potency basis, applicable method, approved source-linked bounds/process limits and intended decision. Missing inputs allow limited arithmetic review, but scientific eligibility remains `insufficient_data`.

## Review

1. Check material identities, amounts, consistent units and mass balance. Percentage totals do not verify dose/potency; follow the explicit basis.
2. Check dose/potency, grades and applicable bounds against approved sources/versions. Record passed, failed and not-evaluated checks separately. Non-applicability needs a reviewed record.
3. Assess compatibility using source-linked results or authorized tool outputs with explicit evidence labels. Material identity or API descriptors alone do not establish compatibility.
4. Assess stability only within supported conditions, packaging, duration and method. Distinguish chemical/physical stability from compatibility; favorable compatibility does not establish shelf life.
5. Check manufacturing constraints against recorded material/process evidence. Do not infer absent compression, coating or storage parameters from public labels.
6. Apply action-specific prerequisites. An authorized assessment/prediction may investigate unknown compatibility or stability when its input, method, applicability, permission and budget requirements are satisfied. Unresolved required evidence still blocks scientific feasibility claims, ranking and advancement. Record objective directions, units/scales, tradeoffs, costs and model applicability before ranking.

Current `Check.valid` means no failed checks and may coexist with unknown constraints. Do not interpret it as scientific feasibility. When implementing T03, enforce a separate eligibility decision in actions, verifier, ranking and acquisition together.

## Deliver

Produce candidate/case and constraint versions, each check/status/source, arithmetic status, scientific eligibility, missing evidence, compatibility/stability scope and allowed next analysis. Predictions remain predictions; ranking is not product validation or manufacturing authorization.

Test first: balanced candidate with unknown bounds, incomplete potency, missing required stability/process evidence and out-of-domain prediction. Each stays ineligible for the decision requiring that evidence. Preserve previous state on rejection.

Send supported questions to [experiment design](../formulation-experiment-design/SKILL.md). Arithmetic validity does not establish a root cause.
