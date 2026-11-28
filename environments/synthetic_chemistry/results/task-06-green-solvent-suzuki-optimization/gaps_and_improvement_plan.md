# Task 06 — gaps and improvement plan

[Task](../../tasks/task-06-green-solvent-suzuki-optimization/README.md) · [Achievements](achievements_and_comparison.md)

## Why the gaps occurred

1. **Interface gap:** the four Boltzmann synthesis tools accept only reactant/product SMILES; solvent, DES ratio, catalyst loading, temperature and time cannot be supplied. All 10 condition candidates defaulted to dioxane/water.
2. **Model-input gap:** frozen ReactionT5 yield encodes only reactants, catalyst/reagent SMILES and product; it cannot distinguish DES from dioxane or 100 °C from 129 °C.
3. **Data gap:** curated ORD v2 returned zero recipes matching the exact benchmark pair; bundled seeds are illustrative and excluded.
4. **Measurement gap:** the BayBE optimizer learns solvent/temperature/time effects only from reviewed laboratory measurements; none exist, and literature yields must not be used as campaign observations.
5. **Boundary gap:** no workup masses, solvent-recovery data or conventional-heating duration; E-factor is scenario-only.
6. **Blinding gap:** user-reported yields disclosed before prediction; literature after freeze. Training-data leakage risk unknown.
7. **Operational notes:** one condition job failed with HTTP 429/timeout and was retried as a distinct job; notebook-kernel Python shadowed the local tool's RDKit and was fixed by clean shell invocation.

## Improvement plan

1. Acquire or validate a condition-aware yield model accepting solvent components, composition basis, catalyst loading, temperature and time.
2. Execute the designed 12-run batch under a preregistered protocol with matched NMR or isolated basis; record reviewed measurements in the campaign store, then run Bayesian optimization rounds.
3. Retrieve official ICH Q3C(R9) classifications for every component and define whether the exclusion covers precatalyst-associated CH₂Cl₂.
4. Record all input/workup/recovery masses and water policy; recompute measured E-factor/PMI.
5. Curate Table 2/3, response-surface and Scheme 3 scope rows into the benchmark folder; evaluate matched rows only with PASS/FAIL/NOT EVALUABLE and denominators.
6. Require experimental evidence for impurity directions; track Pd-black as a materials event, not a SMILES.
7. Freeze predictions and hashes before any future unblinding; keep literature-only information behind the evaluation boundary.
