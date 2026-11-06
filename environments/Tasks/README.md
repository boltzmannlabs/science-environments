# Literature-Grounded Benchmark Suite for Synthetic-Chemistry Agent Tools

Five benchmark tasks, each comparing one (or all) of our tools — **retrosynthesis**, **forward reaction prediction**, **condition recommendation**, **impurity prediction** — against recently published synthetic-chemistry papers with concrete reactions, conditions, and yields.

Papers were selected in November 2026 via literature search; all are 2025–2026 publications. Full texts were not reachable from the authoring machine (publisher domains blocked), so each task file marks which ground-truth values are **verified at abstract level** and which must be **transcribed from the paper + SI before running** (`ground_truth/` step). Anti-leakage rule for all tasks: **mask tool corpora at 2025-12-31**.

| # | Task file | Tool | Paper (journal, year) | Benchmark question |
|---|---|---|---|---|
| 1 | [task1_retrosynthesis_hispidospermidin.md](task1_retrosynthesis_hispidospermidin.md) | Retrosynthesis | "Inside-Out" 14-step hispidospermidin synthesis (*JACS Au*, 2026, DOI 10.1021/jacsau.5c01567) | Can the planner recover expert strategic logic on a classic polycyclic alkaloid? |
| 2 | [task2_forward_prediction_indole_skeletal_editing.md](task2_forward_prediction_indole_skeletal_editing.md) | Forward reaction | Precision indole skeletal editing / single-carbon editing of tryptamines (*Science*, 2026, DOI 10.1126/science.aec3587) | Does the predictor find (or honestly flag as novel) a 2026 skeletal-editing product? |
| 3 | [task3_condition_recommendation_cn_coupling.md](task3_condition_recommendation_cn_coupling.md) | Condition recommendation | Metal-free benzamide–sulfonamide C–N coupling via Smiles rearrangement (*Commun. Chem.*, 2026, DOI 10.1038/s42004-026-02131-2) | Can it recommend metal-free conditions and predict yields on a fresh optimization campaign? |
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

---

# Part 2 — SC/FM curated paper benchmark series

Twenty-six paper-grounded task specs from the synthetic-chemistry & pharmaceutical-formulation curation, plus two cross-cutting modules. Same protocol as Part 1 (fill ground truth → freeze → run blind → score → report); exact citations are captured per file when the paper is retrieved (marked **To fill**).

## Synthetic chemistry (SC01–SC12)

| ID | File | Theme |
|---|---|---|
| SC01 | [SC01_suzuki_miyaura_pd_nhc_conditions.md](SC01_suzuki_miyaura_pd_nhc_conditions.md) | Pd-NHC catalyst/condition optimization (2026) |
| SC02 | [SC02_microwave_catalytic_amidation.md](SC02_microwave_catalytic_amidation.md) | µw catalytic amidation yield + generalization (2025) |
| SC03 | [SC03_microwave_suzuki_betaine_glycerol.md](SC03_microwave_suzuki_betaine_glycerol.md) | Green solvent substitution in Suzuki (2025) |
| SC04 | [SC04_desymmetrization_paracyclophane.md](SC04_desymmetrization_paracyclophane.md) | Yield + ee via catalyst/oxidant/base (2024) |
| SC05 | [SC05_solid_phase_thiazolopyridinone.md](SC05_solid_phase_thiazolopyridinone.md) | Heterocycle cyclization optimization (2025) |
| SC06 | [SC06_microflow_coupling_cyclization.md](SC06_microflow_coupling_cyclization.md) | Continuous-flow process improvement (2025) — *skip if BO prohibited* |
| SC07 | [SC07_adagrasib_second_gen_process.md](SC07_adagrasib_second_gen_process.md) | Adagrasib process redesign + cost (2024) |
| SC08 | [SC08_ceritinib_doe_scaleup.md](SC08_ceritinib_doe_scaleup.md) | Ceritinib DoE robustness/scale-up (2025) |
| SC09 | [SC09_pregabalin_continuous_flow.md](SC09_pregabalin_continuous_flow.md) | Pregabalin flow: time + impurity (2024) |
| SC10 | [SC10_dilute_workup_doe.md](SC10_dilute_workup_doe.md) | Dilute workup improvement via DoE (2024) |
| SC11 | [SC11_shared_routes_multiple_apis.md](SC11_shared_routes_multiple_apis.md) | Shared API routes via retrosynthesis (2025) |
| SC12 | [SC12_doe_practical_guide.md](SC12_doe_practical_guide.md) | DoE methodology: OFAT vs factorial vs RSM (2025) — shared oracle engine |

