# Task: target_conditioned_de_novo_design

## Description

Design new small molecules for the human **p38α protein**. Use its supplied
**1A9U three-dimensional structure** for the common final docking assessment.
Assess molecular properties as well as docking performance. Choose suitable generation,
screening and search strategies using authorized tools. Multiple workflows may
be combined within one shared budget. Return a complete evaluation panel and
an evidence-backed shortlist, preserving failures and resource use.

Execution requires the supplied input bundle, scoring interface and frozen limits.
No particular generation model or search algorithm is required.

## Objective and target

Return a final evaluation panel of **ten molecular candidates per run**, or
explicitly report unfilled slots when generation cannot be completed. An
"endpoint" below means a molecule committed to this panel, rather than every
intermediate molecule explored. The primary outcome is the **mean derived Smina
score over the complete ten-slot panel**; higher is preferred. Seek favorable Smina
docking scores while reporting drug-likeness, lipophilicity, synthetic-accessibility
and natural-product-likeness descriptors. These are distinct measurements; no
single composite reward defines success.

There is one target: **p38α**. **1A9U identifies its supplied 3D structure** used
for docking; no gene analysis is required. Keep the same target structure and
binding-site definition across runs. Do not add protein targets or alternative
structures. Generation methods may use other permitted inputs and need not use
the structure. Keep `p38_1a9u` only as an internal tracking ID in manifests/results.

## Required inputs

| Input | Required contents |
| --- | --- |
| `target_inputs.json` | Protein name p38α, structure ID 1A9U, internal tracking ID, local structure/sequence/control paths, hashes and allowed generation information |
| Structural bundle | Supplied 1A9U coordinates, fixed prepared target protein, reference ligand coordinates and sequence/chain maps |
| `scorer_manifest.json` | Smina executable/version/hash, preparation adapter, docking settings, descriptor/model files, identity policy and scoring interface |
| `execution_manifest.json` | Repeats, final-panel policy, permitted inputs/tools, generation/scoring/service/compute/reasoning limits and stopping rules |
| Evaluator interface | Separately controlled final-assessment interface and output-freeze procedure |

Verify construct sequence, observed/missing coordinates, chain mapping and
reference ligand identity. Keep observed records, supplied prepared inputs and
any further derived preparation separate. Never overwrite source inputs or
silently replace a supplied target protein.

The supplied bound molecule locates the docking site and provides a fresh control.
Its molecular graph
must not be used as editable starting leads or inserted into generated candidates.
Use only the declared information when conditioning generation. Protein-sequence,
structure-conditioned and other authorized generation routes are allowed; pocket
conditioning is not required. Record any pocket extraction or coordinate transform.

Missing inputs/assets are `NEEDS_INPUT`; unresolved rules/limits are
`PROTOCOL_REQUIRED`.

## Workflow freedom

Choose generation methods, libraries, proposal screening, evaluation allocation
and follow-up actions. You may use docking feedback during search within its
allowance, or generate first and assess afterward. Explain choices from actual
observations. All methods, retries and parent/child activity share total limits.

Use existing Agent Scientist wrappers/connectors for Boltzmann jobs. Verify tool
contracts and actual model availability. Permitted local packages may supplement
hosted tools. Record real versions, weights, libraries, parameters and seed support.
Do not invent controls absent from a tool's interface.

Keep search-pool candidates and committed endpoint records distinct. Preserve
all observable emissions, invalids, duplicates, failed operations and hidden-count
limitations. Do not use archived solution molecules or previous outcome tables
as candidate sources. No additional property cutoff may silently alter the primary
evaluation population.

Require actual generation/editing provenance for proposed molecules. Retrieving
an existing library alone does not complete this generation task. Tool generation
does not establish chemical novelty: record any verified known-structure overlap,
and report novelty as unverified when no defined reference collection was checked.

## Final evaluation panel and shortlist

Use `search_selected_endpoints` as the panel policy, identically across compared
runs. Generation, screening, internal docking and ranking may select the ten
committed molecules from the search pool. Declare the selection rule and output
allocation before generation. Record all pool members and costs, not just winners.

