# scrnaseq_celltype_annotation v1

## 1. Environment Overview

**Environment Name:** scrnaseq_celltype_annotation  
**Version:** v1  
**Omics Domain:** Single-cell transcriptomics  
**Status:** Specification

This document describes the intended inputs, outputs, agent capabilities, and evaluation requirements for the environment. It does not record a completed implementation or benchmark result.

Computational dependencies are declared in `config/environment.yml`. Concrete datasets, required output formats, and task-specific evaluation criteria are documented under `tasks/`.

The presence of configuration files and task definitions does not establish that environment recreation, workflow execution, or scientific evaluation has been completed successfully.

## 2. Objective

Evaluate whether Agent Scientist can identify and annotate major cell populations from a single-cell RNA sequencing (scRNA-seq) dataset using clustering, marker-gene evidence, and suitable biological references.

The environment should support dataset-appropriate analytical choices and evidence-based uncertainty reporting.

## 3. Scientific Question

Given an scRNA-seq dataset, can the system:

- Identify distinct cell populations.
- Determine marker genes associated with each population.
- Assign biologically meaningful cell-type labels.
- Provide evidence supporting each annotation.
- Report uncertainty or ambiguous annotations where appropriate.

No fixed number of clusters or predetermined set of labels should be imposed independently of the evidence available in the dataset.

## 4. Inputs Required

### Expression Data

A single-cell gene-expression dataset in one of the following formats:

- AnnData `.h5ad`.
- 10x Genomics Matrix Market format.
- An equivalent format explicitly supported and documented by the task.

Each task must identify the dataset location and provenance and document, where applicable:

- Organism and available tissue or sample context.
- Cell identifiers and gene-identifier conventions.
- Expression-matrix location and orientation.
- Whether the expression values are raw counts, normalized, transformed, or otherwise processed.
- Relevant expression layers and existing cluster assignments.
- Known limitations or missing information.

The agent must inspect the input before analysis and report information that cannot be established reliably.

### Optional Resources

- Reference marker-gene databases or published marker lists.
- Cell Ontology mappings.
- Additional dataset and sample metadata.
- Reference cell-type annotations, where their use is explicitly permitted by the task.

Reference annotations available to the agent for annotation assistance must be distinguished from labels reserved for evaluation.

Datasets, pretrained annotation models, and biological reference resources are separate from the software dependencies declared in `config/environment.yml`.

Annotation resources must be appropriate for the organism, tissue, technology, and requested annotation resolution. Availability of a software package does not establish suitability of its pretrained models for every dataset.

Each task must specify permitted external resources and any network-access restrictions. Labels reserved for evaluation must remain outside the task-solving agent's accessible inputs.

## 5. Agent Actions

Agent Scientist should be able to:

1. Load and inspect the supplied dataset, including its structure, identifiers, metadata, and preprocessing status.
2. Assess data quality, report relevant QC metrics, and justify filtering decisions.
3. Assess potential doublets when required by the task or appropriate for the dataset. Document the method, settings, predictions, and any resulting exclusions. Distinguish an unavailable or failed assessment from a negative prediction.
4. Perform preprocessing and normalization when required, avoiding inappropriate repeated transformations.
5. Identify cell populations through clustering or an appropriate reference-based method.
6. Identify cluster- or population-associated marker genes when applicable.
7. Consult suitable biological references to support cell-type assignments.
8. Assign cell-type labels and explicitly identify ambiguous, conflicting, or unresolved assignments.
9. Provide numerical confidence estimates only when supported by the method and accompanied by an explanation of their interpretation.
10. Generate an annotation report containing the workflow, supporting evidence, uncertainties, and limitations.

Existing preprocessing results or cluster assignments may be reused when justified. Analytical methods and parameters should be selected according to the dataset and task requirements.

If required data, dependencies, or reference resources are unavailable, the agent must report the limitation and identify the affected analytical steps.

## 6. Expected Outputs

### Primary Outputs

- A cell-level annotation table containing cell identifiers and assigned labels, including an explicit value for unresolved assignments.
- A cluster- or population-level marker-gene table when marker analysis is performed.
- A cluster-to-cell-type mapping when clustering is performed.
- Annotation evidence supporting the proposed labels.
- Explicit reporting of ambiguous or unresolved assignments and annotation limitations.
- An analysis report describing the input assessment, workflow, preprocessing decisions, annotations, supporting and conflicting evidence, uncertainties, and limitations.

