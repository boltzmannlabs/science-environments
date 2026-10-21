scRNA Cell Type Annotation Environment v1
 1. Environment Overview 

**Environment Name:** Cell Type Annotation Environment  
**Version:** v1  
**Omics Domain:** Single-cell transcriptomics  
**Status:** Specification / Initial Development

 2. Objective

Evaluate whether Agent Scientist can identify and annotate major cell populations from a single-cell RNA sequencing (scRNA-seq) dataset using clustering, marker-gene evidence, and biological references.

3. Scientific Question

Given an scRNA-seq dataset, can the system:

- Identify distinct cell populations.
- Determine marker genes associated with each population.
- Assign biologically meaningful cell-type labels.
- Provide evidence supporting each annotation.
- Report uncertainty or ambiguous annotations where appropriate.

 4. Inputs Required

- Single-cell gene expression dataset in H5AD, 10x Matrix Market format, or an equivalent supported format.

### Optional

- Reference marker-gene database or published marker lists.
- Cell Ontology mappings.
- Dataset and sample metadata.
- Reference cell-type annotations, when available.

### Initial Dataset

**PBMC 3k — peripheral blood mononuclear cells**

Source: [10x Genomics PBMC 3k dataset](https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz)


Expected broad immune-cell populations may include:

- CD4 T cells
- CD8 T cells
- B cells
- Natural killer (NK) cells
- Monocytes
- Dendritic cells


### Future Datasets

- PBMC 4k or other independently documented PBMC datasets.
- Selected Tabula Sapiens subsets.
- Disease-specific public scRNA-seq datasets.

Each additional dataset should have its own documented provenance and evaluation reference.

 5. Agent Actions

Agent Scientist should be able to:

1. Load and inspect the supplied dataset.
2. Assess data quality and report relevant QC metrics.
3. Perform documented preprocessing and normalization.
4. Identify cell populations through clustering or an appropriate reference-based method.
5. Identify cluster-associated marker genes.
6. Consult biological references to support cell-type assignments.
7. Assign cell-type labels and confidence estimates, where supported.
8. Generate an annotation report with supporting evidence and limitations.

6. Expected Outputs

### Primary Outputs

- Cell-level annotation table containing cell identifiers and assigned labels.
- Cluster-level marker-gene table.
- Cluster-to-cell-type mapping.
- Annotation confidence or uncertainty, if available.

### Supporting Outputs

- QC summary.
- Cluster summaries.
- UMAP visualizations, where appropriate.
- Marker-gene evidence tables.
- Analysis configuration, software versions, and parameters.
- Final report describing the workflow, annotations, supporting evidence, and limitations.


7. Reference Workflow and Published Results

The environment should include a documented reference workflow based on an established scRNA-seq analysis procedure.

Candidate workflow reference: [Scanpy PBMC 3k tutorial](https://scanpy-tutorials.readthedocs.io/en/multiomics/pbmc3k.html).

The reference package should document:

- Data preprocessing and QC choices.
- Clustering and marker-identification methods.
- The source of reference cell-type labels.
- Representative marker genes and their supporting evidence.
- Relevant published or reference workflow outputs.
- Known limitations and differences between the reference and the environment's implementation.

Where the original publication or tutorial does not provide authoritative cell-level labels, a reference annotation must be curated and its methodology documented before it is used for evaluation.

8. Success Criteria

The system should:

1. Identify the major cell populations represented in the dataset.
2. Assign biologically plausible cell-type labels at an appropriate level of granularity.
3. Associate each annotation with relevant marker-gene evidence.
4. Produce valid, complete outputs in the required formats.
5. Provide reproducible analysis steps and report uncertainty where appropriate.

9. Evaluation Metrics

9.1 Cell-Type Annotation Accuracy

Measure agreement between predicted cell-type labels and a fixed reference annotation.

Report accuracy and, where appropriate, macro-F1 and per-cell-type precision and recall. Class imbalance and differences in annotation granularity must be considered.

9.2 Adjusted Rand Index (ARI)

Measure agreement between predicted and reference partitions. ARI can be used to assess clustering agreement, but it does not independently establish the biological correctness of cell-type labels.

9.3 Normalized Mutual Information (NMI)

Measure the similarity between predicted and reference partitions or label assignments. Interpret the result alongside other metrics and biological evidence.

9.4 Marker Agreement

Assess whether reported marker genes support the assigned cell types using a documented, cell-type-specific reference marker set.

The evaluation should define how marker overlap is measured and account for differences in marker detection and ranking.

9.5 Output Validity and Reproducibility

Check that required outputs exist, can be parsed, and contain valid identifiers and annotations. Verify that the workflow and software configuration are recorded and that results can be reproduced within defined tolerances.

