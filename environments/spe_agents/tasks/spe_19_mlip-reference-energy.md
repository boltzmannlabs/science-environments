# Task: spe_19_mlip-reference-energy

**Task family:** mlip reference energy. **Status:** specification; execution and qualification are case-specific. This file follows the BioDesignBench-style task structure used by the repository.

## Description

Compare an MLIP energy with a versioned QM reference set. Use the [environment specification](../ENVIRONMENT_SPEC.md) for the scientific contract. Do not invent missing inputs, thresholds, engine capabilities or successful results.

## Target

- **System:** Versioned model, reference structures and compatible units.
- **Specialist decision:** MLIP reference energy.
- **Evidence:** preserve the original inputs, settings, engine/version, output artifacts and hashes.
- **Status:** return PASS, FAIL, UNRESOLVED or the environment's typed infrastructure status based on evidence.

## Design Constraints

- Preserve atom identity/order, charge, multiplicity and declared method/model settings.
- Use only supported adapters and the frozen evaluator; do not silently substitute settings.
- Keep scientific failures separate from malformed-input, provenance, runtime and reporting failures.
- A process exit or an agent opinion is not evidence of scientific correctness.

## Required Execution Steps

1. Resolve and validate the task request and required artifacts.
2. Freeze the calculation settings, inputs, versions, seeds and resource limits.
3. Run the specialist operation or inspect the supplied execution fixture.
4. Independently validate the reported output against the acceptance criteria.
5. Record raw evidence, decision, failure category, runtime and provenance.
6. Return the complete task result, including unresolved or unsupported requirements.

## Expected Output

**Format:** spe_task_bundle.

Required output includes a readable report, machine-readable decision, input/output hashes, method/model settings, units, convergence or applicability evidence, resource use, limitations and an exact stop reason. Empty or incomplete scientific results remain unresolved; they must not be filled with fabricated values.

## Constraints

- **Compute/time:** obey the declared task and adapter budgets; retries are bounded and charged.
- **Knowledge/data:** use only versioned references and supplied artifacts.
- **Scope:** computational evidence only; no unsupported experimental claim.
- **Reproducibility:** preserve native outputs, normalized outputs, seeds, implementation versions and failed attempts.

## Important Instructions

- Do not modify the evaluator, acceptance criteria, frozen task data or reference protocol.
- Do not relax thresholds or omit required evidence to obtain a pass.
- Report missing, unsupported or unconverged work explicitly.
- Distinguish an illustrative fixture from a live engine result.
- Preserve all provenance and candidate/task lineage.

