# MD runtime contracts

The runtime accepts one JSON packet from `inputs/MD-*/task.json`, preserves
the packet hash, selects the declared engine adapter, and returns evidence with
`PASS`, `REVIEW`, `NEEDS_INPUT`, or `FAIL`. Adapter success is not scientific
qualification. Qualification requires the independent evaluator and all
task-specific reference evidence.

Use `scripts/run_agent_harness.py` for bounded execution. Original inputs and
derived repairs are never overwritten; outputs are written under `results/`.
