# Task: reference_constrained_molecular_optimization

## Description

Optimize supplied starting molecules for the **DRD2 protein**, using the supplied
activity predictor. Generate close analogues that improve predicted activity and
calculated drug-likeness while retaining structural similarity to the original
starting molecule. Choose the workflow independently using available
authorized molecular tools. Adapt decisions using actual observations, stay within
the declared budget, and return qualifying unique candidates with their evidence.

**Status:** task definition for review. The actual starting structures, verified
predictor/scorer assets and execution limits must be supplied before execution.
This Markdown is not a completed data bundle or an execution authorization.

Before running, supply the starting molecules, working activity scorer,
descriptor/similarity calculations, actual limits and final evaluator. There is
**one protein target: DRD2**. Multiple starting molecules are separate optimization
cases for that same target, not additional protein targets.

## Target and objective

- **Target:** DRD2, assessed using the supplied computational predictor.
- **Starting inputs:** the original molecules in the supplied case bundle,
  with verified complete structures and stable case IDs.
- **Goal:** find distinct, chemically valid analogues meeting all of the following
  conditions for the same candidate:

| Requirement | Qualification rule |
| --- | --- |
| Predicted activity | `P_DRD2(candidate) > P_DRD2(original_reference)` |
| Drug-likeness | `QED(candidate) > QED(original_reference)` |
| Structural similarity | Specified Morgan-count Tanimoto to original starting molecule **>0.7** |

The original starting molecule stays fixed throughout the case. An intermediate candidate
may seed the next round, but it does not replace the original comparison reference.
Use full precision and strict inequalities. There is no minimum qualifying count.
A fully evaluated search with no qualifying candidates is a valid negative result.

**Default primary outcome:** the number of unique generated molecules that improve both
predicted activity and QED while retaining similarity strictly above 0.7.
Count all qualifying molecules; the displayed shortlist is only a subset.

Predicted DRD2 activity is a model output, not docking energy or experimentally
demonstrated potency. QED is a calculated descriptor, not an ADMET assay.

## Required input bundle

| Input | Required contents |
| --- | --- |
| `cases.csv` | `case_id,reference_id,reference_smiles,reference_sha256`; verified original identities |
| `scorer_manifest.json` | Exact predictor and code hashes, preprocessing/features, QED implementation/version, molecular identity rules and fingerprint/similarity settings |
| Scorer assets/interface | Supplied DRD2 predictor and dependencies, with a verified local interface or equivalent authorized service |
| `execution_manifest.json` | Starting-molecule cases, objective variant, task scale, replicates, supported seeds, allowed inputs/tools/rewards, all resource limits, stopping rules and independent evaluator identity/interface |

Calculate the reference's predictions afresh. Precomputed summary values are not control
measurements. Do not reconstruct a reference structure from reported scalar scores.
Missing structures/model assets are `NEEDS_INPUT`; undefined scientific or resource
rules are `PROTOCOL_REQUIRED`. Do not silently substitute another target/model.

## Frozen measurement definitions

Use the predictor's own feature pipeline, separately from similarity evaluation:

| Calculation | Required implementation |
| --- | --- |
| DRD2 prediction | Use the supplied model and exact feature pipeline. Verify radius, bit/count representation, vector size, chirality/features, successful loading and positive-class interpretation against the scorer manifest before execution. |
| QED | Pinned RDKit implementation specified in the scorer manifest; retain unrounded output. |
| Starting-molecule similarity | Sparse, non-feature Morgan **count** fingerprints, radius **2**, and the matching Tanimoto implementation. Preserve remaining implementation defaults explicitly. |
| Molecular identity | Frozen canonicalization/deduplication policy, including stereochemistry, salts and tautomer treatment; use the supplied scoring implementation. |

Do not confuse predictor features with the count fingerprints used for similarity.
A hashed bit vector is not an interchangeable similarity fingerprint.

## Design constraints and method freedom

