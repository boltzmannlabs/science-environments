# Task: crispr_prime_editing_006

**Task family:** application-aware CRISPR design — **prime editing (pegRNA + PE3
nicking)**. **Status:** In Progress; protocol v0.1 (DRAFT gates). Executed evidence:
fresh matched held-out outcome evaluations (PRIDICT2.0 intended ρ 0.9056 HEK293T / 0.8081
K562; DeepPrime PE2 fixed test ρ 0.861474 — endpoint-level; see the
[completed-only registry](../benchmark/BENCHMARK_RUNS.md)); PE3 nicking design not
validated. Start from the [general task](001_crispr_design_general.md) for mode routing.

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

*Universal contract from [task 001](001_crispr_design_general.md) applies in full.* Modality-specific layers:

**pegRNA structural constraints**
- pegRNA = spacer + 3′ extension (PBS + RTT); both sequences are part of the candidate
  contract (`pegrna_pbs`, `pegRNA_rtt`) and are enumerated as design variants, not fixed.
- PBS/RTT length choices are model- and protocol-scoped — declared per run against the
  model in force (DeepPE's length recommendations are HEK293T-PE2-calibrated; treat as
  context, not universal rules); edit position inside the RTT and primer-binding
  annealing temperature context recorded.
- **Extension-encoded poly-T risk**: the 3′ extension is transcribed by Pol III too —
  ≥4-T runs in PBS/RTT carry the same termination flag as the spacer; extension
  self-complementarity and GC are checked as separate physico-chem columns.

**PE system & nicking constraints**
- PE system declared per run (PE2/PE3/PE3b + editor generation); PE3 nicking sgRNA is
  designed as a second candidate with its own off-target record; PE3b (mutant-strand
  nicking) preference recorded for correction requests where allele discrimination
  matters.
- Edit-size scope: standard predictions cover ≤3-bp edits; ≤40-bp edits carry the
  ePRIDICT-class context label and are extrapolation-flagged under other models.

**Endpoint constraints**
- Intended-edit efficiency and purity/unintended endpoints are separate columns, never
  blended; PRIDICT2.0's score>70 ⇒ ~12× higher in-vitro efficiency is context evidence,
  not a promise; purity uses the model's own unintended definition (disclosed per model).
- Expression context binds DeepPrime-class outputs (8 PE systems × 7 cell types):
  system × cell-type combinations outside the trained grid are flagged extrapolation;
  cell type and delivery are part of the provenance block.

**Specificity constraints**
- pegRNA spacer + nicking spacer each get the E3 stack; the 3′ extension's target
  complement is noted as an additional alignment feature (extension-derived binding is
  model-limited and disclosed as such — no verified extension-aware genome search exists
  in battery v0.1).

**Model availability/licensing**
- PRIDICT2.0 CLI (uzh-dqbm-cmi) clean to run locally; DeepPrime CLI local; OptiPrime
  web URL unverified — curated-only; ePRIDICT protocol (Nat Protoc 2026) is the
  current reference standard for ≤40-bp + chromatin context.

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

- **Published anchors:** PRIDICT1 (92,423 pegRNAs / 13,349 pathogenic mutations; ρ 0.85
  intended / 0.78 unintended), PRIDICT2.0 (intended ρ 0.91 HEK293T / 0.81 K562), DeepPrime
  (338,996 pairs; 8 PE systems × 7 cell types), ePRIDICT (≤40 bp + chromatin; Nat Protoc
  2026), Cirincione 2024/25 (~240,000 epegRNAs experimental platform). No neutral PE
  benchmark; all cross-tool claims self-reported.
- **Executed evidence (local):** [PRIDICT2.0 published grouped OOF
  outcomes](../benchmark/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) ·
  [DeepPrime base fixed test](../benchmark/006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) —
  PRIDICT2 intended-edit ρ 0.9056 HEK293T / 0.8081 K562 (source-fold mismatches 0);
  DeepPrime PE2 conventional-scaffold fixed test n=28,883, ρ 0.861474. Result record
  [Run-2](../results/006_prime_editing/Run-2_2026-11-12/REPORT.md); historical Run-2/Run-3
  comparisons in [execution_history](../execution_history/before_completed_only_20261112T061830Z/benchmark/006_prime-editing/Run-3_2026-11-12/README.md).
- **Gaps:** cell/editor matched only; pretraining-overlap audit incomplete for PRIDICT2;
  unintended-edit score is not purity; PE3 nicking design not validated; unexecuted
  evaluation slots stay `NOT_EXECUTED`.
