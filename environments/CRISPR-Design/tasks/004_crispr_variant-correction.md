# Task: crispr_variant_correction_004

**Task family:** application-aware CRISPR design — **genetic-disease variant correction &
precision repair (modality router: BE / PE / HDR)**. **Status:** specification phase;
runtime pending; published anchors only.

## Description

Given a reference-verified pathogenic variant and a correction objective, route the
modality by edit type and distance, then run the modality-specific design (tasks 005/006
or HDR below) with allele-discrimination checks: base edit reachable in editor window →
BE; otherwise PE (≤40 bp per ePRIDICT scope); larger/tag constructs → HDR.

## Target

Resolved per request ([004 example brief](../config/004_variant-correction.request.example.json) — illustrative only).

- **Variant:** ClinVar/dbSNP + VEP verified before any allele-selective design.
- **Default vetoes:** off_target_exact_match, pam_shared_with_wt_allele.
- **Default weight emphasis:** specificity .35 / outcome_quality .30 / on_target .25 / context .10.

## Design Constraints

- WT-sparing: PAM/spacer discrimination between mutant and WT allele checked (PAM created/
  destroyed by the variant is the clean case); mismatch-position discrimination scored
  (CFD/Elevation on both alleles).
- HDR path: donor design by verified rules only — Richardson-2016 asymmetric ssODN
  (donor complementary to non-target strand; ~36-nt PAM-distal / ~91-nt PAM-proximal
  convention) + CUNE arm-composition context (n=30 — thin, disclosed); **no large ML HDR
  predictor exists** — stated, never approximated.
- Modality decision recorded with reasons; task 005/006 stages inherited on hand-off.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm correction objective; verify variant. | Confirmed hashed brief + verified `variant.json`. |
| 2. Modality router | Edit type + distance → BE / PE / HDR with recorded reasons. | Router decision. |
| 3. Allele discrimination | WT vs mutant PAM/spacer + mismatch scoring both alleles. | Discrimination assay record. |
| 4. Modality design | Hand off to task 005 (BE) / 006 (PE) or HDR donor design (rules). | Modality candidates. |
| 5. Battery | Full E-stack incl. variant-aware off-target (E3c). | Per-dimension evidence. |
| 6. Rank + deliver | Purity-weighted ranking (intended vs unintended). | Typed bundle. |

## Expected Output

Modality-decision record + ranked candidates with intended-edit + purity evidence +
allele-discrimination assay + provenance; `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Never claim correction from efficiency scores; bystander/purity endpoints disclosed per
model; HDR efficiency never predicted beyond rules + context.

## Important Instructions

Published anchors: BE-Hive (3,388 pathogenic SNVs correctable at ≥90% precision),
PRIDICT2.0 (13,349 pathogenic mutations; purity ρ 0.78), CUNE (n=30 — thin). No neutral
BE/PE benchmark exists — cross-tool claims are self-reported; local plan uses
BE-dataHIVE + Mathis held-out. Run slots NOT_EXECUTED.
