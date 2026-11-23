# Task: crispr_epigenome_editing_008

**Task family:** application-aware CRISPR design — **epigenome editing (CRISPRoff/on
durable silencing)**. **Status:** In Progress; protocol v0.1 (DRAFT gates). Executed
evidence: blocked on a matched epigenetic endpoint — PCSK9 enumeration/TSS/CpG context
exists, but no durable-silencing performance has been evaluated (labels and matched
predictor adapter missing). Start from the [general task](001_crispr_design_general.md)
for mode routing.

## Description

Guide design for CRISPRoff-class durable methylation-based silencing under the three
tiling-derived design rules; CRISPRon (TET-demethylase) reversal context annotated.
**No dedicated CRISPRoff design tool exists** — the design layer is a rules overlay on
spacer enumeration (CRISPick CRISPRi mode is the practical proxy; the source paper
itself used CRISPRi rules) with the differences below made explicit.

## Target

Resolved per request ([008 example brief](../config/008_epigenome-editing.request.example.json) — PCSK9 silencing, illustrative only).

- **Default vetoes:** off_target_exact_match.
- **Default weight emphasis:** context .35 (rules + chromatin) / on_target .25 / specificity .25 / outcome_quality .15.

## Design Constraints

*Universal contract from [task 001](001_crispr_design_general.md) applies in full.* Modality-specific layers — the three verified rules (Nuñez 2021 tiling, ~116k sgRNAs, 520 genes) are the design core:

**Rule 1 — wide targeting window**
- Active sgRNAs spread **−500..+500 bp around the TSS** (occasionally ~2 kb upstream for
  some loci) — far wider than CRISPRi's ~75-bp downstream window; battery enumerates the
  full ±500-bp window with per-guide distance-from-TSS recorded; guides beyond the
  window carry an out-of-window flag.

**Rule 2 — nucleosome-depleted regions (NDR)**
- Most active sgRNAs sit in NDRs (activity tracks MNase occupancy in periodic pattern);
  nucleosome-dense promoters (RAB11A-class) restrict activity — NDR annotation (MNase/
  DNase proxy, source declared) is a first-class context column; missing chromatin data
  is NOT_RUN(context-absent), never imputed.

**Rule 3 — functional CpG density (CGI annotation NOT required)**
- CpG-density profile of the targeted promoter is recorded; CGI annotation is explicitly
  **not** a filter — 300+ non-CGI genes were durably silenced via low-density functional
  CpGs (DYNC2LI1/LAMP2/VPS25 validated); fully CpG-devoid promoters (CALD1-class) fail —
  candidates in CpG-devoid promoters are flagged likely-inert with the rule citation.

**Panel & mechanism constraints**
- **Multiple guides per gene improve silencing** — panel-size defaults are larger than
  single-guide tasks; combination proposals (2–4 guides spanning the window + NDR +
  CpG-dense sites) are part of the deliverable.
- Mechanism is methylation-based durable repression by dCas9-DNMT fusion (no cutting):
  E4 indel endpoints are NOT_RUN by definition; CRISPRon/TET reversal context is
  annotated as the reversibility dimension (experimental endpoint).
- Proxy-activity disclosure: **no dedicated CRISPRoff designer exists** — CRISPick
  CRISPRi-class activity is the declared proxy with the CRISPRi≠CRISPRoff caveat on
  every score column (the source paper itself used CRISPRi rules).
- Silencing durability and methylation maintenance are experimental endpoints — never
  predicted; no methylation model exists and none is approximated.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm CRISPRoff objective; TSS + CpG context resolution. | Confirmed hashed brief. |
| 2. Verify reference | TSS annotation + promoter CpG density profile. | Verified TSS/CpG record. |
| 3. Enumerate | Spacers across the wide window (both strands). | `candidate_pool.csv`. |
| 4. Rules overlay | Window + NDR (MNase/DNase proxy where available) + functional-CpG scoring. | Rule scores + flags. |
| 5. Proxy activity | CRISPick-CRISPRi-class activity with CRISPRi≠CRISPRoff caveat disclosed. | Proxy scores. |
| 6. E3 off-target + E6 | Spacer stack; physico-chem. | Off-target + flags. |
| 7. Gates + rank | Rules-weighted ranking; multi-guide panel. | Ranked panel. |
| 8. Deliver | Panel + rule evidence + provenance. | Typed bundle. |

## Expected Output

Ranked multi-guide panel with per-rule evidence, proxy-activity caveat, off-target
record, provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Silencing durability is an experimental endpoint — never claimed computationally;
methylation predictions are not made (no model exists).

## Important Instructions

- **Published anchors:** Nuñez 2021 (*Cell* 184:2503) — GSE168012 (RNA-seq/ChIP/WGBS),
  tiling + 21,378-element genome-wide screen; the paper designed its own guides with
  CRISPRi rules (proxy lineage disclosed). Gap: no dedicated designer tool (negative
  result recorded).
- **Executed evidence (local):** blocked — functional methylation/durable-repression
  labels and a matched predictor adapter are missing; GSE168012 metadata retrieval
  failed; CpG count is not methylation efficacy ([Run-3 blocker record,
  execution_history](../execution_history/before_completed_only_20261112T061830Z/benchmark/008_epigenome-editing/Run-3_2026-11-12/README.md)).
  Result record [Run-2](../results/008_epigenome_editing/Run-2_2026-11-12/REPORT.md).
  Executed metrics from other modalities in the shared campaign do not substitute for
  this endpoint.
- **Gaps:** the matched epigenetic endpoint remains unexecuted — evaluation slots stay
  `NOT_EXECUTED` until labels and an adapter exist.
