# Published-model upgrade assessment — Run-5_2026-11-16

Status: PARTIAL. A fresh incumbent control was executed. No new challenger produced valid efficacy predictions; no improved model is claimed or promoted.

## Scope and decision

The user approved local SiaRNA research use and licensed-component ENsiRNA assessment, then explicitly chose published pretrained models only and declined new research-baseline training. This run honors both decisions. Current Boltzmann RNA property contracts were inspected: neither SiaRNA nor ENsiRNA is a selectable documented backend, so no remote scientific job was submitted. The selected incumbent remains RN.Ai-Predict with source guides verbatim. This is retention, not discovery of a new best model.

Seven task frames have fresh control outputs and two blocked challenger branches each. They reuse two underlying input sets, not seven independent biological cohorts. All eleven tasks have task-indexed workflow/status records. Four tasks are explicitly skipped because their benchmark/application inputs or endpoint are unsuitable for these on-target models. All full-design tasks remain incomplete; best_design is null.

## Published model selection and actual readiness

SiaRNA reports PCC 0.5163, Spearman 0.3849 and AUC 0.7586 on 322 independent Simone pairs, making it a relevant candidate for investigation, not proof it will improve this repository.[1]

At the pinned author commit, preprocess.py replaces previously calculated mRNA folding features with two unseeded random 100-element vectors.[2] We executed that exact assignment twice and verified different outputs; this is a software diagnostic, not simulated biological data. The pretrained checkpoint passed weights-only loading and strict architecture/state-dict matching. Efficacy forward inference was deliberately stopped: successful checkpoint loading does not establish valid features. The CLI also returns only its first prediction. All 322 current measured guides are 21 nt and match their full transcripts, but none of the six full transcripts meets the native CLI's 2000-nt mRNA limit. We did not invent shorter transcripts, surrogate AGO2 scores or random/zero learned inputs. See siarna_software_probe.json and native_input_applicability.csv.

ENsiRNA combines RNA-language-model features, structural characteristics and thermodynamic information.[3] Its author README declares Apache v2.0 and documents separate Rosetta acquisition and RNA-FM requirements.[4] The published pre-folded-structure download redirected to accounts.google.com with a Google Drive sign-in page; the alternate file-view URL returned HTTP 401. These observations are recorded in ENsiRNA_asset_assessment.json, not interpreted as a permanent service outage. No verified per-row PDBs are locally available for our evaluation rows, no Rosetta license was accepted, and RNA-FM/PyG are not installed. We did not replace missing structural inputs with zero or generic coordinates. Author dataset CSVs were hash-verified, but the supplied 702-row test CSV has no exact first-19-guide match to our 322-row cohort; it was not relabeled as our benchmark. No ENsiRNA weights or runtime installation was attempted after the required-input blocker was established.

The additional BERT-siRNA repository identifies the published 2024 paper and provides model code.[5] Both exact-name and broader repository searches were performed. The broader search located the author repository; its current complete tree contains source, two CSVs and an image, but no fine-tuned checkpoint. No alternative checkpoint or structure assets were found in either the BERT-siRNA or ENsiRNA GitHub releases listing; see additional_release_assets_audit.json. No training was substituted. This is an asset-availability finding, not evidence of poor predictive performance. The unrelated Siarnaq game returned by the initial SiaRNA metadata search was excluded from scientific model selection.

## Fresh control results

| Matched cohort | n | Prior C00 AUC | Fresh U00 AUC | Change |
|---|---:|---:|---:|---:|
| HIF1A | 100 | 0.7803125 | 0.7803125 | 0 |
| HPSE | 106 | 0.6366228070 | 0.6366228070 | 0 |
| HK2 | 95 | 0.7176214197 | 0.7176214197 | 0 |
| Macro over the three targets | 301 total | 0.7115189089 | 0.7115189089 | 0 |
| Full Simone replay | 322 | 0.7021412837 | 0.7021412837 | 0 |

MYC has seven observations and one positive; its numerical AUC is descriptive only and excluded from the three-target macro result. Fresh predictions exactly reproduced the old scores (maximum absolute difference zero). These data have been examined previously. Replay is a software consistency check, not new independent validation. The repository evaluates observed labels >=0.7; the published SiaRNA training/evaluation code uses >0.7, so its published value is contextual, not an automatically matched-protocol superiority comparison.

