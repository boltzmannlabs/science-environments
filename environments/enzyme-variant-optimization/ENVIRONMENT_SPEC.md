# Enzyme Variant Optimization Specification

## Purpose

Improve a declared property of an existing enzyme while retaining the functional features specified by the task. Produce complete new sequences, candidate-specific scientific evidence, a results-driven optimization round and a final comparison with the parent. This is variant optimization, not mandatory de novo backbone generation.

The same environment serves Agent-Scientist alone and Agent-Scientist with an enzyme proposer and critic. Both approaches must execute the same required capabilities and meet the same evidence requirements. Tools and design strategies may differ.

## Inputs and task preparation

Each task identifies the parent, reaction, target property and relevant conditions. Before scientific comparison, prepare a shared input bundle containing the exact parent sequence and construct, source structure, residue correspondence, substrate chemical identity and state, required cofactors, protected positions and allowed edits. Preserve biologically relevant chains and components. An accession alone is not a verified construct.

Use SCI's existing search and reading tools to research chemistry and prepare a source-backed reaction description. Read mechanism references, not the target study's winning mutations or outcome tables. Resolve chemistry that changes the calculation before using it; otherwise mark that assessment unresolved. Do not create an extra chemistry service or require an external template registry.

Freeze the public input bundle, task, conditions, budgets and final evaluation protocol in the run's `RUN_PLAN.json`, with their hashes and actual software versions. Parent preparation is shared; candidate generation and design results are not. The selected task/version/approach profile under [config](config/README.md) contains execution settings, not an already-frozen scientific protocol or historical run receipt.

## Computational tool capabilities

| Stage | Required work | Evidence that completes the stage |
| --- | --- | --- |
| Prepare | Establish parent identity, reaction, construct, chemical states, allowed edits and protected functional features. | Input files, residue/atom mapping, chemical identities, sources and frozen design constraints. |
| Parent baseline | Measure the target property and required safeguards on the parent using declared methods. | Native outputs, numeric baseline, conditions, method versions and limitations. |
| Generate | Execute a suitable sequence-design, mutation-search or library-generation tool. Choose the tool from current Boltzmann or ToolUniverse capabilities. | Full sequences, candidate IDs, parent IDs, edits, generation tool, parameters, seeds and native output references. |
| Screen | Assess the target property and task-relevant stability, solubility or sequence risks. | Per-candidate observations, exclusions, uncertainty and a documented structural shortlist. |
| Structure and function | Build candidate structures and relevant complexes; assess structure quality, substrate interactions and catalytic features. | Candidate-specific structures, sequence verification, component/atom mapping, measurements and missing evidence. |
| Optimize | Use observed weaknesses to choose and execute a revised generation/search step. Change method, constraints or design region when justified. | Decision tied to actual observations, tool-generated revised sequences and a testable expectation. |
| Re-evaluate | Repeat the assessments affected by each revision and the required final checks. | Comparable parent/candidate observations, including combined mutations assessed directly. |
| Compare | Seal the selection, then evaluate it under the common protocol. | Final sequences, ranked selection, evidence table, failures, usage and comparison report. |

Cheap screening may precede expensive modeling. A parent structure can guide sequence design, but every final candidate needs its own structural assessment; copying the parent coordinates is not evidence of the candidate's fold.

Generation may use an inverse-folding model, a constrained mutation-search method, an explicitly executed saturation-library tool or another suitable algorithm. Plain Python may transfer files, apply a tool-generated edit list or deduplicate results. A language-model-written list of substitutions followed only by string replacement does not satisfy generation. Initial and revised sequence batches need recorded algorithmic origins. A correction to a scoring input is a method repair, not a new sequence-design round.

## Tool selection and chemistry

Consult the installed catalogue and current contracts rather than copying tool names or payload schemas into this environment. MLDE and aliases resolving to it are excluded from every workflow. A ToolUniverse search result identifies a capability; it does not prove the underlying executable or credentials are available. Save the actual execution path and output. Do not silently replace an unavailable mandatory capability with reasoning alone.

Use the current CSV headers and types required by each tool. Do not impose one universal header set. Preserve IDs explicitly across files and verify sequence identity after structure prediction. Keep protonation, stereochemistry, covalent state, oligomeric assembly and essential waters/metals consistent with the modeled reaction. A substrate complex and a transition-state model are different inputs.

Catalytic acceptance ranges require evidence for that reaction and structural state. If justified ranges are unavailable, report measurements descriptively. If an interface requires bounds even for measurement mode, use an available genuinely descriptive calculation or record the capability as unavailable; never invent permissive ranges. A required descriptive assessment may complete without a catalytic pass/fail verdict. Do not rank activity by geometry alone.

## Execution errors and recovery

Handling execution errors and invalid outputs is part of the workflow for both Agent-Scientist alone and specialist-assisted runs. The agent independently determines whether a problem comes from its inputs, a tool contract, service behavior or an unresolved dependency, using actual diagnostics and available evidence. The environment defines acceptance requirements; it does not prescribe an error-specific fix or add a retry service around SCI.

