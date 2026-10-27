# siRNA Designing Harness — environment specification

**Lifecycle:** In Progress. **Implemented surface:** portable technical CLI, workflow skill, task/config contracts and tests. **Not established:** self-contained scientific-backend deployment, independent predictor generalization or biological qualification.

## 1. Scientific objective and exclusions

Support auditable siRNA research from a precisely identified target to a conditional computational review panel. Distinguish design, specificity, predicted potency, source experimental efficacy, generalization and exact-construct qualification. Do not route ASOs, shRNAs, gapmers, miRNA mimics, aptamers or CRISPR guides through siRNA efficacy predictors. The exercised default is human RefSeq NM_ coding transcripts and documented 19-nt paired RNA cores; other species/constructs require separately verified interfaces and model applicability.

## 2. Modes and observation unit

| Mode | Actual unit | Supported conclusion |
|---|---|---|
| DESIGN | exact transcript version, generated core pair and mapped site | compatible computed features and conditional research ranking |
| AUDIT | preserved source artifact, candidate record and reference window | technical evidence/lineage consistency; not new inference |
| SENSITIVITY | matched candidate cohort and preserved endpoint-specific scores | ranking/cohort sensitivity, not biological change |
| BENCHMARK | source sequence/construct × assay endpoint × dose/time/cell/study | measured-endpoint evaluation only after independence and compatibility gates |

Mode actions are defined by the skill and task contracts. This repository's CLI implements technical checks, not backend job dispatch. A task JSON is an agent instruction contract, not a submitted scientific job.

## 3. Input contract

Require experiment ID, explicit organism, transcript accession.version or approved explicit FASTA, declared isoform coverage, representation, requested count and provider policy. Preserve malformed tokens for resolution rather than repairing them. Default review count is 20, not a guarantee. Resolve target/coverage decisions before affected design steps. Cell context, assay, chemistry, overhangs, delivery and biological acceptance rules may be unknown for sequence-only work but must block dependent claims.

`tasks/kras-shared-review.json` fixes the previously authorized KRAS reference set. It is not a new target selection or rerun request. Configured paths live in user-reviewed project copies of templates, not source files. Credentials never enter JSON, reports, prompts or Git.

## 4. Reference, orientation and representation invariants

Preserve original source FASTA/annotations and retrieval URL/time/accession/version/length/SHA-256. Verify organism/gene, alphabet, transcript-sense orientation, CDS translation and every coordinate. Map sites into every declared reference independently; the same RNA segment may have distinct CDS/UTR annotation across isoforms. Retain all occurrence positions and distinguish unique primary eligibility from valid repeated binding sites.

Guide and passenger are explicitly 5′→3′ RNA. The default technical contract is uppercase unambiguous 19-nt exact reverse complements. Reference DNA-to-RNA comparison requires explicit declaration and never modifies original bytes. Do not invent overhangs, trim full duplexes, flip strands or pad model context silently. Valid sequence pairing does not establish model eligibility, synthesis readiness or biological activity.

## 5. Architecture and tool boundary

The portable skill drives intake → provider discovery → source verification → approved generation → bounded compatible assessment → criticism → typed qualification → report/receipt. Inspect full scientific provider contracts before choosing execution; respect explicit local choices and authorization. Missing plugin/session/authentication must not trigger silent provider substitution.

Existing OligoFormer/RNA-FM, RN.Ai-Predict, RNAiSpline, frozen Ridge, ViennaRNA, transcript references and seed annotations are separate dependencies. The current-host execution evidence is described centrally in [references](../../research/sirna-designing-harness/references.md). Neither copied instructions nor available checkpoint files prove working inference on another host. NUPACK/RNAstructure and siRNADiscovery availability remain explicit rather than fabricated.

Submit once and retain job ID/request/input hashes. On timeouts inspect the same job/process/log/result; do not duplicate ambiguous submissions. Writable caches/results must be staged outside original sources and isolated from SCI's runtime. Safe header mappings, arguments-as-lists, applicable licensing and reviewed downloads are mandatory. Remote transfer is opt-in, not conferred by this specification.

## 6. Evidence and score semantics

Preserve native/eval OligoFormer modes separately; do not overwrite stock scores or rerun embeddings merely to toggle eval mode. Its scaled class output is not measured inhibition. RN.Ai predicted inhibition, RNAiSpline effective-class probability, unbounded Ridge estimates and exploratory composite priorities remain separate endpoints. Out-of-range Ridge values are extrapolations, not inhibition above 100%.

Record generated, unique, assessed, eligible, failed and NOT_RUN counts. Missing models/domains are not imputed. Reuse efficacy only for identical guide/full-context inputs; identical inference reused across isoforms is not independent confirmation. Accessibility/duplex calculations are supporting molecular features, not cellular knockdown.

## 7. Specificity and critical review

Review BOTH guide and passenger exact/near sites and declared 6/7/8-nt seed opportunities. Record reference version, ambiguity exclusions, mismatch/gap/variant limits, alignment versus transcript/gene counts, whole-transcript versus UTR scope and expression/loading uncertainty. Native guide-only screening is not a fresh both-strand assessment.

A permissive operational rule may retain perfect outside-gene matches; flag that separate diagnostic rather than calling the candidate gene-exclusive. Relevant paralog/pseudogene analysis includes KRASP1/HRAS/NRAS for KRAS. Neutral-scaffold seed viability is neither exact-duplex toxicity nor immune tolerance. No candidate is labelled safe or off-target-free by negative sequence findings.

