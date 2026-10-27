# Task: fep_ps01_mapping

**Task family:** alchemical mapping. **Status:** specification; case-specific.

## Description and target

Validate atom correspondence, transformed bonds, and endpoint topology.
Specialist: FEP-PS01.

## Required output and acceptance

Return a `fep_task_bundle` with mapping, hashes, and stop reason. PASS requires
validated correspondence; ambiguous mapping is REVIEW.
