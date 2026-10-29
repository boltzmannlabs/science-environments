# siRNA Designing Harness — research notes

## Scope and evidence basis

These notes consolidate completed Agent Scientist siRNA work into a research environment. They distinguish historical computed observations, source-reported experiments, hypotheses and missing evidence. Scientific source lists are centralized in [references.md](references.md); do not interpret this document as new model execution or an efficacy benchmark.

The historical case used human KRAS NM_004985.5 with NM_033360.4, NM_001369786.1 and NM_001369787.1 coverage. Exact source versions, annotations, mappings and SHA-256 receipts were verified in the original runs. New-target or new-machine readiness must be checked independently. [R1–R5]

## Observed computational results

- 5,288 unique generated 19-nt cores; 5,243 primary sites exact-covered across the four references.
- 100 candidates deep-assessed; 81 passed inherited operational filters.
- 20 nonoverlapping candidate records investigated; six had perfect outside-KRAS matches on a strand. Two implicated guide co-matches to KRASP1 and four passenger co-matches to ETFRF1 annotations.
- 14 had no detected perfect outside-KRAS match within the declared unambiguous reference scope. Near/seed concerns remained; this subset was not called safe or off-target-free.
- 14 of the 20 Ridge estimates exceeded the nominal range. Nine of the conditional 14 were extrapolations.
- Excluding extrapolations left five candidates in a numerical sensitivity stratum. Ridge-versus-RN.Ai Spearman changed from −0.165 to −0.600; Ridge-versus-RNAiSpline from 0.327 to −0.500. These were cohort/rank effects, not new biological measurements. [R1–R3]

The source receipts and aggregate summaries are hash-bound in the environment's historical evidence index. These counts are observations of one case, not universally expected outcomes or a new run's test answers.

## Recorded repeat and technical-validation milestone

A later local repeat used the same four frozen exact-version references and new OligoFormer/Bench runs. It reproduced the 5,288-guide pool, 100-candidate assessment, 81 operational passers, 20-site operational panel and14-site no-perfect-outside-gene-match subset. Every reported alignment Hamming distance was independently checked in that run. Reference reuse, new inference and cached reference seed-count lookups were explicitly distinguished. [R9]

The user then supplied those exact14 pairs for a separate siRNA-Bench run. Both required efficacy models returned14 scores; all14 passed the inherited operational filters. RN.Ai predictions ranged83.94–92.00 and RNAiSpline probabilities0.6760–0.6897. Recorded values reproduced the earlier assessment exactly. Native Bench prioritized site1391 first rather than the Ridge-leading site280. Agreement/repeatability on this preselected cohort is not independent model-accuracy evidence. [R10]

The repository now includes a bounded source-bound snapshot and an executable standard-library technical report. Its seven mandatory categories are sequence integrity, reference mapping, actual model statuses, configured properties, native filter integrity, earlier-job reproducibility and provenance. The included record passes those technical gates. Raw native gate fields and candidate-specific flags remain visible: nine Ridge extrapolations, four low passenger-seed source annotations, native orientation-metadata gaps and the inherited POTS percentile-direction issue. The report does not rewrite those underlying findings. [R9,R10]

Technical validation covers the declared computational checks; biological efficacy, safety and delivery are separate evaluation stages. The success-first technical headline is appropriate for the environment's defined research deliverable, without replacing the legacy scientific qualification records.

## Literature workflow and discrepancy

The original Pecot article reports shared/pan-KRAS Seq #2 and Seq #3 pairs. Both were recovered in the full generated pool at primary positions 342–360 and 254–272, respectively, but neither entered the original 20 or conditional 14. Thus generation coverage and downstream prioritization disagree; absent panel membership is not failed generation or proof of inactivity. [R5,R6]

Seq3 carried source functionality code 4, identified as a palindrome criterion, despite experimental support reported for the source construct. This motivates prospective criterion review; it does not establish a general false-negative rate or permit silent threshold relaxation. Seq2 passed that functionality check but had lower frozen-Ridge priority. Literature cores had preserved Ridge/native OligoFormer outputs, but no historical deeper/specificity evidence in the assessed subset. A neighboring guide cannot supply that missing evidence. [R5,R6]

The original paper reports greater than 90% protein knockdown for Seq2/Seq3 in its specified models; the follow-up reports an 86–95% mRNA range across its stated contexts. Endpoints, doses/cells and measurement granularity differ. Do not assign pooled prose ranges to individual guides, claim exact chemistry/overhang equivalence, or interpret common research lineage as independent laboratory validation. A third source pair had a retrieved sense/antisense inconsistency; it was preserved and excluded rather than repaired. [R5–R7]

## Independent experimental benchmark audit

A bounded local audit covered five experimental tables with 7,663 record/endpoint cells (not independent experiments), six released training/development reference files and additional local data. It retained missing labels, repeated doses and distinct reporter/native endpoints. Official source versus derivative row counts, blank-header parsing corrections and endpoint-ID fixes were preserved in the original audit trail. Some local files were Git LFS pointers, not measurements. [R4]

No auditable compatible independent common cohort was established. Final-checkpoint development exposure remained unresolved for pretrained models; classic compilations overlapped training/development sources, and newer modified/scaffold-specific constructs were not equivalent to unmodified 19-nt model inputs. The transparent Ridge partition was documented separately rather than marked universally unknown. The outcome was BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET: zero independent predictions, null metrics and no new untouched test. [R4]

This does not prove favorable or unfavorable model performance. A future model-specific or out-of-domain test could be valid with appropriate provenance, representation and endpoint contracts, but was not established by that work.

## Scientific design decisions

1. Separate literal sequence validation, model applicability, operational filters, specificity acceptance and biological qualification.
2. Prefer actual provider/tool contracts; the procedural skill does not confer scientific tool access, rights or credentials.
3. Keep compatible predictor endpoints separate; frozen composites are exploratory, not calibrated efficacy.
4. Review both strands and state reference/ambiguity/mismatch/seed scope. Source neutral-scaffold viability is not duplex toxicity or immune tolerance.
5. Reuse verified completed work. Audit and sensitivity tasks do not repeat generation, models, folding or screening merely to produce another report.
6. Keep raw source labels, exclusions and missingness. No silent averaging, clipping, strand correction, arbitrary truncation or imputation.
7. Mark mutation-selective work BLOCKED_PENDING_MUTATION_SPECIFICATION until exact mutation/reference context and WT-sparing objective are provided.
8. Fail closed for independent-data eligibility, but complete useful source/provenance audits and technical checks rather than fabricate results.

These are workflow safeguards derived from the case and protocols, not efficacy/safety guarantees. [R1–R5,R8]

## Open questions and evidence needed

- Final construct/chemistry/overhang applicability and exact source equivalence.
- Intended cell/tumor, expressed isoforms, allele expression and passenger loading.
- Acceptable guide/passenger full/seed specificity criteria and actual repression evidence.
- Compatible immune assessment, delivery/assay context and therapeutic window.
- Checkpoint training/development membership and a genuinely compatible independent measured dataset.
- Prospective evaluation of heuristic exclusions before altering criteria.
- Backend deployment/registration checks on a new host and rights review for each dependency.

## Current conclusion

Retain the conditional computational panel plus separately labelled literature-supported comparator cores for future review; no winner or biological qualification is forced. Shared-target computational completion is historical and preserved. Biology remains PARTIAL; mutation and independent-data blockers remain explicit. This repository build implements a technical environment and specification, not new experiments. [R1–R5]
