# Task: gene_silencing_rna

**Task family:** application-aware siRNA design, evaluation and property prediction. **Status:** In Progress; protocol v1.2 with frozen gates and executed computational benchmarks; experimental validation not established. This file follows the environment's house task structure; the siRNA-specific text is original.

## Description

Design and evaluate siRNA candidates for a resolved human target under the user's application and requirements. Route the request (DESIGN / EVALUATE / EXPLORATORY / BENCHMARK / AUDIT), confirm the requirement brief, verify the exact transcript (and variant, for allele-selective objectives), generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, rank under the confirmed requirement weights with mandatory stability reporting, and return a traceable shortlist with per-dimension evidence.

Use the [environment specification](../ENVIRONMENT_SPEC.md) and [runtime contracts](../runtime/CONTRACTS.md). Own routine resolution (isoform confirmation questions excepted), stage execution and bounded recovery. Do not manufacture sequences, scores, thresholds or successful results; a missing stage stays `NOT_RUN(reason)`.

## Target

Resolved per request — never defaulted. Keep the reusable environment unchanged when switching targets.

- **Reference:** exact versioned transcript (GENCODE v50 local or user sequence), RNA alphabet, hashed into provenance.
- **Application:** one of the ten active human profiles; antiviral/pathogen/pest requests are review-only; plant/pest is inactive.
- **Brief:** confirmed priorities — hard vetoes, weights (efficacy/specificity/immune/seed_tox/stability), min-standards (tighten-only), panel size, review window.
- **Allele objective (if claimed):** reference-verified variant + explicit mutant-vs-WT objective before any design.
- **Inputs:** `00_inputs/requirement_brief.json`, `00_inputs/transcript.fa`, and for EVALUATE mode the candidate CSV ([contract](../config/candidate.schema.json)).

The example briefs ([design](ttr_design.example.json), [exploratory](hif1an_exploratory.example.json)) illustrate syntax only; they are not approved runs.

## Design Constraints

- Representation is paired 19-nt RNA cores; clinical-format overhang duplexes are recorded but currently reject at the intake gate (backlog #1).
- Efficacy is reported as two independent endpoints (RN.Ai % inhibition; OligoFormer scaled) — never averaged, ensembled or converted.
- Both strands are screened; heuristic caps are disclosed in the same sentence as their counts.
- Immune flags are hazard filters, not probabilities; chemistry/delivery layers are context annotations only.
- No negative screen proves safety or specificity; computational outcomes cap at `NEEDS_EXPERIMENTAL_VALIDATION`.
- Panels are seed-distinct and site-diverse; ties and near-ties are preserved; return fewer candidates rather than pad.
- Gate thresholds are frozen; briefs tighten only; constraint adaptations are PROPOSED with diagnosis and require user confirmation.

## Required Execution Steps

| Step                                            | What must happen                                                                                                                                                                   | Required result                                                            |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1. Route the request                            | Classify mode and application; exactly one clarifying round for essential ambiguity.                                                                                               | Routed request or specific `NEEDS_INPUT`.                                |
| 2. Resolve and confirm the brief                | Parse priorities from the request + application defaults; echo for confirmation; hash into provenance.                                                                             | Confirmed `requirement_brief.json`.                                      |
| 3. Verify the reference                         | Resolve/fetch the exact transcript (and verified variant for allele objectives); declare alphabet; hash.                                                                           | Verified `transcript.fa` (+ `variant.json`) or stage-specific blocker. |
| 4. Generate candidates                          | Run the local generator; retain every scored window with native score semantics; fresh run directory.                                                                              | Complete `candidate_pool.csv`.                                           |
| 5. Validate (E1)                                | Alphabet, orientation, pairing, coordinates, CDS/UTR classification.                                                                                                               | Validated rows with rejection reasons.                                     |
| 6. Evaluate efficacy (E2)                       | Both endpoints in native units; context handling and N-padding flags recorded.                                                                                                     | Per-candidate E2a/E2b values.                                              |
| 7. Evaluate structure (E3)                      | Guide MFE, duplex ΔG, accessibility with declared parameters.                                                                                                                     | Per-candidate E3 values.                                                   |
| 8. Evaluate specificity (E4)                    | Both-strand near-match screen with caps disclosed; seed counts; POTS; 6merDB; E4e recorded `NOT_RUN(broken-binary)` while defective.                                             | Per-candidate E4 values + flags.                                           |
| 9. Evaluate application layers (E5)             | Immune scan mandatory; allele assay if applicable; chemistry/delivery context; expression context.                                                                                 | Typed flags/context, never invented.                                       |
| 10. Apply gates (R1)                            | Frozen gates ∪ brief vetoes ∪ application defaults; user floors tighten only.                                                                                                    | Survivor set with full decision log.                                       |
| 11. Rank (R2/R3)                                | Cohort-percentile weighted ordering under the confirmed weights; ±25% perturbation stability; seed-distinct panel construction.                                                   | Ranked table + stability report; unstable orderings labeled.               |
| 12. (EXPLORATORY only) Run the exploration loop | X1–X5 strategies, funnel, tiered descent, PROPOSED constraint re-anchoring with `rel_gate_only` marks, brief variants, consensus/Pareto synthesis.                              | Consensus panel + proposed brief.                                          |
| 13. Deliver                                     | Candidates CSV, per-dimension values, flags, `NOT_RUN` list, provenance (tools, versions, hashes, brief hash), evidence tier, application-specific next-evidence recommendation. | Complete typed bundle; `best_design` null absent experimental evidence.  |

## Expected Output

A fresh run directory containing the ranked candidate table with per-dimension evidence, the gate decision log, the stability report, the provenance block and the honest evidence tier. For EXPLORATORY, additionally: strategy/budget report, any PROPOSED constraint adaptation with diagnosis, and the consensus/divergence structure ending in a proposed brief.

## Constraints

Antiviral/pathogen/pest sequence work is review-only and produces no sequences. Plant/pest targets are refused with activation conditions. Non-human extrapolation of human efficacy models is forbidden. License tiers bind redistribution (proprietary OligoFormer; no-license RNAiSpline/SiaRNA/shRNAI stay internal). Ambiguous submissions are resolved by status query, never resubmission.

## Important Instructions

Never blend endpoints or present a preference score as efficacy. Never silently pick an isoform, loosen a frozen gate, or convert `NOT_RUN` to pass. Report target-level gate saturation when diagnosed (see the HIF1AN benchmark). Selection during exploration must not consult measured or published outcomes; benchmarks join labels post-hoc only.
