# Task: cg_01_mapping-preparation

**Task family:** CG system mapping and preparation. **Status:** specification;
execution and qualification are case-specific.

## Description

Validate atom-to-bead mapping, connectivity, bead types, missing atoms, and
mapping ambiguity. Use [the environment specification](../ENVIRONMENT_SPEC.md).

## Target

- **System:** atomistic source, mapping definition, and CG topology.
- **Specialist decision:** CG Representation and Mapping (`CG-01`).
- **Evidence:** mappings, versions, hashes, changes, and validation logs.

## Required execution and output

Freeze inputs, run the mapping adapter, independently check identity and
connectivity, and return a `cg_task_bundle` with PASS, FAIL, or REVIEW. Never
invent missing atoms or silently change the mapping.

## Acceptance and limitations

PASS requires complete mapping and topology evidence. Missing source,
unsupported resolution, or absent reference evidence remains REVIEW.
