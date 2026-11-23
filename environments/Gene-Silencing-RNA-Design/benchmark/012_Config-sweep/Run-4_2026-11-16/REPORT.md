# siRNA fixed configuration sweep — Run-4_2026-11-16

## Outcome

All 11 task-specific configuration folders were created. Nine tasks have executable benchmark/evaluation configurations; 35 task-config result bundles were saved. These reuse 11 unique scientific configurations (four efficacy endpoints/input conventions, four physical-model settings, three degraded-context controls), not 35 independent models or datasets. PCSK9 and TNF performance tuning was skipped for lack of matched efficacy labels.

Observed mean AUC over the three eligible targets increased from 0.7115 (C00) to 0.7203 (C01). This is an exploratory retrospective difference. Other-target config selection yielded 0.7102, versus the 0.7115 baseline: no transferable improvement was demonstrated. Paired target-specific delta intervals for C01 include zero. No config is automatically promoted into production defaults.

## Published reference

The measured target cohorts are derived from Sciabola et al., PMID 23241392, DOI 10.1093/nar/gks1191, with the same locally supplied transcript and outcome records used in Run-3. OligoFormer paper PMID 39321261, DOI 10.1093/bioinformatics/btae577, reports Mixset inter-dataset AUC 0.8163 on a different protocol/cohort; it is cited as context, not a matched superiority threshold. Primary full-text snapshots and detailed source provenance remain in benchmark/011_Campaign-reproduction/Run-3_2026-11-11/sources/.

HTT reporter sequences and mismatch identities come from Pfister et al., PMID 19361997, DOI 10.1016/j.cub.2009.03.030, Table 2. TTR anchors use the previously hash-bound patisiran/vutrisiran projected cores; clinical outcomes are not sequence-level potency labels.

## Run configuration

C00: RN.Ai with source-verbatim guide, 21 nt for measured cohort and 19 nt for generated TTR cores.
C01: RN.Ai with explicitly projected first-19-nt core; guide tokens 20/21 zero-padded.
C02: RNAiSpline with its documented first-19-nt core input.
C03: hash-bound cached OligoFormer native scores, joined by exact coordinate AND guide identity; no new OligoFormer forward pass.

All four efficacy configurations are single, independent endpoints. Native outputs are never averaged or converted into each other. C00/C01 TTR inputs are identical 19-mers and share predictions explicitly. All root-level example configs, frozen biological gates, upstream model code/checkpoints and prior result bundles are unchanged. Historical 24-candidate gate-clean sets are reranked for application panels; no new safety battery or generation is implied.

RNAduplex D00/D01/D02/D03 vary dangles 2/0/1 and the noLP flag, keeping temperature 37 C and default salt 1.021 M fixed. This is physical-model sensitivity, not biological condition optimization. HTT N00/N01/N02 vary input representation when genuine flanks are absent: they are negative/sensitivity controls, not valid-context CNS efficacy tuning.

Execution uses the previously user-approved pinned local backends. Current Boltzmann siRNA contracts were inspected, but do not expose these RN.Ai/RNAiSpline feature-level or physical-model controls. No additional remote submission, installation, training, checkpoint download, or overwrite of another profile was performed.

## Benchmark metrics

| Target | n | C00 RN.Ai native | C01 RN.Ai core19 | C02 RNAiSpline | C03 cached OligoFormer |
|---|---|---|---|---|---|
| HIF1A | 100 | 0.7803 | 0.7709 | 0.7791 | 0.7600 |
| HPSE | 106 | 0.6366 | 0.6671 | 0.6452 | 0.5838 |
| HK2 | 95 | 0.7176 | 0.7229 | 0.6656 | 0.6445 |
| MYC | 7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

MYC has only seven rows and one positive; AUC=1.0 is degenerate and does not prove robust discrimination. It is excluded from config selection. HIF1A/HPSE/HK2 provide the common 301-row main comparison; OligoFormer common coverage including MYC is 308 rows. The other endpoints additionally score the complete 322-row cohort, but unmatched rows are not silently imputed for OligoFormer.

