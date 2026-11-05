# Benchmark and scientific evaluation

The fixed public dataset consists of `../results/route_summary.json` (all 16 AI routes) and `../results/top0_validation.json` (selected route review). Original raw platform output is not bundled. No same-target experimental reference route is established in the searched sources.

## Evidence labels

1. **Exact experimentally reported**: same identified target and reported synthetic experiment (none found here).
2. **Reaction-family benchmark**: an independently reported transformation of a different substrate; [1–3] in the research ledger. Never transfer yields/conditions without same-substrate evidence.
3. **Computational**: retrosynthesis, ranking, step yields, forward scores, mapping confidence, impurity and condition predictions.

## Checks

- Verify SMILES and product graph with RDKit when installed; standard-library tests check schema, count, route uniqueness, models' arithmetic and unsupported-condition flags.
- Separate raw `reported_num_steps` from `explicit_tree_steps`.
- Compare forward score/observed product rank, atom mapping and chemically plausible reagent sources for each reviewed step.
- Treat the product of model yield fractions as an **illustrative value only**, ignoring yield calibration and process losses. Do not rank real synthetic performance by this value.
- Flag missing coupling catalyst and TBAF-in-protection contradiction before considering any route feasible.
- Record unknown availability, selectivity and measured yield rather than making up values.

## Known outcome

No validated complete route to the exact target; top0's central protected ether failed forward checking and model conditions failed chemical plausibility assessment. Reference [3]'s 32% yield concerns a different compound and cannot calibrate top0 or top1.
