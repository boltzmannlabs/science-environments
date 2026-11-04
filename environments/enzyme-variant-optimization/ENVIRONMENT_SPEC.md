# Enzyme Variant Optimization Specification

## Purpose

Improve a declared property of an existing enzyme while retaining the functional features specified by the task. Produce complete new sequences, candidate-specific scientific evidence, a results-driven optimization round and a final comparison with the parent. This is variant optimization, not mandatory de novo backbone generation.

The same environment serves Agent-Scientist alone and Agent-Scientist with an enzyme proposer and critic. Both approaches must execute the same required capabilities and meet the same evidence requirements. Tools and design strategies may differ.

## Inputs and task preparation

Each task identifies the parent, reaction, target property and relevant conditions. Before scientific comparison, prepare a shared input bundle containing the exact parent sequence and construct, source structure, residue correspondence, substrate chemical identity and state, required cofactors, protected positions and allowed edits. Preserve biologically relevant chains and components. An accession alone is not a verified construct.

Use SCI's existing search and reading tools to research chemistry and prepare a source-backed reaction description. Read mechanism references, not the target study's winning mutations or outcome tables. Resolve chemistry that changes the calculation before using it; otherwise mark that assessment unresolved. Do not create an extra chemistry service or require an external template registry.

Freeze the public input bundle, task, conditions, budgets and final evaluation protocol in the run's `RUN_PLAN.json`, with their hashes and actual software versions. Parent preparation is shared; candidate generation and design results are not. [Configuration](config/workflow.json) contains starting limits, not an already-frozen scientific protocol.

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

Consult the installed catalogue and current contracts rather than copying tool names or payload schemas into this environment. A ToolUniverse search result identifies a capability; it does not prove the underlying executable or credentials are available. Save the actual execution path and output. Do not silently replace an unavailable mandatory capability with reasoning alone.

Use the current CSV headers and types required by each tool. Do not impose one universal header set. Preserve IDs explicitly across files and verify sequence identity after structure prediction. Keep protonation, stereochemistry, covalent state, oligomeric assembly and essential waters/metals consistent with the modeled reaction. A substrate complex and a transition-state model are different inputs.

Catalytic acceptance ranges require evidence for that reaction and structural state. If justified ranges are unavailable, report measurements descriptively. If an interface requires bounds even for measurement mode, use an available genuinely descriptive calculation or record the capability as unavailable; never invent permissive ranges. A required descriptive assessment may complete without a catalytic pass/fail verdict. Do not rank activity by geometry alone.

## Specialist contribution

In the assisted approach the parent agent delegates an initial design review and reviews after actual result batches to the native saved proposer and critic. The proposer identifies a supported next experiment; the critic tests the reasoning and recommends an actionable correction. The parent selects and executes the next scientific action using its normal tools.

Pass explicit permitted task files and result paths or inline observations to each child. Do not provide the other approach's results or held-out outcome files. Specialist tools, permissions, setup, transcripts and budgets remain SCI's responsibility. A saved-subagent definition is not an independent evaluator or a newly trained molecular model. Its advice does not guarantee improvement.

## Outputs

Keep each approach and repeat in its own run directory:

| Artifact | Content |
| --- | --- |
| `RUN_PLAN.json` | Frozen inputs, design constraints, numeric budgets, method choices, final evaluation protocol and any reviewed deviations. |
| `candidates.fasta` | Parent and complete unique variant sequences with stable identifiers. |
| `candidate_history.csv` | Parentage, sequence hash, edits, generation tool, batch/round and native evidence paths. |
| `observations.csv` | Candidate IDs, measurements, units, method settings, uncertainty and native output references. |
| `structure_evidence/` | Final-candidate structures, chemical/residue mappings and quality/catalytic reports. |
| `decisions.md` | Reasons for shortlisting and revisions; assisted runs link actual proposer/critic receipts. |
| `jobs.json` | Native job IDs, submitted payload references, statuses, outputs, failures and unresolved requests. Redact credentials. |
| `usage.json` | Available model/scientific runtime, queue time, resources, billing units and missing accounting fields. |
| `selection.csv` | Final `candidate_id,rank,sequence_sha256` rows; exclude the parent and hash before independent evaluation. |
| `REPORT.md` | Completion status, numerical findings, limitations, trade-offs and next experimental questions. |

The evaluator separately writes `evaluation.json`. The helper's expected input is described in [the benchmark protocol](benchmark/PROTOCOL.md). Native tool schemas and result formats are unchanged.

## Completion criteria

The workflow is complete when all required stages—including tool-based generation, results-driven optimization and re-evaluation—have finished and their evidence has been reviewed. Completion does not guarantee improvement; finding no supported improved candidates is a valid result.

Queued jobs or missing required evidence leave the workflow unfinished. Preserve available results and report what remains unresolved.

## Scientific comparison

Use equal frozen inputs and maximum budgets for both approaches. Include proposer and critic usage in the assisted total. Use one evaluator protocol for both sealed selections, with eligible candidates and the parent measured under the same conditions. Compare paper values only when the metric, method, units and modeled state are compatible; otherwise rescore reference structures with that common method or report the historical comparison as unavailable.

Keep experimental activity, predicted kinetics, docking, folding-energy changes, geometry and confidence as separate evidence. Better computational scores do not demonstrate improved experimental catalysis. See [benchmark rules](benchmark/PROTOCOL.md).
