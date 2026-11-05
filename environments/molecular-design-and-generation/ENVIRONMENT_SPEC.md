# ENVIRONMENT_SPEC — molecular-design-and-generation

**Environment ID:** `molecular-design-and-generation`

**Version:** 2.0.0 · **Status:** Qualified (all tasks verified through extraction audit → verbatim audit → rule-compliance validation → exhaustive per-doc critique → closing re-audit; see STATUS.md)

## Purpose

Benchmark environment for hit discovery on the Boltzmann platform: an agent must take a human-disease target from a published virtual-screening study and independently execute the full computational chain — target/structure preparation, ligand or pharmacophore screening, molecular docking, ADMET/drug-likeness profiling, and MD validation — meeting the published pass bar without ever consulting the paper's hit lists.

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
| task_001 | CAII (glaucoma) | Front Chem 2025 · PMC12528100 | ≤ −8.0 kcal/mol (engine-relative) + top-3 MM-GBSA rank |
| task_002 | ROCK2 (cancer) | PLoS ONE 2025 · PMC12074392 | ≥2 hits ≤ −9.89 kcal/mol (Glide SP reference; engine-relative) |
| task_003 | KHK-C (NAFLD/NASH) | Front Pharmacol 2025 · PMC12009819 | < −7.76 kcal/mol (Glide XP reference) |
| task_004 | FoxM1 + Hsp70 (cancer, dual) | Res Pharm Sci 2023 · PMC9872178 | beat FDI-6 (FoxM1) AND VER-155008 (Hsp70) |
| task_005 | FGFR2 (cancer) | Sci Rep 2024 · PMC11339395 | ≤ −11.7 kcal/mol + full ADMET/PAINS pass |
| task_006 | GSK-3β (Alzheimer's) | Sci Rep 2026 · PMC13396737 | < −6.80 kcal/mol (same-engine Vina) + BBB permeant |

Machine-readable anchors: `config/environment.json` and `benchmark/benchmark.json` (generated from `tasks/*.md` by `scripts/gen_config.py` — the task docs are the single source of truth).

## Task-document format (mandatory, enforced by `tests/`)

Nine sections in exact order: Description · Target · Design Constraints · Computational Tool Capabilities (three tiers: Boltzmann platform tools / Other standard tools / Paper tools (verbatim)) · Evaluation Metrics (published values, verbatim) · Expected Output (file table + quantitative Pass bar) · Constraints (Time Limit 240 minutes + Reference Policy) · Important Instructions · Publication (DOI + PMC links).

Verbatim policy: every paper-sourced claim must match the paper exactly; anything not in the paper carries an explicit "(derived)" or "RCSB metadata" label; platform docking arg `exhaustivness` (sic) is the real API spelling and must not be "corrected".

## Grading

- **Pass bar:** each task defines a quantitative bar anchored to the paper's own reference values (same-engine where the paper used Vina; engine-relative with explicit note where the paper used Glide/AutoDock 4 — cross-engine kcal/mol scales are not interchangeable).
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

All inputs public (RCSB, PubChem, ChEMBL, ZINC, NCI). Gated commercial libraries are admissible only with an in-doc public-substitute clause (see task docs). Retired tasks are moved to `science-environments/retired/<environment>/`, never deleted.

## Directory layout

```
molecular-design-and-generation/
├── README.md            # task index (links verified by tests/)
├── ENVIRONMENT_SPEC.md  # this file
├── STATUS.md            # qualification state
├── MODELS_AND_TOOLS.md  # platform tool registry, engine anchoring
├── config/              # environment.json + environment.yaml (generated/hand)
├── tasks/               # task_001..006 documents (source of truth)
├── tests/               # static validators (pytest-compatible)
├── scripts/             # gen_config.py, validate_environment.py, grade_run.py
├── src/                 # env_lib.py (parsing, validation, grading)
├── benchmark/           # benchmark.json + papers.csv (generated)
└── results/             # run outputs: results/<task_id>/<run>/...
```