## 8. Selection and sensitivity protocol

Use declared frozen ranking/filter policy, diverse mapped sites and actual compatible tools; never force the requested count. Numerical order is exploratory. Compare methods on identical successful cohorts with explicit K/ties and separate source/score scales. Existing cohort-normalized composites must not be silently reweighted or renormalized.

Excluding Ridge extrapolations is a numerical sensitivity analysis, not automatic biological exclusion. Preserve missingness and operational-selection effects; K > n is NOT_APPLICABLE, K = n set overlap is non-discriminating. Correlated predictors and shared checkpoints are not independent validation. No definitive winner from score agreement alone.

## 9. Literature workflow

Retrieve original articles and source sequences, not merely search snippets. Validate responses semantically: cookie pages, HTML labelled DOCX, partial text or empty archive entries are not complete evidence. Record search query/date/coverage and unresolved retrievals. Distinguish reported literal pairs from approved corrected constructs, pooled ranges from individual labels, protein from mRNA endpoints and follow-up lineage from independent laboratories.

A published core may occur in the generated pool but fail shortlist heuristics. That is prioritization disagreement, not failed generation or a general sensitivity estimate. Literature-supported cores remain separate comparator controls until their missing context/specificity evidence is assessed. No new mutant is constructed merely because a paper describes one.

## 10. Independent benchmark gate

Audit actual source labels, studies, duplicates, target aliases, dose/time/cell/chemistry and final-checkpoint development exposure before inference. Distinguish known Ridge membership from unknown pretrained membership; no sequence match is not proof of independence. Do not pool source-reported inhibition with incompatible endpoints or apply arbitrary length conversions.

If no auditable compatible independent cohort exists, return BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET, no untouched-test claim, an explicit header-only prediction schema and null metrics/zero attempts. Historical random/grouped results are not a newly sealed test. If the gate passes, preregister original-study/target/duplicate-aware partitions, train-only baselines/mappings and untouched test, then compute endpoint-compatible correlation/ranking/error/calibration metrics and appropriate study-aware uncertainty. No invented interval from inadequate sampling.

## 11. Typed qualification

Gates use literal Boolean `required` and PASSED/FAILED/BLOCKED_MISSING_EVIDENCE/NOT_RUN/NOT_APPLICABLE plus evidence_refs, failed_criteria, missing_evidence, warnings and method_version. Required failure precedes required missing. Required NOT_APPLICABLE cannot evade evidence. Native pass booleans are reviewed with their missing/failed fields.

Technical helper success never confers full biological qualification. Distinguish computational screening completion from biological PARTIAL. Missing independent efficacy, specificity acceptance, immune assessment, final construct, delivery and assay evidence block dependent conclusions.

## 12. Mutation arm

Keep BLOCKED_PENDING_MUTATION_SPECIFICATION unless exact nucleotide mutation or verified mutant sequence, accession.version/context and mutant-versus-wild-type-sparing objective are supplied. Shared transcript coverage is not mutation selectivity. A mutant-perfect/WT-mismatched site is not measured allele-selective silencing. This contribution constructs no hypothetical mutant.

## 13. Outputs, persistence and verification

Per scientific task: target/source specification; raw retrievals; capability registry; generated and assessment tables; filters/NOT_RUN; ranking/critique; specificity/coverage; literature crosswalk; qualification/missing evidence; methods/source/checkpoint provenance; report; input/output hashes and independent receipt. The full lists are in the bundled skill and task contracts. Raw source data and large generated outputs remain outside Git. This repository retains aggregate historical summaries and a bounded `benchmark/KRAS/` snapshot of selected existing reports/candidate/ranking/qualification tables. Copies are byte-identical, include provenance and renamed historical source receipts/manifests, and are explicitly not complete original-run archives or a successful independent benchmark. Large/raw/intermediate artifacts are indexed rather than redistributed. Snapshot verification requires no original scientific backend.

Seal outputs after writers stop. Manifests exclude self/root receipt to avoid circular hashes. Audit input files before/after; do not call an old verifier that writes into originals. Archive failed/superseded artifacts with honest roles. Synthetic software fixtures are not biological designs or measurements.

## 14. Acceptance criteria and maturity

- Required repository structure and matching research links exist; local Markdown/JSON contracts pass checks.
- Portable skill integrity and positive/negative tests pass; existing destination is not overwritten.
- Examples show expected explicit blockers, not fabricated scientific execution.
- Historical aggregates derive from hash-bound real receipts; external verification is read-only and opt-in.
- No private data, weights, third-party implementation, credentials or raw publication text are added.
- Scientific and governance blockers are explicit.

Passing these establishes the implemented technical surface only. Lifecycle remains In Progress pending backend packaging/deployment validation, approved scientific acceptance criteria and review. Independent predictor validation remains blocked; biology remains PARTIAL.

## 15. Research, rights and review

[Research notes](../../research/sirna-designing-harness/research-notes.md), [central references](../../research/sirna-designing-harness/references.md), [status](STATUS.md), [architecture decision](../../docs/decisions/sirna-designing-harness.md). Repository LICENSE is pending; bundled original helper/skill MIT license does not grant third-party rights. Issue/PR/owner/domain review/merge remain pending as stated in STATUS.md. Do not infer a completed repository contribution from a local technical test receipt.
