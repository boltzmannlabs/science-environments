---
name: sirna-harness
description: Use when designing, auditing, or benchmarking siRNAs.
version: 2.0.0
author: SCI research workflow contributors
license: MIT
metadata:
  sci:
    category: science
    tags: [sirna, design, qualification, provenance, benchmarking, portable]
---

# Portable Agent Scientist siRNA research harness

## When to Use

Use this skill to orchestrate siRNA design, computational assessment, ranking criticism, read-only evidence audits, sensitivity analysis and measured-data benchmark eligibility. This is procedural memory plus technical helper software, not a new registered scientific tool, a bundled predictor, an automatic model installer or experimental validation.

Design siRNA only. The exercised default envelope is human RefSeq NM_ coding mRNA with paired19nt RNA cores. Do not silently extend it to other RNA modalities, species, lengths, modified/scaffold-specific constructs or mismatched-target inference. Require appropriate adapters/reference/model validation for such extensions. Core19 output is not an order-ready21nt or chemically specified duplex.

Scientific findings, predictions, calculated features, external annotations, assumptions and missing evidence must remain distinct. Never invent sequences, model outputs, measurements, records, citations, execution or favorable gate states. Historical case counts and receipts are examples, not new-target or new-machine validation. Governing instructions, source rights and authorization override this skill.

## Read the reference matching the task

- [Usage and request templates](references/usage.md) cover DESIGN, AUDIT, SENSITIVITY and BENCHMARK requests.
- New system / transfer / setup: [portability guide](references/portability.md).
- Design / assessment / qualification: references/scientific-protocol.md and [adapter contracts](references/tool-adapters.md).
- Read-only audit / ranking sensitivity / independent experimental benchmarking: [benchmark and sensitivity protocol](references/benchmark-and-sensitivity.md).
- Existing original-host deployment: [originating-host locators](references/current-host-example.md). This is an optional locator, never a portable dependency or standing authorization.
- references/new-target-local-execution.md preserves detailed earlier integration/audit lessons and historical paths; re-discover actual paths/tools elsewhere.

Use additional installed skills such as sirna-design-routing, sirna-benchmarking, scientific-software-integration, sequence analysis and statistics when available. If absent, follow the self-contained references here and disclose unsupported operations instead of inventing access or treating a skill as an installed backend.

## Operating modes

DESIGN: exact target to actual approved generation, compatible assessment, criticism and a conditional research-review panel.
AUDIT: preserved outputs to source/window/annotation consistency and candidate evidence resolution; no rerun of generation/inference/folding/screening without explicit justification/authorization.
SENSITIVITY: preserved compatible scores only, declared cohorts/K/ties, extrapolation and missing-output restrictions; do not infer biological changes from changed rankings.
BENCHMARK: source-audited measured experimental endpoints plus independence/training-exposure gate before testing. Fail closed with BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET when a suitable independent cohort is not established.

Choose the user's requested mode and preserve completed work. New analyses use versioned directories; audit reports never write back into the original run. Do not carry old case evidence into a new target as if newly executed.

## Workflow

