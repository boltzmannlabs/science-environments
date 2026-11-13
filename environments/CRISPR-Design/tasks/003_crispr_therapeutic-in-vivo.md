# Task: crispr_therapeutic_in_vivo_003

**Task family:** application-aware CRISPR design — **therapeutic in-vivo editing
(systemic/LNP context)**. **Status:** In Progress; protocol v0.1 (DRAFT gates). Executed
evidence: specificity component only (CFD2016 assay-matched benchmark — endpoint-level;
see the [completed-only registry](../benchmark/BENCHMARK_RUNS.md)); no delivery, in-vivo
efficacy or therapeutic-safety validation. Core battery shared; the specificity stack is
elevated here. Start from the [general task](001_crispr_design_general.md) for mode routing.

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

*Universal contract from [task 001](001_crispr_design_general.md) applies in full; the
specificity constraints are elevated here.* Task-specific layers:

**Specificity stack (regulator-grade)**
- Full stack mandatory: E3a enumeration + E3b pair/aggregate scores + **E3c variant-aware
  layer** (CRISPRitz VCF search; CRISPRme population panels). Rationale is
  clinically load-bearing: CRISPRme found a PAM-creating MAF-4.5% allele driving the top
  off-target for a clinical BCL11A-enhancer guide; CHANGE-seq found human SNVs affect
  ~15.2% of analyzed off-target sites. Reference-genome-only search is insufficient and
  is flagged as such, never silently accepted.
- Population panel declaration: which VCF panels (1000G-class) and which ancestries are
  in scope is part of the confirmed brief — panel choice is surfaced, not defaulted.
- Guides with any exonic near-match (≤2 mm) in coding/regulatory annotated regions are
  vetoed by default in this profile regardless of score.

**Assay hierarchy & claims discipline**
- Every deliverable states the hierarchy: in-silico → in-vitro (CHANGE-seq class) →
  cell-based (GUIDE-seq class) — and that in-silico ≈77% recall @ top-500 with weak
  score↔indel correlation (Kaufmann 2026). Computational output nominates candidates for
  experimental assessment; it never clears them.
- No off-target-safety, genotoxicity, or therapeutic-qualification claims of any kind;
  "clean" is prohibited vocabulary for in-silico results.

**Anchor honesty (therapeutic context)**
- **No therapeutic guide sequence is public** (exa-cel "SPY101" redacted (b)(4) in FDA
  SBRA; NTLA-2001 patent-bound; VERVE-101 unverified in open text) — benchmark anchors
  are target identity + edit mechanism + off-target-assay strategy; circulating
  "therapeutic guide sequences" are treated UNVERIFIED and never adopted.

**Delivery & biology context**
- Delivery prediction (LNP/GalNAc tropism, exposure) does not exist for sequence-level
  design — stated, never approximated; tissue-of-action expression context is annotation
  only. Editing in delivery-relevant tissue types outside model training contexts is
  flagged extrapolation.

**Prioritization posture**
- Default weight emphasis specificity-heavy (.55); panel sized for downstream
  experimental nomination, not breadth; every ranked candidate carries its
  assay-hierarchy next-evidence recommendation.

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

- **Published anchors:** CHANGE-seq (110 guides / 201,934 sites), Kaufmann-2026 14-tool
  independent benchmark (recall ≈77% @ top-500; weak score↔indel correlation — in-silico
  tools prioritize, never replace experimental assessment), exa-cel BLA off-target record,
  CRISPRme BCL11A analysis.
- **Executed evidence (local):** [CFD2016 experimentally assayed
  specificity](../benchmark/003_CFD2016/Run-4_2026-11-12/REPORT.md) — WT SpCas9
  assay-matched CFD on 1,684 assayed sites (108 positives, 1,576 negatives, 9 guides).
  Result record [Run-2](../results/003_therapeutic_in_vivo_editing/Run-2_2026-11-12/REPORT.md);
  historical Run-2/Run-3 comparisons in [execution_history](../execution_history/before_completed_only_20261112T061830Z/benchmark/003_therapeutic-in-vivo/Run-3_2026-11-12/README.md).
- **Gaps:** no delivery, in-vivo efficacy, patient-haplotype, therapeutic-safety or
  clinical detection-limit validation; the variant-aware layer (E3c) remains uninstalled;
  unexecuted evaluation slots stay `NOT_EXECUTED`.
