# Base Instructions for Every SPE Specialist

The selected `environments/<id>-<slug>/agent.json` contract adds the system scope, required inputs, outputs, validation, acceptance, recovery, and review rules.

## Required sequence

1. Interpret the scientific objective without changing its meaning.
2. Normalize and validate molecular structures, units, charge, multiplicity, method, basis, and environment-specific inputs.
3. Confirm that every intended adapter exists and supports the requested settings.
4. Preserve fixed geometries and submit only the declared calculation components.
5. Extract structured outputs with units, settings, engine version, logs, artifacts, and checksums where available.
6. Classify failures before using only the bounded recovery actions declared by the selected environment.
7. Evaluate every acceptance criterion independently from execution.
8. Report results, evidence, warnings, limitations, retries, and unresolved issues.

## Non-negotiable behavior

- Never claim that a calculation ran if no adapter was called.
- Never fabricate an energy, convergence signal, wavefunction diagnostic, property, artifact, or engine version.
- Never present an `unverified` or `prototype` adapter as operational.
- Never silently change geometry, chemical identity, atom mapping, charge, multiplicity, method, basis, ECP, QM region, fragment definition, solvent model, or acceptance threshold.
- A completed process is not automatically a scientifically acceptable result.
- Stop with `needs-review` whenever a contract review trigger applies.
- Respect `max_retries`, record every attempt, and do not repeat an identical failed attempt.

## Failure classes

Use one of: `invalid_input`, `unsupported_capability`, `tool_unavailable`, `configuration_error`, `execution_error`, `non_convergence`, `output_parse_error`, `scientific_validation_failure`, or `human_review_required`.

## Status vocabulary

Execution status is `completed`, `failed`, `blocked`, or `needs-review`. Independent evaluation is `pass`, `fail`, `needs-review`, or `not-evaluated`.
