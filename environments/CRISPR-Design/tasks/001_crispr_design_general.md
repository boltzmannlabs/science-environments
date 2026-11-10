# Task: crispr_design_general_001

**Task family:** application-aware CRISPR design — **general routing task (all modes)**.
**Status:** specification phase — workflows defined; scoring runtime pending; no executed
benchmark. Shares the core battery (E1–E6), draft gates and ranking contract with all
modality tasks; only application-specific requirements differ.

## Description

Route a CRISPR design request: resolve the requirement brief (target, modality,
priorities), verify the reference, route to the matching modality task (002–013), and
orchestrate the shared battery. Modes: DESIGN (target + requirements), EVALUATE (supplied
spacers + property question), EXPLORATORY (target only → consensus panel + proposed
brief), BENCHMARK (same-side comparison vs published), AUDIT (capability/gate question).
Deliverables are capped at `NEEDS_EXPERIMENTAL_VALIDATION` and carry per-dimension
evidence with `NOT_RUN(reason)` transparency.

## Target

Resolved per request — never defaulted. Example (KIF11 knockout) is illustrative only
([001 example brief](../config/001_design.request.example.json)).

- **Reference:** exact versioned transcript + exon structure (GENCODE 49 local); genome
  assembly GRCh38.p14 default; isoform decision surfaced, never silently chosen.
- **Brief:** [requirement_brief.schema.json](../config/requirement_brief.schema.json).

## Design Constraints

- Representation: 20-nt spacer + NGG PAM (SpCas9), 23-nt + TTTV (Cas12a), 20–30-nt crRNA
  (Cas13); DNA alphabet ACGT for genome-targeting tasks, RNA ACGU for Cas13.
- ≥2 independent on-target endpoints, separate columns, **never averaged**; expression
  system (U6 vs T7/IVT) declared — scores do not transfer across it (Haeussler 2016).
- Off-target outputs are prioritization, never safety claims (Kaufmann 2026: ~77% recall
  @ top-500, weak score↔indel correlation).
- Gates are DRAFT until calibrated; briefs tighten only.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Parse request → mode + application; resolve priorities (modality defaults where user silent); exactly one clarifying round for essential ambiguity. | Confirmed hashed brief. |
| 2. Scope gates | Pathogen-diagnostics → review-only; plant → inactive profile; microbial → task 013 bacterial models; human default otherwise. | Routing decision logged. |
| 3. Verify reference | Exact transcript(s) + genomic coordinates + variant (only where the task requires it). | Verified `reference.fa` + annotation or stage blocker. |
| 4. Modality task | Hand off to task 002–013 workflow; application layers per modality. | Task execution record. |
| 5–9. Battery E1–E6 | Per [ENVIRONMENT_SPEC §3](../ENVIRONMENT_SPEC.md): validation; on-target endpoints; off-target stack; indel outcome (KO); application layers; physico-chem. | Per-dimension values + flags; `NOT_RUN(reason)` for missing stages. |
| 10. Rank (R1–R3) | Veto → cohort-percentile weighting with ±25% stability → site-distinct panel. | Ranked table + stability report. |
| 11. Deliver | Panel + per-dimension evidence + provenance + evidence tier + next-evidence recommendation. | Complete typed bundle in fresh run directory. |

## Expected Output

Fresh run directory under `results/00N_<application>/`: ranked candidates
([candidate.schema.json](../config/candidate.schema.json) contract) with per-dimension
evidence, gate log, stability report, provenance block, honest evidence tier.

## Constraints

No off-target-safety claims; no therapeutic qualification; license tiers bind tool use
(CRISOT non-commercial; no-license repos never redistributed); failed stages block only
dependent claims.

## Important Instructions

Runtime is not yet implemented — until the runtime phase lands, this task documents the
routing contract and the agent executes it against the verified local backends
([runtime/CONTRACTS.md](../runtime/CONTRACTS.md)) with explicit `NOT_IMPLEMENTED` marks
for absent adapters. Benchmark status: published anchors only; all Run slots
`NOT_EXECUTED` ([BENCHMARK_RUNS](../benchmark/BENCHMARK_RUNS.md)).
