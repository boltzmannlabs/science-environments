# Task: crispr_epigenome_editing_008

**Task family:** application-aware CRISPR design — **epigenome editing (CRISPRoff/on
durable silencing)**. **Status:** specification phase; runtime pending; published
anchors only.

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

The three verified rules (Nuñez 2021 tiling, ~116k sgRNAs, 520 genes):
1. **Wide targeting window** −500..+500 bp around TSS (far wider than CRISPRi's ~75 bp).
2. **Nucleosome-depleted regions** — activity tracks NDR placement; nucleosome-dense
   promoters restrict activity.
3. **Functional-CpG density, CGI annotation NOT required** — 300+ non-CGI genes silenced
   via low-density functional CpGs; fully CpG-devoid promoters fail.
Multiple guides per gene improve silencing — panel size defaults reflect this.

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

Published anchors: Nuñez 2021 (*Cell* 184:2503) — GSE168012 (RNA-seq/ChIP/WGBS), tiling
+ 21,378-element genome-wide screen; the paper designed its own guides with CRISPRi
rules (proxy lineage disclosed). Gap: no dedicated designer tool (negative result
recorded). Run slots NOT_EXECUTED.
