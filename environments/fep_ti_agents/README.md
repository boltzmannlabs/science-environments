# FEP/TI Specialist Agents

**Status: Specification with fixture validation.** This environment defines
ten FEP/TI problem-solving specialists, their inputs/outputs, acceptance
criteria, and evidence rules. It does not claim a production free-energy
calculation without real windows, trajectories, overlap, convergence,
uncertainty, and reference evidence.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Configuration and schemas](config/)
3. [Agent contracts](agents/contracts.json)
4. [Task cards](tasks/)
5. [Fixture results](results/fixture_results.json)
6. [Acceptance tests](tests/)

Shared diagnosis, retry, audit, and provenance logic is in
[`../md_agents/recovery_agents/cross_domain`](../md_agents/recovery_agents/cross_domain/).

## Agents

FEP-PS01 audits alchemical mapping; FEP-PS02 transformation feasibility;
FEP-PS03 lambda schedules; FEP-PS04 phase-space overlap; FEP-PS05 convergence;
FEP-PS06 hysteresis and cycle closure; FEP-PS07 estimators and uncertainty;
FEP-PS08 charge-changing corrections; FEP-PS09 restraints and standard state;
and FEP-PS10 final result qualification.

The package also records 15 environment families in
[`agents/fep_environment_contracts.json`](agents/fep_environment_contracts.json)
and 15 specialist contracts in
[`agents/fep_agent_contracts.json`](agents/fep_agent_contracts.json). Each
family has a uniform task card in `tasks/fep_env_*.md`, covering inputs,
execution, independent evaluation, acceptance criteria, and failure status.

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

[`benchmarks/sampl6/manifest.json`](benchmarks/sampl6/manifest.json) pins a
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
├── agents/contracts.json
├── agents/fep_environment_contracts.json / fep_agent_contracts.json
├── config/
├── tasks/ (10 problem-solving cards + 15 environment cards)
├── results/
├── scripts/
└── tests/
```
