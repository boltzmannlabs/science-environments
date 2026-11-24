# FEP-PAPER-002 results — PTP1B `23477 -> 23482`

This directory indexes the paper-reconstruction evidence for the selected
PTP1B edge. The source task and immutable inputs remain in
`../../tasks/fep_paper_002/`; generated artifacts are retained there beside
their execution logs and hashes.

## Recorded evidence

- Input identity validation: `../../tasks/fep_paper_002/evaluation/input_validation.json`
- Paper parameter comparison: `../../tasks/fep_paper_002/evaluation/paper_parameter_comparison.json`
- Agent/tool trace: `../../tasks/fep_paper_002/execution/agent_execution_trace.json`
- Configuration matrix: `../../tasks/fep_paper_002/execution/config_comparison.json`
- Endpoint parameterization and hashes: `../../tasks/fep_paper_002/execution/parameterization.json`
- Human-readable benchmark: `../../benchmark/fep_paper_002_ptp1b.md`

## Result

Endpoint setup is `SETUP_PASS` for the specialist-generated configuration.
The overall scientific result is `REVIEW`: complex/solvent hybrid topologies,
lambda-window trajectories, overlap, convergence, uncertainty and an
independent free-energy estimate are not available for this selected edge.

The results are therefore setup-reconstruction evidence, not a publication-
qualified FEP reproduction.
