# FEP/TI Environment Implementation Plan

## Purpose

This plan turns the FEP/TI proposal into independently testable scientific
tasks. Each environment follows the same evidence path:

**Concrete inputs → scientific validation → diagnosis/planning → controlled
execution or recovery → independent evaluation → structured outputs → benchmark
qualification.**

The plan does not label a task as qualified until its executable adapter,
frozen inputs, evaluator, fault cases, reproducibility evidence, and review are
complete.

## Uniform package contract

Every environment is stored below `environments/fep_ti_agents/` and includes:

```text
tasks/fep_<task>_001.md                 # exact scientific task
tasks/inputs/fep_<task>_001/            # immutable, concrete files
scripts/<agent_validator_or_runner>.py  # executable adapter
tests/test_<task>.py                    # baseline and fault-injection tests
results/<task>_001/                     # small, versioned evidence
```

Each task document must name exact file paths, engine/library versions,
parameters, seeds, output schemas, failure statuses, and machine-checkable
acceptance criteria. Inputs are never edited in place. Recovery actions must
write a new artifact and a provenance record.

## Lifecycle gates

1. **Specification** — task, contract, input schema, and acceptance criteria
   are reviewed.
2. **Implemented** — executable logic and native adapter exist.
3. **Tested** — valid, recoverable-failure, adversarial, and stop/FAIL cases
   pass automated tests.
4. **Qualified** — independent evaluator, frozen reference evidence,
   reproducibility checks, and scientific review are complete.

`PASS` means all required evidence is present. `REVIEW` means the input was
consumed but scientific evidence is incomplete. `FAIL` means a required check
failed. Never convert `REVIEW` to `PASS` because an engine exited successfully.

## Execution order and issue map

Implement one issue, branch, and pull request at a time. The first two entries
already have tracked work; the remaining issues are the next queue.

| Order | Environment / task ID | Specialist | Branch | Issue | Current state |
|---:|---|---|---|---:|---|
| 1 | `fep_atom_mapping_001` | Alchemical Mapping Auditor | `feat/fep-atom-mapping-auditor` | #54 | Implemented and merged |
| 2 | `fep_transformation_001` | Transformation Feasibility Auditor | `feat/fep-transformation-feasibility-auditor` | #56 | Implemented; PR #57 |
| 3 | `fep_parameter_validation_001` | Force-Field and Parameter Auditor | `feat/fep-parameter-validation-auditor` | to create | Pending |
| 4 | `fep_lambda_schedule_001` | Lambda Schedule Optimizer | `feat/fep-lambda-schedule-auditor` | to create | Pending |
| 5 | `fep_system_preparation_001` | System Preparation Auditor | `feat/fep-system-preparation-auditor` | to create | Pending |
| 6 | `fep_charge_change_001` | Charge and Electrostatics Auditor | `feat/fep-charge-change-auditor` | to create | Pending |
| 7 | `fep_simulation_recovery_001` | FEP Failure Diagnosis and Recovery | `feat/fep-simulation-recovery` | to create | Pending |
| 8 | `fep_phase_space_overlap_001` | Phase-Space Overlap Auditor | `feat/fep-overlap-auditor` | to create | Pending |
| 9 | `fep_convergence_001` | FEP Convergence Auditor | `feat/fep-convergence-auditor` | to create | Pending |
| 10 | `fep_binding_site_water_001` | Binding-Site Water Analyzer | `feat/fep-binding-water-analyzer` | to create | Pending |
| 11 | `fep_estimator_validation_001` | Free-Energy Estimator Auditor | `feat/fep-estimator-auditor` | to create | Pending |
| 12 | `fep_thermodynamic_cycle_001` | Thermodynamic Cycle Auditor | `feat/fep-cycle-auditor` | to create | Pending |
| 13 | `fep_restraint_correction_001` | Restraint and Standard-State Auditor | `feat/fep-restraint-auditor` | to create | Pending |
| 14 | `fep_affinity_ranking_001` | Relative Affinity Ranking Auditor | `feat/fep-affinity-ranking-auditor` | to create | Pending |
| 15 | `fep_benchmark_qualification_001` | Independent FEP Qualification Agent | `feat/fep-independent-qualification` | to create | Pending |

For each pending item, create the issue before the branch. The issue must name
the exact benchmark system, input files, output contract, failure cases,
acceptance criteria, owner, and reviewer. Link the issue in the PR and close it
only after merge.

## Environment-specific deliverables

| Task | Required scientific checks | Required evidence |
|---|---|---|
| Atom mapping | elements, bonds, stereochemistry, dummy regions | mapping JSON, diagnostics, qualification |
| Transformation feasibility | scaffold overlap, charge, protonation, tautomer, force-field support | assessment JSON, chemical changes CSV, report |
| Parameter validation | atom types, charges, bonded terms, topology counts, water/ion compatibility | parameter audit, missing-parameter CSV, topology report |
| Lambda schedule | ordering, duplicates, electrostatic/steric staging, soft-core settings | schedule JSON, window configuration, recommendations |
| System preparation | coordinates, box, neutralization, minimization, NVT/NPT stability | preparation reports, equilibration metrics, readiness decision |
| Charge change | endpoint charge delta, corrections, counterions, leg consistency | charge audit, correction requirements, protocol report |
| Recovery | earliest failure, checkpoint integrity, bounded retry, rollback | diagnosis, recovery plan/history, recovered evidence |
| Overlap | energy matrix integrity, adjacent overlap, disconnected windows | overlap matrix, heatmap, poorly connected windows |
| Convergence | equilibration, blocks, replicas, drift, hysteresis, uncertainty | block analysis, replica comparison, convergence report |
| Binding water | occupancy, residence, displacement, protein rearrangement | occupancy CSV, hydration analysis, structural report |
| Estimator | estimator assumptions, units, signs, independent estimator, uncertainty | estimates, comparison, uncertainty report |
| Thermodynamic cycle | matching endpoints, complex/solvent legs, signs, closure | cycle JSON, leg comparison, closure analysis |
| Restraints | restraint definitions, force constants, release and standard state | correction audit, restraint and standard-state reports |
| Affinity ranking | network connectivity, uncertainty propagation, reference comparison | network JSON, ranking CSV, robustness report |
| Qualification | provenance, protocol, overlap, convergence, estimator, reproducibility | PASS/REVIEW/FAIL audit and immutable manifest |

## Benchmark rule

Each environment must include at least one valid baseline, one recoverable
failure, one adversarial input, and one case that must stop with `REVIEW` or
`FAIL`. Public systems such as SAMPL6 may be used only with a pinned revision,
exact paths, checksums, protocol, and reference evidence. Synthetic fixtures
are useful for adapter tests but cannot be presented as experimental or
production binding results.

## Pull-request definition of done

- Issue exists and is linked.
- Feature branch contains only the one environment/agent change.
- Exact input packet and task document are present.
- Executable adapter and independent evaluator are present.
- Baseline and failure tests pass.
- Results and limitations are recorded without fabricated measurements.
- PR has scientific/software review and passing checks.
- Issue and task status are updated only after merge.