When an error is recoverable, investigate the cause, correct the inputs or preparation according to the current contract, and execute the justified corrected request. If a completed job returns outputs that violate the task's requirements, investigate why and whether that tool can satisfy those requirements. If it can, correct its use and retry; if it cannot, select and execute a compatible alternative. Preserve the scientific objective and protected constraints. Do not force an output to qualify by relaxing those constraints, silently editing rejected candidates or bypassing validation. Check actual returned outputs before continuing; successful job status alone is insufficient.

Record the original failure or output violation, supporting diagnostics, the reason for the chosen correction or tool change, replacement job IDs and verification results in the existing `jobs.json` and `decisions.md`; retain cumulative usage in `usage.json`. Repeated identical attempts without a supported correction are not recovery. Accepted, pending or ambiguously submitted work remains associated with its original ID and is not duplicated because a status check timed out. SCI supplies execution, validation, status and session mechanisms.

Both approaches receive the same recovery requirements. The agent chooses corrections and alternatives without an operator supplying per-error solutions during normal execution. Preserve unsuccessful recovery attempts and report genuine blockers explicitly. Recovery attempts do not replace required scientific stages, and missing evidence remains incomplete work.

## Specialist contribution

In the assisted approach the parent agent delegates an initial design review and reviews after actual result batches to the native saved proposer and critic. The proposer identifies a supported next experiment; the critic tests the reasoning and recommends an actionable correction. The parent selects and executes the next scientific action using its normal tools.

Pass explicit permitted task files and result paths or inline observations to each child. Do not provide the other approach's results or held-out outcome files. Specialist tools, permissions, setup, transcripts and budgets remain SCI's responsibility. A saved-subagent definition is not an independent evaluator or a newly trained molecular model. Its advice does not guarantee improvement.

## Outputs

Keep each approach and repeat in its own run directory:

| Artifact | Content |
| --- | --- |
| `RUN_PLAN.json` | Frozen inputs, design constraints, explicit budget policies, method choices, final evaluation protocol and any reviewed deviations. |
| `candidates.fasta` | Parent and complete unique variant sequences with stable identifiers. |
| `candidate_history.csv` | Parentage, sequence hash, edits, generation tool, batch/round and native evidence paths. |
| `observations.csv` | Candidate IDs, measurements, units, method settings, uncertainty and native output references. |
| `structure_evidence/` | Final-candidate structures, chemical/residue mappings and quality/catalytic reports. |
| `decisions.md` | Reasons for shortlisting and revisions; assisted runs link actual proposer/critic receipts. |
| `jobs.json` | Native job IDs, submitted payload references, statuses, outputs, failures and unresolved requests. Redact credentials. |
| `usage.json` | Available model/scientific runtime, queue time, resources, billing units and missing accounting fields. |
| `selection.csv` | Final `candidate_id,rank,sequence_sha256` rows; exclude the parent and hash before independent evaluation. |
| `REPORT.md` | Completion status, numerical findings, limitations, trade-offs and next experimental questions. |

The evaluator separately writes `evaluation.json`. The helper's expected input is described in [the common comparison protocol](#common-comparison-protocol). Native tool schemas and result formats are unchanged.

## Completion criteria

The workflow is complete when all required stages—including tool-based generation, results-driven optimization and re-evaluation—have finished and their evidence has been reviewed. Completion does not guarantee improvement; finding no supported improved candidates is a valid result.

Queued jobs or missing required evidence leave the workflow unfinished. Preserve available results and report what remains unresolved.

## Scientific comparison

Use equal frozen inputs and maximum budgets for both approaches. Include proposer and critic usage in the assisted total. Use one evaluator protocol for both sealed selections, with eligible candidates and the parent measured under the same conditions. Compare paper values only when the metric, method, units and modeled state are compatible; otherwise rescore reference structures with that common method or report the historical comparison as unavailable.

