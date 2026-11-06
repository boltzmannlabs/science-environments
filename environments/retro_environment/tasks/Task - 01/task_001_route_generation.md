# T001 — Generate and reconstruct routes

## Problem / input
Generate synthetic candidates for the exact target in [route_summary.json](../../results/Task%20-%2001/route_summary.json), experiment label `test_agent`.

## Work
Retrieve the authenticated retrosynthesis output, traverse each topN reaction tree, preserve source SMILES, and separate explicit transformation counts from unreliable reported num_steps. Archive a sanitized public derivative without private backend identifiers.

## Expected outcomes / acceptance
Every route must have precursor/product strings, model step-yield fields, route ranking and explicit transformation count. Missing parameters (model version, seed, training corpus) must remain unknown. Do not assume commercial availability.

## Actual outcome
16 candidate paths and 56 reaction-node occurrences across those paths were preserved. Repeated chemistry across routes is not deduplicated. No target synthesis was run. Source-derived model results: [route_summary.json](../../results/Task%20-%2001/route_summary.json); numerical comparison: [CSV](../../results/Task%20-%2001/route_yield_comparison.csv).
