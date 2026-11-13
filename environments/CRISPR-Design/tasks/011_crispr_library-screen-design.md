# Task: crispr_library_screen_design_011

**Task family:** application-aware CRISPR design — **pooled library / screen design**.
**Status:** In Progress; protocol v0.1 (DRAFT gates). Executed evidence: shared guide
metrics, not screen validation (RS3/CRISPRon guide-level benchmarks + within-gene
rank-loss evidence; no library-level essentiality/enrichment/power validation; see the
[completed-only registry](../benchmark/BENCHMARK_RUNS.md)). Start from the
[general task](001_crispr_design_general.md) for mode routing.

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

*Universal contract from [task 001](001_crispr_design_general.md) applies in full — at
genome scale.* Task-specific layers:

**Enumeration-at-scale constraints**
- Genome-scale enumeration across the declared gene set: Bowtie-1 ungapped (verified
  local) for off-target counts; FlashFry-class for large sets (fastest enumeration; **no
  VCF-aware search — disclosed cap**); CRISPRitz only when variant-aware screening is
  declared; runtime budgets declared before enumeration (screen-budget discipline).
- All genes resolve or are reported unresolved — never silently skipped; per-gene
  candidate counts recorded (genes with no passing guide are explicit output).

**Multi-targeting & confound constraints (screen validity)**
- Guides with additional perfect/near-perfect matches genome-wide are excluded
  (multi-targeting confound — Kuscu 2019); seed-level repeats across the library are
  capped (seed-distinctness constraint) to avoid correlated depletion artifacts.
- Documented screen confounds carried as flags: multi-cut toxicity (Álvarez 2022,
  TP53-dependent) and off-target-mediated gRNA depletion (Pérez 2021 CSC correction);
  copy-number-amplified loci flagged where annotation is available (false-positive
  dropouts); essential-gene lists used for positive-control placement are
  source-cited.

**Sizing & composition constraints**
- Compact-library evidence governs sizing: score-based 3-guide-per-gene libraries match
  or beat larger unscored libraries (Lukasiak 2024) — panel size is a declared
  brief constraint, default 3–6 guides/gene depending on screen type.
- Controls are part of the library contract: non-targeting controls matched for GC and
  dinucleotide content; safe-harbor/essential-gene positive controls included on
  request; CRISPRi/a libraries inherit task 007 window constraints.

**Calibration & ranking constraints**
- Guide-quality baseline: RS2/RS3 via CRISPick-class rules (Avana/Brunello lineage);
  quality targets consistent with the RS3 tiling validation (84,609-sgRNA library);
  ranking at library level balances per-guide quality with cohort diversity
  (site-distinctness across the library, not just within gene).

**Boundary**
- Screen readout analysis (MAGeCK-class statistics) is downstream and out of scope —
  the deliverable is the library + per-guide evidence + confound flags.

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

- **Published anchors:** RS3 tiling validation (DeWeirdt 2022; 84,609 sgRNAs), Lukasiak
  2024 (VBC vs RS3 vs 6 public libraries; compact-library efficiency), Kuscu 2019 /
  Pérez 2021 / Álvarez 2022 (confound literature), GuideScan2 (multi-locus-binding
  exclusion — citation UNVERIFIED, curated-only).
- **Executed evidence (local):** [RS3 Sequence held-out
  activity](../benchmark/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) ·
  [CRISPRon v1 external activity](../benchmark/002_CRISPRon/Run-4_2026-11-12/REPORT.md) —
  shared Cas9 guide-level and within-gene rank-loss evidence; supplemental
  explicitly-defined nDCG retained ([Run-3 comparison, execution_history](../execution_history/before_completed_only_20261112T061830Z/benchmark/011_library-screen-design/Run-3_2026-11-12/README.md)).
  Result record [Run-2](../results/011_library_screen_design/Run-2_2026-11-12/REPORT.md).
- **Gaps:** no library-level essential-gene detection, enrichment, screen-power or
  target-diversity validation; shared guides are not independent task benchmarks;
  unexecuted evaluation slots stay `NOT_EXECUTED`.
