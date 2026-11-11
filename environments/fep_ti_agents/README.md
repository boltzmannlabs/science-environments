# FEP/TI Specialist Agents

This environment now follows the paper-benchmark layout used by the other
Science-Environments packages. Read `ENVIRONMENT_SPEC.md`, `MODELS_AND_TOOLS.md`
and `STATUS.md` first; paper tasks are indexed in `tasks/README.md`, benchmark
scope is in `benchmark/README.md`, and current evidence is in `results/`.

**Status: In progress.** The environment contains paper-derived setup
benchmarks, specialist/problem-solving contracts and executable validation.
It does not claim a production free-energy calculation without real windows,
trajectories, overlap, convergence, uncertainty and reference evidence.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Configuration and schemas](config/)
3. [Agent contracts](src/agents/contracts.json)
4. [Task cards](tasks/)
5. [Fixture results](results/fixture_results.json)
6. [Acceptance tests](tests/)

Paper-reconstruction tasks are the primary benchmark. The bounded SAMPL6
manifest remains a separate provenance fixture and is not the required scope
of the publication-based tasks.

The paper catalogue targets eight concrete task definitions from five distinct
publication/study families, following the grouping style used by the De Novo
Enzyme Design environment. At present, two FEP paper tasks are implemented;
the remaining catalogue entries are planned until their inputs and protocols
are pinned.

Shared diagnosis, retry, audit, and provenance logic is in
[`../md_agents/recovery_agents/cross_domain`](../md_agents/recovery_agents/cross_domain/).

## Agents

FEP-PS01 audits alchemical mapping; FEP-PS02 transformation feasibility;
FEP-PS03 lambda schedules; FEP-PS04 phase-space overlap; FEP-PS05 convergence;
FEP-PS06 hysteresis and cycle closure; FEP-PS07 estimators and uncertainty;
FEP-PS08 charge-changing corrections; FEP-PS09 restraints and standard state;
and FEP-PS10 final result qualification.

The package also records 15 environment families in
[`src/agents/fep_environment_contracts.json`](src/agents/fep_environment_contracts.json)
and 15 specialist contracts in
[`src/agents/fep_agent_contracts.json`](src/agents/fep_agent_contracts.json). Each
family has a uniform task card in `tasks/fep_env_*.md`, covering inputs,
execution, independent evaluation, acceptance criteria, and failure status.
Each of the 15 specialist agents has a corresponding detailed task card in
`tasks/fep_ag*.md`; the 10 problem-solving agents are documented in
`tasks/fep_ps*.md`.

## Executable calculation evidence

Run the reproducible smoke calculation with:

```bash
python scripts/run_toy_ti.py
```

It samples an 11-window harmonic alchemical path twice, computes the TI
estimate, adjacent-window overlap, and error against an analytic reference.
The evidence is written to `results/toy_ti/toy_results.json`. This validates
the calculation/evaluator path only; it is explicitly **not** a qualified
protein–ligand FEP result. Production qualification still requires a supported
engine, molecular topology and parameters, real trajectories, frozen reference
data, and independent repeats.

## Molecular benchmark manifest

[`benchmark/sampl6/manifest.json`](benchmark/sampl6/manifest.json) pins a
bounded SAMPL6 OA-G3/OA-G6 pair, including structures-at-source URLs, guest
SMILES, experimental ΔG values, the OA-G3→OA-G6 relative target (0.21 ± 0.028
kcal/mol), and 12 controlled fault-injection cases. The manifest deliberately
does not vendor multi-megabyte topology/trajectory files. Use the recorded
upstream revision and URLs to retrieve them, verify hashes, and record the
actual revision before engine execution.

Validate the manifest with:

```bash
python scripts/validate_sampl6_manifest.py
```

This is a benchmark input/provenance layer; it does not claim that the
SAMPL6 molecular simulations have already been executed.

## Package structure

```text
fep_ti_agents/
├── README.md / ENVIRONMENT_SPEC.md / REFERENCES.md
├── STATUS.md / MODELS_AND_TOOLS.md
├── config/ (schemas and policy)
├── src/ (shared task and evidence contracts)
├── src/agents/contracts.json
├── src/agents/fep_environment_contracts.json / fep_agent_contracts.json
├── tasks/ (15 specialist cards + 10 problem-solving cards + 15 environment cards)
├── scripts/ (execution and validation entry points)
├── tests/ (package and task tests)
├── benchmark/ (publication-derived benchmark records)
└── results/ (run indexes and qualification evidence)
```
