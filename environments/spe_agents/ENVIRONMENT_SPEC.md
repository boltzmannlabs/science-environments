# SPE Agents Environment Specification

## Objective

Evaluate specialist agents that prepare, execute, diagnose, and validate
single-point electronic-structure calculations under frozen scientific task
contracts.

## Inputs

Each task defines a molecular structure, charge, multiplicity, method, basis,
requested property, expected behavior, and acceptance criteria. Inputs and
reference artifacts are versioned under `tasks/`, `examples/`, and
`references/`.

## Outputs

An agent result must include its decision, scientific evidence, failure
category when applicable, runtime/token fields when measured, provenance, and
reproducibility information. A reported pass is not accepted without the
independent evaluator evidence required by the task.

## Evaluation

The evaluator uses frozen rules and numerical tolerances. It separates
scientific errors, input/software failures, unsupported claims, and reporting
errors. Unsupported calculations must be withheld or reported as review;
they must not be silently converted into successful results.

## Maturity and limitations

The contracts and benchmark harness are implemented and the recorded reports
are validated for their declared scope. Backend-dependent coverage and any
Agent Scientist runtime comparison are only claimed where raw evidence exists.
