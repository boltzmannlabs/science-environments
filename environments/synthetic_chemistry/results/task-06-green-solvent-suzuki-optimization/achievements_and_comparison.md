# Task 06 — achievements and comparison

[Task](../../tasks/task-06-green-solvent-suzuki-optimization/README.md) · [Benchmark](../../benchmarks/task-06-green-solvent-suzuki-optimization/README.md) · [Full comparison](comparison_report.md)

## Achieved

| Item | Evidence |
|---|---|
| 17/17 structures validated | RDKit parse and canonicalization |
| 55 retrosynthesis routes | Job `6b05593ab5ae2f156e63e787` |
| Correct forward target | Exact SMILES-string top-1; score ~1.0 |
| Full condition space compiled | Local optimizer: 480 candidates (10 media incl. DES 1:2/1:4/1:8, 4 catalysts, 2 bases, 3 temperatures, 2 times) |
| Diverse 12-run design batch | All three DES ratios and all green/conventional comparators represented |
| Catalyst family and base aligned | Pd(dppf) family and Na₂CO₃ independently selected, matching Table 2 dppf preference (80–82%) |
| 13 frozen yield estimates | Generated after supplying valid catalyst/base SMILES |
| Labelled E-factor scenario | 22.54 at 0% recovery; 3.29 at 95% |

## Underperformed or not achieved

- No solvent-aware yield prediction: Boltzmann tools accept only SMILES; ReactionT5 yield ignores solvent/temperature/time (≤0.117 pp within-pair spread).
- No DES top-3 ranking, no MAE (0 matched rows), no green-vs-conventional yield claim, no impurity direction, no final protocol selection, no substrate scope.
- Hazard classification incomplete; official ICH Q3C(R9) table not retrieved.
- No measured E-factor; no mass-balance or recovery data.
- Blinding compromised by pre-disclosed user yields; training-data provenance unknown.

## Self-assessed completion

6 of 14 objective items fully achieved, 2 partial, 7 not achieved → approximately 43%. This is a transparent internal rubric, not an official evaluator score.

## Comparison with literature

The paper's own fixed screen ranks choline chloride/ethylene glycol (83%) above betaine/glycerol 1:4 (72%), while its optimized DES protocol reaches 85% NMR / 75% isolated. Our run reproduced reaction chemistry and catalyst family but could not evaluate DES versus conventional media on a comparable basis. See [comparison_report.md](comparison_report.md) for the full table and numeric caveats.
