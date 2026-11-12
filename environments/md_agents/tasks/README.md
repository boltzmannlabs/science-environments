# Molecular dynamics task catalogue

This folder contains the task cards used to evaluate MD agents. Cards cover
system preparation, simulation control, sampling, analysis, online resources,
recovery, and published-protocol reconstruction.

## Task catalogue

| Task family | Scope | Evidence target |
| --- | --- | --- |
| `md_01`–`md_20` | Core setup and execution | Valid inputs, controls, recovery, and finite trajectories |
| `md_21`–`md_30` | Literature, models, datasets, provenance | Source identity, hashes, licences, and compatibility |
| `md_31`–`md_50` | Scientific analysis and sampling | Observables, convergence, uncertainty, and reproducibility |
| `md_51`–`md_62` | Failure and orchestration scenarios | Correct stop reasons and evidence-backed recovery |
| `publication_md_001` | Published MD setup reconstruction | Matched protocol fields and paper comparison |

## How to execute a task

1. Read the selected card, [environment specification](../ENVIRONMENT_SPEC.md),
   and [tool policy](../MODELS_AND_TOOLS.md).
2. Preserve the frozen input under `benchmark/` and record its SHA-256 hash.
3. Declare engine, force field, solvent, sampling, resource limits, and
   evaluation definitions before dispatch.
4. Keep published values, calculated outputs, and experimental context in
   separate records.
5. Report unsupported steps and missing reference data as `REVIEW`; never infer
   them from defaults.

## Expected result bundle

Return the task identifier, source/input manifest, settings, raw outputs,
normalized observables, uncertainty, comparison table, resource accounting,
and evaluator decision. A bounded pilot is not a paper reproduction.
