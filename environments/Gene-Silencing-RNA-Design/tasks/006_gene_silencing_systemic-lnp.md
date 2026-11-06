# Task: gene_silencing_systemic-lnp_006

**Task family:** application-aware siRNA design — **Systemic / LNP siRNA design**. **Status:** In Progress; protocol v1.2, frozen gates, computational scope only. Shares the environment battery, ranking contract and gates with all application tasks; only the application-specific requirements differ. Start from the [general task](001_gene_silencing_rna.md) for mode routing.

## Description

non-conjugate systemic exposure; patisiran is the reference modality, for a resolved human transcript under the user's confirmed requirement brief. Generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: TLR3 >=21-nt class-effect flag interpreted as a formulation problem, not a sequence problem; tissue-of-action expression context.

## Target

Resolved per request — never defaulted. Example gene (TTR) and any example values are illustrative, not defaults.

- **Reference:** exact versioned transcript (RNA alphabet), hashed into provenance.
- **Brief:** [006_006_systemic-lnp.request.example.json](006_006_systemic-lnp.request.example.json) illustrates syntax only.
- **Default vetoes:** immune_ugugu.
- **Default weight emphasis:** efficacy .35 / specificity .25 / immune .25 / seed_tox .10 / stability .05.

## Design Constraints

- Representation: paired 19-nt RNA cores; clinical-format overhang duplexes currently reject at intake (backlog #1).
- Two efficacy endpoints, never blended; both strands screened; heuristic caps disclosed.
- Frozen gates tightened-only by the brief; constraint adaptations PROPOSED with diagnosis.
- Sequence cannot predict LNP biodistribution; complement/angiogenesis effects are length-class effects — flag, do not score.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm mode=systemic_lnp brief; resolve priorities (defaults above where user silent). | Confirmed hashed brief. |
| 2. Verify reference | Exact transcript (+ variant only where this application requires it). | Verified `transcript.fa` or stage blocker. |
| 3. Application preparation | TLR3 >=21-nt class-effect flag interpreted as a formulation problem, not a sequence problem; tissue-of-action expression context | Application readiness record. |
| 4. Generate | Local generator; all windows retained; fresh run directory. | `candidate_pool.csv`. |
| 5–8. Battery E1–E4 | Validation; both efficacy endpoints; structure; both-strand specificity (E4e NOT_RUN(broken-binary)). | Per-dimension values + flags. |
| 9. Application layers (E5) | Immune scan mandatory; chemistry/expression context per application; allele assay only where required. | Typed flags/context. |
| 10. Gates (R1) | Frozen gates ∪ brief vetoes ∪ application defaults. | Survivor set + decision log. |
| 11. Rank (R2/R3) | Cohort-percentile weighting under confirmed weights; ±25% stability; seed-distinct panel. | Ranked table + stability report. |
| 12. Deliver | panel + class-effect framing + delivery-uncertainty statement; per-dimension values; provenance; honest tier. | Complete typed bundle. |

## Expected Output

Fresh run directory: ranked candidates with per-dimension evidence, gate log, stability report, provenance block, evidence tier, and the application-specific next-evidence recommendation.

## Constraints

Antiviral/pathogen/pest work is review-only; plant/pest inactive; human models never transfer; license tiers bind redistribution.

## Important Instructions

Never present a favorable core score as evidence of tissue exposure. Application benchmark status: Anchor (descriptive): patisiran sequence/site participates in the approved-drug cohort — ../../benchmark/003_TTR-approved-drugs-cohort/README.md.
