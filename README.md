# Boltsim simulation-agent environments

`Boltsim` is the simulation-focused branch of Science-Environments. It
contains seven executable specialist environment families and their uniform
portable subagent packages. Unrelated pod environments are intentionally not
included on this branch.

## Included environments

| Module | Environment | Scope |
| --- | --- | --- |
| SPE | `environments/spe_agents/` | Single-point energy execution and recovery |
| Geo-Opt | `environments/geo_opt_agents/` | Geometry optimization and minimum verification |
| HOMO–LUMO | `environments/homo_lumo_agents/` | Frontier-orbital and electronic-state analysis |
| QM/MM | `environments/qmmm_agents/` | QM-region, boundary, embedding, and coupling validation |
| FEP/TI | `environments/fep_ti_agents/` | Alchemical setup, sampling, estimation, and qualification |
| MD | `environments/md_agents/` | Atomistic molecular-dynamics execution, analysis, and recovery |
| Coarse-grained MD | `environments/coarse_grained_md/` | Mapping, CG simulation, and structural/thermodynamic validation |

The portable contribution packages in `subagent-catalog/` mirror the three
simulation families currently prepared for the contribution workflow: MD,
coarse-grained MD, and FEP/TI. The other four module environments retain their
native contracts and tests and can be packaged using the same template.

## Research and evidence

The [research index](research/README.md) records the scientific scope,
references, and qualification boundaries for the retained modules. Environment
README files contain their exact commands, inputs, tests, and evidence status.
Results marked `REVIEW` are not production-qualified claims.

## Paper-based reconstruction benchmarks

The focused paper-to-environment benchmark is under
`benchmarks/publication_replication/`. The first executable task packets are:

- `environments/md_paper_reproduction/tasks/md_paper_001/` — CDK2–CS3 MD
  protocol reconstruction from a published hypersound-accelerated MD study.
- `environments/fep_paper_reproduction/tasks/fep_paper_001/` — CDK2 FEP
  protocol reconstruction from a force-field comparison study.

Each packet keeps paper-reported, agent-generated, supported-alternative, and
deliberately perturbed configurations separate. Run
`python scripts/evaluate_paper_tasks.py` to evaluate setup construction locally.

## Contribution layout

Each portable package follows:

```text
subagent-catalog/<module>/
├── manifest.yaml
├── instructions.md
├── README.md
├── skills/<skill>/SKILL.md
└── tests/{sample.json,expected.json,validation.json}
```

Do not add credentials, installed environments, private datasets, generated
trajectories, or machine-specific paths. Follow
[CONTRIBUTING.md](CONTRIBUTING.md) for issue, branch, test, and PR workflow.
