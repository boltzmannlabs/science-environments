# Task: crispr_library_screen_design_011

**Task family:** application-aware CRISPR design — **pooled library / screen design**.
**Status:** specification phase; runtime pending; published anchors only.

## Description

Multi-guide-per-gene library design across a declared gene set: per-guide quality
(on-target + off-target + frameshift), multi-targeting avoidance, seed/copy-number
confound control, and compact-library sizing (score-based 3-guide libraries match or beat
larger ones — Lukasiak 2024).

## Target

Resolved per request — gene list supplied at intake
([011 example brief](../config/011_library.request.example.json) illustrative only).

- **Default vetoes:** off_target_exact_match, poly_t_termination_risk.
- **Default weight emphasis:** on_target .40 / specificity .35 / outcome_quality .15 / context .10.

## Design Constraints

- Enumeration at genome scale: Bowtie-1 ungapped (verified local) for off-target counts;
  FlashFry-class for large sets (fastest enumeration; no VCF-aware search — disclosed);
  CRISPRitz only when variant-aware screening is declared.
- Multi-targeting avoidance: guides with additional perfect/near-perfect matches
  genome-wide excluded (Kuscu-2019 confound); multi-cut toxicity (Álvarez 2022,
  TP53-dependent) and off-target-mediated depletion (Pérez 2021 CSC) documented as
  screen-analysis confounds.
- Calibration baseline: RS2/RS3 via CRISPick-class rules (Avana/Brunello lineage);
  guide-quality targets consistent with RS3 tiling validation (84,609-sgRNA library).
- Non-targeting controls and safe-harbor/positive controls included per screen-design
  convention when requested.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm gene list, screen type (KO/CRISPRi), library size target. | Confirmed hashed brief. |
| 2. Verify references | All genes resolved (unresolved genes reported, never skipped silently). | Resolution record. |
| 3. Enumerate | Genome-scale spacer enumeration per gene. | Pooled `candidate_pool.csv`. |
| 4. E2/E3/E4 | On-target endpoints; off-target counts incl. multi-targeting flags; frameshift. | Per-guide evidence. |
| 5. Confound flags | Multi-targeting, seed repeats, copy-number context where annotation available. | Flag set. |
| 6. Library assembly | Per-gene guide selection under sizing target; controls. | Library table. |
| 7. Deliver | Library + per-guide evidence + provenance. | Typed bundle. |

## Expected Output

Library table (per-gene guides with full per-dimension evidence), confound flags,
controls, provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Screen readout analysis (MAGeCK-class) is out of scope for design; library quality claims
stay computational.

## Important Instructions

Published anchors: RS3 tiling validation (DeWeirdt 2022; 84,609 sgRNAs), Lukasiak 2024
(VBC vs RS3 vs 6 public libraries; compact-library efficiency), Kuscu 2019 / Pérez 2021 /
Álvarez 2022 (confound literature), GuideScan2 (multi-locus-binding exclusion — citation
UNVERIFIED, curated-only). Run slots NOT_EXECUTED.