Define each search episode before it starts: target, allowed information, resource
allocation, output slots, candidate-selection rule and stopping condition. A single
batch-and-screen operation can constitute an episode; extra reasoning calls are
not required. Log changes prospectively for subsequent episodes, never by
relabeling past winners after the final assessment.

Commit endpoint identities before receiving their final evaluator results. Earlier
internal search feedback is allowed and recorded. Retain ten slots, including
repeated identities; uniqueness is measured rather than imposed on all methods.
Record invalid endpoints and unfilled slots without silently replenishing after
exhaustion. Do not replace committed endpoints after final scoring. Keep the full
search pool and any additional best-of-pool report distinct from the frozen panel.

The ten-slot panel is the complete evaluation output. From that frozen panel,
display up to **three** shortlisted candidates per run. Each must be valid,
connected, unique, different from the control, have verified molecular identity,
and have successful final Smina, QED and SA measurements. Missing values make it
ineligible for the shortlist, with a reason; retain its full panel record and do
not replace it silently.
Order by higher derived Smina score, then higher QED, lower SA score and ascending
canonical identity. Preserve the full panel metrics regardless of this shortlist.
Control recoveries remain in generated records/metrics but cannot enter the
new-candidate shortlist. An empty shortlist is valid.

## Common docking evaluation

Use the supplied pinned Smina evaluator for every endpoint, case control and
comparison arm. Its primary settings are:

| Setting | Value |
| --- | --- |
| Smina version | 2020.12.10, verified executable/build identity in manifest |
| Target protein input | Supplied prepared p38α structure from 1A9U; rigid primary assessment |
| Box reference | Corresponding supplied site-control ligand coordinates |
| Autobox addition | 10 angstrom, using the executable's native option semantics |
| Seed | 1000 |
| Exhaustiveness | 9 |

Keep the same case box for every molecule; candidates cannot define their own
boxes. Use the supplied preparation interface consistently for candidates and
controls. Retain hydrogens, protonation, stereochemistry, embedding and atom-map
decisions in provenance. Record unsupported/uncontrolled stochastic behavior.

Before evaluation, freeze embedding attempts/seeds, conformer/protonation
enumeration, failed-preparation handling, repeated docking, cache keys and score
aggregation. One Smina seed does not control stochastic ligand embedding. Do not
retry preparations until a favorable score appears. Use declared replicates when
preparation randomness is uncontrolled, and retain every attempt. Cached reuse
must identify the same structure, preparation and scoring configuration.

Retain the top-pose raw Smina value and its sign. Define the reported higher-is-
better score as **negative raw Smina value**. For example, raw -9 gives derived +9.
Keep both fields. Never convert a failure sentinel into an energy measurement.
Changing docking software, preparation or settings requires a separately named
assessment configuration; its scores cannot replace the primary ones.

Preserve pose files, stdout/stderr and all preparation failures. A raw generated
pose and an independently docked pose are separate artifacts. Predicted docking
scores are not experimentally measured binding affinities. Native-pose RMSD is
applicable to a matched control; generated molecules have no supplied experimental
pose against which to claim pose accuracy.

## Required metrics

| Metric ID | Measurement |
| --- | --- |
| `smina_raw`, `smina_score` | Raw top-pose value and its negation; preserve native units/scale |
| `logp` | RDKit Crippen MolLogP; dimensionless, no universal maximize rule |
| `qed` | RDKit QED, dimensionless |
| `sa` | Specified synthetic-accessibility implementation; lower is preferred |
| `np_likeness` | Specified natural-product-likeness implementation/model; descriptive score |
| `endpoint_counts` | Ten requested slots, committed/invalid/unfilled/repeated/fully-assessed records |
| `generation_counts` | Observable raw attempts/emissions, valid/unique outputs, duplicates, control recoveries and failures |
| `identity_repetition` | Unique valid endpoint identities divided by observed endpoint records per case; report invalid/missing-slot coverage separately |
| `control_measurements` | Fresh descriptor/docking controls and supported identity/pose checks |
| `resource_use` | Draws, internal/external scoring, cache hits, jobs, credits, compute/runtime and reasoning use |

