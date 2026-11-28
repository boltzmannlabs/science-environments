# Task 05 — microwave catalytic amidation benchmark

[Task and exact inputs](../../tasks/task-05-microwave-catalytic-amidation/README.md) · [Results and outputs](../../results/task-05-microwave-catalytic-amidation/README.md)

## Evaluation boundary

This is a blind computational benchmark. The withheld experimental optimum, measured yields, reference microwave time, prespecified pass cutoff, side-product answers and designated 2025 HTE paper were not accessed during prediction. Consequently no matched experimental yield, yield MAE, optimum-in-top-5, solvent-top-3, steric-class floor, time comparison or impurity match can be computed here. The literature rows below are verified contextual sources for the reaction class — not results for the exact illustrative pair. Model scores are not percentage yields.

## Source references

- Zarecki, A. P.; Kolanowski, J. L.; Markiewicz, W. T. "Microwave-Assisted Catalytic Method for a Green Synthesis of Amides Directly from Amines and Carboxylic Acids." *Molecules* **2020**, *25*, 1761. [DOI 10.3390/molecules25081761](https://doi.org/10.3390/molecules25081761). Verified: ceric ammonium nitrate (CAN) catalyst, solvent-free, open microwave reactor; high yields; primary amines in most examples. Nearest microwave + catalytic precedent, but solvent-free and not 2025. PMID 32290373.
- Procter, R. J. et al. "Borate-catalysed direct amidation reactions of coordinating substrates." *Chemical Science* **2025**, *16*, 4718–4724. [DOI 10.1039/d4sc07744j](https://doi.org/10.1039/d4sc07744j); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11831689/). Verified from full text: novel borate ester catalyst; tert-butyl acetate gave >80% isolated yield after 20 h; toluene used where t-BuOAc caused side reactions; electron-deficient and hindered anilines tolerated. Thermal, not microwave; not verified as the designated HTE paper.
- "Borane-Pyridine: An Efficient Catalyst for Direct Amidation." *Molecules* **2024**, *29*, 268. [DOI 10.3390/molecules29010268](https://doi.org/10.3390/molecules29010268). Verified: borane–pyridine at 5 mol%; aromatic/aliphatic acid and amine scope; halo, nitro and alkene tolerance. Heating mode not specified in the abstract. PMID 38202849.
- "Development of fluorous boronic acid catalysts integrated with sulfur for enhanced amidation efficiency." *RSC Advances* **2023**, *13*, 17420–17426. [DOI 10.1039/D3RA03300G](https://doi.org/10.1039/D3RA03300G). Verified abstract: thermally stable fluorous sulfur-containing boronic acid catalyst for dehydrative condensation of acids and amines. Secondary context only.
- Bruce-Salmenkivi, V. K. et al. "Catalytic Amidation of Carboxylic Acids Using ortho-Aminophenylboronic Acids." *ACS Organic & Inorganic Au* **2026**, *6*, 422–429. [PMC13449423](https://pmc.ncbi.nlm.nih.gov/articles/PMC13449423/). Verified full text: ortho-substituted boronic acids as direct-amidation catalysts; (2-(piperidin-1-yl)phenyl)boronic acid optimal. Published after 2025; excluded from training-time evidence under a 2025-12-31 cutoff.

See [papers.md](papers.md) for match-vs-analogy status and [achieved_metrics.json](achieved_metrics.json) for observed software metrics with unavailable experimental fields as `null`.

## Baseline methods and comparators

| Comparator | Role | Eligibility |
|---|---|---|
| CAN / solvent-free / microwave (L1) | Closest catalytic microwave precedent | 2020; solvent-free, so cannot substantiate a solvent ranking |
| Borate ester / t-BuOAc / toluene (L2) | Hindered-aniline catalytic amidation context | 2025 but thermal, not microwave HTE |
| Borane–pyridine 5 mol% (L3) | Catalytic loading and functional-group tolerance context | Different heating mode; class analogy only |
| Internal `condition_recommendation` job | Prediction under test | Ten conditions; no catalyst identity returned |
| Local `reaction-optimize` BayBE v1 | Catalytic design-of-experiments | Explicit condition space; design hypotheses only; no measurements |
| Withheld 2025 HTE benchmark | Experimental validation | Not identified or accessed; outside blind stage |

## Comparison criteria and metric interpretation

- **Catalyst constraint:** candidate must name a catalyst; empty `catalyst_name` is a FAIL against `catalyst_required: true`, independent of yield.
- **Microwave/time:** heating mode and time must be explicit; temperature alone does not establish microwave use or duration.
- **Solvents:** rank only under comparable catalytic conditions; solvent-free (L1) and thermal (L2) rows are not interchangeable with microwave HTE rows.
- **Yield:** only native model fields; near-identical yields across chemically different conditions are substrate-typical estimates, not condition-resolved predictions. No MAE without matched measured rows.
- **Priors:** model-predicted yields seeded into the optimizer are `excluded` with QC flags; they are never `reviewed` measurements and never contribute to the Bayesian fit.
- **BO status:** no fit without at least four distinct reviewed measured candidates.

## Achieved metrics

See [achieved_metrics.json](achieved_metrics.json). Missing experimental numbers are `null`; no assumed zero replaces unavailable data.

## Project and literature values

No exact-pair literature yield or measured value was obtained. The exact illustrative product N-(2,6-dimethylphenyl)-2-methylbenzamide returned no dedicated methodological paper in the searches performed. Literature entries are verified contextual facts; our quantitative values are software outputs from named tools and are labelled as such.

## Improvement criterion (prespecified after freezing, before validation)

For a later non-blind or laboratory evaluation: (i) at least one returned condition must name a catalyst compatible with direct amidation; (ii) heating mode and microwave time must be explicit; (iii) the experimental optimum should appear in the top 5 under predefined tolerances; (iv) yield MAE should be ≤15 percentage points on matched measured conditions; (v) the best three solvents should be recovered under a matched catalytic microwave grid; (vi) the worst steric class should be identified correctly; (vii) microwave time should not exceed the designated reference time; (viii) at least one experimentally reported side product should be predicted. None of these criteria is claimed satisfied here.