Keep experimental activity, predicted kinetics, docking, folding-energy changes, geometry and confidence as separate evidence. Better computational scores do not demonstrate improved experimental catalysis. See [common comparison rules](#common-comparison-protocol).

## Common comparison protocol

### Question and approaches

Does a native proposer/critic specialist help Agent-Scientist produce stronger computational enzyme variants under equal constraints and maximum budgets?

Compare Agent-Scientist alone with Agent-Scientist using the proposer and critic. Both execute the complete environment workflow, including tool-based initial and revised generation. A historical paper supplies external context; it is not automatically a third executed workflow. A separately run fixed baseline may be added only with its own frozen settings and accounting.

### Freeze before design

Record the exact public parent bundle, task version, chemical state, protected/editable positions, initial and revised candidate limits, required final evidence and evaluation method in `RUN_PLAN.json`. Record explicit scientific-compute, model-token, financial and wall-time policies: numeric ceilings or explicitly authorized unbounded limits. Record starting limits from the selected config version and authorized amendments without erasing prior usage. The starting limits are 24 unique sequences including the parent, at most eight substitutions per variant, at most two sequence-revision rounds, at most 60 scientific submission attempts and up to five final candidates. Require at least one actual results-driven sequence revision unless a documented blocker leaves the run incomplete.

Count all parent and specialist model usage in each approach's total. Record unsuccessful attempts and ambiguous submissions. Share parent preparation and the public task, not candidates or decisions. Do not silently change frozen metrics or budgets after seeing outcomes. Record every owner-authorized limit amendment with old/new settings, reason and cumulative usage; retain the original frozen comparison and disclose resulting comparability limits. Changed scientific methods require a separately identified comparison.

The public specification does not enforce token/cost limits or file isolation. Use SCI's existing limits and the selected execution backend. Prompt-only information boundaries are not a sandbox, and language-model prior knowledge cannot be excluded by hiding local files alone.

### Scientific acceptance

An evaluator separate from the design conversation reviews generation provenance, edit constraints, sequence/structure identity, chemical state, required structure/quality/catalytic reports and revision evidence. Use actual native artifacts; stage declarations alone are insufficient. A proposer/critic conversation does not provide this independence.

Use task-specific evidence-backed acceptance criteria, with uncertainty. Missing justified catalytic ranges may make geometry descriptive rather than a rejection gate; record that choice before selection. Missing measurements or mappings remain unresolved. Do not penalize an unknown result by assigning a numerical zero.

### Common numerical endpoint

Choose one final primary metric for the selected case. Parent and candidates from both approaches must be evaluated with the same method version, settings, units and chemical state. Evaluate selected paper references with that protocol when available, or keep the historical values descriptive. A favorable predictor used to generate candidates should not also be advertised as independent experimental truth. Add an orthogonal evaluator where available and state any shared-model dependency.

The offline helper compares an already-reviewed primary-metric table. It does not execute a method, inspect structures, discover thresholds, establish uncertainty significance or judge whether a proxy measures catalysis.

Protocol JSON fields:

| Field | Meaning |
| --- | --- |
| `parent_id` | Identifier of the exact shared parent. |
| `metric` | One named numerical endpoint, not a mixture of endpoints. |
| `unit` | Exact unit for this endpoint. |
| `direction` | `minimize` or `maximize`. |
| `protocol_id` | Fingerprint/name of the frozen method, settings, input state and evaluation procedure. |
| `min_improvement` | Nonnegative minimum signed change needed to label a numerical improvement; justify it in the frozen protocol. It is not automatically a significance test. |
| `max_selected` | Positive maximum final selection count. |
| `ratio_allowed` | Boolean; true only for a meaningful positive ratio scale, never energies or log-transformed scores. |

The reviewer creates `evaluation_observations.csv` with exact header:

```text
candidate_id,sequence_sha256,metric,value,unit,protocol_id,eligibility,evidence_path
```

Use `true`, `false` or `unknown` for eligibility after reviewing all task requirements. `value` may be blank for unavailable measurements. Every supplied row needs a genuine evidence reference. The helper checks declaration consistency, not the contents of that reference. Keep secondary metrics in the full run observations, not this single-endpoint input.

The design agent seals `selection.csv` with header `candidate_id,rank,sequence_sha256` and a `selection_seal.json` containing `selection_sha256` before receiving evaluator results. Ranks must be unique and contiguous from 1; the parent and duplicate sequences are excluded. The seal detects changes to the file, not when it was created or who could access labels.

From the repository root:

```bash
python -B environments/enzyme-variant-optimization/scripts/evaluate_results.py --protocol /path/to/frozen_evaluation.json --observations /path/to/evaluation_observations.csv --selection /path/to/selection.csv --seal /path/to/selection_seal.json
```

The paths above describe reviewer-owned run artifacts, not tool submission payloads. The command prints JSON and never submits jobs or changes the selection. A nonzero exit means malformed/incompatible declarations; `incomplete` is a valid report with missing evidence, not a completed scientific comparison.

### Reporting

Report each approach's workflow completion, actual generated unique sequences, supported final candidates, signed parent-relative metric changes, mandatory failures and unresolved evidence. Add runtime, queue time, model usage, scientific-resource usage, cost with original units, and repeat variability where available. A single repeat is a case comparison, not a general performance claim.

Assess recovery from the recorded diagnostics, corrections, tool changes and output checks under the shared [environment requirements](#execution-errors-and-recovery). Distinguish execution failures, task-ineligible outputs, justified recovery, unresolved blockers and operator interventions. Report these observations for both approaches without treating a retry or successful job status as scientific improvement.

Only a fully observed eligible selection receives an aggregate numerical score. No qualifying selection and missing evidence are different outcomes. Numerical improvement in a computational endpoint does not establish experimental improvement. Retain unfavorable and incomplete results.

### Reference information

Task-specific reference values under [benchmark](benchmark/README.md) are operator/evaluator material. Keep those reference files and target-study winner data out of tested-agent inputs. Published values are literature observations, never new-run outputs. Each numbered benchmark document records source-verified paper values and comparison limits; run-version comparisons remain pending reviewed evidence.

### Comparisons across configuration versions

A version identifies model/settings/resource policies; approaches and repeats remain distinct run records. Compare the original published reference with v1, v2 and later runs only for compatible endpoints, units, preparation and evaluation conditions. Disclose changed settings and prior-outcome exposure. Show incompatible results separately with an explanation rather than claiming a numerical gain.
