# Task: crispr_microbial_013

**Task family:** application-aware CRISPR design — **microbial CRISPR design
(E. coli / bacteria)**. **Status:** specification phase; runtime pending; published
anchors only; bacterial models only — human models never applied.

## Description

Bacterial guide design (knockout or CRISPRi) using bacterial-trained models: Guo-2018
genome-wide activity predictor and Yu-2024 mixed-effect CRISPRi model (current best);
toxic seed-motif flags (Cui 2018, ~92k-sgRNA E. coli CRISPRi screen) as a confound
layer, not an activity model.

## Target

Resolved per request ([013 example brief](../config/013_microbial.request.example.json) — E. coli K-12 CRISPRi, illustrative only).

- **Default vetoes:** off_target_exact_match.
- **Default weight emphasis:** on_target .40 / specificity .30 / context .20 / outcome_quality .10.

## Design Constraints

- Bacterial genome + annotation resolved at intake (species/strain declared, versioned);
  off-target search scoped to that genome (+ plasmid context if declared).
- Activity endpoints: bacterial models only; the confound layer flags 5-nt seed motifs
  associated with dCas9 toxicity (Cui 2018) — exclusion is a screen-quality decision,
  recorded as such.
- Mixed-effect context (Yu 2024): dataset/batch effects handled by the model's
  conventions — provenance disclosed per run.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm organism/strain, KO vs CRISPRi; scope check. | Confirmed hashed brief. |
| 2. Verify reference | Strain genome + annotation. | Verified reference. |
| 3. Enumerate | PAM-adjacent spacers (KO) or TSS-window spacers (CRISPRi). | `candidate_pool.csv`. |
| 4. Activity scoring | Guo-2018 / Yu-2024 endpoints (model identity disclosed). | Scores. |
| 5. Toxic-seed flags | Cui-2018 motif screen. | Flag set. |
| 6. Off-target | Strain-genome search, intended locus excluded. | Off-target record. |
| 7. Gates + rank | Weighted ranking; stability. | Ranked panel. |
| 8. Deliver | Panel + evidence + provenance. | Typed bundle. |

## Expected Output

Ranked guide panel with bacterial-model scores, toxic-seed flags, off-target record,
provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Growth/essentiality phenotypes are experimental endpoints; no human-model transfer under
any weighting.

## Important Instructions

Published anchors: Guo 2018 (*NAR* 46:7052, E. coli activity corpus), Yu 2024 (*Genome
Biol*, mixed-effect CRISPRi — current best), Cui 2018 (*Nat Commun* 9:1932, toxic seed
motifs), Rousset 2018 (companion screen), CRISPy-web 3.0 (2025, curated-only). "CRISPRi-ML"
as a named tool could not be verified — not used. Run slots NOT_EXECUTED.
