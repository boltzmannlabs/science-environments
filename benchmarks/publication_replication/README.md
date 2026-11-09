# Focused publication-replication benchmark

This benchmark is deliberately small and outcome-focused. It does not attempt
to reproduce all SAMPL6 systems. Each case selects one published molecular
system and tests whether the agent can reconstruct the reported simulation
setup, identify missing parameters, and execute controlled configuration
variants.

The runner performs immutable-input and parameter-consistency checks. A
`PASS` means the declared setup is internally consistent and the local adapter
ran; it is not a claim that a paper's long-timescale observable was reproduced.
Missing trajectories, reference observables, or exact protocol details produce
`REVIEW`.

Run from the repository root:

```bash
python benchmarks/publication_replication/run_benchmark.py \
  --config published --config variant
```

Results are written to `benchmarks/publication_replication/results/`.
