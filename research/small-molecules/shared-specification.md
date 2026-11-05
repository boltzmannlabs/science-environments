# BolChem environment specification

**Status: Specification.** Owner: Ankith116. Tracking:
[#46](https://github.com/boltzmannlabs/science-environments/issues/46).
This document describes requirements; executable implementation and scientific
validation are not claimed.

## Purpose and scope

Provide reviewable small-molecule tasks in which Agent Scientist selects and
adapts scientific workflows, then submits frozen outputs for common evaluation.
The tasks remain independent of a particular generator, specialist implementation
or tool-call sequence. Original scientific wrappers/connectors provide execution.

There are two assignments with distinct targets and inputs:

- **De novo:** one p38α protein target, one supplied structure identified as 1A9U.
  Generation may use any permitted approach; common final docking uses Smina.
- **Optimization:** one DRD2 target, potentially several original starting
  molecules. Each starting molecule is an independent case for the same target.
  Its mandatory objective uses the supplied activity predictor, QED and similarity.

Off-target optimization is excluded. Neither assignment establishes measured
potency, experimental ADMET, synthesis success or clinical utility.

## Authoritative task contracts

Exact inputs, inequalities, fingerprint definitions, selection, sampling,
accounting, failure handling and output fields are maintained in:

- [small-molecule-de-novo-design/tasks/p38alpha-design.md](../../environments/small-molecule-de-novo-design/tasks/p38alpha-design.md).
- [small-molecule-optimization/tasks/drd2-optimization.md](../../environments/small-molecule-optimization/tasks/drd2-optimization.md).

Keep these agent-facing task files free of literature identity, historical
reference outcomes and prescribed reference algorithms. Keep evidence and
scientific provenance in [owner-only research](research-notes.md)
and the [reference index](references.md).

## Inputs and dependencies

Before execution, the task owner supplies original structures/starting molecules,
verified identity mappings, pinned scorer assets and interfaces, allowed scientific
capabilities, deterministic preparation rules or explicit randomness limitations,
resource ceilings and a separately controlled evaluator.

The specific required manifests and fields are defined by each task. No empty
configuration files or invented assets are supplied as substitutes. Software,
model and capability limitations are recorded in [MODELS_AND_TOOLS.md](models-and-tools.md).

The de novo target structure is an input for docking; it does not require a
pocket-conditioned generator. Optimization uses an activity predictor and needs
no target structure for its mandatory assessment. Optional optimization docking
would require a distinct, target-matched protocol and allowance.

## Execution responsibilities

The tested agent validates inputs, plans and executes actual calculations, records
observations and resource use, and freezes candidate identities and outputs.
It may screen, branch or reseed, subject to immutable objectives and limits.
It does not redefine final success conditions after observing results.

Reserve known maximum cost/work before operations subject to hard limits, including
outstanding parallel activity. Unknown acceptance retains its reservation. Hidden
unbounded backend work cannot support claims of enforced draw/oracle budgets.
A different enforceable accounting track requires a separately declared run.

Use durable job receipts/state to resume. Preserve accepted job IDs; do not resubmit
completed jobs or replace a submission with unresolved acceptance. Record local
recovery and all actual retries.

## Evaluation and outputs

De novo freezes ten endpoint slots, measures the complete panel and displays up
to three eligible candidates separately. Optimization counts all unique qualifying
analogues before producing a display shortlist. Missing measurements remain
explicit; partial results are not silently converted into complete success.

For optimization, optional ADMET guidance does not silently alter default
qualification. Mandatory ADMET conditions require a separately frozen objective
variant and its own primary count, with original-condition counts retained.

The separately controlled evaluator uses frozen criteria and scorer/output hashes.
Self-checks are permitted but are labelled `SELF_ASSESSED` if independent assessment
is unavailable. For comparing base and specialist-assisted agents, hold the task,
permitted information/helpers and declared total resource allowances constant.

Each task defines a workspace output bundle containing original/derived input
hashes, candidate identities/lineage, raw results, metric coverage, qualification
or panel decisions, resource/decision logs, shortlist, report and artifact manifest.
Large datasets, native job outputs, credentials and private account information
are not repository deliverables.

## Acceptance criteria for this contribution

- Both task contracts define scientific objectives, inputs, constraints, metrics,
  budgets, outputs, stopping and missing-result behavior.
- De novo uses only p38α/1A9U; optimization distinguishes one DRD2 target from
  its starting-molecule cases.
- Agent-facing tasks contain no literature names/links or required reference
  generator/search method.
- Exact mandatory metrics remain distinct from auxiliary ADMET guidance.
- Documentation distinguishes specification, implementation and scientific evidence.
- Source notes, ownership, issue linkage, blockers and actual validation are traceable.
- No credentials, generated candidate outcomes, large data or unrelated changes
  enter the contribution.

See [validation evidence](specification-validation.md) and
[remaining work](STATUS.md). A future implementation has separate installation,
interface, input/scorer qualification and scientific comparison acceptance criteria.
