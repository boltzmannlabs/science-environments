# Omics Analysis Environment Specification

## 1. Environment overview

**Environment name:** Omics Analysis  
**Version:** v1  
**Primary purpose:** Evaluation of AI agents on independent omics data-analysis tasks  
**Status:** Active benchmark environment under development

This environment contains a collection of independent scientific tasks. Each task defines a biological or computational objective, the data and resources available to an AI agent, the expected outputs, and the criteria used to evaluate the result.

Tasks may use different datasets, omics modalities, organisms, analytical workflows, and evaluation methods. The environment is not limited to a single dataset or analysis type.

The repository currently contains four PBMC3k single-cell RNA-seq tasks. Five additional independent tasks are planned and will be specified separately when they are added.

The environment specification defines shared principles. Each task specification is authoritative for that task's inputs, outputs, constraints, and scoring procedure.

## 2. Objective

Evaluate whether an AI agent can complete an omics-analysis task accurately, reproducibly, and transparently using the data and resources permitted by the task.

The environment should reward:

- Appropriate scientific and computational reasoning
- Dataset-appropriate analytical choices
- Correct and complete machine-readable outputs
- Evidence-based biological interpretation
- Honest reporting of uncertainty and limitations
- Reproducible analysis provenance

The environment should not reward unsupported specificity, unexplained parameter choices, or superficial agreement with a reference output.

## 3. Task model

Every task should document the following:

1. Scientific objective and questions
2. Dataset identity, provenance, and access instructions
3. Omics modality and relevant biological context
4. Input files and their formats
5. Permitted software, references, models, and network resources
6. Required and optional outputs
7. Output schemas and identifier conventions
8. Restrictions and prohibited sources of information
9. Evaluation criteria and scoring rules
10. Reproducibility requirements

Tasks are independent. A task may reuse a dataset or output from another task only when this is explicitly stated in its task specification.

## 4. Inputs and data provenance

Each task must identify its input data clearly and document, where applicable:

- Dataset name, source, version, and stable identifier or download URL
- Organism, tissue, condition, and sample context
- Omics modality and assay technology
- Cell, sample, gene, feature, or observation identifiers
- Matrix orientation and data types
- Whether values are raw, normalized, transformed, imputed, or otherwise processed
- Available metadata, layers, annotations, and prior analyses
- Known limitations, missing information, and possible confounders

The agent must inspect its inputs before analysis and report information that cannot be established reliably.

Input identifiers must be preserved consistently in all derived machine-readable outputs. If rows or observations are filtered, excluded, merged, or unresolved, the task must define how those records are represented and accounted for.

## 5. Permitted resources

Task specifications may permit resources such as:

- Public biological databases and reference annotations
- Published marker or feature sets
- Ontologies and controlled vocabularies
- Pretrained models
- Statistical and machine-learning libraries
- External documentation or network access

The task must distinguish resources available for solving the task from reference data reserved for evaluation. Hidden labels, hidden benchmark files, and evaluator-only outputs must not be accessible to the agent.

Permitted resources should be appropriate for the dataset, organism, technology, and requested resolution. The availability of a package or pretrained model does not establish that it is scientifically suitable for every task.

## 6. Expected agent behavior

An AI agent should:

1. Inspect and validate the supplied inputs.
2. Identify missing, inconsistent, or ambiguous information.
3. Select methods appropriate to the task and dataset.
4. Justify important preprocessing, filtering, modeling, and interpretation choices.
5. Preserve identifiers and maintain consistency across outputs.
6. Generate all required machine-readable outputs.
7. Provide supporting evidence for biological or analytical conclusions.
8. Report uncertainty, conflicting evidence, failed steps, and limitations.
9. Record parameters, software versions, random seeds, and provenance where relevant.
10. Avoid claiming conclusions that are not supported by the data or method.

If a required dependency, input, reference, or computational step is unavailable, the agent must report the limitation and identify the affected outputs rather than silently substituting an unsupported procedure.

## 7. Expected outputs

Each task defines its own required output files and schemas. Depending on the task, outputs may include:

- Cell-, sample-, gene-, feature-, or observation-level result tables
- Quality-control and filtering summaries
- Cluster, group, or class assignments
- Differential-expression or feature-importance tables
- Biological annotations and evidence tables
- Processed data objects such as AnnData or equivalent formats
- Visualizations that support the reported conclusions
- A run manifest containing counts, parameters, seeds, and software versions
- An analysis report describing the workflow and limitations

Machine-readable outputs should:

- Use documented column names and data types
- Preserve original identifiers exactly where required
- Account for retained, excluded, missing, and unresolved records
- Be readable by the evaluator without manual correction
- Contain sufficient metadata to interpret the results

Visualizations should complement the underlying data and evidence. They should not be treated as a substitute for required machine-readable outputs.

## 8. Evaluation principles

Each task must define its evaluation procedure before results are assessed.

### Functional validity

Evaluation may check whether:

- Inputs can be loaded and validated
- Required analysis steps execute successfully
- Required files exist and are readable
- Output schemas and identifiers are valid
- Counts and relationships between outputs are consistent

Successful installation or import checks alone do not establish successful workflow execution or scientific validity.

### Scientific and analytical quality

Evaluation may assess:

- Whether methods are appropriate for the data and objective
- Whether preprocessing and filtering decisions are justified
- Whether reported findings are supported by relevant evidence
- Whether uncertainty and conflicting evidence are acknowledged
- Whether unsupported specificity or overinterpretation is avoided

### Reference-based evaluation

Where reviewed reference labels or results are available, evaluation may report metrics such as precision, recall, F1, macro-F1, correlation, ranking agreement, or task-specific scores.

Reference outputs are not automatically biological ground truth. Their provenance, limitations, annotation granularity, and eligible evaluation records must be documented.

Where reviewed references are unavailable, evaluation should focus on technical validity, analytical reasoning, evidence quality, and reproducibility without claiming independently validated biological accuracy.

Agreement with an automated prediction, tutorial result, or computational baseline must be distinguished from biological correctness.

## 9. Reproducibility

Each evaluated run should record, when applicable:

- Input dataset provenance and version
- Software and model versions
- Preprocessing and filtering decisions
- Analytical methods and parameters
- Random seeds
- External resources and access dates
- Output file descriptions
- Execution instructions
- Observed limitations or deviations from the task specification

Results from one dataset or task must not be presented as evidence of generalization to other datasets, organisms, technologies, or biological contexts unless that generalization has been evaluated explicitly.

## 10. Success criteria

A task is successful when it satisfies its task-specific acceptance criteria and:

1. Produces valid and complete required outputs.
2. Uses methods appropriate to the stated objective and input data.
3. Provides evidence supporting important conclusions.
4. Preserves identifiers and accounts for filtered or unresolved records.
5. Reports uncertainty, limitations, and failed or unavailable steps honestly.
6. Records enough provenance for the analysis to be reproduced or audited.

The exact definition of success is task-specific and must be documented in the corresponding task specification.

## 11. Current and planned tasks

The current repository includes four PBMC3k single-cell RNA-seq tasks covering quality control, filtering, clustering, marker analysis, and cell-type annotation.

Five additional independent omics-analysis tasks are planned. They are not part of the current environment until their task specifications, inputs, evaluation criteria, and supporting artifacts have been added to the repository.
