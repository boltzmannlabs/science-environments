# ENVIRONMENT_SPEC — structure-based-discovery

**Environment ID:** `structure-based-discovery`

**Version:** 2.0.0 · **Status:** Qualified (all tasks verified through extraction audit → verbatim audit → rule-compliance validation → exhaustive per-doc critique → closing re-audit; see STATUS.md)

## Purpose

Benchmark environment for structure-based hit discovery on the Boltzmann platform: an agent must take a human-disease target from a published virtual-screening study and independently execute the full computational chain — target/structure preparation, ligand or pharmacophore screening, molecular docking, ADMET/drug-likeness profiling, and MD validation — meeting the published pass bar without ever consulting the paper's hit lists.

## Workflow model

Every task follows the same five-stage chain (paper-verbatim parameters, engine-anchored scores):

1. **Target & data** — public PDB structure(s), public compound libraries
2. **Screening** — pharmacophore or similarity-based hit generation
3. **Docking** — platform `Vina_basic_docking` (+ `Diffdock` as second engine)
4. **ADMET/drug-likeness** — `Property_Prediction` (SwissADME-class filters)
5. **MD validation** — `MDS_openMM` + `Binding_affinity_Prediction` (secondary validation only)

## Task inventory

| Task | Target (disease) | Paper | Docking anchor |
|---|---|---|---|
| task_001 | EGFR (cancer) | PLoS ONE 2024 · PMC11627428 | out-dock R85/known inhibitors + QikProp range pass |
| task_002 | TrkB agonist pharmacophore (CDKL5-deficiency disorder) | Bioinform Biol Insights 2023 · PMC9989394 | beat 7,8-DHF (−7.1 kcal/mol; published hits −9.6) + high GI absorption |
| task_003 | MMP-9 (cerebral ischemia) | PLoS ONE 2026 · PMC13175377 | −9.96 kcal/mol (Glide SP reference; engine-relative) + MM-GBSA < −45.17 |
| task_004 | PI5P4Kγ allosteric site (cancer) | Sci Rep 2025 · PMC12485083 | beat same-engine DVF redock (−9.26 AutoDock 4.2 / −10.4 PyRx) + MM-PBSA < −68.44 kJ/mol |
| task_005 | PI3Kα (NSCLC) | RSC Adv 2022 · PMC9346375 | ≤ −3.941 kcal/mol (Glide XP reference; engine-relative) + MMGBSA ≤ −42.58 |
| task_006 | VEGFR-2 + c-Met (cancer, dual) | Front Pharmacol 2025 · PMC11926154 | < −60 kJ/mol against both kinases + acceptable ADMET |
| task_007 | Human HKII (anti-dengue discovery) | BioTech 2021 · PMC9245486 | GLC/BG6/2DG-group Vina anchors ≤ −7.2/−7.8/−6.8 kcal/mol; documented ADME/toxicity; MD optional |

**Task 007 qualification:** added as a documentation-level specification. Its optional-MD scope overrides the general workflow description above. Exact USRCAT screening, platform endpoint equivalence and effective docking controls remain unverified, and the paper has unresolved internal conflicts. The existing single-score grader is insufficient for its three-group criteria and must not certify this task before qualification. Tasks 001–006 retain their existing specifications.

Machine-readable anchors: `config/environment.json` and `benchmark/benchmark.json` (generated from `tasks/*.md` by `scripts/gen_config.py` — the task docs are the single source of truth).

## Task-document format (mandatory, enforced by `tests/`)

Nine sections in exact order: Description · Target · Design Constraints · Computational Tool Capabilities (three tiers: Boltzmann platform tools / Other standard tools / Paper tools (verbatim)) · Evaluation Metrics (published values, verbatim) · Expected Output (file table + quantitative Pass bar) · Constraints (Time Limit 240 minutes + Reference Policy) · Important Instructions · Publication (DOI + PMC links).

Verbatim policy: every paper-sourced claim must match the paper exactly; anything not in the paper carries an explicit "(derived)" or "RCSB metadata" label; platform docking arg `exhaustivness` (sic) is the real API spelling and must not be "corrected".

## Grading

- **Pass bar:** each task defines a quantitative bar anchored to the paper's own reference values (same-engine where the paper used Vina; engine-relative with explicit note where the paper used Glide/AutoDock 4; self-calibrating redock anchors where the bar is a reference ligand the agent must out-dock in its own engine — cross-engine kcal/mol scales are not interchangeable).
- **Meet-or-beat:** runs are graded on completing the workflow and meeting the bar, never on reproducing the paper's exact hit lists.
- **Automation:** `scripts/grade_run.py <task_id> <run_dir>` checks expected output files and `metrics.json` (docking score vs anchor); MD/ADMET rows are human-reviewed.
- **Validity:** `scripts/validate_environment.py` must exit 0 before any benchmark run.

## Agent rules

- 240 minutes of agent working time; long-running platform jobs may complete asynchronously beyond it
- Reference Policy: do not look up the source publication to copy hit lists or scores
- All docking via Boltzmann platform tools; no local docking engines
- No QSAR, DFT, ML, or wet-lab stages

## Maintainer rules (paper vetting, applied before any task enters this environment)

Simple target→screening→docking→ADMET chain; computational only; MD as secondary validation; all data public — verified at the **file level** (supplement downloaded from Europe PMC and inspected, not just the data-availability statement); human disease target; no repurposing (no FDA/DrugBank libraries or lead provenance); no flora/natural-product libraries; no QSAR/DFT/ML; full-text scan (never abstracts) before acceptance; paper-internal conflicts must be annotated in-doc, never silently resolved.

## Data & provenance policy

All inputs public (RCSB, PubChem, ChEMBL, ZINC, NCI). Gated commercial libraries are admissible only with an in-doc public-substitute clause (see task docs; task_006's ChemDiv library carries one). Retired tasks are moved to `science-environments/retired/<environment>/`, never deleted.

## Directory layout

```
structure-based-discovery/
├── README.md            # task index (links verified by tests/)
├── ENVIRONMENT_SPEC.md  # this file
├── STATUS.md            # qualification state
├── MODELS_AND_TOOLS.md  # platform tool registry, engine anchoring
├── config/              # environment.json + environment.yaml (generated/hand)
├── tasks/               # task_001..007 documents (source of truth)
├── tests/               # static validators (pytest-compatible)
├── scripts/             # gen_config.py, validate_environment.py, grade_run.py
├── src/                 # env_lib.py (parsing, validation, grading)
├── benchmark/           # benchmark.json + papers.csv (generated)
└── results/             # run outputs: results/<task_id>/<run>/...
```
