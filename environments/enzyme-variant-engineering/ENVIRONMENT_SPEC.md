# Enzyme Variant Optimization Environment Specification

## Purpose and inputs

Improve variants of an existing enzyme for a defined reaction and objective.
A task supplies the parent sequence or qualified structural reference, substrate,
assay context, allowed mutations, protected sites, resource scope and required
outputs. New scaffold generation is not a default requirement for variant design.

The environment adds scientific assignments and evidence rules to native
Agent-Scientist. It does not replace the runtime or retrain a molecular model.

## Reuse of native capabilities

| Capability | Responsibility |
| --- | --- |
| Search and literature reading | Native Agent-Scientist tools research chemistry and methods. |
| Scientific tool discovery | Current Boltzmann catalogue and ToolUniverse discovery, when configured. |
| Input validation and tool execution | The chosen operation's existing schema, validation and connector. |
| Authorization and job handling | Existing SCI permissions, receipts, polling and artifact retrieval. |
| Sessions and delegation | Existing native conversations and reviewed subagents. |
| Scientific acceptance | The task's declared criteria and later output evaluation. |

The contribution supplies no second implementation of the first five rows.
Tool availability and service charges remain properties of the configured services.

## Required scientific process

1. **Qualify the starting material.** Establish the sequence, construct, residue
   numbering, catalytic roles, assembly, substrate identity and chemical state.
2. **Define the design.** State the objective, protected positions, allowed changes,
   ranking criteria and resources before examining candidate predictions.
3. **Generate variants.** Save complete sequences, mutations, parent relationships
   and distinct candidate identifiers.
4. **Evaluate candidates.** Choose relevant functional and property methods, then
   obtain structures and complexes for the shortlist. Keep every result attached
   to the exact candidate and structural version that produced it.
5. **Diagnose weaknesses.** Separate a design defect from an execution failure,
   incorrect preparation, unsuitable method or missing evidence.
6. **Revise and re-evaluate.** Change the design or workflow when justified by
   actual results. Rerun affected checks; revised candidates do not inherit their
   parent's structural or property results.
7. **Finalize and report.** Preserve the ranking, rejected candidates, uncertainties,
   methods, failures, actual usage and output references.

The order of named software is not fixed. Independent work can continue while
another branch waits, but a missing required result remains missing.

## Method choice and chemistry

Agent-Scientist may use Boltzmann, ToolUniverse or both. Choose by reaction and
endpoint suitability, evidence, input compatibility, executable availability and
resource demands. Inspect current operation schemas rather than copying a second
catalogue into this repository. A software-description tool does not execute that
software. Record the actual method, provider, settings and version or explicit
unknown for every scientific result.

Research reaction-specific geometry when the task does not supply it. Record the
source, modeled state and rationale for any acceptance range. A reactant, covalent
intermediate and transition state are not interchangeable. Without justified
ranges, use descriptive measurements through a suitable available operation;
do not invent bounds to satisfy a request schema or declare a pass.

Folding stability, melting temperature, thermal half-life, solubility, binding and
catalytic activity measure different properties. Do not treat one as another.
Retain the ligand and relevant chemistry when assessing a complex; protein-only
validation cannot establish ligand quality. Predictions for mutation combinations
need their own evidence because single-site effects may not add up.

## Optional domain subagents

Subagent definitions and implementation belong in Agent-Scientist and are not
shipped here. The Est30 assisted assignment expects a reviewed
`enzyme-variant-proposer` and `enzyme-variant-critic`.

The proposer suggests evidence-backed strategies and revisions. The critic
challenges consequential assumptions, method choices and missing controls.
The parent receives both recommendations, makes the decision and executes the
scientific tools. After real results, it requests a targeted proposal and critique
before the justified follow-up. Keep the advice, parent decisions and native run
identifiers so the specialist's actual contribution can be examined.

The critic is neither a new operator-approval gate nor the independent outcome
evaluator. If a role is unavailable, report that fact rather than silently using
an unrestricted replacement. The agent-alone arm prohibits all delegation.

## Comparisons

Keep three records distinct: published reference, agent-alone output and assisted
output. A matched independent comparison starts each agent with the same allowed
inputs, objective, method access and declared resource ceilings. The assisted run
sees its own results, not the other arm's report. Child calls count within that
arm's resources. A separate recovery exercise may use an earlier failure report,
but must report the extra context and cumulative work instead of calling it an
equal-information comparison.

Record scope ceilings and actual scientific/model usage. The Est30 task limits
sequence count, revisions and submission attempts; those prompt limits do not
enforce an exact monetary, compute or model-token budget. Do not claim tightly
cost-matched benchmarking unless those additional controls are established.

Save final selections before reference evaluation. A computational comparison
requires matching metric, units, conditions, structural state and method settings,
or a declared common-method evaluation of both candidate sets. Common-method
rescoring is not historical reproduction. New predictions cannot establish that
a novel sequence exceeds a published experimental measurement.

Withhold winning mutations, sequences, outcomes and the target study's procedure
from independent design inputs. Generic chemistry research remains available.
Disclose recalled or accidentally exposed answers. Prompt restrictions are not
an OS sandbox, and training exposure to a public paper is unknown.

## Outputs and publication

Tasks define the exact artifacts. A complete record includes qualified inputs,
full candidate sequences, candidate-specific structures and mappings, tool
outputs, original/revised comparisons, job references, usage and a final report.
Unknown submission outcomes are reconciled through their existing connector;
do not resubmit them merely because no output arrived.

Keep live runs and private receipts in ignored local storage. Add tasks as they
are prepared; add scientific tests and reviewed result reports as the evidence
becomes available. Never commit account state, tokens, signed URLs or protected
answer files. Failed work and negative comparisons remain reportable outcomes.
