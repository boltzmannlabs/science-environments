# Task 04 — Pd-NHC Suzuki–Miyaura optimization benchmark

[Task and exact inputs](../../tasks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Results and outputs](../../results/task-04-pdnhc-suzuki-miyaura-optimization/README.md)

## Evaluation boundary

This is a blind computational benchmark. The withheld experimental optimum, measured yields, known best catalyst and reference condition settings were not accessed during prediction. Consequently, no matched experimental yield, MAE, top-5 condition accuracy or loading-retention value can be computed here. The "literature" rows below are general chemistry expectations for the reaction class, substrate motif and Pd-NHC catalyst family — not results for this exact reactant pair. Model scores are not percentages.

## Source references

- Zhou, Ma, Nahra, Obled, Poater, Cavallo, Cazin, Nolan and Szostak, “[Pd(NHC)(μ-Cl)Cl]₂: Versatile and Highly Reactive Complexes for Cross-Coupling Reactions that Avoid Formation of Inactive Pd(I) Off-Cycle Products,” *iScience* (2020), [DOI 10.1016/j.isci.2020.101377](https://doi.org/10.1016/j.isci.2020.101377). Reports air-stable Pd(II)–NHC chloro-dimers as highly reactive Suzuki precatalysts, including aryl chlorides. Catalyst-family analogy; no exact substrate match inspected.
- Liu, Scattolin, Gobbo and Beliš, “A Simple Synthetic Route to Well-Defined [Pd(NHC)Cl(1-tBu-indenyl)] Pre-catalysts for Cross-Coupling Reactions,” *European Journal of Inorganic Chemistry* (2021), [DOI 10.1002/ejic.202100840](https://doi.org/10.1002/ejic.202100840). Pd-NHC precatalyst family context; IPr, IPrCl, IMes, SIMes, IPr*.
- Liu, Voloshkin, Scattolin, Peng et al., “Versatile and Highly Efficient trans-[Pd(NHC)Cl₂(DMS/THT)] Precatalysts for C−N and C−C Coupling Reactions in Green Solvents,” *European Journal of Organic Chemistry* (2022), [DOI 10.1002/ejoc.202200309](https://doi.org/10.1002/ejoc.202200309). Pd-NHC precatalyst family context.
- Wang et al., “Generic Interpretable Reaction Condition Predictions with Open Reaction Condition Datasets and Unsupervised Learning of Reaction Center,” *Research* 6, 0231 (2023), [DOI 10.34133/research.0231](https://doi.org/10.34133/research.0231); code [github.com/wangxr0526/Parrot](https://github.com/wangxr0526/Parrot). External condition-prediction method actually executed in this task.
- Local `reaction_optimizer_tool` documentation was read from the user-provided installation at `/home/boltzmann16/GopiKrishna/reaction_optimizer_tool` (README.md, OPTIMIZATION.md, CAMPAIGNS.md, OPERATING_WINDOWS.md); it is a local tool, not a GitHub source for this benchmark. Its Bayesian design rationale follows BayBE ([project](https://github.com/emdgroup/baybe), [paper DOI 10.1039/D5DD00050E](https://doi.org/10.1039/D5DD00050E)).

None of these citations supplies a measured yield for 4-chloroanisole + 4-(trifluoromethyl)phenylboronic acid. The original task file explicitly embedded no reference literature or experimental answers.

## Baseline methods and comparators

| Comparator | Role | Eligibility |
|---|---|---|
| Structural target supplied in task | Forward-prediction identity check | Structural input only; not independent discovery |
| General Suzuki–Miyaura mechanistic expectation | Reaction-class comparison | Class-level, not exact-pair measurement |
| General Pd-NHC aryl-chloride Suzuki literature | Catalyst-family comparison | Family analogy only |
| Frozen ReactionT5-yield advisor in local tool | Numerical yield comparator | Structure-based only; excludes loading, solvent, temperature, time, concentration and equivalents |
| Parrot USPTO-Condition model | External condition comparator | Executed; predictions recorded but chemically weak for this reaction |
| Withheld benchmark evaluation | Experimental validation | Not accessed; outside blind stage |

## Comparison criteria and metric interpretation

- **Forward prediction:** exact RDKit canonical isomeric SMILES match of top prediction to supplied target.
- **Retrosynthesis:** recovery of the supplied reactant pair among candidates; partial recovery noted by canonical identity.
- **Conditions:** parameter completeness, chemical plausibility and score/feasibility semantics; no experimental optimum comparison in blind stage.
- **Catalyst:** Pd-NHC family presence in tool output; no experimental best-catalyst ranking without measured data.
- **Yield:** only native model fields; unit conventions retained as returned. No MAE or improvement claim without matched measurements.
- **Loading:** mol% inferred from encoded equivalents relative to aryl chloride (1.0 equiv); retention computable only from measured or loading-sensitive matched yields.

## Achieved metrics

See [achieved_metrics.json](achieved_metrics.json). Missing experimental numbers are `null`; no assumed zero replaces unavailable data.

## Project and literature values

No exact-pair literature yield or measured value was obtained. Literature rows are qualitative family/class analogies. Our quantitative values are model predictions from named tools and are labelled as such in [achieved_metrics.json](achieved_metrics.json) and [comparison_report.md](../../results/task-04-pdnhc-suzuki-miyaura-optimization/comparison_report.md).

## Improvement criterion (prespecified after freezing, before validation)

For a later non-blind or laboratory evaluation: (i) top-1 product must match by canonical identity; (ii) experimental best catalyst family should appear in top 3; (iii) a measured condition optimum should appear in top 5 under predefined tolerances; (iv) yield MAE should be ≤15 percentage points on matched measured conditions; (v) reduced loading should retain ≥90% measured yield versus a named reference condition. None of these criteria is claimed satisfied here.
