# Task: crispr_design_general_001

**Task family:** application-aware CRISPR design — **general routing task (all modes)**.
**Status:** In Progress; protocol v0.1 (DRAFT gates), partial runtime. Executed evidence:
shared component benchmarks only (RS3 Sequence, CRISPRon — endpoint-level, not routing
validation; see the [completed-only registry](../benchmark/BENCHMARK_RUNS.md)). Shares
the core battery (E1–E6), draft gates and ranking contract with all modality tasks; only
application-specific requirements differ.

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

The universal constraint contract — binding on every task (002–013 add modality-specific
layers on top):

**Representation & alphabet**
- 20-nt spacer + NGG PAM (SpCas9); 23-nt spacer + 5′ TTTV PAM (Cas12a); 20–30-nt crRNA
  spacer (Cas13, RNA alphabet ACGU). DNA tasks use ACGT; orientation checked, never
  silently swapped; coordinates 1-based closed with strand; PAM reported with every spacer.
- No ambiguous bases (N) pass intake; supplied sequences with U/T mismatch are converted
  with the conversion logged, never guessed.

**Reference & annotation**
- Versioned transcript + exon structure (GENCODE 49 local) on GRCh38.p14; isoform
  decision surfaced to the user, never silently chosen; spliced-exon and CDS-translation
  validation before design (prior-run recipe).
- Allele-selective objectives require a reference-verified variant (ClinVar/dbSNP + VEP)
  before any design step.

**On-target endpoints**
- ≥2 independent model endpoints per candidate, separate columns, native units,
  **never averaged, ensembled or blended**; every score column carries model identity +
  version; correlated models disclosed (e.g., CRISPRon's training includes Kim-2019 data —
  split discipline stated per benchmark).
- Expression system (U6 Pol III vs T7/IVT) is declared and binding — scores do not
  transfer across it (Haeussler 2016); cell types outside a model's training contexts are
  flagged extrapolation.
- Realistic performance envelope disclosed with benchmark claims: replicate ρ≈0.7 ceiling;
  ≥0.4 on truly independent data is respectable (Haeussler 2016; Konstantakos 2022).

**Specificity**
- Genome-wide off-target enumeration ≤3 mismatches, both strands, ungapped (bulges
  NOT_EVALUATED — disclosed cap in every off-target deliverable); intended locus excluded
  by verified coordinates.
- Pair scores (CFD, Elevation) reported separately from enumeration counts; aggregate
  specificity disclosed as a preference view, never an efficacy estimate.
- **Off-target output is prioritization, never a safety claim** (Kaufmann 2026: ~77%
  recall @ top-500; weak score↔indel correlation); regulator-grade contexts additionally
  require the variant-aware layer and the assay-hierarchy statement (task 003).

**Outcome honesty**
- Every computational deliverable caps at `NEEDS_EXPERIMENTAL_VALIDATION`; failed/missing
  stages are `NOT_RUN(reason)` — never imputed; a failed stage blocks only dependent claims;
  small/degenerate evaluation sets reported as degenerate.
- `best_design` stays null without experimental evidence.

**Gates & thresholds**
- Gates are DRAFT (provenance-tagged) until calibrated on Kim-2019 held-out +
  Konstantakos-2022 protocol (on-target) and CHANGE-seq 110-guide set (off-target);
  briefs tighten only — loosening requires explicit logged user instruction; gate
  saturation is diagnosed and surfaced, never silently passed.

**Tooling & licensing discipline**
- Licenses bind use: CRISOT (CC BY-NC 2.0) research-internal only; no-license repos
  (DeepBE, yachielab, Cas13design mirror) never redistributed; research-use portals
  (deepcrispr.info, pridict.it) provenance-only; third-party weights never shipped.
- Backend liveness probed before every run (`runtime/probe_backends.py`); absolute-path
  invocation; fresh run directories; inputs read-only; provenance block mandatory.

**Scope gates**
- Pathogen-targeting diagnostics design: review-only. Plant editing: inactive (no
  verified plant activity model; human models never transfer). Microbial: bacterial
  models only. Delivery prediction: does not exist — stated, never approximated.

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

- **Runtime is partial:** task 002's knockout stack has executed end-to-end (Run1,
  2026-11-10 — see [runtime contracts](../runtime/CONTRACTS.md)); other modality adapters
  land in later phases. Execute this routing contract against the verified local backends
  with explicit `NOT_IMPLEMENTED` marks for absent adapters; never fake a stage.
- **Executed evidence (local):** shared component benchmarks — [RS3 Sequence held-out
  activity](../benchmark/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) ·
  [CRISPRon v1 external activity](../benchmark/002_CRISPRon/Run-4_2026-11-12/REPORT.md);
  result record [results/001_general/Run-2](../results/001_general/Run-2_2026-11-12/REPORT.md);
  historical Run-2/Run-3 comparisons in
  [execution_history](../execution_history/before_completed_only_20261112T061830Z/benchmark/001_general-routing/Run-3_2026-11-12/README.md).
  These are endpoint-level model benchmarks, not routing validation: no labeled
  modality-routing corpus exists and no complete all-mode workflow has been validated.
- **Honesty rules:** shared component benchmarks are not independent task replications;
  unexecuted evaluation slots stay `NOT_EXECUTED`; `best_design=null` absent experimental
  evidence.
