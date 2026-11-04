# Task: gene_silencing_metabolic-liver-galnac_005

**Task family:** application-aware siRNA design — **Metabolic / liver siRNA design (GalNAc context)**. **Status:** In Progress; protocol v1.2, frozen gates, computational scope only. Shares the environment battery, ranking contract and gates with all application tasks; only the application-specific requirements differ. Start from the [general task](gene_silencing_rna_001.md) for mode routing.

## Description

hepatic target-lowering hypothesis in the GalNAc-siRNA reference modality, for a resolved human transcript under the user's confirmed requirement brief. Generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: chemistry rule cards (ESC/ESC+ 2'-F/2'-OMe/PS placement, GalNAc on sense 3') as context annotations; GTEx/HPA liver expression context; seed toxicity emphasized (6merDB with its scaffold caveat disclosed).

## Target

Resolved per request — never defaulted. Example gene (PCSK9) and any example values are illustrative, not defaults.

- **Reference:** exact versioned transcript (RNA alphabet), hashed into provenance.
- **Brief:** [metabolic-liver-galnac.request.example.json](metabolic-liver-galnac.request.example.json) illustrates syntax only.
- **Default vetoes:** immune_ugugu.
- **Default weight emphasis:** efficacy .35 / specificity .20 / seed_tox .20 / immune .20 / stability .05.

## Design Constraints

- Representation: paired 19-nt RNA cores; clinical-format overhang duplexes currently reject at intake (backlog #1).
- Two efficacy endpoints, never blended; both strands screened; heuristic caps disclosed.
- Frozen gates tightened-only by the brief; constraint adaptations PROPOSED with diagnosis.
- mRNA biomarker, secreted protein and clinical endpoints are distinct; hepatic delivery is assumed by modality, not proven by sequence.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm mode=metabolic_liver_galnac brief; resolve priorities (defaults above where user silent). | Confirmed hashed brief. |
| 2. Verify reference | Exact transcript (+ variant only where this application requires it). | Verified `transcript.fa` or stage blocker. |
| 3. Application preparation | chemistry rule cards (ESC/ESC+ 2'-F/2'-OMe/PS placement, GalNAc on sense 3') as context annotations; GTEx/HPA liver expression context; seed toxicity emphasized (6merDB with its scaffold caveat disclosed) | Application readiness record. |
| 4. Generate | Local generator; all windows retained; fresh run directory. | `candidate_pool.csv`. |
| 5–8. Battery E1–E4 | Validation; both efficacy endpoints; structure; both-strand specificity (E4e NOT_RUN(broken-binary)). | Per-dimension values + flags. |
| 9. Application layers (E5) | Immune scan mandatory; chemistry/expression context per application; allele assay only where required. | Typed flags/context. |
| 10. Gates (R1) | Frozen gates ∪ brief vetoes ∪ application defaults. | Survivor set + decision log. |
| 11. Rank (R2/R3) | Cohort-percentile weighting under confirmed weights; ±25% stability; seed-distinct panel. | Ranked table + stability report. |
| 12. Deliver | panel + chemistry-context annotation + benchmark comparison option vs approved drugs; per-dimension values; provenance; honest tier. | Complete typed bundle. |

## Expected Output

Fresh run directory: ranked candidates with per-dimension evidence, gate log, stability report, provenance block, evidence tier, and the application-specific next-evidence recommendation.

## Constraints

Antiviral/pathogen/pest work is review-only; plant/pest inactive; human models never transfer; license tiers bind redistribution.

## Important Instructions

Chemistry/delivery layers are annotations from published rule cards, never predictions; no sequence-based delivery predictor exists — state it, do not approximate it. Application benchmark status: BENCHMARKED in this frame: all-7-approved-drugs same-side cohort and the HIF1AN end-to-end case study (generator clean AUC 0.760; measured-top-10 at median 97.5th pct) — ../../benchmark/HIF1AN-case-study/README.md.
