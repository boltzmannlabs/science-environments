# Acceptance and validation plan

## Package checks

Validate JSON schemas, the 30-agent registry, task links and contract IDs with
`python3 tests/validate_spec.py`. These checks do not establish a working MD
engine or scientific qualification.

## Required before execution

1. Select and version a supported engine and force field.
2. Freeze systems, topology, parameters, seeds, hardware and resource limits.
3. Add independent reference trajectories and domain-specific evaluators.
4. Test minimization, equilibration, restart, trajectory integrity and analysis.
5. For online resources, verify URL, version, license, checksum, compatibility
   and reproducible cache before execution.

## Required benchmark arms

Compare a fixed workflow, general Agent Scientist workflow and specialist
workflow on identical frozen cases. Report stability, sampling, scientific
metrics, failure categories, wall time, compute cost and reproducibility.
