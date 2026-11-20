# Environment specification

Lifecycle: In Progress. Scientific scope and interfaces are implemented for an evidence-first investigation and bounded research-scenario case study, not a general calibrated formulation predictor. Sources: [research](../../research/formulation_dissolution/research-notes.md), [references](../../research/formulation_dissolution/references.md), [inventory](MODELS_AND_TOOLS.md).

## 1. Scientific objective and scope

Investigate source-supported formulation/process hypotheses affecting ranolazine ER dissolution; preserve provenance, missingness and uncertainty. Exercise empirical release modeling and optimization methodology without inventing recalled-lot measurements. Two historical public recall identities are separate case records, not simulation tasks. No causal or clinical inference is supported.

## 2. Supported problems

Implemented: composition validation, evidence triage, method-stratified summaries, published-curve reconstruction, a descriptive whole-formulation holdout baseline, synthetic whole-batch model comparison, and an assumption-conditional 500 mg research-prototype search. Supplied predicted/experimental profile pairs can be compared after explicit context/unit gates. Arbitrary APIs, doses, tablet geometries or excipients require a new scientifically reviewed model/config, not changing the strength label on this case study.

## 3. State

`environment.state.Episode` holds task, source attestations, materials, constraints, candidates, predictions, experiment proposals/results, evidence, hypotheses, rankings, status, audit and budget. JSON persistence uses atomic replace. Records are mutable local objects, not a tamper-evident or authenticated regulated record system. The scenario wrapper separately writes a frozen configuration/seed/version/hash receipt and per-candidate records. It does not pretend that those candidate records are measured episode evidence.

## 4. Actions

`Action.kind`: verify_source, register_material, validate_candidate, assess_compatibility, predict_dissolution, design_experiment, record_measurement, update_ranking, finalize_episode. Unknown actions are rejected; finalized episodes reject further transitions. Material registration requires an attested source. Predictions require valid candidates and an approved callable. Experiment proposals return approval_required; recording a measured result requires an authorized source/experiment/approval/confirmation and measured-labelled source-linked values. These are local attestations, not authentication of approval authority. No action executes a physical experiment, spend or product change.

## 5. Observations and separated outcomes

`Observation` contains task/candidate, status, result type, values with units/evidence/source, constraints, uncertainty, provenance, warnings, missing data and next actions. Statuses: success, failure, insufficient_data, tool_unavailable, approval_required. Evidence types: measured, literature_reported, predicted, derived, assumed, unknown. Scenario candidate records keep predicted dissolution, compatibility, stability, objective, constraint violations, uncertainty, and experimental_observations in separate fields. Compatibility/stability are insufficient_data and experiments null unless independently supplied; a numeric score is never an experimental observation.

## 6. Objective / reward

No universal RL reward is claimed. The scenario score is the configured weighted sum of (i) the fraction of 256 assumed kinetic scenarios meeting an illustrative 2 h maximum and 24 h minimum, (ii) clipped release margins, and (iii) a lower-polymer-mass preference. Weights 0.75/0.15/0.10 and goals 25% maximum at 2 h, 85% minimum at 24 h are unapproved assumptions. This is not a QC pass rate, learned utility or cost estimate. Pareto analysis uses scenario fraction, 24 h p05, polymer mass and 2 h p95. A separate ranker scores caller-supplied feasible objective/cost rows; it is not Bayesian optimization.

## 7. Constraints and failure

Composition vector m has finite nonnegative ingredient amounts in mg, caller-specified bounds l_i <= m_i <= u_i and sum m_i = M. Percent-basis vectors must sum to 100; mixed units are rejected. In the research case M=695 mg, API amount=500 mg, potency=1, excipients sum=195 mg. Variable Compritol C and Carbopol B are balanced by Avicel=165-C-B; fixed povidone/Aerosil/TiO2 contribute 30 mg. Dose = API amount * potency, all on mg basis. General percent-only validation does not verify a milligram dose. Hardness bounds are supplied in the historical kg/cm2 notation, not a portable manufacturing control. Unknown bounds/process constraints remain not_evaluated, never inferred.

Invalid units/dose/bounds/finite values, missing config, empty or duplicate grids and unsupported strengths fail before simulation. Existing run directory -> failure without overwrite. Missing OpenPKFlow -> tool_unavailable receipt. Insufficient budget -> budget_exhausted with zero evaluations, no partial-grid winner. A numerical scenario or audit failure cannot be a successful scientific result.

## 8. Workflow

Load `configs/environment.yaml` (JSON subset of YAML) and referenced scenario JSON; validate supported dose/units, ranges and every feasible recipe; preflight budget; use the existing simulator to enumerate feasible grid points; draw seeded independent uniforms for each first-order/Weibull parameter scenario; calculate scores/quantiles/Pareto/sensitivity; record every grid candidate; independently audit mass/labels/score/order/quantiles; emit new JSON files with hashes, versions, seed/config and status. Seed 2931, 128 draws per model, 117 feasible candidates in the supplied case. Wrapper rejects non-null experimental_observations rather than silently ignoring them; use the comparison interface below for supplied observations.

