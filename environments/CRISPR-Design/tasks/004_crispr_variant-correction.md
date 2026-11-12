# Task: crispr_variant_correction_004

**Task family:** application-aware CRISPR design — **genetic-disease variant correction &
precision repair (modality router: BE / PE / HDR)**. **Status:** In Progress; protocol
v0.1 (DRAFT gates). Executed evidence: matched model-component evaluations (BE-Hive BE4,
PRIDICT2.0 grouped OOF, DeepPrime fixed test — endpoint-level; see the
[completed-only registry](../benchmark/BENCHMARK_RUNS.md)); no allele-specific repair or
HDR validation. Start from the [general task](001_crispr_design_general.md) for mode routing.

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

*Universal contract from [task 001](001_crispr_design_general.md) applies in full.* Task-specific layers:

**Variant verification (hard gate)**
- The variant is reference-verified (ClinVar/dbSNP + VEP; coordinate + ref/alt alleles
  against GRCh38.p14) **before any design step**; an unverifiable variant blocks the run
  (`NEEDS_INPUT`), never a best-effort guess. Haplotype/phase context surfaced where the
  user supplies it.

**Modality router constraints (decision recorded with reasons)**
- Edit type + distance decide the modality: A→G or C→T reachable inside an editor's
  window with acceptable bystanders → base editing (task 005); other SNVs / small indels /
  insertions ≤3 bp standard (≤40 bp with ePRIDICT-class context) → prime editing
  (task 006); larger constructs / tags → HDR (below). Router reasons and rejected
  alternatives are part of the deliverable.

**Allele discrimination (WT-sparing)**
- PAM/spacer discrimination between mutant and WT allele is checked at the sequence level:
  the clean case is a variant-created PAM or variant-disrupted PAM; spacer-position
  mismatch discrimination scored with CFD/Elevation on **both** alleles (position +
  type-dependent; mismatch-position sensitivity is the design lever).
- Discrimination is reported as a margin (mutant vs WT predicted activity), never as a
  guarantee of allele selectivity — experimental confirmation is the next-evidence step.
- Therapeutic-context correction requests inherit task 003 constraints (variant-aware
  off-target mandatory).

**HDR path (rules-bounded)**
- Donor design uses verified rules only: Richardson-2016 asymmetric ssODN — donor
  complementary to the **non-target strand**; commonly cited arm lengths (~36-nt
  PAM-distal / ~91-nt PAM-proximal) are per-paper-figure conventions, stated as such.
- 3′ homology-arm composition is the dominant known predictor (CUNE, n=30 — thin;
  disclosed as weak evidence); **no large ML HDR-efficiency predictor exists** — stated,
  never approximated; silent/blocking mutations that would recode the target site
  (PAM-disrupting donor edits) are offered where compatible with the repair design.
- HDR efficiency is never predicted beyond rules + context; the deliverable states this
  gap explicitly.

**Outcome semantics**
- Intended-edit efficiency and purity (intended vs unintended outcomes) are separate
  endpoints; a high-efficiency guide with poor purity is reported as such, never blended
  into one "correction score"; bystander context inherited from tasks 005/006 on hand-off.

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

- **Published anchors:** BE-Hive (3,388 pathogenic SNVs correctable at ≥90% precision),
  PRIDICT1 (13,349 pathogenic mutations; unintended-edit ρ 0.78, not purity); PRIDICT2.0
  is the later matched-cell model, CUNE (n=30 — thin). No neutral BE/PE benchmark exists —
  cross-tool claims are self-reported.
- **Executed evidence (local):** [BE-Hive BE4 any-edit
  efficiency](../benchmark/004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) ·
  [PRIDICT2.0 published grouped OOF outcomes](../benchmark/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) ·
  [DeepPrime base fixed test](../benchmark/006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) —
  PRIDICT2 grouped-OOF and DeepPrime HEK293T/PE2 fixed-test components; BE4 any-edit
  efficiency separately. Result record [Run-2](../results/004_variant_correction_precision_repair/Run-2_2026-11-12/REPORT.md);
  historical Run-2/Run-3 comparisons in [execution_history](../execution_history/before_completed_only_20261112T061830Z/benchmark/004_variant-correction/Run-3_2026-11-12/README.md).
- **Gaps:** not allele-specific HBB repair or HDR validation; BE4 labels cannot validate
  BE4max intended purity; unexecuted evaluation slots stay `NOT_EXECUTED`.
