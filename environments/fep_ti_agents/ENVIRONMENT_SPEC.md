# FEP/TI Environment Specification

## Objective

Diagnose and qualify alchemical free-energy and thermodynamic-integration
workflows without forcing a numerical answer when sampling or thermodynamic
evidence is insufficient.

## Required inputs

Mapped endpoints, transformation graph, topology/parameters, lambda schedule,
ensemble and restraints, charge-change corrections, engine/version, windows,
replicas, estimator, uncertainty method, and reference protocol.

## Required outputs

Mapping and endpoint audit, window/overlap diagnostics, convergence and
uncertainty, cycle/hysteresis checks, corrections, provenance, and typed
PASS/FAIL/REVIEW status with raw artifacts.

## Rules

Do not silently change atom mappings, endpoints, charges, restraints, lambda
windows, estimator, or standard-state convention. A free-energy number without
overlap, convergence, uncertainty, and provenance is REVIEW.
