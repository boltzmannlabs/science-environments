# Task: fep_ag09_binding_water

## Description

Investigate trapped waters, pocket rearrangements, alternative poses, and slowly interconverting binding-site states that can bias FEP.

## Dataset and inputs

- Complex trajectories, water occupancy/contact records, pocket-state clusters, and independent replicas

## Tools to use

Trajectory imaging, contact and hydration analysis, clustering, and state-population uncertainty estimation.

## Expected outputs

`binding_site_state_report.json` with water occupancy, state populations, transitions, and sampling gaps.

## Acceptance and limitations

PASS requires relevant states to be reproducibly sampled. Unresolved slow states require REVIEW; no affinity number should be forced.
