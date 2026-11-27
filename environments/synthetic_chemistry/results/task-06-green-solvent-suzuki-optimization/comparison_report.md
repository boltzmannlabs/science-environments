# Task 06 — comparison report

[Task](../../tasks/task-06-green-solvent-suzuki-optimization/README.md) · [Benchmark and literature](../../benchmarks/task-06-green-solvent-suzuki-optimization/README.md) · [Result files](README.md)

## Source and evidence boundaries

Literature values come from the user-supplied verified comparison of Salami et al. (*ChemistryOpen* 2025, DOI 10.1002/open.202500138). Tool outputs come from completed Boltzmann jobs and local `reaction_optimizer_tool` runs recorded in [run_log.md](run_log.md). No literature yield or user-reported 85%/38% was entered into a prediction call. No wet-lab experiment was performed. Model scores and unqualified yield fields are not experimental yields.

## Structured comparison

| Metric | Literature / benchmark | Our computational outcome | Status |
|---|---|---|---|
| Benchmark reaction identity | bromobenzene + 4-MeO-phenylboronic acid → 4-MeO-biphenyl | 55 retrosynthesis routes; top-1 forward exactly matches target, model score 0.99999998 | PASS (structure only) |
| Solvent screen Table 1 | 10 media; DES 1:2/1:4 = 72%, 1:8 = 64%; best choline chloride/EG = 83%; DMF = 62% | No ranking; Boltzmann returned only dioxane/water | NOT ACHIEVABLE via SMILES-only tool |
| DES in top 3 media | DES 1:4 = 72% fixed conditions | Local batch includes DES 1:2/1:4/1:8 but does not rank them | NOT EVALUABLE |
| Yield MAE ≤15 pp | Requires matched rows | 0 matched rows; model yields ignore solvent/temperature/time | NOT EVALUABLE (n=0) |
| Green vs conventional | DES 72% − DMF 62% = +10 pp (Table 1 only) | No comparable pair; model changes ≤0.12 pp across media | NOT EVALUABLE |
| Catalyst family | Table 2: PdCl₂dppf 80%, PdCl₂dppf·CH₂Cl₂ 82%, Pd(OAc)₂ 72%, Pd(PPh₃)₄ 49% | Top-1 Pd(dppf)Cl₂; local prior favours Pd + carbonate | QUALITATIVE ALIGNMENT |
| Base | Na₂CO₃ 1.25 equiv | Na₂CO₃ top-ranked; local equivalents 1.25 | ALIGNED |
| Optimized protocol | 1:4 DES, dppf·CH₂Cl₂ 1.5 mol%, 129 °C/15 min, 85% NMR / 75% isolated | Local batch has 129 °C/15 min rows but no selected protocol | PARTIAL |
| Impurity direction | No row-level observations in supplied reference | Condition-blind candidates; Pd-black not representable | NOT EVALUABLE |
| ICH exclusion | DMF/MeCN Class 2, EtOH Class 3 confirmed; others not retrieved | Official table not retrieved; dioxane default likely violation | UNRESOLVED |
| E-factor / waste | CHEM21/PMI assessed in paper; masses not supplied | E = 22.54 reaction-charge scenario; 3.29 at 95% recovery | SCENARIO ONLY |
| Substrate scope | Scheme 3 / SI not transcribed | Only model reaction run | NOT EVALUABLE |
| Duration | Optimized 15 min; gram-scale 30 min | Local grid includes both but no experimental comparison | PARTIAL |
| Blinding | Ground truth withheld during prediction | User yields disclosed before runs; literature after freeze | COMPROMISED |

## Quantitative notes

- ReactionT5 model input contains only `REACTANT:...REAGENT:...PRODUCT:...`; no solvent, temperature or time. Repeated catalyst/base pairs across up to four solvents, 29 °C and 2× time differed by at most **0.117 pp**, while catalyst/base identity spanned **39.73 pp**. The model cannot rank solvents.
- Apparent gaps (DES model 68.43% vs literature 72%, −3.57 pp; DMF model 35.01% vs 62%, −26.99 pp) are **not errors**: solvent, catalyst, temperature, time and yield basis are mismatched.
- The retrosynthesis 75.177% field has undocumented basis; it must not be read as agreement with the 75% isolated literature yield.
- E-factor boundary: 1 mmol each reactant, Na₂CO₃ 1.25 equiv, dppf·CH₂Cl₂ 1.5 mol%, 2.8 g DES, 75% isolated product, no workup mass or recovery.

## Interpretation

Structural prediction performed well; catalyst-family and base suggestions aligned with literature without literature input. The decisive gap is that no available yield model encodes reaction conditions. A Bayesian optimizer can learn solvent effects only from reviewed measurements, which do not exist here. Published yields were deliberately not used as campaign observations.
