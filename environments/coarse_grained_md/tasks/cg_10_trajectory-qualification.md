# Task: cg_10_trajectory-qualification

**Task family:** CG trajectory analysis and qualification. **Status:**
specification; execution and qualification are case-specific.

## Description and target

Validate RDF, density, radius of gyration, diffusion, phase behavior,
convergence, trajectory integrity, replicas, and reference agreement. The
specialists are Uncertainty/Sensitivity (`CG-19`) and Benchmark/Qualification
(`CG-20`).

## Required execution and output

Freeze topology, trajectory, state, analysis code, replicas, and tolerances;
independently validate metrics and provenance; return a `cg_task_bundle` with
raw artifacts, normalized values, uncertainty, status, and stop reason.

## Acceptance and limitations

PASS requires complete trajectory provenance, independent repeats, and
appropriate references. Finite energy and a completed run alone are not enough.
