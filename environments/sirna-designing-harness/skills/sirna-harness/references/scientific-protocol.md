# Scientific execution, scope and evidence gates

## Intake and provider selection

Restrict this workflow to siRNA. Do not route ASO, gapmer, shRNA, miRNA mimic, aptamer, mRNA construct or CRISPR guide design through the siRNA predictors. The exercised default envelope is human RefSeq NM_ coding mRNA and paired19nt RNA cores; other species, lengths, modified constructs and mismatched targets require separately validated adapters and references.

Record organism, exact accession.version or explicit sequence, experiment name, transcript-coverage objective, requested count and provider choice. Default to20 nonoverlapping research-review candidates, not a guarantee of20 qualifying designs. Ask when transcript/organism/variant choice affects correctness. Cell, assay, chemistry and delivery can remain unresolved for context-independent sequence work but must block dependent biological claims.

Inspect actual tools and complete contracts. When an authorized matching Boltzmann workflow exists, follow the plugin route unless the user explicitly chooses local/another provider. Absence from a visible tool list is not proof a deferred tool is unavailable. Never silently switch after an authentication/contract failure. Local mode is an explicit provider choice, not permission to bypass licensing or transfer restrictions.

## References and generation

Retrieve exact-version original FASTA and annotation bytes. Verify human/gene identity beyond a FASTA header, alphabet, transcript-sense orientation, CDS translation, length/hash, source URL and time. Do not silently normalize malformed accession tokens. Derive approved working copies without modifying originals.

Map every core into each declared transcript independently; preserve every occurrence. Collinear common blocks explain the reference relation but exact per-site lookup is authoritative for repeats. Classify CDS/UTR per transcript: the same shared RNA sequence can occupy different annotated regions.

Use an actual approved generator and record provider/job identity, input/artifact/source/checkpoint hashes, inference mode, score semantics, parameters and resources. Preserve every generated row and duplicate provenance; no unscored sliding-window replacement for a model. Guard header-derived shell calls with approved safe working IDs and original-header mappings. Never append arbitrary bases or infer final chemistry from core19 output.

Submit once and poll the returned job. On an interface timeout inspect the matching request, process, log and result; ambiguous execution is not a license to resubmit. Recover the same job when live. Preserve wrapper failures separately from scientific failures.

Native OligoFormer omits explicit eval mode. Preserve native scores; any eval-mode comparison must be separately named/versioned, use the actual verified cache and checkpoint, record seeds/batch size/all-module eval flags and repeatability. Do not rerun RNA-FM merely to change inference mode, or describe eval mode as proved better biology. Its class1 output times1.341 is its own scale, not measured inhibition.

## Assessments and critique

Require documented5to3 guide/passenger orientation, exact19nt complementarity and coordinates, unique primary mapping and the protocol's true full57nt context when required. Valid cores near an edge or at repeated sites can be model-ineligible; retain them with explicit reasons rather than fabricating flanks or using the first match.

Keep endpoints separate: Ridge is an unbounded linear estimate, RN.Ai-Predict predicted inhibition, RNAiSpline effective-class probability, OligoFormer native/eval scores and native/frozen composite priorities. Prefer the verified frozen Ridge baseline within its audited scope; never fit/refit on unmeasured candidate predictions. Flag values outside0..100 rather than clipping or claiming inhibition above100 percent. If no verified Ridge asset is available, declare that limitation and obtain an explicit ranking-policy decision; do not synthesize coefficients.

Assess structure/accessibility with actual methods/temperature/window settings; these are calculated features, not cellular accessibility. Reuse efficacy only for identical guide+full57nt inputs across isoforms and document this as input equivalence, not independent confirmation. Local folding contexts can differ even when57nt inputs match; reuse only identical structure inputs.

Screen BOTH strands. Distinguish native guide-only Bowtie behavior/score-floor limits from an exhaustive declared-scope ungapped0/1/2-substitution scan. Verify reference/scanner hashes and count alignments, transcripts and genes separately. Record skipped ambiguity, gaps, variants and annotation/expression limitations. Count strand positions2..7/8/9 seed complements with explicit overlapping occurrence versus transcript semantics; subtract only the declared on-gene scope. Whole-transcript seed opportunities are not a UTR-only repression model.

