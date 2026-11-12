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

*Universal contract from [task 001](001_crispr_design_general.md) applies in full — with
the review-only scope gate as the first constraint.* Task-specific layers:

**Scope gate (binding, first)**
- **Pathogen-targeting sequence design is review-only** — viral/bacterial isolate
  targets produce no generation and no evaluation; the refusal is logged with this task
  as reference; contrived/synthetic targets and non-pathogen allele-detection assays
  remain runnable; tool presence (EasyDesign/PrimedSherlock) is not authorization.

**Assay architecture constraints**
- Cas12a detection is TTTV-PAM-dependent: enumeration is PAM-constrained on the target
  (collateral trans-cleavage of the reporter drives signal); crRNA–target duplex
  constraints follow Cas12a geometry (orientation mapping shown, not assumed).
- Primer–crRNA co-design: RPA/LAMP isothermal primers must flank the crRNA site without
  competing secondary structure overlap; primer compatibility is a veto-class constraint
  (an unscreenable genomic neighborhood blocks the candidate, not just down-ranks it);
  amplicon length context recorded per assay design.

**Discrimination constraints (allele/SNP detection)**
- For allele-discrimination assays, the mismatch position at the crRNA–target duplex is
  the design lever: central/discriminating positions are preferred and the mechanism
  (bubble position → cleavage-rate difference) is stated per design; both alleles are
  enumerated and the discrimination margin is reported — never claimed as proven
  specificity (assay-level experimental endpoint).

**Model & evidence constraints**
- Sensitivity endpoint: EasyDesign CNN (ρ 0.812 on 11,496 validated cases; 4 held-out
  pathogens) — the **only large ML pair in diagnostics**; no independent benchmark
  exists (disclosed per deliverable); specificity of the screen is bounded by the
  declared reference context (supplied background genomes/transcripts — never implicitly
  "everything").
- Limit-of-detection, false-positive rate, and clinical performance are assay-level
  experimental endpoints — never claimed computationally.

**Safety & dual-use**
- No design that increases detectable virulence/transmissibility markers; no clinical
  diagnostic claims; review gate escalation is documented rather than worked around.

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
