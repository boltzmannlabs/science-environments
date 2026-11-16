# Task: 08_dlpfc_spatial_domain_identification

## Description

Identify spatially coherent gene-expression domains in a human dorsolateral prefrontal cortex (DLPFC) tissue section using spatial transcriptomics data.

Characterize the molecular features of the inferred domains, identify genes that distinguish them, and propose biologically supported interpretations of their spatial organization. Report uncertainty and limitations, and ensure that domain assignments and interpretations are supported by evidence from the data.

## Dataset

- **Name:** Human dorsolateral prefrontal cortex (DLPFC), spatial transcriptomics
- **Organism:** *Homo sapiens*
- **Tissue:** Dorsolateral prefrontal cortex
- **Assay:** 10x Genomics Visium spatial gene-expression profiling
- **Sample ID:** 151673
- **Format:** AnnData (`.h5ad`)

## Input

The processed dataset is provided in the agent-accessible workspace.

**Dataset path:** `tasks/08_dlpfc_spatial_domain_identification/DLPFC_151673_agent_input.h5ad`

The dataset contains gene-expression measurements, spot identifiers, spatial coordinates, and non-label metadata.

Use the provided dataset as the input for the analysis. Preserve the original spot identifiers and their association with spatial coordinates in all relevant outputs.

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Expression analysis, preprocessing, clustering, and marker-gene analysis |
| AnnData | Store and manage expression matrices, spot metadata, and spatial information |
| Squidpy | Spatial transcriptomics analysis and spatial statistics |
| pandas / NumPy / SciPy | Data handling and statistical analysis |
| scikit-learn | Clustering and dimensionality-reduction utilities |
| Matplotlib / Seaborn | Visualizations |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory.

**`spatial_domains.csv`** contains one row for every spot included in the domain-identification analysis.

| Column | Description |
|---|---|
| `spot_id` | The original spot identifier exactly as it appears in the input |
| `domain_id` | The inferred spatial-domain assignment |

**`domain_markers.csv`** contains marker evidence for each inferred domain, with the following columns where available:

- `domain_id`
- `gene`
- `effect_size`
- `p_value`
- `adjusted_p_value`
- `rank`

If a statistic is not calculated by the selected method, report this clearly rather than providing fabricated values.

**`answers.json`** contains:

- `dataset_id`: dataset identifier
- `spots_input`: number of spots in the input
- `spots_analyzed`: number of spots included in the analysis
- `n_domains`: number of inferred spatial domains
- `domain_interpretations`: proposed interpretation of each domain
- `domain_markers`: top marker genes for each domain
- `supporting_evidence`: evidence supporting each proposed interpretation
- `model`: a short description of the methods used
- `software_used`: software and package versions, including installed packages
- `limitations`: important uncertainties and limitations

## Recommended outputs 

**`spatial_domains.png`**: a spatial plot showing the inferred domain assignments across the tissue section, using the original spatial coordinates.

**`Analysis report.txt`**: dataset summary; quality control and preprocessing; domain-identification methods and parameters; marker-gene evidence; proposed biological interpretations; spatial organization; uncertainties and limitations; and reproducibility details.

## Evaluation

The outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed.

Areas assessed:

- Agreement between inferred spot-level domains and the hidden reference labels
- Identification of biologically meaningful spatial domains
- Marker-gene evidence supporting the inferred domains
- Spatial coherence of the domain assignments
- Biological plausibility and evidence supporting domain interpretations
- Reproducibility, consistency of spot identifiers, and completeness of outputs

Missing recommended outputs may be reported as not scored and do not block evaluation of the required outputs.

## Constraints

- Do not use externally supplied spatial-domain or anatomical labels to determine domain assignments.
- Do not force the results to match a predetermined number of domains.
- Do not infer labels from spot identifiers.
- Do not look for, request, or rely on hidden evaluation or reference material while solving the task.
- Use the provided dataset as the primary source of evidence.
- Clearly distinguish data-supported findings from hypotheses or uncertain biological interpretations.

## Important Instructions

- Solve this task using your general knowledge and reasoning abilities.
- Do not search for, reference, or reproduce solutions from published papers or tutorials.
- Do not attempt to identify the source of this benchmark or look up known solutions.
- Your solution will be evaluated on correctness, biological plausibility, spatial organization, and supporting evidence—not on matching a known reference implementation.
- Prioritize producing the required output files in the specified formats, with consistent spot identifiers.
- Report the analyses actually performed and do not fabricate results, statistics, or biological conclusions.
