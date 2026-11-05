# Tasks — Gene Silencing RNA Design

One task per runnable application, plus the general routing task. All share the environment
battery, frozen gates and ranking contract ([ENVIRONMENT_SPEC](../ENVIRONMENT_SPEC.md));
application tasks add required stages, hard vetoes, default weight emphasis, endpoint
distinctions and honest benchmark status. Example requests illustrate syntax only.

| Task | Application | Benchmark status |
| --- | --- | --- |
| [gene_silencing_rna_001](gene_silencing_rna_001.md) | general routing + all modes | see [benchmark/](../benchmark/README.md) |
| [gene_silencing_oncology_002](gene_silencing_oncology_002.md) | oncology (e.g., KRAS) | **benchmarked** ([HPSE+HK2](../benchmark/Oncology-HPSE-HK2-cohorts/README.md)) |
| [gene_silencing_genetic-disease-total-lowering_003](gene_silencing_genetic-disease-total-lowering_003.md) | genetic disease, total lowering (TTR) | **benchmarked** ([approved-drug cohort](../benchmark/TTR-approved-drugs-cohort/README.md)) |
| [gene_silencing_genetic-disease-allele-selective_004](gene_silencing_genetic-disease-allele-selective_004.md) | genetic disease, allele-selective (HTT) | **benchmarked** (ΔΔG arm; DESIGN arm gated) |
| [gene_silencing_metabolic-liver-galnac_005](gene_silencing_metabolic-liver-galnac_005.md) | metabolic / liver, GalNAc (PCSK9) | **benchmarked frame** ([HIF1A case](../benchmark/HIF1A-case-study/README.md)) |
| [gene_silencing_systemic-lnp_006](gene_silencing_systemic-lnp_006.md) | systemic / LNP (TTR) | descriptive anchor (patisiran) |
| [gene_silencing_neuro-cns_007](gene_silencing_neuro-cns_007.md) | neurodegeneration / CNS (MAPT) | **benchmarked** (EVALUATE arm, limited) |
| [gene_silencing_inflammation-immune_008](gene_silencing_inflammation-immune_008.md) | inflammation / immune modulation (TNF) | **benchmarked** (IFN cohort, scanner calibration) |
| [gene_silencing_functional-genomics_009](gene_silencing_functional-genomics_009.md) | functional-genomics panels (KIF11) | **benchmarked** (panels, overlap-limited) |
| [gene_silencing_gene-regulation_010](gene_silencing_gene-regulation_010.md) | gene-expression regulation (MYC) | **benchmarked** (MYC n=7, percentile-only) |
| [gene_silencing_drug-target-validation_011](gene_silencing_drug-target-validation_011.md) | drug-target validation (BCL2) | not benchmarked |

Non-runnable scopes stay out of this list by design: antiviral/pathogen/pest is review-only
(no task); agricultural/plant is inactive pending a species adapter. Adding a task does not
make its application biologically validated — benchmark status is stated per task.
