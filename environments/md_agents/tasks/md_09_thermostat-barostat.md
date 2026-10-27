# Task: md_09_thermostat-barostat

**Task family:** thermostat and barostat. **Status:** specification; execution and qualification require a supported profile. This task follows the repository's BioDesignBench-style structure.

## Description

Configure temperature and pressure control without hidden state changes. Use the [environment specification](../ENVIRONMENT_SPEC.md) for the shared contract. Do not invent trajectories, model suitability, benchmark scores or online-resource evidence.

## Target

- **System/resource:** Thermodynamic targets and control settings.
- **Specialist decision:** Thermostat and Barostat.
- **Evidence:** preserve inputs, versions, settings, URLs, hashes, logs and outputs.
- **Status:** return PASS, FAIL, REVIEW, NEEDS_INPUT, PROTOCOL_REQUIRED or BLOCKED based on evidence.

## Design Constraints

- Preserve molecular identity, topology, parameters, units, seeds and declared scientific settings.
- Use only supported engines, models, data and resource permissions.
- Keep numerical, sampling, scientific, infrastructure, provenance and license failures separate.
- A stable trajectory, high model score or popular online resource is not sufficient scientific evidence.

## Required Execution Steps

1. Resolve and validate the task request and required artifacts.
2. Freeze the system, protocol, versions, seeds, resource limits and source metadata.
3. Run the specialist operation or inspect the supplied fixture.
4. Independently validate outputs against domain-specific acceptance rules.
5. Record raw artifacts, decision, failure category, runtime/cost and provenance.
6. Return unresolved or unsupported requirements explicitly.

## Expected Output

**Format:** md_task_bundle.

Required output includes a readable report, machine-readable decision, settings and versions, units, hashes, resource use, limitations and exact stop reason. Missing or unconverged evidence remains unresolved and is never fabricated.

## Constraints

- **Compute/time:** obey declared budgets; retries and downloads are bounded and recorded.
- **Knowledge/data:** use versioned, licensed resources and declared source cutoffs.
- **Scope:** computational evidence only; trajectory stability does not establish affinity, mechanism or experimental activity.
- **Reproducibility:** preserve native artifacts, normalized metrics, seeds, hardware, code/model/data revisions and failed attempts.

## Important Instructions

- Do not silently replace force fields, engines, checkpoints, datasets, topology, analysis settings or acceptance criteria.
- Do not claim online resource suitability before integrity, compatibility, license and provenance checks.
- Do not relax gates to obtain a pass.
- Distinguish reproduced published results from new observations and unverified claims.
- Preserve all task lineage and audit evidence.