Review relevant paralog/pseudogene full and seed evidence, including HRAS/NRAS/KRASP1 for KRAS. A permissive operational filter can pass a perfect outside-gene match. Preserve that filter's semantics while separately flagging reference gene-exclusivity failures. Do not present those entries as gene-exclusive recommendations or silently invent a new biological threshold. Passenger viability annotations and loading uncertainty matter; neutral-scaffold cell viability is not exact-duplex toxicity or immune safety.

Use bounded assessment budgets, immutable source IDs and explicit NOT_RUN coverage. Compare methods on matched eligible cohorts, report disagreement/near-tie tiers and what could reverse preference. Give fewer than requested if unsupported; never pad or relax thresholds to force a count.

## Qualification

Use PASSED, FAILED, BLOCKED_MISSING_EVIDENCE, NOT_RUN and NOT_APPLICABLE with literal Boolean required, evidence_refs, failed_criteria, missing_evidence, warnings and method_version. A required failure takes precedence over required missing; missing/NOT_RUN blocks, never implies a safe score. A mandatory gate cannot evade review by being marked NOT_APPLICABLE.

Retain source/native booleans together with their missing_evidence and failed_criteria; passed=True alone is insufficient. Missing optional software blocks only its dependent conclusion, not independent valid work.

Separate technical integrity, computational screening, predicted potency, specificity, immune assessment, experiments, delivery/context and biological qualification. COMPUTATIONAL_SCREENING_PASSED can be a successful milestone while overall biology remains PARTIAL. Biological qualification requires appropriate actual evidence; the helper gate checker cannot establish it from JSON claims or file existence.

## Mutation arm

Shared transcript targeting is not mutant targeting and has no wild-type-sparing guarantee. Without an exact nucleotide mutation/reference context and mutant-versus-wild-type objective, retain BLOCKED_PENDING_MUTATION_SPECIFICATION and generate zero mutant sequences/candidates. Protein shorthand can be nucleotide-ambiguous. Once specified, first validate the reference allele and mapping; then inspect mutant/WT mismatch positions and model applicability. Perfect mutant match versus WT mismatch is not proof of selective knockdown. Do not use a perfect-match potency model as an unvalidated mismatch-discrimination assay.

## Capability registry

Audit15 categories: reference resolution; sequence validation; generation; transparent baseline potency; complementary efficacy; structure/accessibility; transcript coverage; both-strand full/near matching; seed/family annotations; immune evidence; delivery/assay context; chemistry-aware applicability; measured-data/training exposure; ranking/critique; qualification/reporting.

For each record actual versions/source/mode, checkpoint state, input representation/strand/length, reference hashes, execution/validation evidence, resource usage, rights and limits. Use AVAILABLE_VERIFIED, AVAILABLE_UNVERIFIED, AVAILABLE_WITH_ADAPTER, REQUIRES_INSTALLATION, REQUIRES_EXTERNAL_AUTHORIZATION or UNAVAILABLE. Repository presence is not readiness; ready software is not validated biology.

## Deliverables and stopping

Preserve raw reference responses; target_specification.json; target_sequence.fasta; transcript_isoform_audit.csv; target_reconnaissance.md; tool_capability_registry.json; tool_execution_plan.md; missing_capabilities.csv; generated_candidates.csv; generation/diversity manifests; candidate_assessment_matrix.csv; candidate_tool_outputs/; candidate_failures.csv; candidate_ranking.csv; ranking_comparison.csv; candidate_critique.md; ranking_uncertainty_report.md; qualification_results.json; missing_evidence.csv; checks_to_proceed.csv; evidence_provenance.json; run_manifest.json; hashes and independent verification receipt.

For a design run provide an18-section review: executive summary; objective/target; references/isoforms; ecosystem/workflow; generation; methods/units; comparison table; review designs; selection rationale; rejected alternatives; specificity; structure; disagreement/uncertainty; gates/missing evidence; benchmark/leakage; reproducibility; unsupported conclusions; next action. Adapt audit-only reports to their narrower scope without repeating expensive analyses.

Use COMPLETED/PARTIAL/BLOCKED/NOT_APPLICABLE/FAILED per stage. Seal artifacts only after writers finish. Avoid circular hashes: output manifest excludes itself/root receipt; receipt binds manifest. Snapshot inputs before/after read-only audits. Archive drafts/failures with explicit superseded roles, including their hashes. Never write original sources or treat software fixtures as biological results.
