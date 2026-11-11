# FEP-PAPER-002 — PTP1B public benchmark edge

This task is the second paper-derived FEP benchmark. It uses the PTP1B
`23477 -> 23482` edge from the public binding free-energy benchmark released
with Ross et al., *The maximal and current accuracy of rigorous protein-ligand
binding free energy calculations* (Communications Chemistry, 2023).

The task evaluates whether an agent can reconstruct a protein–ligand RBFE
environment from a public paper/dataset source. It is intentionally separate
from the CDK2/Alchaware task and does not reuse its answer files.

Run:

```bash
python scripts/validate_inputs.py
python -m pytest -q tests
```

The first endpoint parameterization is retained as superseded evidence because
it incorrectly forced charge zero for SDF inputs whose formal charge is -2.
The corrected GAFF2/AM1-BCC parameterization is recorded in
`execution/parameterization_corrected.json`; the corrected complexes use nine
Na+ ions and have total charge within 0.002 e of neutral.

Protein preparation is recorded in `execution/protein_preparation.json`.
The ff14SB protein topology has a recorded net charge of `-7` before ion
neutralization. Both endpoint complexes were then assembled, solvated with
TIP3P and neutralized with seven sodium ions. ParmEd independently checked
atom counts, box dimensions, ion counts and final charge; see
`execution/complex_preparation.json` and the preserved `tleap` logs.

This is an environment-construction and bounded execution result, not a
scientifically qualified production FEP result.
The corrected endpoint complex/solvent preparation and OpenFE hybrid topology
generation are setup-validated. An extended OpenFE run was executed on the RTX
3060 through the registered OpenCL backend (CUDA is unavailable in this
OpenMM build). Both solvent and complex legs completed 11-window simulations
with 2 ps equilibration and 10 ps production per window. The independent
evaluation records finite energies and overlap proxies, but one repeat and 10
production samples per window are insufficient for convergence, replica
agreement or uncertainty; the case therefore remains REVIEW.

Run/evaluate the bounded GPU smoke test with:

```bash
python scripts/run_openfe_bounded.py
python scripts/evaluate_bounded_run.py
```

The extended run is preserved in
`execution/openfe_production_replica1/`. Checkpoint files are retained locally
for restart; their SHA-256 values are recorded in `run_record.json` because
they exceed the GitHub file-size limit.

Agent/tool provenance is recorded in `execution/agent_execution_trace.json`.
It identifies the parameter, preparation and evaluation roles, commands,
outputs and independent checks. The trace explicitly records that this run
used a deterministic specialist harness; it does not falsely claim autonomous
LLM execution. The paper comparison is in
`evaluation/paper_parameter_comparison.json`, and the A/B/C architecture
matrix is in `evaluation/agent_configuration_comparison.json`.

The executable setup matrix is recorded in
`execution/config_comparison.json`. It evaluates the paper reference, the
specialist-generated setup, a supported alternative and a deliberately
reversed transformation. The invalid configuration is stopped before any
simulation, while the valid setup is accepted only at the environment
construction stage.

The current result is `REVIEW`: input identity, ligand extraction and the
published experimental edge and endpoint ligand parameterization are
validated, but the source paper does not provide a complete open alchemical
trajectory bundle for this edge.
