# Molecular Dynamics Specialist Agents — Environment Specification

**Environment ID:** `md-agents`  
**Status:** Specification

## Objective

Provide reusable, auditable specialist contracts for molecular-dynamics system
preparation, execution, sampling, analysis, free-energy workflows, learned
potentials and online scientific-resource discovery.

## Specialist groups

### Core MD specialists (MD-01–MD-20)

Input validation; system preparation; force-field selection; parameterization;
solvation/ion placement; minimization; equilibration; integrator/timestep;
thermostat/barostat; execution; failure recovery; sampling; enhanced sampling;
trajectory quality; structural analysis; interaction analysis; free-energy
analysis; statistics/uncertainty; resource optimization; and orchestration.

### Online-resource specialists (MD-21–MD-30)

Literature discovery; model/checkpoint discovery; dataset discovery; download
and cache; model compatibility; dataset integrity; scientific reproduction;
model evaluation/selection; resource updates; and provenance/licensing.

## Required evidence

Every run records system inputs, topology/parameters, engine and version,
integrator, timestep, thermostat/barostat, seed, hardware, trajectory hashes,
analysis settings, resource use, failures/restarts, and evaluator decisions.
Published claims and newly observed results must be separated.

## Scientific safety rules

- A stable trajectory does not prove binding affinity, mechanism, or kinetics.
- Sampling claims require independent replicas or an explicitly justified design.
- Free energies require matched states, units, uncertainty and reference data.
- Learned models require versioned checkpoints, force/energy validation and
  compatibility checks before production use.
- Online downloads never execute automatically; integrity, license and safety
  checks precede use.

## Maturity boundary

This specification does not provide a qualified force field, production MD
engine adapter, LFM checkpoint, trajectory dataset, or benchmark score.
