# molecular-design-and-generation

Computational drug discovery environment covering pharmacophore-based virtual screening, structure-based docking, and ADMET profiling.

## Tasks

| Task | Target | Paper |
|------|--------|-------|
| [task_001](tasks/task_001_caii_fragment_screening.md) | Carbonic anhydrase II (glaucoma) | [Front Chem 2025](https://doi.org/10.3389/fchem.2025.1627793) · [PMC12528100](https://pmc.ncbi.nlm.nih.gov/articles/PMC12528100/) |
| [task_002](tasks/task_002_rock2_pharmacophore.md) | ROCK2 (cancer) | [PLoS ONE 2025](https://doi.org/10.1371/journal.pone.0323781) · [PMC12074392](https://pmc.ncbi.nlm.nih.gov/articles/PMC12074392/) |
| [task_003](tasks/task_003_khkc_pharmacophore_vs.md) | Ketohexokinase-C (NASH/NAFLD) | [Front Pharmacol 2025](https://doi.org/10.3389/fphar.2025.1531512) · [PMC12009819](https://pmc.ncbi.nlm.nih.gov/articles/PMC12009819/) |
| [task_004](tasks/task_004_foxm1_hsp70_dual_vs.md) | FoxM1 + Hsp70 (cancer, dual) | [Res Pharm Sci 2023](https://doi.org/10.4103/1735-5362.359431) · [PMC9872178](https://pmc.ncbi.nlm.nih.gov/articles/PMC9872178/) |
| [task_005](tasks/task_005_fgfr2_similarity_sbvs.md) | FGFR2 (cancer) | [Sci Rep 2024](https://doi.org/10.1038/s41598-024-69850-1) · [PMC11339395](https://pmc.ncbi.nlm.nih.gov/articles/PMC11339395/) |
| [task_006](tasks/task_006_gsk3b_pharmacophore_admet.md) | GSK-3β (Alzheimer's disease) | [Sci Rep 2026](https://doi.org/10.1038/s41598-026-56505-6) · [PMC13396737](https://pmc.ncbi.nlm.nih.gov/articles/PMC13396737/) |

## Layout

`ENVIRONMENT_SPEC.md` — environment definition, grading and rules · `MODELS_AND_TOOLS.md` — platform tool registry and engine anchoring · `config/` — machine-readable environment config (generated) · `tasks/` — task documents · `tests/` — static validators · `scripts/` — config generation, validation, run grading · `src/` — shared library · `benchmark/` — grading anchors and paper inventory · `results/` — run outputs.

Validate: `python3 scripts/validate_environment.py` · Grade a run: `python3 scripts/grade_run.py task_001 results/task_001/<run>`