All three C01-minus-C00 exploratory paired AUC confidence intervals cross zero. Row-bootstrap intervals use 1000 class-stratified paired resamples; overlapping sites, shared genes, previously examined labels and multiple comparisons limit inference. The leave-one-target-out procedure chooses only using the other two genes, but this is not an untouched prospective holdout or proof of pretrained-model training independence.

HTT RNAduplex correlations remain approximately -0.30 across the four physical-model configs. Missing-context RN.Ai correlations are approximately 0.259–0.273; these do not establish a better CNS predictor. Five censored reporter discrimination ratios are retained in the data and excluded from exact-value correlations. No physical/input config is selected as a clinical optimum.

## Task coverage

| Task | Config bundles | Status |
|---|---|---|
| 001_general | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |
| 002_oncology | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |
| 003_genetic-disease-total-lowering | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| 004_genetic-disease-allele-selective | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| 005_metabolic-liver-galnac | 0 | SKIPPED_NO_MATCHED_BENCHMARK |
| 006_systemic-lnp | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| 007_neuro-cns | 3 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| 008_inflammation-immune | 0 | SKIPPED_NO_MATCHED_BENCHMARK |
| 009_functional-genomics | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |
| 010_gene-regulation | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| 011_drug-target-validation | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |

General/oncology/functional-genomics/drug-target-validation frames share target-level datasets; systemic-LNP and total-lowering frames share TTR anchors. They are not independent biological validations. Full application tasks remain incomplete where expression/orthogonal/context annotations or reference/variant requirements were previously unrun.

## Tool improvement

Added runtime/sirna_context_audit.py: it requires an exact first-19-nt guide target match before using the upstream tokenizer, preventing the upstream find==-1 path from constructing meaningless flank features. It records actual known flank coverage and duplicate sites instead of trusting a length-only in_domain label. Batched RN.Ai execution is checked against native single-row inference. The new baseline reproduces all 322 prior RN.Ai scores exactly. This is a correctness/traceability improvement; it is not a newly trained model or demonstrated biological efficacy gain.

## Figures and history

Overview: results/001_general/Run-4_2026-11-16/performance_overview.png (also SVG). Each active task has performance.png/SVG and performance_history.csv/JSON; each tried config has performance_until_this_config.png. All points, including flat or worse results, remain visible. The order is a frozen experiment grid, not training epochs. PNG decoding, dimensions and finite plotted axes are checked programmatically; no claim of manual visual review is made.

## Reproduction and audit

Original example JSON files are preserved at config root and copied under their task folders. Per-config benchmark_config.json files are frozen intent; execution.json sidecars record actual execution. Root config/README.md is the index. Results configs are hash-identical to the frozen configs. Use the pinned siRNA-Bench interpreter for runtime/config_sweep_20261116.py and runtime/analyze_config_sweep_20261116.py; existing run directories refuse inference/report overwrite. To start a new experiment, create a new versioned run rather than editing a tried config.

Run registry: benchmark/012_Config-sweep/BENCHMARK_RUNS.md. The historical root run registry is intentionally not edited because the old Run-3 manifest includes it; all 341 historical Run-3 checksum entries can therefore still be verified. All new scientific artifacts are under the requested repository.

## Verification

The pinned scientific interpreter passed all 11 package checks and all 37 runtime/artifact tests. The tests verify all 341 historical Run-3 checksum entries remain unchanged, frozen config/result identity, exact native-baseline replay, target-out selection isolation, explicit cached/identical-input reuse, reporter censoring, panel gates/diversity, and decoding of the overview/task/snapshot images. All new relative links resolve. The immutable Run-4 manifest verified 450 entries. See validation_summary.json, unittest.log and PROVENANCE.sha256. These checks establish software/artifact consistency, not biological validation.

## Evidence status

No newly generated design, assay result or measured efficacy is invented. No model ensemble, label-tuned gate, prospective superiority or clinical equivalence is claimed. Panels remain NEEDS_EXPERIMENTAL_VALIDATION and best_design=null.
