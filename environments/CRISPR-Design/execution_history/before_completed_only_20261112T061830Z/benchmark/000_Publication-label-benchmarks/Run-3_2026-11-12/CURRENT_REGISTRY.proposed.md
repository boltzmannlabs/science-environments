# Benchmark runs — executed evidence and remaining scope

Current: Run-3_2026-11-12 [publication-label report](000_Publication-label-benchmarks/Run-3_2026-11-12/REPORT.md), [numeric metrics](000_Publication-label-benchmarks/Run-3_2026-11-12/reports/measured_label_correlations.csv), [comparability ledger](000_Publication-label-benchmarks/Run-3_2026-11-12/publication_comparability.csv). Run3 executed metrics on retained real predictions, not new model inference. Earlier native inference and full protocols: [Run2](000_Protocol-reproduction/Run-2_2026-11-12/REPORT.md). No complete biological application, therapeutic safety or experimental validation is claimed.

## 1. Cas9 activity — EXECUTED, matched evaluation components

RS3 Sequence and CRISPRon v1: six author-defined training-excluded cohorts;23629unique contexts. Exact publication row-weighted replay, official30nt/tracr inputs, confidence intervals and rankloss retained inRun2. Run3 independently recomputes deduplicated measured-label metrics and paired cluster-resampled model differences. RuleSet2/DeepSpCas9 baselines inRun2 are author-score replays, not fresh inference. OriginalCRISPRonv0internal/<=3mm and RS3Sequence+Target protocols remain outside completed scope.

## 2. Off-target specificity — EXECUTED, assay-matched panel

CFD2016:1684WTSpCas9 assayed sites,108positive/1576negative,9guides. AP0.186039,PR-AUC0.178991;cluster intervals and recall@K retained. Nominal0.1%detection limit; no site-specificrawreadLoD,variant-awareorpopulation evaluation. Not the proposed CHANGEseq/Elevation or Kaufmann genomewide nomination protocol; direct77%top500 comparison would be invalid.

## 3. Base editing — EXECUTED, editor-matched efficiency transfer test

BE-Hive HEK293T/BE4external measured labels,n9975,rho0.165766. Weak result published. This is any-edit efficiency,not BE4max intended-edit purity or bystander-genotype accuracy. BEDICT2/DeepBE/editor-choice or intended-genotype protocols have not run.

## 4. Prime editing — EXECUTED, model-specific held-out evaluations

PRIDICT2.0 groupedOOF intendedrho0.905629HEK293T/0.808119K562;zero originalfold assignment mismatches. DeepPrime base officialHEK293T/PE2fixed-testn28883,rho0.861474. Correct features,weights,labels and percondition scopes retained. Full PRIDICT2pretraining disjointness incomplete;unintended edit is notpurity. No PE3design/outcomeorall-editor generalization claim.

## 5. Cas13 — EXECUTED, qualified published-method reimplementation

RFcombined1000corrected2000tree fits;medianrho0.667308versuspaper~0.67. Source seed schedule/training-onlyscaling recovered. Split/refit percentiles[0.629895,0.700127],notpopulationCI;paper/codeparameter discrepancies disclosed. GFPLOSO0.294688warns against universaltransfer. No TIGER/transcriptomespecificityvalidation.

## 6. Specialized modality evidence

CRISPRiTSSwindow:3607heldoutguides/307genes;componentonly. Diagnostics: completednumeric-onlyEasyDesignauthor-score replay,859commonrows;notclinical/nativeworkflowvalidation. Plant:52N.benthamiana actualplantmeasurements,authorscorereplay. Microbial:642gene-datasetMERFauthorscorecomparisons,median0.381385versuspaper0.396;discrepancyunresolved. Epigeneticfunctionalbenchmark:BLOCKED_MATCHED_ENDPOINT. Library/screenlevel,fullCRISPRa,clinicalandpatientvariantvalidation remain incomplete. None is converted to a success by substituting a mammalian nuclease score.

## 7. Per-task execution records

| Task | Executed evidence/status | Artifacts |
| --- | --- | --- |
| 001 general | SHARED_COMPONENT_BENCHMARKS | [task report](../benchmark/001_general-routing/Run-2_2026-11-12/README.md) |
| 002 knockout_gene_disruption | FRESH_CAS9_COMPONENT_EVALUATION | [task report](../benchmark/002_knockout/Run-2_2026-11-12/README.md) |
| 003 therapeutic_in_vivo_editing | SPECIFICITY_COMPONENT_ONLY | [task report](../benchmark/003_therapeutic-in-vivo/Run-2_2026-11-12/README.md) |
| 004 variant_correction_precision_repair | MATCHED_MODEL_COMPONENT_EVALUATIONS | [task report](../benchmark/004_variant-correction/Run-2_2026-11-12/README.md) |
| 005 base_editing | FRESH_BE4_EFFICIENCY_EXTERNAL_TEST | [task report](../benchmark/005_base-editing/Run-2_2026-11-12/README.md) |
| 006 prime_editing | FRESH_MATCHED_HELDOUT_OUTCOME_EVALUATIONS | [task report](../benchmark/006_prime-editing/Run-2_2026-11-12/README.md) |
| 007 crispr_regulation | CRISPRI_WINDOW_COMPONENT_TEST_ONLY | [task report](../benchmark/007_regulation/Run-2_2026-11-12/README.md) |
| 008 epigenome_editing | BLOCKED_MATCHED_EPIGENETIC_ENDPOINT | [task report](../benchmark/008_epigenome-editing/Run-2_2026-11-12/README.md) |
| 009 rna_targeting_cas13 | COMPLETED_QUALIFIED_RFCOMBINED_REIMPLEMENTATION | [task report](../benchmark/009_rna-targeting-cas13/Run-2_2026-11-12/README.md) |
| 010 diagnostics_pathogen | COMPLETED_NUMERIC_AUTHOR_SCORE_REPLAY | [task report](../benchmark/010_diagnostics/Run-2_2026-11-12/README.md) |
| 011 library_screen_design | SHARED_GUIDE_METRICS_NOT_SCREEN_VALIDATION | [task report](../benchmark/011_library-screen-design/Run-2_2026-11-12/README.md) |
| 012 plant_genome_editing | PLANT_ASSAY_MATCHED_AUTHOR_SCORE_REPLAY | [task report](../benchmark/012_plant-editing/Run-2_2026-11-12/README.md) |
| 013 microbial_crispr_design | BACTERIAL_PHENOTYPE_AUTHOR_SCORE_REPLAY | [task report](../benchmark/013_microbial/Run-2_2026-11-12/README.md) |

## Historical plans and runs

Original registry is preserved in [Run3pre-update snapshot](000_Publication-label-benchmarks/Run-3_2026-11-12/public_update_snapshot/benchmark/BENCHMARK_RUNS.md); earlier runs remain unchanged. Old NOT_EXECUTED plan rows are historical, not the current execution status. XiangDay10+dox had incomplete training-exposure audit;D8/D10concordance is not a predictor ceiling. Mathis2023rho0.85intended/0.78unintended isPRIDICT1,notPRIDICT2orpurity.

## No-tuning attestation and limits

No models were fit or tuned inRun3;metrics/resampling and missingness handling are explicit. Existing native-model feature/split manifests apply;this is not blinded newlabel evaluation. Draft application gates remainDRAFT. [Inputhashes](000_Publication-label-benchmarks/Run-3_2026-11-12/input_provenance.json), [execution](000_Publication-label-benchmarks/Run-3_2026-11-12/execution_completed.json), and [comparison limits](000_Publication-label-benchmarks/Run-3_2026-11-12/publication_comparability.csv) make the claims auditable.
