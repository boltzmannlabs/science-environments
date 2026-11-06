# Antibody Design Models and Tools

Model and tool selection should follow the scientific question, antibody format, available inputs and evaluation objective. This guide defines capability requirements and representative use cases for monoclonal, bispecific and multispecific design, including de novo discovery and reference-guided optimization.

The current release provides monoclonal task specifications and benchmark references. Tool integrations and executable workflows are planned additions; current availability is summarized in [status.md](status.md).

## Capability Areas

| Capability | Intended role | Expected evidence |
| --- | --- | --- |
| Target and reference review | Establish sequence identity, construct boundaries, structural provenance and relevant biological context. | Verified input records, chain and residue mappings, missing regions and preparation history. |
| Antibody annotation | Identify domains, chain pairing, framework regions and CDR boundaries under a declared numbering scheme. | Consistent annotations and an explicit record of permitted and protected positions. |
| Candidate generation | Propose candidates within the selected design mode, molecular format and editing constraints. | Complete candidate representations, unique identifiers and traceable sequence origins or reference changes. |
| Structure assessment | Evaluate antibody folding, target complexes and relevant assembled architectures. | Structural models, confidence and geometry measurements, assessed regions and uncertainty. |
| Interface assessment | Examine binding-region compatibility, contacts, clashes and applicable interaction scores. | Candidate-level measurements with target context, definitions and matched reference comparisons. |
| Property assessment | Assess applicable stability, solubility, aggregation, expression, humanness and other sequence or structural liabilities. | Separate property estimates, method applicability and limitations for the evaluated format. |
| Specificity assessment | Compare evidence for intended recognition and relevant alternative targets or binding regions. | Defined comparison panels, controls and the scope of any selectivity conclusion. |
| Architecture assessment | Evaluate binding components, pairing, domain organization and whole-molecule compatibility. | Component-level and assembly-level findings tied to the declared mechanism. |
| Benchmarking and reporting | Compare eligible results, retain uncertainty and produce reproducible summaries. | Metric definitions, benchmark scope, candidate/reference comparisons and supporting artifacts. |

These capabilities describe the intended tool roles. A single model need not cover every role, and a workflow should include only stages justified by the task.

## Representative Use Cases

| Use case | Starting information | Selection and evaluation priorities |
| --- | --- | --- |
| De novo monoclonal design | Target sequence or structure, design objective and any allowed framework or scaffold. | Methods applicable to the available target context and antibody format; explicit candidate origins and independent evaluation. |
| Reference-antibody optimization | Verified paired reference, target context and permitted edits. | Constraint-aware changes and matched reference/candidate assessment of the requested objective. |
| Epitope-directed design | A defined target construct and mapped binding region. | Methods that can represent the supplied epitope constraints and assess accessibility in the relevant target context. |
| Framework-guided CDR design | Complete framework sequences, CDR boundaries and allowed loop changes. | Preservation of protected residues, chain pairing and the declared antibody representation. |
| Humanization | A supplied antibody, humanness objective and properties to retain. | Sequence assessment alongside structural, interaction and developability evidence; humanness scores alone do not establish reduced immunogenicity. |
| Developability optimization | A candidate or reference with identified property concerns. | Methods relevant to the specific liability and format, with explicit trade-offs against binding and structural requirements. |
| Bispecific design | Two intended binding specificities, molecular architecture and any supplied binding components. | Evidence for both specificities and the assembled molecule; evaluation of simultaneous engagement when the mechanism requires it. |
| Multispecific design | Three or more intended specificities and a complete architecture definition. | Applicable component and assembly assessments; explicit identification of interactions or configurations beyond a method's supported scope. |
| Glycan-aware interface assessment | Target modification context, structural mapping and a reference or candidate complex. | Preservation of the declared target context and explicit assumptions when assessing accessibility and interface compatibility. |
| Reconstruction benchmarking | A controlled design input and independently retained reference. | Separation of design inputs from held-out evaluation evidence, with matching sequence, structure and interface metric definitions. |

The [environment specification](ENVIRONMENT_SPEC.md) defines the broader scientific scope. The [task catalog](tasks/monoclonal_antibody_design/) identifies the currently published cases.

## Selection Criteria

Choose methods using the following criteria:

1. **User constraints:** permitted providers, open-source requirements, access restrictions, computational budget and requested outputs.
2. **Scientific applicability:** target context, antibody format, input requirements and the specific endpoint being evaluated.
3. **Evidence quality:** relevant primary publications, released benchmarks, independent comparisons and documented failure cases.
4. **Reproducibility:** identifiable model or software revisions, accessible dependencies, supported input/output formats and retained native artifacts.
5. **Practical availability:** working access, licensing, hardware requirements and a verified route to execute the selected method.

Consider established and newly released methods using the same criteria. Popularity or recency alone does not establish suitability. Record why a method was selected and any limitations affecting interpretation.

Where multiple approaches are requested, propose up to five distinct, feasible workflow options and prioritize them using comparable evidence, input readiness and resource requirements. Present fewer options when the evidence does not support five. Keep published benchmark performance separate from expectations for the new task.

## Model and Tool Records

Each proposed integration should document:

| Record | Required information |
| --- | --- |
| Identity | Model or tool name, primary source, software revision and model-weight version where applicable. |
| Applicability | Supported formats, target context, input assumptions and known exclusions. |
| Access | Provider or execution mode, license, dependencies and resource requirements. |
| Inputs and outputs | Accepted data types, chain and residue conventions, output artifacts and metric definitions. |
| Evidence | Relevant benchmark population, evaluation conditions, uncertainty and comparison limitations. |
| Integration status | Whether the method is proposed, connected or verified for a specified use case, with supporting evidence. |

Record the actual method revisions and settings used in each run. Installation, successful execution and scientific suitability are separate aspects of integration readiness.
