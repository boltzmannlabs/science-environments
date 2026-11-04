# Literature-Grounded Benchmark Suite for Synthetic-Chemistry Agent Tools

Five benchmark tasks, each comparing one (or all) of our tools — **retrosynthesis**, **forward reaction prediction**, **condition recommendation**, **impurity prediction** — against recently published synthetic-chemistry papers with concrete reactions, conditions, and yields.

Papers were selected in November 2026 via literature search; all are 2025–2026 publications. Full texts were not reachable from the authoring machine (publisher domains blocked), so each task file marks which ground-truth values are **verified at abstract level** and which must be **transcribed from the paper + SI before running** (`ground_truth/` step). Anti-leakage rule for all tasks: **mask tool corpora at 2025-12-31**.

| # | Task file | Tool | Paper (journal, year) | Benchmark question |
|---|---|---|---|---|
| 1 | [task1_retrosynthesis_hispidospermidin.md](task1_retrosynthesis_hispidospermidin.md) | Retrosynthesis | "Inside-Out" 14-step hispidospermidin synthesis (*JACS Au*, 2026, DOI 10.1021/jacsau.5c01567) | Can the planner recover expert strategic logic on a classic polycyclic alkaloid? |
| 2 | [task2_forward_prediction_indole_skeletal_editing.md](task2_forward_prediction_indole_skeletal_editing.md) | Forward reaction | Precision indole skeletal editing / single-carbon editing of tryptamines (*Science*, 2026, DOI 10.1126/science.aec3587) | Does the predictor find (or honestly flag as novel) a 2026 skeletal-editing product? |
| 3 | [task3_condition_recommendation_smiles_cn_coupling.md](task3_condition_recommendation_smiles_cn_coupling.md) | Condition recommendation | Metal-free benzamide–sulfonamide C–N coupling via Smiles rearrangement (*Commun. Chem.*, 2026, DOI 10.1038/s42004-026-02131-2) | Can it recommend metal-free conditions and predict yields on a fresh optimization campaign? |
| 4 | [task4_impurity_prediction_epalrestat.md](task4_impurity_prediction_epalrestat.md) | Impurity prediction | Scale-dependent impurity escalation in epalrestat synthesis (*OPRD*, 2025, 29(7), 1749) | Does it predict the RRT 0.47 hydrolysis→Michael-addition impurity and its scale-up risk? |
| 5 | [task5_integrated_gregatin_a.md](task5_integrated_gregatin_a.md) | All four (pipeline) | Evolution of gregatin A total syntheses review (*Chem. Eur. J.*, 2026, DOI 10.1002/chem.202503396) | Can the full agent-scientist pipeline deliver a self-consistent ≤10-step dossier vs. the published route record? |

## Shared run protocol

1. **Fill ground truth** — for each task, open the paper (+ SI), transcribe reactions/conditions/yields into `env/taskN_*/ground_truth/` per the "to extract" checklist in the task file.
2. **Freeze inputs** — commit `input/` + `ground_truth/` before any tool run.
3. **Run blind** — agent scientist executes tools with the paper masked; outputs to `env/taskN_*/runs/`.
4. **Score** — apply the per-task metric tables; write `env/taskN_*/scores/results.md`.
5. **Report** — one summary row per task in the table above gets pass/fail per metric; honest failure logging is a first-class output (Tasks 2 and 5 are expected to be hard).

## Design rules

- **Anti-leakage:** all tool corpora masked at 2025-12-31; the 2026 papers post-date the cutoff.
- **Calibration over raw accuracy:** confident wrong answers (e.g., classical indole reactivity in Task 2, metal catalysis in Task 3) are tracked as the primary failure signal.
- **Structure-aware honesty:** every task file separates verified-vs-to-confirm ground truth; no bibliographic or numeric value is asserted beyond what the searches supported.
- Environments follow the `science-environments` conventions (`input/ ground_truth/ runs/ scores/`), so tasks can graduate into `environments/<domain>/tasks/` when the executable contracts land.
