# Task: crispr_regulation_007

**Task family:** application-aware CRISPR design — **CRISPRi / CRISPRa gene regulation
(dCas9)**. **Status:** specification phase; runtime pending; published anchors only.

## Description

Non-cutting dCas9-KRAB repression (CRISPRi) or dCas9-activator (CRISPRa) guide design:
TSS-window placement, chromatin context, standard on-target/specificity battery for the
spacer. CRISPRi optimal guides sit in a narrow (~75-bp) nucleosome-depleted window just
downstream of the TSS; CRISPRa windows differ by system ( Calabrese/SAM lineage) —
declared per run.

## Target

Resolved per request ([007 example brief](../config/007_crispr-regulation.request.example.json) — MYC CRISPRi, illustrative only).

- **Default vetoes:** off_target_exact_match.
- **Default weight emphasis:** on_target .35 / specificity .25 / context .25 (TSS/chromatin) / outcome_quality .15.
- **Window:** CRISPRi [−75, +200] bp vs TSS (DRAFT gate, Horlbeck-2016 convention);
  CRISPRa window declared per activator system.

## Design Constraints

*Universal contract from [task 001](001_crispr_design_general.md) applies in full.* Modality-specific layers:

**Targeting-window constraints**
- CRISPRi (dCas9-KRAB): optimal guides sit in a narrow (~75-bp) nucleosome-depleted
  window just **downstream of the TSS** (Horlbeck 2016); battery window DRAFT
  [−75, +200] bp vs TSS; guides outside the window are enumerated but carry an
  out-of-window flag rather than silent exclusion.
- CRISPRa: window differs by activator system (Calabrese/SAM lineage) — the activator
  system is declared per run and its window recorded; upstream-of-TSS placement
  dominates CRISPRa by convention (system-scoped, disclosed).
- All major TSSs of the resolved transcript set are surfaced; a multi-TSS gene gets
  per-TSS coverage assessment, never a single-TSS assumption.

**Model constraints (the gap is load-bearing)**
- Activity rules are Horlbeck-2016-derived (chromatin/MNase + position + sequence) via
  CRISPick-class calibration; **no dedicated CRISPRi/a DL model 2024–26 was found** —
  the gap is stated per deliverable, never approximated with nuclease-activity models.
- Nuclease-trained on-target endpoints may appear only as clearly-labeled comparator
  columns (proxy context), never as the CRISPRi/a activity estimate.
- Chromatin features are K562-calibrated — other cell types carry an extrapolation
  flag; dCas9 binding (not cutting) is the mechanism, so E4 indel endpoints are NOT_RUN
  for this task by definition.

**Specificity constraints**
- Binding off-targets still matter for dCas9: the full E3 spacer stack applies;
  guides with additional high-fidelity binding sites in promoters/enhancers of
  expressed genes are flagged (mis-targeted repression risk).
- Seed-region near-matches in accessible chromatin are the priority screen
  (K562-calibrated caveat where chromatin data is borrowed).

**Endpoint semantics**
- Repression/activation outcomes are experimental endpoints (mRNA, protein) — distinct
  from each other and from activity scores; partial knockdown ≠ knockout — graded
  expectation recorded with the panel (titrating designs via attenuated guides are a
  documented extension, Jost-2020 lineage, marked out-of-scope for battery v0.1).
- Essentiality-screen use inherits library confound flags from task 011.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm CRISPRi/CRISPRa + activator system; TSS resolution. | Confirmed hashed brief. |
| 2. Verify reference | TSS annotation + isoform TSS set (all major TSSs surfaced). | Verified TSS record. |
| 3. Enumerate | Spacers in the declared window(s). | `candidate_pool.csv`. |
| 4. Activity scoring | Horlbeck-rule activity + ≥1 independent nuclease-trained on-target endpoint as comparator (disclosed as proxy). | Scores + caveats. |
| 5. E3 off-target | Full spacer stack (binding off-targets still matter for dCas9). | Off-target record. |
| 6. Gates + rank | Window-scoped ranking; stability. | Ranked panel. |
| 7. Deliver | Panel + TSS/window evidence + provenance. | Typed bundle. |

## Expected Output

Ranked guides with TSS-window placement, activity evidence, off-target record,
provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

mRNA knockdown and protein outcomes are distinct endpoints; CRISPRi/a activity ≠ nuclease
activity — proxy use disclosed per column.

## Important Instructions

Published anchors: Horlbeck 2016 (*eLife*; K562 tiling + genome-wide γ-scores; compact
5-guide libraries detect >90% essential genes), Sanson 2018 (Dolcetto/Calabrese library
benchmarks via CRISPick). Gap: no 2024–26 dedicated DL model found (negative result
recorded). Run slots NOT_EXECUTED.