1. Establish input, objective and permissions. Require an explicit organism, exact transcript.version or explicit sequence, experiment name and coverage objective. Default to20 nonoverlapping review candidates unless another count is requested. Resolve ambiguous references; do not silently choose isoforms, repair malformed identifiers, infer chemistry/delivery or invent biological acceptance criteria. Missing context blocks dependent qualification, not every valid sequence task.
2. Discover actual tools/contracts, schemas, environments, assets, references, licenses and live session permissions. For scientific execution inspect Boltzmann contracts before provider selection unless explicitly directed to local/another provider. Honor explicit local choice without bypassing restrictions. Do not install/download large assets, upload read-local sequences, incur costs or copy credentials without required approval. On authentication/session/contract failure stop the dependent step, not silently switch providers.
3. Verify exact source sequence and annotations before target-specific final designs. Preserve original bytes, retrieval URL/time, accession/version, species/gene, alphabet/orientation, CDS translation, length and hashes. Map every candidate site to each declared reference independently; classify CDS/UTR per reference. Coverage of reference isoforms is not coverage of every mutant or expression in a cell.
4. Execute the approved existing generator once and retain its exact job/directory. Preserve every row, strand orientation, duplicate provenance, coordinates, representation, provider/source/checkpoint identity, mode and raw score semantics. Never substitute unscored windows, pad/truncate guides or invent a requested count. On a tool-interface timeout inspect the same request/process/log/result before retrying; ambiguous submission must not be duplicated.
5. Validate pairing, target identity, unique primary mapping and model-specific context/applicability. Preserve model-ineligible but valid sequence cases with explicit reasons. Use bounded assessment budgets and record each NOT_RUN row. Native pipeline pass booleans must be read with failed_criteria/missing_evidence, not promoted blindly into scientific passes.
6. Evaluate compatible potency, structure/accessibility, exact isoform coverage, BOTH-strand full/near matches and6/7/8nt seed evidence. Keep ideal molecular calculations, guide/passenger neutral-scaffold annotations and measured exact-duplex data distinct. Declare reference/search scope and ambiguity/indel/variant/expression limitations. A permissive inherited filter may allow perfect outside-gene matches; flag those separately instead of calling them gene-exclusive recommendations or silently changing thresholds.
7. Preserve the verified frozen Ridge baseline when available within its audited scope; keep frozen composites exploratory. A missing Ridge asset requires a declared limitation/policy decision, not synthesized coefficients. Preserve distinct RN.Ai percent, RNAiSpline class probability, native/eval OligoFormer and priority-score endpoints. Flag unbounded Ridge estimates outside0..100. Correlated predictors/shared checkpoints are not independent confirmation.
8. Compare only compatible common cohorts. Report actual scored/missing counts and uncertainty limits, tied ranks, alternatives and contradictions. Reuse verified baseline statistics for new sensitivity restrictions. Excluding extrapolations is not a biological exclusion rule; K=n overlap is non-discriminating. Never impute missing domains or renormalize weights silently. Return fewer candidates if unsupported, never pad or force a winner.
9. Resolve qualification as typed evidence gates. Separate technical integrity, computational screening, potency, specificity acceptance, immune risk, final construct, delivery/assay context, measured efficacy, independent validation and overall biology. Required failure takes precedence over required missing; NOT_RUN/missing cannot pass. Successful COMPUTATIONAL_SCREENING_PASSED can coexist with overall PARTIAL. Do not label EXPERIMENTALLY_VALIDATED or biologically qualified without suitable sequence/chemistry-linked measurements and context.
10. Deliver actual artifacts, critique and next evidence needed; seal hashes only after writers finish. Preserve failed attempts and explicitly superseded drafts. Verify source preservation, sequence/coordinate/score lineage, cohort equality and gate semantics with independent checks. Explain what was run versus reused, blocked or only available.

## Mutation-selective boundary

Shared-reference silencing is not mutant-selective and has no wild-type-sparing guarantee. Unless an exact nucleotide mutation or verified mutant sequence, transcript/reference context and mutant-versus-wild-type objective are supplied, keep BLOCKED_PENDING_MUTATION_SPECIFICATION and construct zero hypothetical mutants. Validate the reference allele and mapping before variant design. A perfect mutant match versus WT mismatch supports sequence discrimination only; do not use ordinary perfect-match potency models as validated allele-selectivity assays. Cell/assay/chemistry/delivery requirements are separately needed for dependent qualification.

## Portable technical helpers

Python3.10+ standard library only; no pip/model installation. All paths below are relative to this skill directory.

- scripts/transfer_skill.py check/install: verify a portable manifest, dry-run by default, copy instructions/helpers into an explicitly selected empty profile destination. Refuse existing destinations, symlinks, unsafe paths and model/dataset/credential payloads. This does not register scientific tools or install models.
- scripts/sirna_portable.py preflight: check configured paths/checksums WITHOUT executing backends. Files present remain execution-unverified.
- validate-objective: intake/format/scope checks; never authoritative reference or mutation validation.
- validate-candidates: exact supplied19nt core pairing/coordinate/unique-site/flank checks; requires explicit DNA/RNA reference alphabet; no generation or inference.
- check-gates: strict Boolean/status/schema and local evidence-file checks with mandatory category coverage; required failures precede missing. It never certifies biological qualification from claims or file existence. Map legacy gates explicitly, do not silently coerce them.
- audit-label-table: minimal table/header/missingness checks with explicit sequence/label/unit columns; always leaves independence unresolved. It is not the full experimental benchmark protocol.
- scripts/test_portable.py: software-only positive/negative fixtures; never experimental or efficacy evidence.

Examples and configuration/credential boundaries: [portability guide](references/portability.md). Fill templates in a new project directory, not inside the installed skill. Intentional blocked helper results use exit2 and structured JSON; they are not successful inference or fabricated negative performance.

## Required reporting

For a design run use the18-section review and artifact list in [scientific protocol](references/scientific-protocol.md). Build the15-category actual capability registry, not an assumed universal ecosystem. For audit/sensitivity include a candidate evidence table, exact failed diagnostics, common-pool metrics, missing evidence, input/output hashes, source preservation and receipt. For benchmarking use the eight named deliverables plus eligibility/duplicate/scale audits in references/benchmark-and-sensitivity.md; if blocked, retain null metrics and an empty independent-prediction schema rather than plausible-looking substitute results.

Report achievement-first without hiding adverse findings. State the successful computational milestone, limitations and precise next action. Installing this skill or passing its helper tests is not proof of scientific backend readiness, independent predictor performance, safety, immune tolerance, delivery success, mutation selectivity or clinical readiness.
