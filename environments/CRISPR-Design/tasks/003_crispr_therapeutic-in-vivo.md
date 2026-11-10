# Task: crispr_therapeutic_in_vivo_003

**Task family:** application-aware CRISPR design — **therapeutic in-vivo editing
(systemic/LNP context)**. **Status:** specification phase; runtime pending; published
anchors only. Core battery shared; the specificity stack is elevated here.

## Description

Guide design under regulator-grade specificity requirements: variant/population-aware
off-target nomination, explicit experimental-assay hierarchy, delivery-tissue context.
Computational output supports prioritization only — regulators required in-vitro +
cellular off-target assays on top of in-silico scoring (exa-cel BLA record).

## Target

Resolved per request ([003 example brief](../config/003_therapeutic-in-vivo.request.example.json) — TTR, illustrative only).

- **Default vetoes:** off_target_exact_match, high_top1_cfd.
- **Default weight emphasis:** specificity .55 / on_target .20 / outcome_quality .15 / context .10.

## Design Constraints

- Off-target stack: E3a/b plus **E3c variant-aware layer** (CRISPRitz VCF search;
  CRISPRme population panels) — clinically load-bearing: CRISPRme found a PAM-creating
  MAF-4.5% allele driving the top off-target for a clinical BCL11A guide; CHANGE-seq
  found SNVs affect ~15.2% of off-target sites.
- Assay hierarchy stated with every deliverable: in-silico → in-vitro (CHANGE-seq class)
  → cell-based (GUIDE-seq class); in-silico ≈77% recall @ top-500 (Kaufmann 2026).
- **No therapeutic guide sequence is public** (exa-cel "SPY101" redacted (b)(4) in FDA
  SBRA; NTLA-2001 patent-bound; VERVE-101 unverified) — anchors are strategy-level;
  never fabricate or adopt circulating "therapeutic guide sequences".
- Delivery prediction does not exist — stated, never approximated.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm application=therapeutic; specificity-heavy defaults. | Confirmed hashed brief. |
| 2. Verify reference | Transcript + coordinates; population-VCF panel declaration. | Verified reference + panel manifest. |
| 3–4. Enumerate + E1 | All windows; validation. | `candidate_pool.csv` + pass/reject. |
| 5. E2 on-target | ≥2 endpoints; expression system declared. | Separate scores. |
| 6. E3a–c off-target | Full stack incl. variant-aware layer; caps disclosed. | Counts + scores + allele nominations. |
| 7. E4 outcome | Lindel indel profile. | Probabilities. |
| 8. Gates (R1) | DRAFT gates ∪ brief vetoes. | Survivor set + decision log. |
| 9. Rank + deliver | Panel with per-nomination assay-hierarchy recommendation. | Typed bundle. |

## Expected Output

Ranked panel + off-target nomination table with variant annotations + assay-hierarchy
next-evidence recommendation per candidate; provenance; `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

No safety or therapeutic claims from computational outputs; variant-aware layer mandatory
here; licenses bind (CRISOT CC BY-NC — research-internal only).

## Important Instructions

Published anchors: CHANGE-seq (110 guides / 201,934 sites), Kaufmann-2026 14-tool
independent benchmark (recall ≈77% @ top-500; weak score↔indel correlation — in-silico
tools prioritize, never replace experimental assessment), exa-cel BLA off-target record,
CRISPRme BCL11A analysis. Run slots NOT_EXECUTED.
