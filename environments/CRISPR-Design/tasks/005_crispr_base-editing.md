# Task: crispr_base_editing_005

**Task family:** application-aware CRISPR design — **base editing (CBE/ABE, editor
choice)**. **Status:** specification phase; runtime pending; published anchors only.
Subsumes the prior `crispr-base-editing-environment` single-task scope.

## Description

Guide–editor pairing for a specified base edit: place the target base in the editor
window, enumerate bystanders in-window, choose/predict across editor families, and rank
by intended-edit efficiency vs purity. Endpoints come from BE-Hive-class outcome models;
editor-choice context from DeepBE-class models.

## Target

Resolved per request ([005 example brief](../config/005_base-editing.request.example.json) — PCSK9 ABE strategy class, illustrative only).

- **Default vetoes:** off_target_exact_match, bystander_in_window (window scoped to the
  declared editor).
- **Default weight emphasis:** outcome_quality .35 / on_target .30 / specificity .25 / context .10.

## Design Constraints

- Editor window declared per editor (the prior environment's interface convention: ABE
  positions 4–7, CBE 4–8; editor-specific windows from the model in force — disclosed per run).
- Prediction input conventions carry over where wrapped tools are used (50-nt context:
  19-nt upstream + 20-nt protospacer + 3-nt PAM + 8-nt downstream; orientation verified).
- Bystander outputs are window-scoped — they do not prove absence of editing outside the
  window; predicted fraction-of-reads-edited is not automatically the intended-correction
  rate (both caveats inherited verbatim from the prior environment's rules).
- Strand mapping: ABE predicts A→G on the editable strand; map complementary-strand
  changes when the variant sits on the other strand.
- Training-distribution caveat: landing-pad-trained models (BE-Hive/BE-DICT) vs
  endogenous-trained (DeepABE/DeepCBE) — model provenance disclosed per run.
- License tiers: DeepBE + yachielab repos have **no license** — research-internal,
  never redistributed; BEDICT2.0 CLI and BE-dataHIVE are the clean local candidates.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm edit spec (position/ref/alt verified); editor constraint or router. | Confirmed hashed brief. |
| 2. Enumerate | All spacers whose window contains the target base (both strands, orientation mapped). | `candidate_pool.csv`. |
| 3. Bystander enumeration | All editable bases in each window. | Bystander table. |
| 4. Outcome prediction | Intended fraction + purity per guide–editor (model identity disclosed). | Per-pair predictions. |
| 5. E3 off-target | Spacer enumeration + pair scores (BE off-target differs from nuclease — CHANGE-seq-BE evidence; layer marked accordingly). | Off-target record. |
| 6. Gates + rank | Purity-weighted; ±25% stability. | Ranked panel. |
| 7. Deliver | Panel + window/bystander evidence + provenance. | Typed bundle. |

## Expected Output

Ranked guide–editor combinations (counted separately from unique spacers) with intended
fraction, purity, bystander table, off-target record, provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Simulated edited sequence ≠ all eligible bases edited together; keep each
guide–editor–model prediction a separate result; never compare scores as calibrated
probabilities across differently configured models.

## Important Instructions

Published anchors: BE-Hive (38,538 targets, outcome R≈0.9 / efficiency R≈0.7), BE-dataHIVE
(460,000+ combos, 5 studies harmonized — fair-comparison substrate), DeepBE (63 editors),
BEDICT2.0 (R 0.60–0.94). **No neutral BE benchmark exists** — cross-tool claims
self-reported. Run slots NOT_EXECUTED.
