# Gene-Silencing RNA campaign Run-3_2026-11-11

Status: PARTIAL. All 11 task documents have an explicit execution record; nine application frames have candidate panels, two use published-reporter EVALUATE mode. No full application task is claimed complete because required context/annotation stages remain unrun.

## Repository structure

`tasks/` contains workflow specifications, not executable batch jobs. `config/` contains schemas, immutable gates and syntax-only example briefs. `runtime/` contains three inherited scripts plus additive campaign orchestration. `results/00N_<application>/<RunID>/` holds inputs, candidates, per-dimension evidence, gates, panels and provenance. `benchmark/00N_*/<RunID>/` links the evaluation evidence. External backends, reference indexes and checkpoints remain outside the repository.

## Execution and accounting

Fresh generation: 5877 windows across TTR, PCSK9 and TNF. Historical full-pool reuse: 9311 windows across HK2 and MYC. The full battery ran freshly on 120 unique target candidates (24 per target), with an additional passenger-strand near-match screen. The nine application panels contain 51 rows representing 31 unique guide sequences; shared-target frames are not independent validations.

| Task | Target | Gate survivors | Panel | Stable under all ±25% perturbations | Status |
|---|---|---|---|---|---|
| 001_general | TTR | 18 | 5 | True | PARTIAL_APPLICATION_CONTEXT |
| 002_oncology | HK2 | 10 | 6 | False | PARTIAL_APPLICATION_CONTEXT |
| 003_genetic-disease-total-lowering | TTR | 18 | 5 | True | PARTIAL_APPLICATION_CONTEXT |
| 004_genetic-disease-allele-selective | HTT | None | 0 | None | PUBLISHED_REPORTER_EVALUATION_EXECUTED |
| 005_metabolic-liver-galnac | PCSK9 | 19 | 6 | False | PARTIAL_APPLICATION_CONTEXT |
| 006_systemic-lnp | TTR | 20 | 5 | False | PARTIAL_APPLICATION_CONTEXT |
| 007_neuro-cns | HTT | None | 0 | None | DEGRADED_CONTEXT_EVALUATION_ONLY |
| 008_inflammation-immune | TNF | 19 | 6 | False | PARTIAL_APPLICATION_CONTEXT |
| 009_functional-genomics | HK2 | 15 | 6 | True | PARTIAL_APPLICATION_CONTEXT |
| 010_gene-regulation | MYC | 17 | 6 | True | PARTIAL_APPLICATION_CONTEXT |
| 011_drug-target-validation | HK2 | 14 | 6 | False | PARTIAL_APPLICATION_CONTEXT |

## Published reference

OligoFormer reports inter-dataset Mixset AUC 0.8163, PRC 0.8143, F1 0.769 and PCC 0.5879; these are a different model/cohort/protocol from the RN.Ai Simone replay and cannot support a superiority delta.[1]
Sciabola supplies the biological rationale and prospective siRNA assay context; the locally supplied extracted cohort and dose/sequence handling remain explicitly distinct from a full paper replication.[2]
Pfister Table 2 supplies the 26 literal guides, SNP mismatch identities, secondary mismatches, reporter IC50 values and censored outcomes used for the reporter re-evaluation.[3]
Goodchild screened 207 sequences and described incomplete sequence determinants of innate activation; the small motif-only cohort here is not that complete screen.[4]
APOLLO, ORION-10/11 and HELIOS-A provide clinical modality context only: their neurological and LDL endpoints cannot be compared numerically with predicted mRNA inhibition of unmodified 19-nt cores.[5][6][7]

## Run configuration

User-approved Boltzmann execution was attempted once. Job `6af45c45b7e34e64c3637a3a` returned a confirmed terminal OligoFormer inference failure and no candidate artifact. The user then explicitly approved local execution. The failure and approved fallback are preserved in boltzmann_attempt.json; the remote job was not resubmitted.

