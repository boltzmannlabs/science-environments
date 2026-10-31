# Environment specification — Enzyme Variant Optimization

## Purpose

Improve variants of an existing enzyme while respecting its reaction, allowed
sequence changes and task-specific requirements. The environment is a scientific
process, case assignments, a native specialist definition and output evaluation.
It is not another Agent-Scientist runtime or a newly trained molecular model.

## What is reused, not rebuilt

| Existing Agent-Scientist capability | How this environment uses it |
| --- | --- |
| Literature search and reading | Research reaction chemistry, relevant methods and missing task information. |
| Maintained tool catalogue | Resolve applicable methods and exact input contracts at execution time. |
| Enzyme input validation | Use native upload/submission preflight; do not add a second set of tool input checks. |
| Tool calls and authorization | Use native operations, not direct HTTP clients or account-key files. |
| Conversations, jobs and outputs | Retain existing session and job references; no new state database. |
| Saved specialists and delegation | Import a normal definition and use the native child-agent lifecycle. |
| Execution controls | Respect the current native permissions and limits; task text does not enforce a sandbox. |

The added Python checks evaluate scientific **outputs** against a particular
assignment. They do not validate or dispatch molecular-tool API requests.

## End-to-end process

1. **Understand the assignment.** Establish the parent enzyme, reaction, substrate,
   conditions, desired improvement, allowed mutations and expected deliverables.
2. **Establish the reference.** Verify sequence numbering and starting structures.
   Separate paper measurements from predictions and distinguish assay constructs
   from modelling constructs. Research unresolved scientific details with native
   tools; record assumptions that affect conclusions.
3. **Propose variants.** Select a justified design strategy and a bounded batch.
   Preserve required residues and record full sequences and mutation identities.
4. **Evaluate the relevant evidence.** Assess the requested function/properties,
   structural plausibility and reaction-specific requirements using appropriate
   methods. Do not require every possible analysis for every case.
5. **Identify failure points.** Distinguish an execution failure, missing evidence,
   an unsuitable method and an actual design defect. Independent work may continue
   while a particular dependent calculation is unavailable.
6. **Revise when justified.** Choose an alternative strategy or targeted check
   based on actual findings. Sequence/structure changes require fresh affected
   evidence; they do not inherit the parent's quality or geometry results.
7. **Select and report.** Return the requested shortlist or explain a shortfall.
   Preserve unsuccessful candidates, unresolved criteria, methods, resources and
   native job references. Do not imply experimental improvement from predictions.

These are required scientific operations, not a fixed order of named software.
The base agent and the assisted agent can choose different applicable strategies.

## Case-study tasks

Each `tasks/<case>/TASK.md` names a real study and contains the exact prompt,
biological objective, inputs, constraints, process requirements, project limits,
expected outputs and success definition. Additional cases use the same environment
without creating new runtimes. Case-specific supporting inputs belong with that
case; research rationale and references belong in `research/`.

`tests/<case>/` describes and, where practical, computes that task's scientific
checks. It must state units, direction of improvement, reference comparability,
missing-data handling and which claims cannot be evaluated computationally.

## Native enzyme specialist

The specialist is an advisory native subagent focused on failure analysis:

- Inspect the actual objective, constraints and available results.
- Explain the likely scientific reason for a failed or uncertain objective.
- Identify conflicting endpoints or inappropriate assumptions.
- Propose one or two distinct, evidence-backed next investigations and say what
  result would support or refute each explanation.
- Return a prioritized recommendation, sources, uncertainty and a stop condition.

It does not maintain another catalogue, execute a second orchestration loop,
create its own children, change thresholds, invent results or manage credentials.
The parent agent remains responsible for native scientific execution. Its initial
definition grants only reading and existing web research, not scientific job
submission. Capability review and permission enforcement stay native.

## Comparisons and failure-driven improvement

Maintain three distinct evidence records: published reference, base-agent result,
and specialist-assisted result. The published study is a reference, not a
fabricated executable baseline or an automatically comparable algorithm ranking.

Two assisted modes are useful and must not be confused:

- **Recovery continuation:** the specialist sees the base run's failure report;
  the parent performs targeted follow-up. Report cumulative resources and the
  added context. This is not an independent equal-information run.
- **Matched independent comparison:** start fresh with the same public inputs,
  objective and maximum overall resources. The assisted run consults its native
  specialist about its own results. Count child calls within its total resources.

Use the mode written in the case prompt. Do not run repeatedly until the
specialist wins, remove negative results or change an endpoint after seeing
answers. Genuine scientific improvement is a finding to measure, not a required
outcome that the software manufactures.

## Results and current limits

Result folders contain real outputs only. A pending arm has a status note, not
synthetic candidate scores. Software-test receipts are labelled separately.
Public literature and model-training overlap make this first case a retrospective
reproduction/design exercise, not a blinded or prospective validation.

This environment adds no OS isolation or persistent background runner. Native
session/subagent lifetime and backend execution behavior remain unchanged.
Molecular-tool availability, computational suitability, remote charges and
experimental follow-up are external requirements, not solved by Markdown files.