## Pharmaceutical formulation (FM01–FM14)

| ID | File | Theme |
|---|---|---|
| FM01 | [FM01_efavirenz_solid_dispersion.md](FM01_efavirenz_solid_dispersion.md) | Efavirenz solid dispersion composition (2025) |
| FM02 | [FM02_loratadine_tablet_dissolution.md](FM02_loratadine_tablet_dissolution.md) | Loratadine dissolution + robustness (2025) |
| FM03 | [FM03_lacidipine_ternary_asd.md](FM03_lacidipine_ternary_asd.md) | Lacidipine ternary ASD supersaturation (2024) |
| FM04 | [FM04_asd_tablet_disintegration.md](FM04_asd_tablet_disintegration.md) | ASD tablet disintegration (2025) |
| FM05 | [FM05_fenoprofen_odt_sublimation.md](FM05_fenoprofen_odt_sublimation.md) | Fenoprofen Ca ODT via sublimation (2025) |
| FM06 | [FM06_escitalopram_oral_thin_film.md](FM06_escitalopram_oral_thin_film.md) | Escitalopram oral thin film (2025) |
| FM07 | [FM07_donepezil_er_tablet.md](FM07_donepezil_er_tablet.md) | Donepezil ER + dose-dumping gate (2025) |
| FM08 | [FM08_mab_excipient_viscosity_hts.md](FM08_mab_excipient_viscosity_hts.md) | mAb excipient/viscosity HT screening (2024) |
| FM09 | [FM09_viscosity_llps_stability.md](FM09_viscosity_llps_stability.md) | Viscosity vs. phase separation (2025) |
| FM10 | [FM10_formulation_process_product_design.md](FM10_formulation_process_product_design.md) | Formulation–Process–Product joint design (2025) |
| FM11 | [FM11_wet_granulation_inverse_design.md](FM11_wet_granulation_inverse_design.md) | Wet granulation DoE (2024) — *ML paper: reference only, non-AI benchmark* |
| FM12 | [FM12_fluid_bed_granulation_drying.md](FM12_fluid_bed_granulation_drying.md) | Fluid-bed granulation/drying DoE (2024) |
| FM13 | [FM13_roller_compaction_dissolution.md](FM13_roller_compaction_dissolution.md) | Roller compaction vs. dissolution (2025) |
| FM14 | [FM14_herbal_odt_doe.md](FM14_herbal_odt_doe.md) | Herbal ODT multicomponent optimization (2025) |

## Cross-cutting modules

| ID | File | Content |
|---|---|---|
| SC-C | [SC-C_derived_research_topics.md](SC-C_derived_research_topics.md) | 5 derived topics (substrate generalization, loading reduction, solvent replacement, impurity suppression, time optimization) — run on host tasks |
| SC-P / FM-P | [SC-P_FM-P_research_problem_statements.md](SC-P_FM-P_research_problem_statements.md) | 10 problem statements (SC-P01–P05, FM-P01–P05) mapping papers → generic problems + reporting template |

**FM note:** formulation tasks use the formulation-optimisation / dissolution environments and the shared SC12 oracle-query DoE engine rather than the small-molecule reaction tools; several carry safety gates (FM07 dose dumping, FM09 phase separation).