Inputs: TTR ENST00000237014.8 verified against installed GENCODE v50; HK2 NM_000189.5, MYC NM_002467.6, PCSK9 NM_174936.4 and TNF NM_000594.4 independently retrieved from NCBI RefSeq and identity-checked. Single-reference scope is declared, not all-isoform coverage. Frozen gates are unchanged. Each target reviews the native top 100, then runs the expensive battery on up to 24 cheap-funnel survivors; the budget is not silently expanded to force a quota. Labels are joined only after candidate selection.

Application defaults are adopted—not misrepresented as individually specified user priorities. GU top-decile for the TNF frame is the inherited scanner statistic over the 24-candidate evaluated cohort, not a population-calibrated threshold. The inherited ranker has no immune weighted component; its immune weight contributes zero after hard filtering. Unknown weighted dimensions are disclosed rather than imputed. R3 requires distinct guide seeds and at least 19 nt between selected start coordinates; the ±25% stability report is recomputed after this diversity step.

## Benchmark metrics

| Endpoint | Published/prior | Run-3 | Interpretation |
|---|---|---|---|
| RN.Ai Simone AUC, n=322 | Prior 0.7021 | 0.7021; row CI [0.6286, 0.7705] | All 322 paired predictions match exactly; no improvement claim |
| RN.Ai Simone Pearson / Spearman | Prior 0.5074 / 0.3930 | 0.5074 / 0.3930 | Fresh inference |
| TTR projected drug-core ranks | Patisiran 107; vutrisiran 62 of 598 | 107; 62 of 598 | Fresh generation reproduces ranks; chemistry not modeled |
| HK2 OligoFormer AUC, n=95 | Prior 0.6445 | 0.6445 | Historical OligoFormer scores reused; fresh RN.Ai AUC 0.7176 |
| MYC, n=7 | One positive at cutoff 0.7 | Exploratory metrics only | AUC can be numerically 1.0 with one positive; not robust discrimination |
| HTT RN.Ai Spearman vs -log10 IC50 | Prior 0.296 | 0.2630 | Context recipe differs; absent real flanks, not a guaranteed lower bound |
| HTT ΔΔG vs log DR, uncensored n=21 | No comparable published correlation | -0.3080 | Exact paper mismatch identities; five censored rows excluded from this correlation |
| UGUGU-only sensitivity / specificity, n=8 | Prior 0.10 / 1.00 on different subset | 0.1429 / 1.0000 | 1 TP, 6 FN, 1 TN, 0 FP; changed cohort, not improved model |

Row-bootstrap intervals are descriptive: overlapping sites and common transcripts undermine row independence. A transcript-cluster bootstrap is also saved; only six clusters exist and it is exploratory. CIs are suppressed for per-gene class counts below five. No p-value fishing, refitting or threshold tuning was performed. No equivalence or superiority conclusion is drawn from overlapping confidence intervals. Existing head-to-head claims were not rerun.

## Corrections, limits and next evidence

1. Primary RefSeq resolves NM_001530.4 as HIF1A, not HIF1AN. A historical README claiming HIF1AN and a gene-scoping correction is inconsistent with this primary record; preserve the old artifact but do not inherit that identity claim. The fresh selected targets use verified symbols.
2. The old PCSK9 input ENST00000713785.1 is labeled nonsense_mediated_decay in its own header. The new GalNAc-context run uses RefSeq transcript variant 1 NM_174936.4; the old HIF1A metabolic-frame demonstration is not a PCSK9 validation.
3. The Goodchild PMID 19888456 is unrelated. The verified paper is PMID 19630977, DOI 10.1186/1471-2172-10-40; the derived immune table records original and corrected IDs.[4]
4. The inherited ranker checks only guide UGUGU, omits several application vetoes and lacks an immune scoring dimension. The additive campaign wrapper applies fail-closed numeric gates, either-strand UGUGU, TNF GU-decile and conservative paralog vetoes before invoking it; no original runtime source was edited.
5. The raw harness emits a legacy composite rank involving two efficacy predictors. That raw field is retained only in the raw battery artifacts and is explicitly NOT USED: it is removed from campaign delivery tables and panels. The campaign preference ordering uses RN.Ai alone as efficacy, with independent OligoFormer evidence, never an efficacy ensemble.
6. The scanner docstring overstates UGUGU as necessary-and-sufficient and synthetic RNA as categorically RIG-I-inert. Those statements are not endorsed; the sourced paper supports incomplete context-dependent sequence determinants, not a safety guarantee.[4]
7. E4e remains NOT_RUN(broken-binary). GTEx/HPA tissue context, OpenTargets orthogonal context, CDS/UTR/Tm annotations, 6/8-mer occurrence counts and full isoform coverage were not completed in this bounded campaign. All claimed completed branches are enumerated; no absence is converted to a pass.
8. Allele-selective DESIGN is blocked pending a verified reference/variant and explicit allele objective. CNS DESIGN is not substituted by proxy-context reporter scoring. Reporter-derived target footprints do not establish patient allele selectivity.
9. Required next evidence: target mRNA/protein measurements; multiple independent seeds; non-targeting and orthogonal/rescue controls; expression and paralog review; modality-appropriate delivery, innate response and toxicity measurements. No clinical dosing or therapeutic qualification follows from this campaign.

