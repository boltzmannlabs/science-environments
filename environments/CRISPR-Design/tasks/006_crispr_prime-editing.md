# Task: crispr_prime_editing_006

**Task family:** application-aware CRISPR design — **prime editing (pegRNA + PE3
nicking)**. **Status:** specification phase; runtime pending; published anchors only.

## Description

pegRNA design (spacer + PBS + RTT) plus optional PE3/PE3b nicking sgRNA for a specified
edit (substitution/insertion/deletion ≤3 bp standard; ≤40 bp with ePRIDICT-class
context), with intended-vs-unintended efficiency endpoints from PRIDICT2.0-class models
and breadth context from DeepPrime-class models.

## Target

Resolved per request ([006 example brief](../config/006_prime-editing.request.example.json) — HBB SNV correction, illustrative only).

- **Default vetoes:** off_target_exact_match.
- **Default weight emphasis:** outcome_quality .30 / on_target .35 / specificity .25 / context .10.

## Design Constraints

- pegRNA fields carried in the candidate contract (`pegrna_pbs`, `pegRNA_rtt`,
  `nicking_grna`, `editor`); design-only enumeration may use PrimeDesign/PE-Designer
  conventions — prediction always model-tagged.
- Intended-edit and purity (unintended) endpoints stay separate columns; PRIDICT2.0's
  score>70 ⇒ ~12× efficiency observation is context evidence, not a promise.
- Expression context (cell type) binds DeepPrime-class outputs (7-cell-type models);
  contexts outside trained cell types are flagged extrapolation.
- Model licenses/availability: PRIDICT2.0 CLI (uzh-dqbm-cmi) clean to run locally;
  DeepPrime CLI local; OptiPrime web URL unverified — treat as curated-only.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm edit spec (ref/alt/position verified); PE system constraint. | Confirmed hashed brief. |
| 2. Enumerate pegRNAs | Spacer windows + PBS/RTT length variants (design-only tools admissible). | `candidate_pool.csv`. |
| 3. Nicking design | PE3/PE3b nicking sgRNA candidates where requested. | Nick records. |
| 4. Efficiency prediction | Intended + unintended endpoints per pegRNA (+ system). | Model-tagged predictions. |
| 5. E3 off-target | Spacer + pegRNA-adjacent specificity stack. | Off-target record. |
| 6. Gates + rank | Outcome-quality-weighted ranking; stability. | Ranked panel. |
| 7. Deliver | Panel + PBS/RTT records + evidence + provenance. | Typed bundle. |

## Expected Output

Ranked pegRNA (± nicking) candidates with intended/unintended predictions, design
records, off-target evidence, provenance, `NEEDS_EXPERIMENTAL_VALIDATION`.

## Constraints

Never blend intended and unintended endpoints; RTT/PBS optimality claims stay
model-scoped (DeepPE's PBS/RTT-length recommendations are HEK293T-PE2-calibrated).

## Important Instructions

Published anchors: PRIDICT2.0 (92,423 pegRNAs / 13,349 pathogenic mutations; ρ 0.85
intended / 0.78 purity), DeepPrime (338,996 pairs; 8 PE systems × 7 cell types),
ePRIDICT (≤40 bp + chromatin; Nat Protoc 2026), Cirincione 2024/25 (~240,000 epegRNAs
experimental platform). No neutral PE benchmark; all cross-tool claims self-reported.
Run slots NOT_EXECUTED.
