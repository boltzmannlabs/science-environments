# MODELS_AND_TOOLS — structure-based-discovery

Platform tool registry and docking-engine anchoring policy for this environment. The per-task verbatim tool lists (Boltzmann platform tools / other standard tools / paper tools) live in each `tasks/*.md` and are the source of truth; this file records the registry-level facts that do not vary per task.

## Boltzmann platform tools

| Tool | Workflow role | Key inputs | Underlying model / engine | Notes |
|---|---|---|---|---|
| `Vina_basic_docking` | Primary docking engine | `pdb_file`, `center_x/y/z`, `exhaustivness` (sic), `smiles` | AutoDock Vina scoring function | Produces the graded kcal/mol score. The argument is spelled `exhaustivness` in the real platform API — the misspelling is intentional API surface, never "correct" it |
| `Diffdock` | Second-engine pose corroboration (task_005 additionally uses it as an induced-fit-docking proxy) | `processed_pdb`, `input_csv` | DiffDock diffusion-based pose predictor | No calibrated kcal/mol scale — use for pose/rank agreement with Vina, never as the graded score |
| `pharmacophoreHypothesis` | Pharmacophore generation | `pdb_file` or ligand sets, `features` | Feature extraction from bound-ligand/active-site geometry | Replaces paper-side Discovery Studio / Pharmit hypothesis building |
| `Pharmacophore_Screening` | Library screening vs a hypothesis | hypothesis + library | Feature-matching search | Library inputs must be public (ZINC/PubChem/ChEMBL/NCI); validation sets may be assembled from DUD-E/public actives per each task's Reference Policy |
| `Similarity_Screening` | Analog/similarity hit generation | query + library | 2D/3D similarity retrieval | Used where a paper seeded its search from known ligands |
| `Property_Prediction` | ADMET / drug-likeness profiling | `smiles`, `global_models` | SwissADME-class global property models | Covers Lipinski/PAINS/Brenk-style filters used in pass bars |
| `MDS_openMM` | MD validation (secondary) | `topology`, `duration_ns` (+ force-field options) | OpenMM | Paper engines differ per task (GROMACS/CHARMM36, NAMD); MD validates the top hits, it is never the primary grading gate |
| `Binding_affinity_Prediction` | Affinity corroboration (secondary) | `smiles`, `tar_seq`, `mode` | Graph-DTA-style learned affinity predictor | Corroborates docking; MM/PBSA-style ranking language in task docs refers to this tool's output only when the paper itself used MM/PBSA |

**Docking is platform-only.** Every docking run in this environment goes through `Vina_basic_docking` (+ `Diffdock` as second engine). Local docking engines are not permitted for graded runs.

## Engine anchoring policy

Cross-engine kcal/mol scales are **not** interchangeable (and task_006's paper reports kJ/mol — never mix units against a kcal/mol anchor). Each task's pass bar therefore declares its anchoring mode:

1. **Same-engine** — the paper docked with AutoDock Vina/PyRx; platform Vina scores compare directly (task_002).
2. **Engine-relative** — the paper used Glide (SP/XP), Discovery Studio (LibDock/CDOCKER) or similar; the published value is carried as a reference bar with an explicit "compare engine-relative" caveat (task_003, task_005, task_006).
3. **Self-calibrating** — the bar is defined inside the agent's own run: redock the paper's reference ligand(s) in the platform engine first, then beat that score (task_001's R85/known-inhibitor out-docking bar; task_004's DVF redock bar).

Second-engine corroboration (`Diffdock`) is expected on final candidates but does not replace the Vina score in grading.

## Per-task engine map

| Task | Paper screening | Paper docking engine | Anchoring |
|---|---|---|---|
| task_001 (EGFR) | pharmacophore (see doc) | Glide SP | self-calibrating: out-dock R85/known inhibitors + QikProp ranges |
| task_002 (TrkB) | ligand-based pharmacophore | AutoDock Vina (via PyRx) | same-engine: beat 7,8-DHF −7.1 (hits −9.6) |
| task_003 (MMP-9) | Phase structure-based pharmacophore | Glide SP | engine-relative −9.96 kcal/mol + MM-GBSA < −45.17 |
| task_004 (PI5P4Kγ) | pocket + pharmacophore (fpocket-class site detection) | AutoDock 4.2 / PyRx | self-calibrating: beat same-engine DVF redock (−9.26/−10.4) + MM-PBSA < −68.44 kJ/mol |
| task_005 (PI3Kα) | pharmacophore/similarity (see doc) | Glide XP (+ induced-fit) | engine-relative ≤ −3.941 kcal/mol + MMGBSA ≤ −42.58 |
| task_006 (VEGFR-2 + c-Met) | DS pharmacophore cascade (fit >2.4) | LibDock + CDOCKER | engine-relative < −60 kJ/mol both kinases |

## Other standard tools

Referenced in task docs where the platform has no direct equivalent (fpocket-class pocket detection, MM/PBSA calculators, DUD-E decoy sets, trajectory analyzers). They may be used for non-docking analysis; they never substitute for platform docking.

## Paper tools

Every task doc carries a "Paper tools (verbatim)" tier listing exactly what the source publication used, with versions. These are provenance records — agents run the platform equivalents, and any number an agent reports against a pass bar must come from the platform engine with the anchoring mode above.