All computational candidate panels are capped at NEEDS_EXPERIMENTAL_VALIDATION and best_design=null. No experimental result was generated or invented.

## Artifacts

Entry points: task_execution_status.csv, campaign_counts.json, benchmark_comparison.csv, gene_model_comparisons.csv, transcript_verification.json, endpoint_summary.json, and the sources/ register. Each results task directory includes a report and provenance. Raw external output and native model semantics remain separate from derived interpretation.

## Search coverage

Targeted—not systematic—curation used PubMed seed-identifier fetches, PMC full text and NCBI RefSeq. Queries included `Sciabola siRNA 2013` (one hit), `10.1186/1471-2172-10-40` (three search hits, one identity-verified match), `"patisiran" "APOLLO" randomized` (22 hits, top three returned), and `"Two Phase 3 Trials of Inclisiran"` (11 hits, top three returned; query translation warning retained). An initially overconstrained joint patisiran/inclisiran query returned zero and was replaced by separate queries. The seven selected references were read as full text or detailed metadata, not inferred from titles. Full-text truncation is recorded in sources/fulltext_manifest.json. No claim of comprehensive latest literature coverage is made.

## Verification

The pinned siRNA-Bench interpreter passed all 11 specification checks and all 24 runtime/artifact tests, including preservation of the original 19 benchmark and 11 result checksums, all 11 task records, complete window coverage, guide/passenger coordinate identity, fail-closed panel gates, seed/site diversity, score separation, exact predictor replay, paper mismatch/censoring handling and the guard against rewriting an already evaluated run. Real execution logs are in `spec_validation.log`, `unittest.log` and `validation_summary.json`. These tests establish software/artifact consistency, not biological validation. The final `PROVENANCE.sha256` is checked from the environment root with `sha256sum -c benchmark/011_Campaign-reproduction/Run-3_2026-11-11/PROVENANCE.sha256`.

## Sources

[1] https://pubmed.ncbi.nlm.nih.gov/39321261 — OligoFormer: an accurate and robust prediction method for siRNA design
[2] https://pubmed.ncbi.nlm.nih.gov/23241392 — Improved nucleic acid descriptors for siRNA efficacy prediction
[3] https://pubmed.ncbi.nlm.nih.gov/19361997 — Five siRNAs targeting three SNPs in Huntingtin may provide therapy for three-quarters of Huntington’s disease patients
[4] https://pubmed.ncbi.nlm.nih.gov/19630977 — Sequence determinants of innate immune activation by short interfering RNAs
[5] https://pubmed.ncbi.nlm.nih.gov/29972753 — Patisiran, an RNAi Therapeutic, for Hereditary Transthyretin Amyloidosis.
[6] https://pubmed.ncbi.nlm.nih.gov/32187462 — Two Phase 3 Trials of Inclisiran in Patients with Elevated LDL Cholesterol.
[7] https://pubmed.ncbi.nlm.nih.gov/35875890 — Efficacy and safety of vutrisiran for patients with hereditary transthyretin-mediated amyloidosis with polyneuropathy: a randomized clinical trial.
