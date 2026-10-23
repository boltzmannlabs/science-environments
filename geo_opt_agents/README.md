# GeoOpt-Bench

GeoOpt-Bench is a reproducible benchmark for geometry-optimisation agents,
inspired by the task/workflow/grader/reference-artifact structure of
[CompMat-Bench](https://github.com/cz2014/CompMat-Bench).

The benchmark evaluates scientific decisions with deterministic checks and
numerical tolerances. It does not use an LLM judge and does not require Agent
Scientist for the baseline harness.

## Layout

- `contracts/`: the 18 specialist-agent contracts
- `tasks/`: frozen task cards and pilot manifest
- `references/`: trusted reference metadata and hashes
- `graders/`: independent deterministic graders
- `workflows/`: multi-step validate → optimise → verify workflows
- `schemas/`: submission and result schemas
- `scripts/`: scaffold and benchmark utilities

## Initial pilot

The pilot freezes 18 specialist qualification tasks plus five end-to-end
workflow cases. Each run must preserve the initial geometry, settings,
convergence thresholds, final geometry fingerprint, energy/gradient evidence,
runtime, retry count, token usage, and failure category.

Run the independent contract grader with:

```bash
python graders/grade_submission.py tasks/pilot_reference_submission.json
```

This only validates the benchmark machinery; it is not a claim that all 18
agents have completed live optimisation. Engine execution is a separate,
versioned phase.

## Tier-1 live backend

The first executable backend is `engine/pyscf_scipy.py`, using PySCF B3LYP/
6-31G* energies and analytic gradients with SciPy BFGS. Run the four Tier-1
systems with:

```bash
python -m engine.pyscf_scipy
```

Results are written to `reports/tier1/summary.json` and one JSON file per
system. This is a CPU pilot backend, not yet a qualification of every
specialist or of the three agent-comparison arms.

The same pilot can run on GPU4PySCF:

```bash
python -m engine.run_gpu_tier1
```

GPU evidence is written separately to `reports/tier1_gpu/` and does not
overwrite the CPU baseline.

## Complete input pack

Regenerate the common-schema task packets and molecular/adversarial fixtures:

```bash
python scripts/build_benchmark_pack.py
python scripts/run_suite.py
```

This validates 18 specialist packets and the valid/malformed structure cases;
the report is written to `reports/suite/summary.json`. The backend for live
calculations is PySCF + GPU4PySCF with SciPy BFGS.

## Agent-level qualification run

Run one explicit input fixture for every specialist with:

```bash
python scripts/run_agent_qualification.py
```

The matrix is written to `reports/agent_qualification/`. It records the input
fixture, execution type, status, evidence, hashes, runtime, retries, and token
fields. Deterministic fixture passes are intentionally separated from live
GPU-engine evidence; unsupported Hessian and protein-ligand cases remain
`review`.
