# Task: fep_ag13_affinity_ranking

## Description

Determine whether ligand-ranking claims are supported by uncertainty, replicates, and an appropriate experimental or trusted reference.

## Dataset and inputs

- Predicted ΔΔG values and intervals, ligand identities, reference measurements, and ranking tolerance

## Tools to use

Error/uncertainty comparison, rank correlation with confidence limits, and provenance checker.

## Expected outputs

`ranking_report.json` with pairwise ranking support, reversals within uncertainty, and unsupported claims.

## Acceptance and limitations

PASS requires ranking separation beyond uncertainty where claimed. Correlation alone does not establish causal or prospective validity.
