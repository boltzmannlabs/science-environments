# Task 06 — green-solvent Suzuki–Miyaura microwave optimization

Folder identifier: `task-06-green-solvent-suzuki-optimization`. Use this same identifier under `tasks/`, `benchmarks/` and `results/`.

## Overall objective

Evaluate a multi-tool workflow for a blind computational comparison of conventional, greener and betaine/glycerol deep-eutectic-solvent (DES) media in a microwave-assisted Suzuki–Miyaura coupling. Deliver ranked solvents, predicted yields, a selected green protocol, solvent hazard screening, waste/impurity trade-offs and a substrate-scope view — without accessing withheld experimental answers. Do not assume DES is inherently safe or lower-waste. Distinguish tool predictions, design hypotheses and scenario calculations from measured experimental results at every stage.

## Problem statement and scope

| Input | Value |
|---|---|
| Aryl halide | bromobenzene, `Brc1ccccc1` |
| Boronic acid | 4-methoxyphenylboronic acid, `COc1ccc(B(O)O)cc1` |
| Target biaryl | 4-methoxybiphenyl, `COc1ccc(-c2ccccc2)cc1` |
| Reaction ID | `SC03_BENCHMARK_01` |
| Reaction class | Suzuki–Miyaura C–C coupling |
| Heating mode | microwave |
| Candidate media | 1,4-dioxane, DMF, acetonitrile, 2-MeTHF, CPME, ethanol/water, glycerol, betaine/glycerol DES |
| DES ratios | 1:2, 1:4, 1:8 (molar; 1:4 preferred); no added-water optimization |
| Supplied protocol | PdCl₂(dppf)·CH₂Cl₂ 1.5 mol%, Na₂CO₃ 1.25 equiv, 2.8 g solvent, 129 °C / 15 min |
| User-reported outcome | 85% microwave vs 38% conventional heating (not passed to any tool) |
| Configuration | `blind_mode: true`, `hazard_standard: ICH Q3C`, `exclude_classes: [1,2]` |

The target is a structural input, not an experimental answer. The exact benchmark pair was supplied by the user for this run; the published substrate scope was not transcribed. The benchmark's full reference table, optimized yields and impurity observations were withheld during prediction and are stored only in the benchmark folder. No exact-pair measured-yield lookup was performed during generation.

Problem stages: input validation; retrosynthesis/forward consistency; condition recommendation and impurity prediction; condition-aware local design campaign; literature comparison after freezing; hazard/E-factor trade-off accounting.

## Exact target/input and source provenance

The supplied workflow was `SC03_agent_workflow (1).md` (task identifier `SC03`) and the post-hoc literature comparison file was `SC-03_Literature_Comparison.md`, both external user inputs in the `GopiKrishna/sai_kiran` folder and not redistributed here. Internal jobs: retrosynthesis `6b05593ab5ae2f156e63e787`, forward prediction `6b058889c45f4015f0eb48b3`, condition recommendation `6b0588c27fb17f3eac9cb206` (failed on HTTP 429/timeout) and retry `6b07cb3fb5e9e7e2abe1fade`, impurity prediction `6b058ae6c45f4015f0eb48e1`. All outputs were frozen before literature review. Source call IDs are preserved in [task_record.json](../../results/task-06-green-solvent-suzuki-optimization/task_record.json); raw account-scoped service exports are not redistributed.

## Execution approach

| Stage | Tool or method | Inputs | Origin |
|---|---|---|---|
| SMILES validation | RDKit | reactants, product, solvent/DES components, impurity candidates | local |
| Retrosynthesis | `retrosynthesis` job `6b05593ab5ae2f156e63e787` | target product only | internal platform |
| Forward prediction | `forward_reaction` job `6b058889c45f4015f0eb48b3` | two reactants; target withheld | internal platform |
| Conditions | `condition_recommendation` jobs above | reactants + product | internal platform |
| Impurities | `impurity_prediction` job `6b058ae6c45f4015f0eb48e1` | reactants + product | internal platform |
| Condition-space design | `reaction-optimize` local pipeline, BayBE v1 + frozen ReactionT5 | explicit 480-candidate grid | external local tool |
| Literature comparison | verified ChemistryOpen 2025 paper Table 1/2 | post-hoc, after freeze | external public literature |
| E-factor scenario | declared reaction-charge boundary | stoichiometry, 75% isolated, recovery sweep | local calculation |

The internal jobs were submitted once each; the failed condition job was retried as a distinct new job after a transient rate-limit/timeout, and no accepted-but-pending job was duplicated. The local optimizer was executed in the originating session. No wet-lab experiment, model training or new service job was performed during packaging of these folders.

## Expected outcomes and acceptance criteria

1. Validate structures and recover the benchmark reaction by retrosynthesis and forward prediction; report exact SMILES-string matches as such.
2. Rank all media by comparable predicted yields including conventional controls and DES; recover DES in the top 3.
3. Achieve yield MAE ≤15 pp on experiment-matched solvent rows, with condition-match status recorded per row.
4. Exclude ICH Q3C Class 1–2 components from any final recommendation; flag unresolved classifications rather than assuming safety.
5. Show green predicted yield ≥ conventional −5 pp on a comparable basis; compare microwave duration only on a documented basis.
6. Report impurity changes (Pd-black, homocoupling, protodeboronation) with directions and uncertainty only where experimentally supported.
7. Report E-factor with declared mass boundary, solvent-recovery and water policy; use `SCENARIO ONLY` when masses are incomplete.
8. Freeze predictions and provenance before literature comparison; do not claim clean blinding if outcomes were disclosed.

## Actual outcomes

Structure validation passed for 17 structures; retrosynthesis returned 55 routes with the correct top route; forward prediction top-1 exactly matched the target (model score ~1.0). The internal condition tool returned only dioxane/water conditions, and its retry succeeded after a transient failure. Impurity prediction returned condition-blind candidates. The local optimizer compiled 480 candidates across all media, DES ratios, catalysts, bases, temperatures and times, and selected a diverse 12-run batch covering all three DES ratios, but its frozen ReactionT5 yield model proved solvent/temperature/time-blind (≤0.117 pp within-pair spread versus 39.73 pp across catalyst identity). No solvent ranking, matched MAE, green-vs-conventional yield claim, impurity direction, selected protocol or measured E-factor was obtained. Self-assessed completion is approximately 43% (6/14 items). Full details: [comparison report](../../results/task-06-green-solvent-suzuki-optimization/comparison_report.md), [benchmark](../../benchmarks/task-06-green-solvent-suzuki-optimization/README.md), [results inventory](../../results/task-06-green-solvent-suzuki-optimization/README.md), [achievements](../../results/task-06-green-solvent-suzuki-optimization/achievements_and_comparison.md) and [gaps](../../results/task-06-green-solvent-suzuki-optimization/gaps_and_improvement_plan.md).
