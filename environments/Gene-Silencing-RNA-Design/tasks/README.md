# Tasks — Gene Silencing RNA Design

One task per runnable application, plus the general routing task. All share the environment
battery, frozen gates and ranking contract ([ENVIRONMENT_SPEC](../ENVIRONMENT_SPEC.md));
application tasks add required stages, hard vetoes, default weight emphasis, endpoint
distinctions and honest benchmark status. Example requests illustrate syntax only.

| Task | Application | Benchmark status |
| --- | --- | --- |
| [001_gene_silencing_rna](001_gene_silencing_rna.md) | general routing + all modes | see [benchmark/](../benchmark/README.md) |
| [002_gene_silencing_oncology](002_gene_silencing_oncology.md) | oncology (e.g., KRAS) | **benchmarked** ([HPSE+HK2](../benchmark/002_Oncology-HPSE-HK2-cohorts/README.md)) |
| [003_gene_silencing_genetic-disease-total-lowering](003_gene_silencing_genetic-disease-total-lowering.md) | genetic disease, total lowering (TTR) | **benchmarked** ([approved-drug cohort](../benchmark/003_TTR-approved-drugs-cohort/README.md)) |
| [004_gene_silencing_genetic-disease-allele-selective](004_gene_silencing_genetic-disease-allele-selective.md) | genetic disease, allele-selective (HTT) | **benchmarked** (ΔΔG arm; DESIGN arm gated) |
| [005_gene_silencing_metabolic-liver-galnac](005_gene_silencing_metabolic-liver-galnac.md) | metabolic / liver, GalNAc (PCSK9) | **benchmarked frame** ([HIF1A case](../benchmark/005_HIF1A-case-study/README.md)) |
| [006_gene_silencing_systemic-lnp](006_gene_silencing_systemic-lnp.md) | systemic / LNP (TTR) | descriptive anchor (patisiran) |
| [007_gene_silencing_neuro-cns](007_gene_silencing_neuro-cns.md) | neurodegeneration / CNS (MAPT) | **benchmarked** (EVALUATE arm, limited) |
| [008_gene_silencing_inflammation-immune](008_gene_silencing_inflammation-immune.md) | inflammation / immune modulation (TNF) | **benchmarked** (IFN cohort, scanner calibration) |
| [009_gene_silencing_functional-genomics](009_gene_silencing_functional-genomics.md) | functional-genomics panels (KIF11) | **benchmarked** (panels, overlap-limited) |
| [010_gene_silencing_gene-regulation](010_gene_silencing_gene-regulation.md) | gene-expression regulation (MYC) | **benchmarked** (MYC n=7, percentile-only) |
| [011_gene_silencing_drug-target-validation](011_gene_silencing_drug-target-validation.md) | drug-target validation (BCL2) | not benchmarked |

Non-runnable scopes stay out of this list by design: antiviral/pathogen/pest is review-only
(no task); agricultural/plant is inactive pending a species adapter. Adding a task does not
make its application biologically validated — benchmark status is stated per task.