1. Preserve the original inputs and case identities. Validate each seed before
   submission and verify that the tool used it; never accept an automatic fallback
   to another library molecule as the same case.
2. Use actual authorized tools and documented payloads. Use existing Agent
   Scientist wrappers/connectors for Boltzmann scientific jobs.
3. The agent may choose editing, fragment libraries, seeded generation, population
   search and evaluate/select/reseed loops. Multiple methods and branches share
   one total run budget.
4. Local scoring and permitted open-source proposal methods may supplement hosted
   tools. Record real code, model, library and parameter identities.
5. Do not invent a hosted scorer callback, property name or custom-model ID.
   Verify whether the selected optimizer can use the requested reward.
6. Retain every observed output, invalid structure, duplicate, unsuccessful attempt
   and job receipt. A separately inserted reference control is not a generated draw.
7. No new scaffold, ADMET or other exclusion may silently alter the original-task
   qualifying count. A changed success rule creates a separately named adaptation.
8. Stop on exhausted limits or scientific blockers and report the reason. Missing
   evidence remains unresolved; do not fill it with assumed values.

## ADMET rewards and hosted-tool boundaries

Freeze `objective_variant` before generation:

| Variant | Qualification |
| --- | --- |
| `activity_qed_similarity` (default) | The three activity/QED/similarity tests above; ADMET may guide search without adding pass/fail requirements. |
| `activity_qed_similarity_admet` | The same three tests plus explicitly supplied ADMET conditions. Fix model identities, scales/units, thresholds and missing-value rules before running. |

For the extended variant, its primary count is unique molecules meeting all
activity/QED/similarity and declared ADMET conditions. Always retain the separate
three-condition count, so additional constraints and missing measurements remain
visible.

Supported ADMET property models may contribute to optimization rewards.
Their role must be fixed in the execution manifest. Record selected models,
versions/limitations, raw units/scales, maximize/minimize/range objectives,
transformations, weights, hard constraints and missing-prediction handling.

The connector does not establish that DRD2/QED are hosted global property models,
or that the supplied predictor can be registered through the custom-model API.
An authorized custom model ID is not interchangeable with uploading a model file.

Where hosted optimization requires supported property-model selections, disclose
those selections as proposal guidance. Evaluate imported molecules with the
original local scorer and use those observations for subsequent decisions when
supported. Do not claim the remote optimizer internally used the required reward.

For the default variant, auxiliary ADMET scores do not add mandatory filters.
The extended variant is a separately identified configuration; report its
qualifying count separately from the original three-condition count. Do not
switch variants mid-run or mix their composite scores. Allow auxiliary capabilities
equally when comparing base and specialist-assisted Agent Scientist.

Recalculate mandatory metrics from candidate structures at full precision.
Some current tool CSVs round property values to two decimals; those values cannot
resolve strict parent-improvement tests.

Off-target optimization is outside scope. This predictor-based objective requires
no target structure. Optional docking is supplementary: it cannot replace DRD2
prediction or contribute to the primary count. It requires a target-matched
structure, frozen assessment protocol and separate allowance.

## Sampling and budget

Freeze the track and limits before execution:

| Track | Contract |
| --- | --- |
| `full_scale` | 128,000 nominal molecular draws per original case/run, with ten repeats. The agent chooses its search organization within this total allowance. |
| `development_pilot` | Smaller case set, draw allowance and repeat count frozen in the manifest. Compare with a baseline rerun at the same limits; do not claim a raw count beats a full-budget result. |

A nominal draw, exported row, unique valid structure, property evaluation and remote
submission are different units. Hosted tools may filter invalid or duplicate attempts before returning outputs.
Do not infer raw draws from exported CSV length or treat output molecule count as
the full search cost.

Record requested/observable actual draws, emitted rows, valid structures, unique
identities, duplicates, rejected/failed attempts, predictor evaluations, cache hits,
hidden backend costs, submissions, credits/currency, CPU/GPU/wall time and model
usage. Include all parent/specialist activity and unsuccessful branches.

