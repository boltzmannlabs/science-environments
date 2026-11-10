# Task: crispr_diagnostics_010

**Task family:** application-aware CRISPR design — **CRISPR diagnostics (Cas12/Cas13
biosensors, SHERLOCK/DETECTR class)**. **Status:** specification phase; runtime pending;
**pathogen-targeting sequence design is REVIEW-ONLY** (mirrors the siRNA environment's
antiviral gate).

## Description

crRNA design for Cas12a-based detection assays on **contrived, synthetic, or non-pathogen
targets only without review**: sensitivity endpoints (EasyDesign-class), variant
discrimination for allele detection, primer–crRNA compatibility (RPA/LAMP context per
PrimedSherlock conventions). Pathogen-targeting requests (viral/bacterial isolate
sequences) enter review-only mode: no generation, no evaluation — the gate is documented
here and tool presence is not authorization.

## Target

Resolved per request; contrived/synthetic sequence supplied by the user
([010 example brief](../config/010_diagnostics.request.example.json) deliberately uses a
supplied synthetic control locus).

- **Default vetoes:** gc_out_of_band.
- **Default weight emphasis:** on_target .45 / specificity .30 / context .15 / outcome_quality .10.

## Design Constraints

- Cas12a crRNA (TTTV PAM-dependent) + isothermal primer compatibility co-design; RPA
  primer design context integrated (EasyDesign server convention).
- Sensitivity prediction: EasyDesign CNN (ρ 0.812 on 11,496 validated cases; 4 held-out
  pathogens) — the only large ML pair; no independent benchmark exists (disclosed).
- Variant/allele discrimination assays: mismatch-position sensitivity at the crRNA–target
  duplex evaluated from model + thermodynamic context; SNP-allele detection designs state
  discrimination mechanism explicitly.
- Diagnostics sensitivity claims are assay-level experimental endpoints — never claimed
  computationally.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Scope gate | Target classification: contrived/synthetic/allele vs pathogen. Pathogen → review-only stop with explanation. | Routing decision logged. |
| 2. Route + brief | Confirm detection context (target sequence supplied; assay type). | Confirmed hashed brief. |
| 3. Enumerate | PAM-adjacent crRNA windows on the supplied sequence. | `candidate_pool.csv`. |
| 4. Sensitivity scoring | EasyDesign-class endpoint (model identity disclosed). | Scores. |
| 5. Specificity | Near-match screen against the declared reference context (e.g., human genome/background organisms as supplied). | Hit record. |
| 6. Primer compatibility | RPA/LAMP primer co-design context (PrimedSherlock conventions). | Compatibility record. |
| 7. Gates + rank | Sensitivity-weighted ranking; stability. | Ranked panel. |
| 8. Deliver | Panel + assay-context evidence + provenance. | Typed bundle. |

## Expected Output

Ranked crRNA panel with sensitivity scores, specificity record, primer compatibility,
provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Review-only scope for pathogens is binding; no assay performance claims (limit of
detection, specificity) from in-silico output alone.

## Important Instructions

Published anchors: EasyDesign (Huang 2024, *iMeta*: ρ 0.812, n=11,496; WS
crispr.zhejianglab.com), PrimedSherlock (Mann 2022, *BMC Bioinform*: rule-based design,
Flavivirus validation lineage). Gap: no independent diagnostics benchmark. Run slots
NOT_EXECUTED.