Numerical confidence estimates are optional. When provided, their meaning and limitations must be documented. They must not be presented as calibrated probabilities unless that interpretation is justified.

### Supporting Outputs

Depending on task requirements:

- QC and filtering summaries.
- Cluster or population summaries.
- UMAP or other suitable visualizations.
- Marker-gene evidence tables.
- An annotated AnnData object or equivalent reusable dataset.

Each task must specify required artifacts, filenames, output locations, formats, and fields.

Machine-readable outputs must preserve consistent cell identifiers. Retained, excluded, and unresolved cells must be accounted for. Visualizations must complement the underlying annotation and evidence outputs.

## 7. Evaluation

Each task must define its evaluation procedure before results are assessed.

### Functional and Output Evaluation

Evaluation should check whether:

- The declared input can be loaded and validated.
- Required analytical steps execute successfully.
- Required outputs exist and are readable.
- Output fields and cell identifiers are valid and consistent.
- Excluded and unresolved cells are accounted for.
- Supporting evidence and analysis provenance are provided.

Successful installation or import checks alone do not establish successful workflow execution or annotation quality.

### Dataset-Specific Annotation Evaluation

All tasks are assessed for technical validity, justified analytical choices, supporting biological evidence, uncertainty reporting, and reproducibility.

Where suitable reviewed cell-level reference annotations are available, tasks may additionally report per-cell-type precision, recall, F1, macro-F1, and annotation coverage. Reference provenance, limitations, annotation granularity, and eligible evaluation cells must be documented.

Where suitable reviewed annotations are unavailable, evaluation assesses analysis quality and biological support without claiming independently validated numerical annotation accuracy.

Unreviewed computational outputs, including automated predictions and tutorial results, may serve as comparison baselines. Agreement with those baselines must be distinguished from biological correctness.

Comparisons must align cells by their original identifiers and document any label harmonization. Shared cells, excluded cells, and unresolved assignments must be reported. Each task must define how exclusions and unresolved assignments affect scoring.

Matching cluster identifiers, cluster counts, marker rankings, or visualization coordinates is not required unless explicitly specified by the task.

### Uncertainty and Evidence

Evaluation should assess whether:

- Proposed labels have relevant supporting evidence.
- Conflicting evidence is acknowledged.
- Unsupported specificity is avoided.
- Ambiguous populations remain unresolved when appropriate.
- Numerical confidence estimates, if provided, have a documented interpretation.

### Reproducibility

Each evaluated run should record:

- Input dataset provenance and version or stable identifier.
- Preprocessing and filtering decisions.
- Analytical methods and parameters.
- Random seeds where applicable.
- Software and annotation-resource versions.
- Execution instructions and observed limitations.

Results on PBMC 3k alone must not be presented as evidence of generalization across all tissues, organisms, technologies, or disease contexts.

## 8. Success Criteria

A task is successful when it satisfies its declared acceptance criteria and:

1. Identifies cell populations at a level supported by the dataset and task.
2. Assigns biologically plausible labels with relevant supporting evidence.
3. Reports ambiguous or unresolved assignments without forcing unsupported labels.
4. Produces valid and complete required outputs.
5. Records reproducible analysis steps and relevant provenance.
6. Meets the task's predefined evaluation requirements.

## 9. Computational Environment Verification

Software dependencies and version requirements are declared in `config/environment.yml`. Installation and verification commands must be documented in `README.md`.

Installation and verification must avoid relying on packages outside the declared environment. The documented procedure should set `PYTHONNOUSERSITE=1` before environment creation and testing.

The repository should provide `tests/test_environment.py` with synthetic-data smoke tests for required imports, dependency consistency, preprocessing, dimensionality reduction, clustering, marker analysis, data storage, and plotting.

These checks require no biological dataset, reference results, or pretrained annotation model. CellTypist and Scrublet receive import checks; their prediction workflows require separate validation.

Passing the tests confirms that the tested software operations execute successfully. It does not establish biological annotation accuracy or compatibility with every dataset or computing platform.

Verification should be repeated after dependency changes or environment recreation. Verification records should identify the tested configuration, platform, Python version, and outcome.
