# Task 05 — microwave-assisted catalytic amidation blind study

Folder identifier: `task-05-microwave-catalytic-amidation`. Use this same identifier under `tasks/`, `benchmarks/` and `results/`.

## Overall objective

Evaluate a multi-tool workflow for a blind, microwave-assisted, *catalytic* direct amidation of an aryl amine with an aryl carboxylic acid, focused on a sterically hindered pair. The workflow must return ranked catalytic conditions, predict yields, rank solvents, select one fixed protocol that maximizes the worst-performing substrate class while limiting microwave time, and flag plausible side products — without accessing withheld experimental answers. Distinguish tool predictions and design hypotheses from measured experimental results at every stage. Reagent-mediated coupling alone is not an equivalent catalytic solution.

## Problem statement and scope

| Input | Value |
|---|---|
| Aryl amine | 2,6-dimethylaniline, `Nc1c(C)cccc1C` |
| Aryl acid | 2-methylbenzoic acid (o-toluic acid), `O=C(O)c1ccccc1C` |
| Target amide | N-(2,6-dimethylphenyl)-2-methylbenzamide, `O=C(Nc1c(C)cccc1C)c1ccccc1C` |
| Reaction class | Direct catalytic amidation (dehydrative) |
| Steric class | hindered (both partners ortho-substituted) |
| Heating mode | microwave |
| Constraint | `catalyst_required: true` |
| Configuration | `top_k_conditions: 10`, `blind_mode: true`, `input_mode: illustrative` |

The target is a structural input, not an experimental answer or independent product discovery. The supplied task analysis did not identify the exact benchmark substrate matrix; the structures above are the workflow's **validated illustrative example** (`DEMO_01`), not a claimed benchmark experimental pair. The benchmark's experimental optimum, measured yields, reference microwave time, pass cutoff, side-product answers and designated 2025 high-throughput-experiment (HTE) paper were withheld. No exact-pair, benchmark-ID, original-paper or measured-yield lookup was performed during blind generation.

Problem stages: input validation; condition recommendation with catalyst/microwave constraint checking; literature comparison after freezing; local Bayesian design-of-experiments over an explicit catalytic condition space; provenance recording.

## Exact target/input and source provenance

The supplied workflow was `SC02_agent_workflow (1).md` (task identifier `SC02`). The internal `condition_recommendation` job `6b05bcdf8b9d410520f9a7b3` (experiment `Condition Recommendation - 20261124-163541Z - deb04e`) was submitted and polled to completion during the originating session. All outputs were frozen before any post-hoc literature review. Source call IDs are preserved in [results/task_record.json](../../results/task-05-microwave-catalytic-amidation/task_record.json); raw service exports are not redistributed here.

## Execution approach

| Stage | Tool or method | Inputs | Origin |
|---|---|---|---|
| SMILES validation | RDKit | three supplied structures | local (originating session) |
| Conditions | `condition_recommendation` job `6b05bcdf8b9d410520f9a7b3` | reactants + validated product | internal platform |
| Constraint audit | Check `catalyst_name`, heating mode and time fields | 10 tool-returned conditions | local documentary review |
| Literature comparison | PubMed/E-utilities + PMC full text; Crossref metadata | verified L1–L5 sources | external public literature, post-hoc |
| Catalytic design campaign | `reaction-optimize` local pipeline, BayBE v1 | explicit catalytic `condition_space` | external local tool |
| Persistent campaign | `reaction_optimizer.campaign_cli create/next/summary` | catalytic campaign JSON | external local tool |
| Prior-yield seeding | Earlier predicted yields as `status: excluded`, QC-flagged | 10 prior predictions | external local tool |

The tool job was accepted and polled once to a terminal `completed` state; no duplicate submission was made. The local optimizer was executed directly in the originating session. No wet-lab experiment, model training or new service job was performed during packaging of these folders.

## Expected outcomes and acceptance criteria

1. Return up to ten conditions with original numeric fields; missing catalyst identity, heating mode and time remain null, never filled from hidden evidence.
2. Enforce the catalytic constraint: reagent-only proposals must be flagged as non-compliant with `catalyst_required: true`.
3. Report microwave time and temperature where available; do not infer time from temperature.
4. Provide up to three solvent candidates with an explicit comparison basis; do not rank solvents from incompatible literature (e.g. solvent-free) rows.
5. Report side-product candidates only as hypotheses; never call model scores experimental yields.
6. Rank candidates only where comparable numerical evidence exists; reject condition-invariant yield estimates as discriminating predictions.
7. Attempt a catalytic design-of-experiments campaign; report Bayesian fitting only if at least four reviewed measured candidates exist.
8. Freeze outputs with provenance before literature comparison and avoid prohibited benchmark lookups.

## Actual outcomes

The internal condition tool returned ten ranked conditions with pyridine/HCl/TFA/K2CO3 reagent sets, temperatures of 20–80 °C, and predicted yields clustered at 53.5–60.7%. Every candidate had `catalyst_name: []`; no heating mode or reaction time was returned. The output therefore fails the task's catalytic-microwave requirement before any yield comparison.

Post-hoc literature verification confirmed the contextual sources L1–L5: CAN/solvent-free/open-microwave direct amidation (2020); borate-ester catalysis in tert-butyl acetate with >80% isolated yield after 20 h thermal and tolerance of hindered/electron-poor anilines (2025); borane–pyridine at 5 mol% (2024); fluorous boronic-acid catalysis (2023); and an ortho-aminophenylboronic-acid paper (2026, after a possible 2025-12-31 training cutoff). None of these is the designated 2025 HTE paper, which remains unidentified.

The local optimizer compiled 192 catalytic candidates from an explicit condition space (CAN, borane–pyridine, ortho-aminophenylboronic acid; solvent/temperature/time grids) and selected eight diverse initial designs; a persistent campaign was created and a four-experiment batch reserved with zero measurements. Earlier model-predicted yields were then attached as `excluded`, QC-flagged priors (never as reviewed measurements), blocking their re-selection; eight further untested conditions were selected. No Bayesian fit occurred because zero reviewed measured candidates exist. The benchmark remains `NOT_EVALUABLE`.

See [benchmark definition](../../benchmarks/task-05-microwave-catalytic-amidation/README.md), [paper catalog](../../benchmarks/task-05-microwave-catalytic-amidation/papers.md), [results inventory](../../results/task-05-microwave-catalytic-amidation/README.md), [comparison report](../../results/task-05-microwave-catalytic-amidation/comparison_report.md), [achievements](../../results/task-05-microwave-catalytic-amidation/achievements_and_comparison.md) and [gaps](../../results/task-05-microwave-catalytic-amidation/gaps_and_improvement_plan.md).
