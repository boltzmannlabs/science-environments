---
name: mol-probity-reviewer
description: Interpret protein structure quality reports.
metadata:
  sci:
    category: science
    tags: [enzymes, molprobity, structure-quality]
---

# MolProbity Reviewer Skill

Review hosted `mol_probity` results and localize structural defects. Quality checks
do not establish folding, binding affinity or enzyme activity.

## When to Use

After generation, sequence design plus reconstruction, refinement or docking;
compare reports before and after a justified repair.

## Prerequisites

Prepared single-model protein structures and an active, verified `mol_probity`
backend binding. Read `references/interpretation.md`. Load `boltzmann:tools` and
read the authoritative Boltzmann module referenced by `enzyme_workflow_catalog`.
The workflow catalogue contains compatibility metadata, not scientific input definitions.

## How to Run

Use measurement mode for descriptive analysis. Use validation mode only with
explicit user-approved quality thresholds. Execute through the five existing
Boltzmann operations and ingest the actual result artifact with explicit joins.

## Quick Reference

`measured`: metrics only. `passed`: submitted thresholds passed.
`rejected`: at least one submitted threshold failed. `invalid`: unevaluable.
Only submitted thresholds are applied; no universal hidden quality cutoff.

## Procedure

1. Confirm whether candidate chemistry and coordinate completeness allow analysis.
2. Inspect candidate_summary.csv and validation_outliers.csv. Record missing
   metrics, invalid rows and partial counts instead of presenting them as passes.
3. Localize clashes, rotamers, backbone/peptide anomalies and restraint outliers.
   Check whether an intentionally strained catalytic motif explains an outlier;
   do not silently waive an approved criterion.
4. Propose reject, side-chain repacking, local minimization or broader remodeling.
   Repairs require available audited tools and approved workflow branches.
5. Re-run quality and catalytic geometry after coordinate-changing operations.
   Preserve identity, mapping, provenance and before/after reports.

## Pitfalls

A backbone-only model cannot establish side-chain quality. A clean structure may
still have the wrong sequence, ligand pose, chemistry or catalytic mechanism.
Do not use the public website as an unattended batch service or expose subscriber
structures to third parties without explicit authorization.

## Verification

Every conclusion refers to a candidate, metric, localized outlier and submitted
threshold. Invalid or missing evidence remains explicit. Computational quality
passing is never labeled experimental validation.
