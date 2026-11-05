# MODELS_AND_TOOLS — molecular-design-and-generation

Platform tool registry and docking-engine anchoring policy for this environment. The per-task verbatim tool lists (Boltzmann platform tools / other standard tools / paper tools) live in each `tasks/*.md` and are the source of truth; this file records the registry-level facts that do not vary per task.

## Boltzmann platform tools

| Tool | Workflow role | Key inputs | Underlying model / engine | Notes |
|---|---|---|---|---|
| `Vina_basic_docking` | Primary docking engine | `pdb_file`, `center_x/y/z`, `exhaustivness` (sic), `smiles` | AutoDock Vina scoring function | Produces the graded kcal/mol score. The argument is spelled `exhaustivness` in the real platform API — the misspelling is intentional API surface, never "correct" it |
| `Diffdock` | Second-engine pose corroboration | `processed_pdb`, `input_csv` | DiffDock diffusion-based pose predictor | No calibrated kcal/mol scale — use for pose/rank agreement with Vina, never as the graded score |
| `pharmacophoreHypothesis` | Pharmacophore generation | `pdb_file`, `features` | Feature extraction from bound-ligand/active-site geometry | Replaces paper-side Pharmit/MOE/LigandScout hypothesis building |
| `Pharmacophore_Screening` | Library screening vs a hypothesis | hypothesis + library | Feature-matching search | Library inputs must be public (ZINC/PubChem/ChEMBL/NCI) |
| `Similarity_Screening` | Analog/similarity hit generation | query + library | 2D/3D similarity retrieval | Replaces paper-side SwissSimilarity-style searches |
| `Property_Prediction` | ADMET / drug-likeness profiling | `smiles`, `global_models` | SwissADME-class global property models | Covers Lipinski/PAINS/Brenk-style filters used in pass bars |
| `MDS_openMM` | MD validation (secondary) | `topology`, `duration_ns` (+ force-field options) | OpenMM | Paper engines differ per task (GROMACS/Desmond/GROMACS-era AMBER); MD validates the top hits, it is never the primary grading gate |
| `Binding_affinity_Prediction` | Affinity corroboration (secondary) | `smiles`, `tar_seq`, `mode` | Graph-DTA-style learned affinity predictor | Corroborates docking; MM-GBSA-style ranking language in task docs refers to this tool's output only when the paper itself used MM-GBSA/MM-PBSA |

**Docking is platform-only.** Every docking run in this environment goes through `Vina_basic_docking` (+ `Diffdock` as second engine). Local docking engines are not permitted for graded runs.

## Engine anchoring policy

Cross-engine kcal/mol scales are **not** interchangeable. Each task's pass bar therefore declares its anchoring mode:

1. **Same-engine** — the paper docked with AutoDock Vina; platform Vina scores compare directly (task_005, task_006).
2. **Engine-relative** — the paper used Glide (SP/XP) or another engine; the published kcal/mol value is carried as a reference bar with an explicit "compare engine-relative" caveat (task_001, task_002, task_003).
3. **Self-calibrating** — the bar is defined inside the agent's own run: redock the paper's reference ligand in the platform engine first, then beat that score (task_004's FDI-6 / VER-155008 out-docking bars; task_001's MM-GBSA rank bar).

Second-engine corroboration (`Diffdock`) is expected on final candidates but does not replace the Vina score in grading.

## Per-task engine map

| Task | Paper screening | Paper docking engine | Anchoring |
|---|---|---|---|
| task_001 (CAII) | Phase pharmacophores | DOCK 6 + Glide (+ SQM rescoring, out of scope) | engine-relative ≤ −8.0 kcal/mol + top-3 MM-GBSA rank |
| task_002 (ROCK2) | Pharmit | Glide SP | engine-relative ≥2 hits ≤ −9.89 kcal/mol |
| task_003 (KHK-C) | pharmacophore (see doc) | Glide XP (AutoDock 4.2 also appears) | engine-relative < −7.76 kcal/mol |
| task_004 (FoxM1+Hsp70) | Pharmit | AutoDock 4.2 | self-calibrating: out-dock FDI-6 / VER-155008 |
| task_005 (FGFR2) | similarity retrieval | AutoDock Vina | same-engine ≤ −11.7 kcal/mol |
| task_006 (GSK-3β) | MOE ligand-based + Pharmit/ZINCPharmer structure-based | AutoDock Vina 1.1.2 | same-engine < −6.80 kcal/mol |

## Other standard tools

Referenced in task docs where the platform has no direct equivalent (MM-GBSA/MM-PBSA calculators, Pharmit, ProTox-class toxicity web tools, trajectory analyzers). They may be used for non-docking analysis; they never substitute for platform docking.

## Paper tools

Every task doc carries a "Paper tools (verbatim)" tier listing exactly what the source publication used, with versions. These are provenance records — agents run the platform equivalents, and any number an agent reports against a pass bar must come from the platform engine with the anchoring mode above.
