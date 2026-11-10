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

- Representation: 20–30-nt crRNA spacers, RNA alphabet; transcript (not genome)
  reference; direct-repeat nomenclature per Cas13 system declared at intake.
- Mismatch-intolerance region nt 15–21 (Cas13design-2020 finding) drives placement away
  from near-match positions elsewhere in the transcriptome.
- Models: Cas13design (2020) lineage and **TIGER (2023, current reference — mismatch/
  indel-aware CNN)**; TIGER's G-U wobble-tolerance finding carried into off-target
  interpretation.
- Transcriptome screen: Bowtie2 vs GENCODE transcriptome (local, siRNA-environment
  evidence base) with seed-region mismatch weighting; genome off-target stack NOT run
  (no DNA cutting) — stated.
- Structure/accessibility: RNAplfold/RNAduplex conventions from the siRNA environment
  (W/L/u declared) as context dimensions.

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
