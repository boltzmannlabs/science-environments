# Computational Monoclonal Antibody Benchmark Metrics

The benchmark files contain source-reported computational metrics, numerical reference values, publication years and comparison scopes. See the [task scenarios](../../tasks/monoclonal_antibody_design/README.md) for the matched task definitions.

## Computational Metrics by Source

| Source | Computational metrics retained |
| --- | --- |
| Ab-SELDON / HER2 | REF15 interaction score and final-minus-initial REF15 difference, in REU |
| Germinal / PD-L1 | Global Cα RMSD, CDR sequence identity and interface similarity |
| tFold / PD-1 | AUROC, top-percentile enrichment and CDR-H3 AAR |
| AbFlow / LCAT | AAR, CAAR, TM-score, lDDT, RMSD and DockQ |
| Gal-3BP workflow | Interaction counts, hydrogen-bond contact share, interface RMSD and ΔSASA |
| RFdiffusion / fixed-framework VHH | Spatial aggregation propensity, Rosetta interface ddG, OASis Identity and predicted cross-target specificity |
| AntiBMPNN / huJ3 VHH | Residue-volume descriptor, hydrophilicity descriptor and segment net charge |
| ProteinBase / EGFR | Sequence properties, ESMFold pLDDT, ProteinMPNN scores/recovery, domain confidence and structural-search alignment scores |
| ProteinBase / TREM2 | Sequence properties, ESMFold/ProteinMPNN scores, domain/novelty classes, Boltz2 confidence/interface scores and structural-search alignment scores |
| CHIMERA-Bench | AAR, CAAR, Cα RMSD, Fnat, DockQ and epitope F1 |
| IgDesign | Per-CDR AAR, 1-shot/best-of-100 AAR and predictor-specific CDR/Fv scRMSD |
| IgGM | Per-CDR AAR and backbone RMSD |
| AbBiBench | Within-assay Spearman ρ and fivefold Precision@k |
| FLAb / FLAb2 | Pearson r, Spearman ρ and Kendall τ |
| AbDesign | Per-parent and pooled Pearson r / Spearman ρ |
| AB-Bind | Pearson r and ROC-AUC for computational ΔΔG prediction |
| AbAgym | Mean per-DMS Spearman ρ and ROC-AUC |

## Sources and Versions

| Source family | Publication year | Code/data snapshot | Paper/data reference |
| --- | --- | --- | --- |
| CHIMERA-Bench | 2026 | [mansoor181/chimera-bench @ `c0ada2ff045e`](https://github.com/mansoor181/chimera-bench/tree/c0ada2ff045e1622ef39e4a25db34724813f378a) | [Paper](https://arxiv.org/abs/2603.13431); [data](https://zenodo.org/records/20598827) |
| IgDesign | 2023 preprint / 2024 workshop | [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e) | [Paper](https://doi.org/10.1101/2023.12.08.570889); CSV SHA-256 in tasks 009–015 benchmarks |
| IgGM | 2025 conference | [TencentAI4S/IgGM @ `06abc563b3fc`](https://github.com/TencentAI4S/IgGM/tree/06abc563b3fc8c7ea020543add16b69b6f8a1c8d) | [Conference paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/fa5b423e24b442180bcd4e13ae75a27f-Paper-Conference.pdf) |
| AbBiBench | 2025 preprint; v3 2026 | [MSBMI-SAFE/AbBiBench @ `85645eaa9441`](https://github.com/MSBMI-SAFE/AbBiBench/tree/85645eaa94418034ee6ef6e21666b683c142fa02) | [Manuscript v3](https://arxiv.org/html/2506.04235v3); [data](https://huggingface.co/datasets/AbBibench/Antibody_Binding_Benchmark_Dataset) |
| FLAb / FLAb2 | 2024 / 2025 preprints | [Graylab/FLAb @ `e05e3f013578`](https://github.com/Graylab/FLAb/tree/e05e3f0135783ffb7de412df6a1467e7a0031911) | [FLAb](https://doi.org/10.1101/2024.01.13.575504); [FLAb2](https://doi.org/10.64898/2025.12.27.696706) |
| AbDesign | 2025 | Provider dataset | [Paper](https://doi.org/10.1080/19420862.2025.2567319); [data access](https://naturalantibody.com/ab-design/) |
| AB-Bind | 2015 online / 2016 issue | [sarahsirin/AB-Bind-Database @ `f5af13df8000`](https://github.com/sarahsirin/AB-Bind-Database/tree/f5af13df80000ad9e438a6ccf1147bd5f9d55dba) | [Paper](https://doi.org/10.1002/pro.2829) |
| AbAgym | 2025 | [3BioCompBio/AbAgym @ `87af82ad68bb`](https://github.com/3BioCompBio/AbAgym/tree/87af82ad68bb90921e15fb8b79c7bcb1d05b23d3) | [Paper](https://doi.org/10.1080/19420862.2025.2592421) |

## Preparing an Evaluation

- Match the cited source release, paper table/figure, molecular identity, structural preparation and evaluated sequence region.
- Preserve source split membership, candidate budget, selection rule, score direction and aggregation.
- Keep reference sequences, poses and assay labels in the evaluator according to the task's declared conditioning mode.
- Use the source implementation and exact case population for direct numerical comparisons. Label filtered subsets separately and rerun comparators on the same subset.
- Retain input hashes, model/evaluator revisions, seeds, raw scoring outputs and case-level identifiers with each result.

## Reporting and Failure Rules

- Report the actual computational value, units, method, evaluated region and sample count for each scored case.
- Retain signed correlations and the source label/score orientation.
- Keep published reference values and newly executed results in separate fields.
- Record scoring failures with case IDs and reasons; report coverage alongside aggregate performance.
- State bootstrap/resampling settings and confidence levels for uncertainty estimates.
- Preserve source format, contact definition and structural alignment when comparing scores.

## Run Output Fields

Record task/case ID, source citation, input hash, model/evaluator revision, computational metric, value, units, region, sample count and artifact path. For source comparisons, record the published value and its precise scope alongside the new result. IgDesign panel-ranking outputs follow the corresponding task definition.
