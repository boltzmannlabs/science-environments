# Case-specific tasks

**Version 0.1: task schema and runnable synthetic fixture implemented.** A real scientific task remains under preparation.

The environment contains shared behavior. Each task supplies the lead-optimization case. Target names, compounds, assay endpoints, thresholds, budgets, and reference answers must not be hardcoded into the environment.

## Task brief

| Section | Contents |
| --- | --- |
| Identity/sources | Task ID/version, scientific question, source URLs/revisions, access/licensing notes, and asset provenance. |
| Starting leads | Molecule IDs/representations, structure files, molecular-form uncertainty, and baseline evidence. |
| Scientific context | Target and any prepared structure, pocket, sequence, or assay context required by the methods; declare target-independent tasks explicitly. |
| Objectives | Properties to improve, directions/ranges, designated starting-lead comparators, compatible baseline observations, units/scales, methods, and required improvements where applicable. |
| Preservation | Properties/features held within task-defined tolerances and explicit checks. |
| Hard constraints | Eligibility rules, methods, and consequences of missing/failed evidence. |
| Candidate scope | New analogues permitted, or selection restricted to an identified library. |
| Capabilities/resources | Permitted canonical jobs and separate candidate, model, submission, molecule-evaluation, time, and concurrency limits where applicable. |
| Objective support | For each objective: documented internal optimizer control, separate later assessment, conditional/unverified model mapping, or unsupported capability. |
| Outputs | Candidate artifacts, endpoint comparisons, constraint assessments, investigation outcomes, selection rationale, stopping reason, resource use, and partial/failure reporting. |
| Evaluation | Search-visible scores versus final evidence, shared model/data exposure, compatible endpoints, visibility rules, frozen submission/scoring protocol, comparators, and reference-data partition. |

## Evaluation situations

The agreed environment policy is advisory: warn and record, then let the agent decide. The task still declares eligibility and resource allowances. Continuing after a warning may produce an ineligible submission; reports must retain the violation and actual usage. Missing internal service counts remain unknown rather than implying equal total work.

Finalize the candidate submission before obtaining final-evaluator feedback. Reusing the search scorer measures that objective; a different predictor measures computational transfer subject to overlap review; compatible assay measurements evaluate the actual measured endpoint. Feedback used for further optimization becomes development evidence.

**Open analogue design:** new structures related to starting leads require a declared evaluation. Computational scores support computational claims; experimental improvement needs measurements of those exact candidates under compatible conditions.

**Restricted measured library:** an independent evaluator can score selection from supplied members against their hidden measurements. This tests prioritization within that library, not experimental improvement of newly generated analogues.

Both candidate-scope modes are represented in the [version-1 task schema](../config/task.schema.json). They do not impose a fixed scientific tool sequence. Final objective/constraint signatures are preregistered in `evaluation`; numerical rules and opaque identity associations are implemented, while chemical graph checks and assay curation remain task-specific work.

## Runnable software example

The [synthetic fixture](synthetic/README.md) exercises creation, session attachment, checks, records, comparisons, restart-compatible storage, frozen submission and the offline evaluator. All representations and values are artificial. It is not a scientific benchmark or a model episode.

## Future first scientific case

COVID Moonshot Mpro is the proposed first task. First review source versions, molecular identity/stereochemistry, assay compatibility, qualifiers/censoring, duplicates, visible starting evidence, independent reference storage, and source/model exposure. No library, activity cutoff, split, budget, or benchmark result is selected here.

Protected reference answers must reside outside the tested agent's access when independent scoring is claimed. Public measurements cannot provide experimental scores for new structures.

The [Moonshot preparation dossier](covid-moonshot/README.md) records verified sources and unresolved data/protocol decisions. The [comparison protocol](../benchmark/PROTOCOL.md) defines the base-agent comparison requirements.

See the [specification](../ENVIRONMENT_SPEC.md) and [research notes](../../../research/small-molecule-lead-optimization/research-notes.md).
