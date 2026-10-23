# Geo-Opt Agents Environment Specification

## Objective

Evaluate specialist agents that prepare, troubleshoot, execute, and
scientifically validate molecular geometry optimisations.

## Inputs

Each frozen packet records the structure fixture, atom ordering, charge,
multiplicity, method, basis, optimiser settings, constraints, reference
artifacts, expected behavior, and acceptance criteria. The 18 agent contracts
are in `contracts/`; task packets and fixtures are in `tasks/` and `cases/`.

## Outputs

Results must report the decision, coordinates/energy/gradient evidence when
applicable, convergence classification, failure category, provenance, runtime
and token fields when measured, and reproducibility information.

## Evaluation

Independent graders check finite coordinates and energies, gradient tolerances,
constraints, input validity, stationary-point evidence, and safe handling of
unsupported cases. Convergence alone is not treated as proof of a minimum.

## Maturity and limitations

The 18 contracts and benchmark harness are implemented. The declared live GPU
cases and deterministic qualification results are validated within their
recorded scope. Full three-arm Agent Scientist execution, complete Hessian
coverage, and production QM/MM qualification beyond the preserved prepared
complex remain explicitly limited where raw evidence is absent.
