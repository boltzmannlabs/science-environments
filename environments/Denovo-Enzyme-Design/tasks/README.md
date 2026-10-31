# Published in-silico reproduction tasks

This folder contains tasks for an agent to reproduce published computational enzyme-design workflows and compare its calculated outputs with the literature. Papers containing experimental validation are included; the first comparison is against their computational results.

## Task catalogue

| Task | Reproduction target | Computational reference |
| --- | --- | --- |
| [001 — AME](task_001_ame.md) | Atomic motif scaffolding and predicted recovery | Case coverage, motif RMSD, and ligand clashes |
| [002 — RFdiffusion2 retro-aldolase](task_002_rfdiffusion2_retroaldolase.md) | Reaction-specific generation and structural assessment | Reported TM-score; campaign-specific metrics from the supplement |
| [003 — RFdiffusion2 cysteine hydrolase](task_003_rfdiffusion2_cysteine_hydrolase.md) | Esterase motif scaffolding and assessment | Reported TM-score; campaign-specific filtering and models |
| [004 — Serine hydrolases](task_004_serine_hydrolases.md) | Fold filtering and multistate ensemble analysis | Published confidence/RMSD filters and state-specific contact statistics |
| [005 — Riff-Diff retro-aldolases](task_005_riff_diff_retroaldolases.md) | Motif-to-sequence workflow and computational assessment | Predicted design metrics, structural novelty, and dynamics |
| [006 — Riff-Diff MBHases](task_006_riff_diff_mbhases.md) | Reproduction for two MBH catalytic arrays | Per-design computational values in Supplementary Fig. 12 |
| [007 — Kemp eliminases](task_007_kemp_eliminases.md) | TIM-barrel design, substrate dynamics, and EVB | Calculated substrate retention, geometries, and free-energy profiles |
| [008 — Kemp QM/MM](task_008_kemp_qmmm.md) | Reaction free-energy surface calculations | Published computed activation barriers in kcal/mol |

Tasks 001–003 share one paper; tasks 005–006 share another. Preserve these relationships when reporting the number of independent studies or reaction families. Tasks 002, 003, and 006 require recovery of additional campaign-specific reference data before full numerical comparison.

## How to execute a task

1. Read the publication, supplement, released code, and the selected task. Recover the exact inputs and computational reference data identified there.
2. Create a source manifest containing URLs, release/commit identities, local paths, SHA-256 hashes, and sample identities. Keep inputs, reference outputs, and newly calculated outputs separate.
3. Declare the scope: reproduce calculations on published designs, rerun generation, or both. Existing designs used for reassessment remain imported examples; they are not fresh generated candidates.
4. Record the allowed execution platforms, actual tool capabilities, sampling, resource limits, and evaluation definitions before dispatch. Use the [environment tool policy](../MODELS_AND_TOOLS.md); current scientific execution is restricted to Boltzmann and ToolUniverse, with small preparation/check/analysis scripts.
5. Execute the published computational steps where supported, preserving raw results, invocation receipts, provider/job IDs, parameters, and usage.
6. Compare identical quantities under matched definitions. Report missing reference data, unavailable methods, failed calculations, and protocol changes explicitly.
7. Write the measurements and comparison report in a separate run directory. Keep task definitions in this folder.

The [environment specification](../ENVIRONMENT_SPEC.md), [agent instruction](../src/TASK.md), and [runtime contracts](../src/CONTRACTS.md) govern execution and evidence. For a whole generation run, initialize through `scripts/run.py`, supply this index, the selected task, and prepared manifests through repeated `--input` arguments, then use the frozen controller. The current controller has no documented arbitrary-stage replay interface; a calculation-only reproduction needs a separately identified assessment invocation. Do not manufacture preceding stage acceptances.

## Comparison rules

Distinguish four kinds of numbers:

| Kind | Use |
| --- | --- |
| Published computed result | Compare a matching calculation against the reported value or distribution. |
| Published filter threshold | Reproduce the same predicate; also obtain actual pass counts or per-design outputs before claiming a matching result. |
| Computational setting | Match sampling, temperature, model configuration, and other settings; matching a setting is not a successful outcome. |
| Experimental measurement | Keep as supporting validation. It is not the initial in-silico reproduction target. |

For missing numerical reference values, extract them from the specified source tables, files, or figures before scoring. Prefer raw source data. Label digitized figure values as approximate and include extraction uncertainty. Never substitute experimental activity for a missing computational baseline.

Each result row must identify the task, sample, metric, units, published value, calculated value, difference, uncertainty, source location, and whether protocols match. Preserve all scheduled samples and report denominators. A small pilot has a different scope from a published campaign.

Exact-method reproduction requires the original implementations and conditioning. A substituted predictor, force field, sampling engine, or geometry definition creates an adapted reproduction. Report it separately. Do not install local prediction models or use an external chemistry engine to bypass the current platform restriction.

These tasks assess specific published computational workflows. Their completion is separate from whole-enzyme qualification under every mandatory environment rule. Scope restrictions, controls, and missing evidence remain binding; the task list creates no new spending authorization.

## Expected result bundle

Return a source manifest, frozen method/settings record, raw computational outputs, normalized per-sample metrics, published-versus-calculated comparison table, resource accounting, and a readable comparison report. Include experimental context in a separate section when useful. Keep unsupported steps and unavailable reference values visible in the final comparison.
