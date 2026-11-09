# Boltsim simulation-agent research

This index covers only the seven simulation modules retained on the `Boltsim`
branch. Notes distinguish executable evidence, reference data, planned work,
and unresolved scientific qualification requirements.

| Module | Scope and evidence |
| --- | --- |
| SPE | [Module README](../environments/spe_agents/README.md); method/basis compatibility, charge/spin, SCF recovery, and reproducibility. |
| Geo-Opt | [Module README](../environments/geo_opt_agents/README.md); convergence, gradients/Hessians, constraints, and minimum verification. |
| HOMO–LUMO | [Module README](../environments/homo_lumo_agents/README.md); orbital indexing, occupations, gaps, and state dependence. |
| QM/MM | [Module README](../environments/qmmm_agents/README.md); QM-region choice, link atoms, embedding, and force consistency. |
| FEP/TI | [Module README](../environments/fep_ti_agents/README.md); mapping, OpenFE workflows, overlap, convergence, uncertainty, and qualification. |
| MD | [Module README](../environments/md_agents/README.md); preparation, OpenMM/GROMACS/Amber adapters, recovery, and bounded runs. |
| Coarse-grained MD | [Module README](../environments/coarse_grained_md/README.md); mapping, CG models, membranes, phase behavior, and validation. |

## Shared research notes

See [simulation-agent-notes.md](simulation-agent-notes.md) for the common
scientific evidence policy and [references.md](references.md) for the external
engine and method references used by the environment specifications.
