# scRNA-seq Cell-Type Annotation — References

**Last reviewed:** 2026-10-29

This bibliography records sources supporting the environment design, reference-pipeline development, and [research notes](research-notes.md). The task definition determines which resources the solving agent may consult. Its restrictions on published papers, tutorials, and known solutions take precedence over inclusion here.

Package versions are defined in `config/environment.yml` within the environment directory. Online `stable` and `latest` documentation can change and may describe a different release; consult the installed release's documentation or source when behavior differs.

## Input data

### R01. PBMC 3K input dataset

- **Source:** 10x Genomics, [3k PBMCs from a Healthy Donor](https://www.10xgenomics.com/datasets/3-k-pbm-cs-from-a-healthy-donor-1-standard-1-1-0), published 2016-05-26; Cell Ranger 1.1.0.
- **Task download:** [Filtered gene-barcode matrix archive](https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz).
- **Role:** Input to the example task. The downloaded archive contains the hg19 expression matrix, genes, and barcodes. The locally inspected input has 2,700 cells and 32,738 genes before workflow filtering.
- **Provenance:** SHA-256 of the locally downloaded archive: `847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5`.
- **Access and limitation:** The dataset page identifies CC BY 4.0 licensing. Preserve attribution and check provider conditions when redistributing. This is one healthy human blood donor, not evidence of performance across tissues or disease contexts. The matrix is not a reviewed cell-level annotation standard.

## Methods and software

### R02. Scanpy

- **Publication:** Wolf, F. A., Angerer, P., and Theis, F. J. (2018). [SCANPY: large-scale single-cell gene expression data analysis](https://doi.org/10.1186/s13059-017-1382-0). *Genome Biology*, 19, 15.
- **Role:** Methodological basis for using Scanpy as the analysis toolkit.
- **Limitation:** Tool availability does not determine suitable filtering thresholds, clustering resolution, or biological labels. Actual run settings must be recorded separately.

### R03. AnnData

- **Source:** [Official AnnData documentation](https://anndata.readthedocs.io/en/stable/).
- **Role:** Expression-matrix storage, cell/gene metadata, layers, analysis results, and reusable data exchange.
- **Limitation:** `.X`, `.layers`, and `.raw` do not establish a preprocessing state by their names alone. Document the values stored in each location; `.raw` need not contain integer counts.

### R04. Feature selection and marker testing

- **Sources:** Official Scanpy documentation for [highly variable genes](https://scanpy.readthedocs.io/en/stable/generated/scanpy.pp.highly_variable_genes.html) and [ranked group-associated genes](https://scanpy.readthedocs.io/en/stable/generated/scanpy.tl.rank_genes_groups.html).
- **Role:** Input requirements, parameters, and interpretation of feature selection and marker-ranking outputs. Seurat-v3 feature selection expects count data and requires `scikit-misc`; marker ranking expects logarithmized expression.
- **Limitation:** Matrix selection must match the method. Cluster-associated significance is exploratory evidence, not experimental confirmation of cell identity or replicated donor-level differential expression.

### R05. Scrublet

- **Publication:** Wolock, S. L., Lopez, R., and Klein, A. M. (2019). [Scrublet: Computational Identification of Cell Doublets in Single-Cell Transcriptomic Data](https://pmc.ncbi.nlm.nih.gov/articles/PMC6625319/). *Cell Systems*, 8(4), 281–291.e9. DOI: `10.1016/j.cels.2018.11.005`.
- **Role:** Computational doublet assessment when appropriate or required by the task.
- **Limitation:** Predictions depend on data and settings and are not experimental doublet labels. Failed or unavailable assessment must not be encoded as an all-negative result.

### R06. Leiden clustering

- **Publication:** Traag, V. A., Waltman, L., and van Eck, N. J. (2019). [From Louvain to Leiden: guaranteeing well-connected communities](https://www.nature.com/articles/s41598-019-41695-z). *Scientific Reports*, 9, 5233.
- **Role:** Graph-community detection used to identify candidate cell populations.
- **Limitation:** A graph community is not itself a validated cell type. Resolution, graph construction, and preprocessing affect the partition; cluster numbering has no biological meaning.

### R07. CellTypist predictions

- **Sources:** [Official prediction-function documentation](https://celltypist.readthedocs.io/en/latest/celltypist.annotate.html); Domínguez Conde et al. (2022), [Cross-tissue immune cell analysis reveals tissue-specific features in humans](https://doi.org/10.1126/science.abl5197), *Science*, 376, eabl5197.
- **Role:** Automated annotation and optional cluster-based voting; interpretation of individual and voted labels.
- **Limitation:** Predictions depend on model scope, expression preprocessing, gene matching, and clustering. Preserve individual predictions when voting is used. A prediction score or cluster vote does not independently establish identity or calibrated confidence.

### R08. Annotation-model selection

- **Source:** [Official CellTypist model catalogue](https://www.celltypist.org/models).
- **Role:** Select resources appropriate to the query's biological context and annotation resolution. Pretrained models are acquired separately from package installation.
- **Limitation:** An immune-cell model is not a comprehensive reference for every tissue or organism. Record the model name, release/version, download source, and checksum for each run; package and model versions are separate.

### R09. Cell Ontology

- **Source:** [Official Cell Ontology website](https://cell-ontology.github.io/).
- **Role:** Optional controlled vocabulary and identifiers for harmonizing supported cell-type labels.
- **Limitation:** Ontology mapping standardizes terminology; it does not validate an annotation. Record the ontology release and leave unsupported fine-resolution mappings unresolved.

## Evaluation and reproducibility

### R10. Clustering agreement

- **Source:** [Scikit-learn adjusted Rand index documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html).
- **Role:** Compare partitions after aligning shared cells by barcode. ARI is invariant to permutations of cluster identifiers and adjusted for chance.
- **Limitation:** Agreement between computational partitions is not independently validated annotation accuracy. Report cell retention and annotation granularity alongside it.

### R11. Annotation performance metrics

- **Source:** [Scikit-learn F1 documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html).
- **Role:** Per-cell-type F1 and macro-F1, together with precision, recall, support, and coverage, when appropriate reviewed evaluation annotations exist. Macro-F1 averages the specified class scores equally.
- **Limitation:** Define evaluation cells, label mappings, zero-support handling, and treatment of excluded/unresolved cells in advance. Scores against unreviewed computational labels measure baseline agreement rather than independently established correctness.

### R12. Python user-site isolation

- **Source:** [Python 3.13 environment-variable documentation](https://docs.python.org/3.13/using/cmdline.html#envvar-PYTHONNOUSERSITE).
- **Role:** `PYTHONNOUSERSITE=1` excludes user-site packages from Python's import path. Enable it before environment creation and verification to reduce accidental reliance on external packages.
- **Limitation:** This does not replace dependency checks, functional tests, or checks of other configuration such as `PYTHONPATH`.

## Evaluator-only comparison resources

These sources support external evaluator research. They are not supplied as permitted solutions to the example task. Their presence in a public bibliography does not enforce access restrictions; the benchmark runner must enforce the task's resource rules.

### R13. Scanpy PBMC 3K tutorial

- **Source:** [Preprocessing and clustering 3k PBMCs](https://scanpy-tutorials.readthedocs.io/en/multiomics/pbmc3k.html).
- **Role:** Historical external workflow comparison for evaluator review.
- **Limitation:** The displayed notebook and separately distributed processed dataset can represent different versions. Tutorial labels are computational interpretations rather than independent experimental cell-level truth. The example task prohibits reproducing tutorial solutions.

### R14. Saved Scanpy processed PBMC artifact

- **Sources:** [Official processed-dataset documentation](https://scanpy.readthedocs.io/en/stable/generated/scanpy.datasets.pbmc3k_processed.html) and [official artifact download](https://exampledata.scverse.org/scanpy/pbmc3k.h5ad).
- **Role:** Frozen external artifact used in local evaluator comparisons; it is not the task's raw input.
- **Provenance:** SHA-256 of the locally inspected download: `0db367b991dd95809732b218539ede489bea99113807f62ebd7ccc970025fe38`.
- **Limitation:** The inspected artifact contains a legacy Louvain analysis; it is not an exact rerun of the displayed Leiden notebook. Confirm actual metadata and matrix transformations rather than assuming current documentation describes every stored field. This checksum identifies the inspected file, not every future download.

## Reference-pipeline development sources

### R15. Scanpy preprocessing and clustering tutorial

- **Source:** Scanpy development team, [Preprocessing and clustering](https://scanpy.readthedocs.io/en/latest/tutorials/basics/clustering.html), official Scanpy tutorial. Bibliography review date: 2026-10-29.
- **Use in this project:** Used as methodological and implementation guidance when understanding cell annotation pipeline. This attribution records a source used to construct the reference workflow; it does not claim an exact reproduction of the tutorial. It is separate from the PBMC 3K comparison tutorial in R13.
- **Scope:** The currently inspected page demonstrates analysis of human bone-marrow mononuclear-cell samples. It is not the PBMC 3K dataset or its evaluation-label source.
- **Version and interpretation:** The URL tracks the changing `latest` documentation. The bibliography review date is not the original consultation date or a frozen tutorial version.This tutorial supports implementation provenance, not independently validated evaluation labels, and does not change the solving agent's task-specific resource restrictions.

## Maintaining this list

Record additions with their purpose, stable identifier or version where available, access conditions, and limitations. Link claims to the relevant source, and retain dataset/model checksums in run provenance. Method papers and documentation support implementation choices; they do not establish that this environment or its annotations have been independently validated.