## 9. Model and tool interfaces

`fitted_curve(time, release, label)` delegates nonlinear fits to OpenPKFlow 2.9.0; pipeline units minutes/%; scenario evaluator uses hours with rates/scales defined in hours. Korsmeyer–Peppas uses <=60% points only; full-curve scoring is explicitly extrapolation. Missing/failed fits are logged. Approved callable registry requires capability/name/version/invoke/request+response validators/timeouts/retry policy and explicit registration approval. Absent tools return tool_unavailable. A thread timeout stops waiting but cannot guarantee cancellation of remote work; never use it as a safe retry strategy for physical lab jobs. Local laboratory controller supports fixture-only jobs incapable of creating measured evidence.

## 10. Architecture adaptation

Reuse the original flat packages rather than duplicating them under src. Proposed environment.py -> `run.py` + `simulation.py`; state/actions/observations/budget -> `environment/`; formulation design/compatibility/stability -> `agents/`; constraints -> `tools/mixture_validator.py`; dissolution/optimization/evaluation -> `evaluation/`; uncertainty -> `models/uncertainty.py` plus explicit scenario/holdout routines. No empty stability, ODE/PDE, RDKit or GP module is created. Use an isolated virtualenv because generic inherited package names can collide. The wheel ships executable code; configs/schemas/data/tasks remain checkout assets. No native Agent-Scientist plugin entry point or automatic host-tool interception is implemented.

## 11. Data requirements

Real qualification requires authorized formulation/batch/material/process/storage, actual method/version/media/agitation/time/assay units, replicate unit profiles, approved stage/unit criteria and independent comparator batches. Source licence/permissions must permit intended processing. FDA recalls/SPL identity and public research summaries do not supply these. Raw observations must remain immutable. Do not relabel literature or synthetic data measured. Supplied comparison JSON has `predicted` and `observed` objects with time, values, api, candidate_id, strength_mg, dosage_form, method_id, method_version, storage_condition, dose_basis, time_unit, release_unit and evidence_label; observed additionally needs experimental data_origin and source_id. Provenance remains user-attested. Exact context/time matching is mandatory; no silent interpolation or unit conversion.

## 12. Budget and stopping

Episode Budget supports actions/tool_calls/proposed_experiments/completed_experiments/elapsed_seconds; finite nonnegative counters only. Unknown limits are omitted, not passed as null counters. Commercial task metadata retains null budgets and therefore does not authorize an optimization loop. Scenario budget independently caps feasible candidates and scenarios per candidate before any curves are generated: all-or-abstain full-grid search, no partial search. Comparator/sensitivity/detail evaluations reuse draws and are not additional independent candidate proposals; max_candidates bounds distinct grid designs, not primitive equation calls. No hard process walltime or monetary estimate is provided.

## 13. Uncertainty

Scenario p05/p50/p95 are uniform-assumption Monte Carlo quantiles and model-form disagreement, NOT calibrated confidence/predictive intervals. Synthetic holdout intervals use a validation-batch max-residual statistic and interpolated 90th percentile across only four batches; calibration/coverage guarantees are not established. Descriptive point error calibration reports insufficient_data at low independent-pair counts; no posterior is trained. Missing uncertainty remains unestablished.

## 14. Evaluation

Published summary LOFO keeps whole related formulations together, excludes shared zero time and separates pH 6.8/HCl; same-curve fitting is reconstruction, not blind prediction. Synthetic fixture: 24 invented batches, 12 train/4 validation/8 test, per-formulation training mean, validation RMSE model selection, frozen test metrics; no heldout-curve fitting. MAE/RMSE/signed bias are percentage points, macro-averaged by batch/profile; residuals by time and interval widths/coverage are retained. F2 in the six-model run is arithmetic only, not regulatory. Supplied-profile evaluator excludes zero time; mathematical f1/f2 requires >=3 matched nonzero times, 0..100%, positive reference sum and <=1 time above 85% in each curve. Regulatory unit counts, CV, method validity and ER-specific applicability are not established; regulatory_similarity stays not_evaluated. Above-100 source observations are preserved for error scoring, not clipped. No supplied measured dataset was evaluated in this integration.

## 15. Reproducibility and exclusions

Retain source/config/artifact hashes, fixed seeds, versions, split IDs, failures and exact commands. Use new output directories and isolated CPU Python environments; lock file captures the tested dependency set, not support for every Python platform. Code/fixture tests and independent arithmetic audits do not validate ranolazine predictions. Out of scope: calibrated commercial mixture predictor, mechanism proof, mechanistic dissolution, ODE/PDE transport, degradation/Arrhenius/humidity models, descriptor screening, automated LIMS retrieval, authorized lab execution, clinical equivalence, base-agent superiority and manufacturing recommendations. Maintainer and scientific reviews remain required.
