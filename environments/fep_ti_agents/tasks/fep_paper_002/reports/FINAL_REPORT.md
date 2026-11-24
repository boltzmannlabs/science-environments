# PTP1B FEP Paper-Benchmark Final Report

**Task:** `fep_paper_002`  
**System:** PTP1B, PDB `2QBS`  
**Transformation:** ligand `23477 → 23482`  
**Published reference:** `-1.16 kcal/mol`  
**Branch:** `Boltsim`  
**Overall scientific status:** `REVIEW`

## Scope

This benchmark tests whether a paper-driven Agent Scientist can construct and
execute a reproducible relative-binding-free-energy environment. It separates
engineering completion, execution completion and scientific reproduction. A
successful engine run is not treated as evidence of converged free energy.

## Completed evidence

| Gate | Result | Evidence |
|---|---|---|
| Input identity and hashes | PASS | `evaluation/input_validation.json` |
| Ligand parameterization | PASS | `execution/parameterization_corrected.json` |
| Protein and endpoint preparation | PASS/REVIEW | `execution/complex_preparation_corrected.json` |
| Hybrid topology generation | PASS | OpenFE setup records for both legs |
| GPU execution | PASS | `execution/openfe_production_replica1/run_record.json` |
| Finite energies | PASS | `independent_evaluation.json` |
| Lambda coverage | PASS for execution | 11 windows per leg |
| Scientific convergence | REVIEW | 10 production samples/window |
| Replica agreement | REVIEW | one independent repeat |
| Free-energy uncertainty | REVIEW | not estimable from current sample depth |
| Publication-level reproduction | REVIEW | no defensible ΔΔG comparison yet |

## Production execution

The extended run used OpenFE/OpenMM on the NVIDIA GeForce RTX 3060 through the
registered OpenCL platform. CUDA was attempted but is not registered by the
current OpenMM build. Both solvent and complex legs completed setup and
simulation with:

- 11 lambda windows;
- 2 ps equilibration per window;
- 10 ps production per window;
- finite recorded energies;
- successful NetCDF output for both legs.

The independent evaluator recorded overlap proxies of `0.02288` for solvent
and `0.01465` for complex. These values are diagnostic evidence only; they are
not a substitute for a validated overlap matrix or converged estimator.

## Agent and tool evidence

The specialist-assisted workflow generated corrected GAFF2/AM1-BCC ligand
parameters, ff14SB/TIP3P endpoint systems and OpenFE hybrid systems. The
recorded trace identifies the tools and validation checks. It does not claim
autonomous LLM execution where only a deterministic harness was used.

The agent-architecture comparison remains explicit:

- General-purpose agent alone: not executed in this local package.
- Specialist-assisted workflow: setup and execution evidence available.
- Orchestrated workflow with independent evaluator: partially executed; final
  status remains REVIEW.

## Why scientific PASS is not assigned

The current run has only one repeat and ten production samples per window.
That is insufficient to demonstrate stable block estimates, independent
replica agreement, estimator uncertainty or publication-level reproducibility.
The OpenFE analysis stage therefore remains unresolved rather than being
converted into a numerical result from inadequate data.

## Remaining work for scientific qualification

1. Extend production from the validated checkpoints without changing the
   protocol.
2. Run at least two additional independent repeats with distinct seeds.
3. Recompute adjacent-window overlap from the complete energy matrix.
4. Perform block/time-series convergence and effective-sample-size analysis.
5. Calculate complex and solvent ΔG with BAR/MBAR and propagate uncertainty.
6. Compare the resulting ΔΔG with `-1.16 kcal/mol` using predefined criteria.
7. Have an independent evaluator assign `PASS`, `REVIEW` or `FAIL`.

## Reproducibility and provenance

All tracked setup, NetCDF, hybrid-system and evaluation artifacts are under
`execution/`. Large OpenMM checkpoint files are retained locally for restart;
their SHA-256 hashes are recorded in
`execution/openfe_production_replica1/run_record.json` because they exceed the
GitHub file-size limit.

## Validation commands

```bash
python scripts/validate_inputs.py
python scripts/evaluate_bounded_run.py \
  --run execution/openfe_production_replica1 --minimum-samples 10
python -m pytest -q tests
```

The final recorded software validation passed **39 tests**, and the package
specification validator passed. This establishes engineering and bounded
execution completion; it does not establish scientific reproduction.
