# structure-based-discovery

Structure-based drug discovery environment covering pharmacophore screening, molecular docking, and ADMET profiling against structural targets.

## Tasks

| Task | Target | Paper |
|------|--------|-------|
| [task_001](tasks/task_001_egfr_pharmacophore_vs.md) | EGFR (cancer) | [PLoS ONE 2024](https://doi.org/10.1371/journal.pone.0311527) · [PMC11627428](https://pmc.ncbi.nlm.nih.gov/articles/PMC11627428/) |
| [task_002](tasks/task_002_trkb_pharmacophore_vs.md) | TrkB agonist pharmacophore VS (CDKL5-deficiency disorder) | [Bioinform Biol Insights 2023](https://doi.org/10.1177/11779322231158254) · [PMC9989394](https://pmc.ncbi.nlm.nih.gov/articles/PMC9989394/) |
| [task_003](tasks/task_003_mmp9_sbvs.md) | MMP-9 (cerebral ischemia) | [PLoS ONE 2026](https://doi.org/10.1371/journal.pone.0346627) · [PMC13175377](https://pmc.ncbi.nlm.nih.gov/articles/PMC13175377/) |
| [task_004](tasks/task_004_pi5p4k_allosteric_docking.md) | PI5P4Kγ allosteric site (cancer) | [Sci Rep 2025](https://doi.org/10.1038/s41598-025-07480-x) · [PMC12485083](https://pmc.ncbi.nlm.nih.gov/articles/PMC12485083/) |
| [task_005](tasks/task_005_pi3ka_docking_dynamics.md) | PI3Kα (NSCLC) | [RSC Adv 2022](https://doi.org/10.1039/D2RA03451D) · [PMC9346375](https://pmc.ncbi.nlm.nih.gov/articles/PMC9346375/) |
| [task_006](tasks/task_006_dual_kinase_pharmacophore.md) | VEGFR-2 + c-Met (cancer) | [Front Pharmacol 2025](https://doi.org/10.3389/fphar.2025.1534707) · [PMC11926154](https://pmc.ncbi.nlm.nih.gov/articles/PMC11926154/) |
| [task_007](tasks/task_007_hkii_antidengue_virtual_screening.md) | Human hexokinase II (anti-dengue discovery; screening, filtering, docking and 20 ns dynamics) | [BioTech 2021](https://doi.org/10.3390/biotech10010001) · [PMC9245486](https://pmc.ncbi.nlm.nih.gov/articles/PMC9245486/) |

Task 007 is an agent-facing capability workflow: the agent discovers and selects relevant suite tools while preserving the scientific sequence and constraints. Publication identity, historical results, tool provenance and source conflicts are retained in its [evaluator specification](benchmark/task_007_hkii_antidengue_virtual_screening.md), which must not be included in the agent execution bundle. Scientific capability coverage remains to be verified. The legacy single-score grading helper refuses to certify this task; it requires evidence-based scientific review.

## Layout

`ENVIRONMENT_SPEC.md` — environment definition, grading and rules · `MODELS_AND_TOOLS.md` — platform tool registry and engine anchoring · `config/` — machine-readable environment config (generated) · `tasks/` — task documents · `tests/` — static validators · `scripts/` — config generation, validation, run grading · `src/` — shared library · `benchmark/` — grading anchors and paper inventory · `results/` — run outputs.

Validate: `python3 scripts/validate_environment.py` · Grade a run: `python3 scripts/grade_run.py task_001 results/task_001/<run>`
