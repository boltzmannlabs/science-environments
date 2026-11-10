# Task: crispr_rna_targeting_cas13_009

**Task family:** application-aware CRISPR design — **RNA targeting (Cas13)**.
**Status:** specification phase; runtime pending; published anchors only.

## Description

Cas13d crRNA design for transcript knockdown without DNA cutting: spacer selection
respecting the nt 15–21 mismatch-intolerance region, transcript accessibility context
(reusing the siRNA environment's RNA structure battery), and transcriptome off-target
screening. Collateral-activity caveat disclosed (Cas13 trans-cleavage depends on system/
assay — flagged, never predicted).

## Target

Resolved per request ([009 example brief](../config/009_cas13.request.example.json) — MALAT1, illustrative only).

- **Default vetoes:** gc_out_of_band.
- **Default weight emphasis:** on_target .40 / specificity .35 / context .20 / outcome_quality .05.

## Design Constraints

*Universal contract from [task 001](001_crispr_design_general.md) applies in full — with the DNA-specific layers replaced by RNA-targeting equivalents.* Modality-specific layers:

**Representation & reference constraints**
- 20–30-nt crRNA spacers, RNA alphabet (ACGU); the reference is the **transcript**, not
  the genome (versioned GENCODE transcript; both-strand considerations do not apply —
  target orientation is the transcript sense); direct-repeat nomenclature per Cas13
  system declared at intake; system-specific flanking-site (PFS) preferences are
  system-scoped and declared at intake (commonly-reported PFS patterns were **not
  re-verified** in the 2026-11-10 sweep — none are assumed by default).

**Placement constraints (Cas13-specific determinants)**
- Mismatch-intolerance concentrates at spacer **nt 15–21** (Cas13design-2020 finding):
  (a) within-guide — positions 15–21 are treated as the sensitive region for
  near-match avoidance; (b) endogenous mismatches between guide and target at those
  positions depress activity — placement avoids guides whose target carries known SNPs
  at 15–21.
- Transcript accessibility context (RNAplfold/RNAduplex conventions, W/L/u declared —
  siRNA-environment evidence base) is a ranking context column, never an efficacy
  promise.

**Model constraints**
- Endpoints from Cas13design (2020) lineage and **TIGER (2023, current reference —
  mismatch/indel-aware CNN)**; TIGER's G-U wobble-tolerance finding is carried into
  off-target interpretation (wobble mismatches are more tolerated → near-match screens
  must include G-U pairs); the Arc Institute 2025 tool is curated-only (UNVERIFIED).
- TIGER head-to-head deltas vs Cas13design are paywalled-UNVERIFIED — both endpoints
  run as separate columns where available.

**Specificity constraints (transcriptome-scale)**
- Genome off-target stack is NOT_RUN by definition (no DNA cutting) — stated, not
  omitted silently; instead: transcriptome screen vs declared reference (Bowtie2,
  GENCODE local) with seed-region mismatch weighting and nt 15–21 protection.
- Guides with ≤1-mismatch near-matches in abundant off-target transcripts are vetoed
  (default); knockdown of unintended transcripts is the primary hazard model.
- **Collateral activity** (trans-cleavage upon target recognition — system/assay
  dependent) is a disclosed caveat on every deliverable; no collateral predictor exists
  and none is approximated.

**Scope**
- Human transcripts by default; pathogen-transcript targeting routes to task 010 gates
  (review-only); Cas13 systems beyond Cas13d/Cas13a carry a system-declaration
  requirement at intake.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm Cas13 system + transcript target. | Confirmed hashed brief. |
| 2. Verify reference | Versioned transcript (RNA). | Verified `reference.fa`. |
| 3. Enumerate | All candidate spacers across the transcript. | `candidate_pool.csv`. |
| 4. Activity scoring | Cas13design/TIGER-class endpoints (model identity disclosed). | Scores. |
| 5. Transcriptome off-target | ≤1–2 mismatch screen, seed-region weighting, nt 15–21 protection. | Hit counts. |
| 6. Structure context | Accessibility endpoints (method + parameters declared). | Context values. |
| 7. Gates + rank | Weighted ranking; stability; site-distinct panel. | Ranked panel. |
| 8. Deliver | Panel + evidence + collateral caveat + provenance. | Typed bundle. |

## Expected Output

Ranked crRNA panel with activity scores, transcriptome off-target record, accessibility
context, provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Knockdown is an experimental endpoint; collateral activity flagged, never predicted;
human transcripts only by default (pathogen-transcript targeting routes to task 010
gates).

## Important Instructions

Published anchors: Cas13design (Wessels 2020, *NBT*: 24,460 guides; validated 3,979/48
genes; WS cas13design.nygenome.org) and TIGER (Wessels & Stirn 2023, *NBT*: ~200,000
RfxCas13d guides; current reference). Arc Institute 2025 Cas13d tool is emerging —
details UNVERIFIED, curated-only. Run slots NOT_EXECUTED.
