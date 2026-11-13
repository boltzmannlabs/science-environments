# Antibody Design Environment Specification

**Environment ID:** `antibody_design`

## Purpose

The Antibody Design environment defines a common framework for computational antibody discovery, design, optimization and evaluation. Its intended scope covers monoclonal, bispecific and multispecific antibody projects, from a target-defined design objective to traceable candidate comparisons.

The specification describes scientific requirements as the environment develops. The current release includes monoclonal task specifications, published benchmark references and retained execution/results packages for five tasks. Capability and scientific coverage are recorded in [status.md](status.md). The shared execution and artifact contract is defined below.

## Antibody Design Families

| Design family | Intended scope | Evaluation focus |
| --- | --- | --- |
| Monoclonal antibody design | Design or refine an individual antibody for a defined target and binding region. The current task collection focuses on single-specificity designs. | Target recognition, reference or framework constraints, structural quality, specificity and developability. |
| Bispecific antibody design | Combine two distinct binding specificities in one defined molecule, directed at different antigens or different epitopes of the same antigen. | Evidence for each binding component, assembly, pairing, geometry and the intended combined mechanism. |
| Multispecific antibody design | Extend the design framework to molecules with three or more intended binding specificities. | Evidence for every component, compatibility across the assembled molecule and the overall design objective. |

