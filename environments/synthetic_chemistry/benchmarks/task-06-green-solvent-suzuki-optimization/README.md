# Task 06 — green-solvent Suzuki benchmark

[Task and exact inputs](../../tasks/task-06-green-solvent-suzuki-optimization/README.md) · [Results and outputs](../../results/task-06-green-solvent-suzuki-optimization/README.md)

## Evaluation boundary

This is a blind computational benchmark with a post-hoc literature comparison. The exact benchmark pair and user-reported 85%/38% were supplied by the user; the verified paper table was disclosed only after predictions were frozen. The 85%/38% figures were never passed to any tool, but their disclosure before the runs compromises full blinding. No literature yield was used as a prediction input or campaign measurement. Consequently no matched experimental yield, yield MAE, DES top-3, green-vs-conventional lift, impurity direction or measured E-factor can be claimed. Model scores and unqualified yield fields are not experimental yields.

## Source references

- Salami, C.; Boudesocque-Delaye, L.; Delaye, P.-O.; Thiery, E. “Simple and Rapid Microwave-Assisted Suzuki–Miyaura Cross-coupling in Betaine/Glycerol Natural Eutectic Solvent.” *ChemistryOpen* **2025**, *14*(11), e202500138. [DOI 10.1002/open.202500138](https://doi.org/10.1002/open.202500138); first published 17 June 2025. Verified exact-pair primary paper; Tables 1–3 were supplied by the user in `SC-03_Literature_Comparison.md` (external input, not redistributed). SI/substrate-scope row-level curation was not performed.
- ICH Q3C(R9) classification as stated in the supplied comparison: DMF and acetonitrile Class 2, ethanol Class 3. Official guideline table was not retrieved in this run; other components are unresolved.

## Baseline methods and comparators

| Comparator | Role | Eligibility |
|---|---|---|
| Table 1 fixed-condition screen (10 media) | Matched solvent benchmark | Only at 120 °C/30 min/Pd(OAc)₂ 1 mol%/NMR; no model row matched |
| Table 2 catalyst screen in betaine/glycerol 1:4 | Catalyst-family context | dppf variants 80–82%; different yield basis from isolated |
| Optimized protocol 129 °C/15 min | Green protocol reference | 85% NMR, 75% isolated, 66% isolated at 8 mmol — distinct outcomes |
| Internal `condition_recommendation` job | Prediction under test | Ten dioxane/water conditions; no DES comparison possible |
| Local `reaction-optimize` BayBE v1 + ReactionT5 | Condition-aware design under test | 480 candidate grid; yield model is solvent-blind |
| Curated ORD v2 recipes | Experimental recipe source | Zero recipes matched the exact benchmark pair |

## Table 1 — fixed-condition solvent screen (NMR yield, %)

| Medium | Ratio | Yield |
|---|---|---:|
| Water | — | 69 |
| DMF | — | 62 |
| Choline chloride / ethylene glycol | 1:2 | 83 |
| Choline chloride / glycerol | 1:2 | 69 |
| Choline chloride / urea | 1:2 | 50 |
| Glycerol / urea | 4:1 | 75 |
| Betaine / glycerol | 1:2 | 72 |
| Betaine / glycerol | 1:4 | 72 |
| Betaine / glycerol | 1:8 | 64 |
| Glycerol | — | 64 |

The fixed-screen winner is choline chloride/ethylene glycol (83%), not betaine/glycerol. Matched DES 1:4 − DMF = +10 pp at these fixed conditions; this is not an isolated-yield lift.

## Comparison criteria and metric interpretation

- **Solvents:** rank only across matched substrate, catalyst, temperature, time and yield type; no ranking from the solvent-blind yield field.
- **Yield:** native model fields have undocumented basis; model scores are not percentage yields; report `condition_match_status` per row and compute MAE only over matched rows.
- **Catalyst/base:** qualitative alignment with Table 2 dppf preference; not proof of yield accuracy.
- **Hazard:** keep ICH class separate from yield; unresolved mixtures are not safe by default.
- **Waste:** E-factor only from declared mass inputs and isolated product; incomplete mass data give a labeled scenario with recovery sensitivity.
- **Impurity:** a reaction-only candidate list cannot show DES-vs-conventional direction; Pd-black is a material event, not a SMILES.

## Improvement criterion (prespecified after freezing)

For a later non-blind or laboratory evaluation: DES in the top 3 media; yield MAE ≤15 pp on matched rows; no Class 1–2 bulk medium in the final protocol; green yield ≥ conventional −5 pp on a comparable basis; at least one correct impurity direction; microwave time ≤ reference; transparent measured E-factor. None of these is claimed satisfied here.

See [achieved_metrics.json](achieved_metrics.json) for observed software metrics with unavailable experimental fields as `null`.
