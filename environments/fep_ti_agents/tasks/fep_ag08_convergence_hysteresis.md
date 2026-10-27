# Task: fep_ag08_convergence_hysteresis

## Description

Assess block stability, independent replica agreement, forward/reverse hysteresis, autocorrelation, and effective sampling.

## Dataset and inputs

- Window time series, replica estimates, forward/reverse legs, block length, and convergence tolerance

## Tools to use

Block analysis, autocorrelation/ESS estimator, replica comparison, and uncertainty propagation.

## Expected outputs

`convergence_report.json` with block traces, replica spread, hysteresis, ESS, uncertainty, and status.

## Acceptance and limitations

PASS requires stable blocks and compatible replicas. A long trajectory without statistical evidence remains REVIEW.