These are task groupings. Monoclonal origin, the number of binding specificities and molecular format describe different properties; an engineered bispecific antibody can also be a monoclonal product. In this specification, the separate multispecific track denotes three or more specificities. Valency describes the number of binding sites and does not by itself determine specificity. The bispecific scope follows the distinction between different antigens and different epitopes described in [FDA guidance](https://www.fda.gov/media/123313/download).

The intended format coverage includes full-length antibodies, Fab and F(ab')2 fragments, scFv constructs, single-domain antibodies and engineered multidomain formats. Each task must declare its actual chain composition, domain organization, valency and pairing requirements. Format-specific support requires an appropriate input representation and evaluator. Antibody fragments, single-domain antibodies and engineered multispecific products are also recognized within the broader antibody-product scope described by [WHO](https://www.who.int/publications/m/item/trs1043-annex4).

## Design Modes and Objectives

| Mode or objective | Starting information | Intended outcome |
| --- | --- | --- |
| De novo design | A defined target and design objective, with an optional scaffold or framework; no supplied antibody known to bind the target is required. | New candidate binding hypotheses with documented sequence origin and supporting evidence. |
| Reference-guided design | A verified reference antibody, target context and permitted changes. | Reference-derived candidates assessed against a comparable baseline. |
| Interaction and specificity optimization | An existing candidate or reference with a defined binding objective and relevant comparison evidence. | Improved computational interaction evidence or selectivity while retaining required properties. |
| Humanization and developability optimization | A supplied antibody and declared sequence, structural and product-property constraints. | Candidates assessed for humanness, stability, solubility, aggregation risk and other relevant liabilities. |
| Architecture and combined-function optimization | Defined binding components, molecular format and intended mechanism. | An assembly-aware design assessed at both component and whole-molecule levels. |
| Reconstruction and benchmarking | A masked or otherwise controlled input and an independently retained reference. | A reproducible assessment of sequence recovery, structural agreement or another declared endpoint. |

De novo design may use a framework or scaffold; it does not necessarily mean generating every residue without prior structural context. A published final design used for comparison must remain distinct from the actual starting antibody or framework. Optimization must identify which properties should improve, which must be retained and which constraints cannot be traded off.

## Scientific Inputs and Constraints

A task must define the target identity, relevant construct, design objective, antibody format and available evidence. Reference-guided work additionally requires verified reference components and permitted modifications. Designs with multiple specificities must identify each target or epitope and the role of each binding component.

Structural inputs must retain their origin and biological context. Experimental coordinates, predicted structures and prepared derivatives must be distinguishable. Document chain and residue mappings, unresolved regions, relevant modifications and any differences between the supplied construct and the evaluated model.

Declare the candidate budget, editable regions, protected residues, pairing rules, comparison controls, output requirements and user-imposed tool or resource constraints before execution. Missing essential inputs must be reported explicitly.

## Workflow and Tool Selection

The environment is intended to support task-dependent workflows rather than prescribe one universal tool sequence. Method selection should account for the target, molecular format, available inputs, relevant benchmark evidence, access restrictions, licensing and computational budget.

Where several workflows are appropriate, compare their applicability, evidence quality, limitations and resource requirements before selecting an approach. Record the tools and revisions actually used. A method's published aggregate performance must not be presented as a predicted success rate for a new target.

The scientific lifecycle connects input review, candidate design, structure and interface assessment, property evaluation, comparison and reporting. These are evidence requirements; their implementation may differ across tasks and formats.

For monoclonal tasks, the agent determines workflow count, methods, execution order and shortlisting strategy from task requirements, verified Boltzmann tool contracts and resource budget. Use Boltzmann tools for design and primary evaluation within the requested scope. Calculate missing benchmark metrics using genuine open-source implementations specified or referenced by the corresponding benchmark; separate local benchmark evaluation requires scope authorization in the task/request. Record execution origin and method differences, without silent local design-model substitution.

Preserve independent workflow executions, repeats and retries under distinct run IDs with lineage. Retain considered approaches and failed attempts in source records. Historical bundles retain their original run IDs and identify component workflows. Schedule GPU work sequentially when needed; respect user stops and do not restart cancelled work automatically.

## Evaluation and Candidate Selection

| Evaluation area | Required evidence |
| --- | --- |
| Molecular identity | Complete candidate representation, chain or domain assignments, reference lineage where applicable and compliance with declared edits. |
| Structure and interface | Folding and interface evidence assessed separately, with explicit structural scope, geometry, contacts and uncertainty. |
| Binding and specificity | Endpoint definitions, matched reference or control comparisons and relevant selectivity evidence. |
| Developability | Distinct assessments of applicable sequence liabilities, stability, solubility, aggregation, expression and immunogenicity-related indicators. |
| Combined architecture | Evidence for each required specificity and the assembled molecule, including compatibility with the declared mechanism. |
| Benchmark comparability | Matching dataset, metric definition, units, structural scope and evaluation conditions. |
| Reproducibility | Input and output provenance, method revisions, analysis settings, artifact identities and resource use. |

Selection must respect mandatory constraints before ranking favorable scores. A strong component cannot compensate for failure of another required component or the assembled molecule. Simultaneous target engagement should be evaluated when required by the proposed mechanism; it is not a universal requirement for every bispecific design. [FDA guidance](https://www.fda.gov/media/123313/download)

Predicted confidence, interaction energies, measured affinity and functional activity are separate endpoints. Published benchmark values provide comparison context and do not automatically define acceptance thresholds. Report uncertainty, missing measurements, failed evaluations and non-comparable results alongside positive findings.

## Iteration and Evidence Handoffs

Each iteration should retain the candidate identity, changes from its predecessor, input and method revisions, results, failed criteria and the reason for the next decision. Promising candidates may guide focused refinement while alternative approaches preserve exploration. New results must remain attributable to the exact candidate and evaluation conditions that produced them.

Revised workflows should respond to documented evidence. An incomplete or failed stage must not be converted into a successful result, and reused evidence must remain applicable to the current candidate. The stopping decision should reflect the declared objective, available evidence and resource budget.

## Agent Workflows and Scientific Results

Use matching task/run identities:

```text
src/<task_id>/runs/<run_id>/
results/<task_id>/<run_id>/
```

| Location | Required records |
| --- | --- |
| `src/<task_id>/` | Explored approaches, chosen workflows, tool inventory, run register and implementation. |
| Source run | Actual execution, inputs, effective configurations, workflow snapshot, provenance and logs. |
| `results/<task_id>/` | Scientific run folders and supported workflow comparisons, organized as described in the main `results/README.md`. |
| Results run | Candidate/prediction inventory, selections, sequences, metrics, structures, benchmark comparison/report and scientific evidence. |

The [source guide](src/readme.md) describes planning, implementation and execution records. The [results guide](results/README.md) describes scientific output files and assessment-run exceptions. An attempt producing no scientific output has a source record without placeholder results. Preserve inherited data, failed outputs and original lineage; reusing evidence is not a fresh execution.

## Benchmark Audit and Completion

Audit task-required and missing metrics against only the matching task-specific benchmark. Recover original tools/versions, data, constructs, atom/residue selections, preprocessing, sampling and aggregation. Verify actual evaluator outputs and retain reproducibility evidence. Report our/reference values, compatible differences and supported outcomes in the run's `benchmark_comparison.csv` and `benchmark_report.md`.

Keep missing predictions `not_predicted`, absent calculations `not_computed` and unsupported comparisons `not_comparable`, with reasons and attempted tools. Unsupported numeric fields remain empty or `null`. Do not fabricate values or transfer another task's benchmark. Distinguish dataset aggregates, single-case measurements, prediction confidence and measured affinity.

Record execution status, scientific coverage and packaging validation separately. File presence and a packaging pass cannot establish scientific completion; required unresolved evaluations leave coverage partial or awaiting input. Validate identities, formats, membership, paths, counts and hashes before handoff, with links between source and result runs.

This specification defines the execution contract. Retained runs document historical work; importing or editing them does not launch jobs or establish a universally runnable executor.