Unknown counters remain null. Mark `SAMPLING_BUDGET_UNVERIFIED` or
`ORACLE_BUDGET_UNVERIFIED` where applicable; this prevents matched-budget efficiency
claims even if output quality can be measured. Do not keep drawing to replace
invalid or duplicate outputs after the fixed draw allowance is exhausted.

The nominal sampling scale does not establish a service spending allowance. Actual service, compute,
wall-time and reasoning ceilings belong in the supplied execution manifest. Missing
limits are `PROTOCOL_REQUIRED`. Report seeds only when supported; otherwise record
`SEED_UNCONTROLLED` with stable replicate IDs.

Before each submission, verify a defensible maximum for every hard-limited
resource and reserve that amount atomically from the remaining allowance. Count
outstanding reservations across parallel branches. Release or reconcile them only
from actual receipts; unresolved acceptance retains its reservation. Do not submit
when the reserved maximum could exceed a limit. If a tool's internal work cannot
be bounded, exclude it from that hard draw/oracle track or use a separately declared
submission/cost-bounded adaptation. A post-run accounting flag does not establish
that a hard limit was enforced. If a service charge itself cannot be bounded, the
paid submission is not executable under a hard financial ceiling.

If the chosen hard-budget track proves unenforceable, stop the run. A different
submission/cost-bounded track must be declared before starting a separately
identified run; do not silently switch tracks or reset spent resources mid-run.

## Computational stages

| Stage | Responsibility | Evidence |
| --- | --- | --- |
| Validate | Check case identities, scorer assets, supported methods and limits. | Hashes, versions, capability checks and blockers |
| Establish controls | Recalculate starting-molecule activity, QED and self-similarity. | Fresh reference measurements and scorer checks |
| Plan | Select initial methods, allocation and observations that would change strategy. | Timestamped plan and remaining budget |
| Propose and evaluate | Generate actual candidates, validate and calculate mandatory metrics. | Native outputs, candidate registry, measurements and query ledger |
| Adapt | Choose subsequent inputs/actions from observed evidence. | Decisions linked to actual candidates/results and cumulative costs |
| Freeze | Preserve all outputs and create the deterministic shortlist. | Immutable candidate/metric lists and artifact hashes |
| Independently evaluate | A separately controlled evaluator recalculates qualification and compares eligible cases/arms after output freeze. | Evaluator identity, frozen output hashes, per-run metrics, uncertainty, coverage and comparability report |

## Evaluation metrics

| Metric ID | Calculation and rule |
| --- | --- |
| `predicted_activity` | Supplied-model DRD2 `P(active)` for candidate and original starting molecule; dimensionless model output |
| `qed` | Frozen RDKit QED, dimensionless, full precision |
| `reference_similarity` | Defined count-Morgan r2 Tanimoto to original starting molecule, dimensionless |
| `property_deltas` | Candidate minus starting-molecule activity and QED, separately |
| `unique_joint_improvements` | Distinct generated identities with both deltas strictly positive; no similarity restriction |
| `unique_constrained_improvements` | Distinct generated identities with both deltas strictly positive **and** similarity strictly above 0.7; default primary count per case/run |
| `unique_admet_constrained_improvements` | Extended variant only: distinct identities satisfying the three conditions plus every frozen mandatory ADMET condition; its primary count. Otherwise `NOT_APPLICABLE`. |
| `generation_and_coverage_counts` | Requested/attempted/emitted/valid/unique/duplicate/reference-recovered/failed/fully-assessed counts; explicit denominators and unknowns |
| `auxiliary_properties` | Declared ADMET predictions actually computed, preserving original units, models and conditions |
| `resource_use` | Scientific calls, caching, jobs, service cost, compute/runtime and reasoning use |
| `repeat_summary` | Per-case mean and sample standard deviation of counts across completed runs, with all run results and completion coverage |

An unavailable mandatory measurement does not establish pass or fail. Report the
number of candidates with unresolved qualification. Do not remove missing results
silently or replace the three qualification tests with an aggregate reward.