The 598-window TTR incumbent replay also exactly reproduced its prior scores. Under this RN.Ai endpoint, patisiran's projected 19-nt core ranks 151 and vutrisiran's ranks 19 among 598 windows. These are not the historical OligoFormer ranks and must not be conflated with them. Anchor recovery is descriptive; chemically unmodified projected cores are not the clinical drugs, and clinical efficacy is not a per-window training label.

## Artifacts and execution

- frozen_workflow_plan.json: decision rule, inputs, hashes and scope frozen before control inference.
- config_execution_ledger.csv: seven control task routes and fourteen blocked task/model routes; copied frames are not independent model runs.
- measured_control_predictions.csv: 322 fresh native RN.Ai predictions.
- ttr_control_predictions.csv: 598 fresh native RN.Ai predictions.
- control_metrics.json, TTR_control_anchor_metrics.csv: calculated endpoints.
- executed_readiness_gates.json: executed fail-closed decisions; blocked branches have no metrics/prediction files.
- performance.png/SVG: extends the historical configuration trajectory with the actual control replay and explicitly unplotted challenger endpoints.
- config/<task>/Run-5_2026-11-16/ and results/<task>/Run-5_2026-11-16/: corresponding task workflows and results/status.

The new local venv inherits pinned scientific dependencies read-only through a .pth file; it is not a fully self-contained dependency installation. Existing environments were not changed and no packages were installed. TensorFlow reported missing GPU runtime libraries and skipped GPU registration; the control completed using the available CPU execution path. GPU management visibility alone was not used as evidence of usable model acceleration. Author source/checkpoint hashes remained unchanged. Model assets stay outside the repository and are not redistributed.

No candidate generation, new model training, battery recomputation, panel reranking, threshold relaxation or complete application workflow was performed. No synthetic scientific results were substituted for the blocked models.

## Verification and reproduction

All 11 package checks and all 45 runtime/artifact tests passed. All prior Run-3 and Run-4 manifest entries verified unchanged. New relative documentation links resolve, all five report sources have verified evidence quotes, and the immutable Run-5 manifest independently verified its recorded entries. These checks establish software/artifact consistency, not biological efficacy or a successful challenger integration. See validation_summary.json, unittest.log, citation_verification.log and PROVENANCE.sha256.

The executed workflow command was the run5-env interpreter with `runtime/run_model_upgrade_20261116.py all`, after the metadata/acquisition/software/asset probes. Verification used `runtime/verify_model_upgrade_20261116.py`. Numerical library threads were limited to two, bytecode writing was disabled, and the profile Matplotlib cache was used. The `all` command now intentionally refuses to overwrite the frozen run. Resume a scientific upgrade only as a new run with resolved model prerequisites, not by editing the retained configs or forcing readiness flags.

## What would unblock a new scientific run

For SiaRNA: an author-corrected/validated deterministic preprocessing and complete cohort feature-generation path, validated handling of the current full-length transcripts, and reliable per-row output, compatible with the released checkpoint. Setting the random seed alone does not make random biological features valid.

For ENsiRNA: accessible, authorized structural assets verified against the actual duplex inputs, or a properly licensed and validated structure-generation installation, followed by the remaining isolated dependencies and input/overlap validation. Obtaining an unrelated 702-row test archive alone would not establish applicability to our cohort.

For BERT-siRNA: an authorized fine-tuned efficacy checkpoint and its tokenizer/config/inference contract; a generic pretrained DNA-BERT encoder alone is not the trained efficacy predictor.

The absence of valid challenger scores means no performance improvement has been established. Incumbent retention is the fail-closed decision, not a claim of global model optimality.

## Sources

[1] https://pmc.ncbi.nlm.nih.gov/articles/PMC13488420
[2] https://github.com/drugparadigm/SiaRNA/blob/0f04a14de283716d812531458ffed7c92373aece/preprocess.py
[3] https://pubmed.ncbi.nlm.nih.gov/40194620
[4] https://github.com/tanwenchong/ENsiRNA
[5] https://github.com/ChengkuiZhao/siRNABERT