Use the supplied descriptor implementations and model files; hosted predictions
with similar names are not interchangeable. Record identity/tautomer/stereo rules.
Do not substitute structural diversity or source novelty for the defined uniqueness
statistics. Training-source overlap is a separate diagnostic when verifiable.

For each run, summarize all endpoint records with mean, median, sample SD,
minimum, maximum and measurement coverage. Summarize repeated runs separately
under the declared configuration. Repeated endpoint identities still contribute
their endpoint records to score means. No cross-target aggregate is required.

For each metric, if a required endpoint value is missing or a slot unfilled, mark
that complete-panel aggregate `INCOMPLETE_EVALUATION`. The primary Smina mean
requires all ten valid final Smina measurements. A missing auxiliary descriptor
does not erase an otherwise complete Smina mean, but its own coverage stays
incomplete. A successful-only mean is a separate diagnostic with its denominator;
do not silently omit failures or impute favorable values.
Uniqueness never establishes biological selectivity.

## Budgets and stopping

Freeze raw-attempt limits, search/final docking limits, job/financial ceilings,
compute/wall time, repeats and model usage in the execution manifest. Ten endpoint
molecules do not imply ten docking calls: include all internal search evaluations,
controls, failures and repeats. Reserve final endpoint/control assessment allowance
before spending the remainder on search.

Verify and reserve a maximum for each hard-limited resource before submission,
including outstanding parallel work. Unresolved acceptance retains its reservation.
Unbounded hidden work cannot enter a hard draw/oracle track; use only separately
declared enforceable allowances. Unknown counters stay null and prevent matched-
budget claims. Do not treat filtered CSV row counts as raw attempt counts.

Stop on exhausted limits, unresolved acceptance or missing mandatory capability.
Record seed limitations, actual counts and stop reason. Do not replenish poor or
invalid endpoints beyond the declared limits.

## Outputs and independent assessment

Write to `08_results/target_conditioned_de_novo_design/<run_id>/` outside the
task-definition directory in the execution workspace.

- `run_manifest.json`, `inputs/`: frozen protocol, original/derived inputs, maps,
  methods, scoring settings and hashes.
- `candidate_registry.csv`: every observable search emission and its lineage,
  source operation, raw structure, identity and status.
- `endpoint_panel.csv`: committed case/run/slot identities, commit order/times,
  panel rule, repeated identities and unfilled slots.
- `comparison_metrics.csv`, `summary_metrics.json`: all measurements/coverage,
  per-case and aggregate results, raw/derived scores and counts.
- `shortlist.csv`: endpoint-derived ranked candidates and reasons.
- `structures/`, `artifacts/`: conformers, docking poses, native outputs and logs.
- `decisions.jsonl`, `resource_ledger.csv`: evidence-backed choices, all scientific/
  model usage and reservations.
- `measurement_coverage.json`, `report.md`, `artifact_manifest.csv`: status/reasons,
  actual execution, unresolved evidence, stop reason, relative paths and SHA-256.

Each measurement retains case/run/candidate/slot IDs, metric ID, value, unit,
status, method/version, parameters, input hashes and artifact path. Missing values
are null with a reason. Distinguish `NEEDS_INPUT`, `PROTOCOL_REQUIRED`,
`UNSUPPORTED`, `FAILED`, `NOT_EVALUATED_BUDGET` and `NOT_MEASURED`.

Freeze endpoints and outputs before a separately controlled evaluator performs
final assessment. Earlier search scores must not overwrite that assessment.
Record evaluator/scorer identities and output hashes. If absent, report
`SELF_ASSESSED`. Preserve inputs and accepted job IDs; resume from durable state
without resubmitting completed work. Experimental endpoints remain `NOT_MEASURED`
unless independently supplied for the same candidate.