Deduplicate within each case/run using the frozen identity policy. Do not pool
replicates to inflate per-run counts. A generator-recovered original starting molecule is
reported but fails strict improvement; the inserted control is counted separately.

Count **all** qualifying identities before forming a practical shortlist of up to
20 per case/run. For display, order by descending activity delta, QED delta,
reference similarity, then ascending canonical identity string. This is a declared
display convention, not an additional qualification metric or a limit on qualifying counts.

Report failed/incomplete runs alongside completed runs. State which measurements
enter any uncertainty summary. With one completed run, sample standard deviation
is unavailable rather than zero. Different case sets or configurations must be summarized separately.

## Measurement and comparison contract

Every measurement records `run_id`, `replicate_id`, `case_id`, `candidate_id`,
`metric_id`, `value`, `unit`, `status`, `method_version`, `input_hashes`,
`parameters`, `artifact_path` and an unavailable-result reason where needed.
Use null for missing values. Statuses include `COMPUTED`, `NEEDS_INPUT`,
`PROTOCOL_REQUIRED`, `UNSUPPORTED`, `FAILED`, `NOT_EVALUATED_BUDGET` and
`NOT_MEASURED`. Accounting/comparability flags are separate from metric status.

The tested agent supplies artifacts and may perform self-checks. Benchmark
verification belongs to a separately controlled evaluator with a frozen metric
implementation. It must not accept agent-edited criteria or let the tested agent
rewrite frozen outputs. Record evaluator identity/interface, scorer hashes and
evaluated output hashes. If unavailable, label results `SELF_ASSESSED`; do not
claim independent verification. The evaluator assesses the complete frozen output
under the supplied criteria. Keep baseline results and archived candidate outcomes
outside the execution input bundle. Instructions alone do not enforce isolation;
record actual access limitations. Experimental candidate activity/ADMET remains
`NOT_MEASURED` unless independently supplied for the same identities.

## Expected output

Format: `reference_constrained_optimization_bundle`.

Directory: `08_results/reference_constrained_molecular_optimization/<run_id>/`
in the execution workspace, outside the task-definition directory.

- `run_manifest.json`: frozen inputs, methods, scorers, rewards, limits, seeds and
  stopping rules.
- `reference_controls.csv`: freshly computed starting-molecule measurements.
- `candidate_registry.csv`: raw/normalized structures, identity, original starting molecule,
  immediate parent, source operation, draw order and assessment status.
- `comparison_metrics.csv`: per-candidate/control measurements and provenance.
- `qualification.csv`: each mandatory test and joint decision, duplicate membership
  and unresolved outcomes.
- `summary_metrics.json`: per-case/run counts, coverage and replicate summaries.
- `shortlist.csv`: ordered eligible shortlist with case/run/candidate identifiers.
- `decisions.jsonl`: observations, method choices, adaptations and stop rationale.
- `resource_ledger.csv`: observable sampling, scoring, job, compute/service and
  model use, with unknowns and budget-excluded outputs.
- `measurement_coverage.json`: all required metrics and completion/missing reasons.
- `evaluation_receipt.json`: evaluator identity, frozen output hashes and assessment status.
- `report.md`: actual execution, trade-offs, negative results, failures and limitations.
- `artifacts/` and `artifact_manifest.csv`: native outputs/receipts/logs with relative
  paths and SHA-256 hashes.

## Important instructions

Execute actual calculations. Preserve input structures, original starting molecules and
accepted remote job IDs. Save durable progress and use a persistent logged session
for long local work; record the session name and attachment command. Reuse completed
results after interruption, and do not replace a submission whose acceptance is
unresolved. Record retries and recovery. Freeze generated outputs before independent
comparison. Completing generation alone does not complete evaluation.

Do not retrieve or reuse archived qualifying molecules, previous campaign outputs
or precomputed candidate outcomes as search inputs. Keep those data outside the
tested agent's search context.
