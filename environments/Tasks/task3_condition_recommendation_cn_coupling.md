# Task 3 — Condition Recommendation vs. Literature: Metal-Free C–N Cross-Coupling of Benzamides with Sulfonamides (Smiles Rearrangement)

**Environment:** `task3_condition_cn_smiles`
**Tool under test:** Condition recommendation
**Benchmark class:** Catalyst/reagent/solvent/temperature recommendation vs. a published optimization campaign

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Title | Metal-free strategy for C–N cross-coupling of benzamide with sulfonamide enabled by a Smiles rearrangement |
| Authors | S. Pramanick et al. (corresponding author group per ChemRxiv preprint: S. Manna; confirm full list) |
| Journal | *Communications Chemistry* **2026**, *9*(1), article 252 — published **2026-07-20** (open access) |
| DOI | 10.1038/s42004-026-02131-2 |
| PMID | 42477424 |
| Links | [Nature article (open access)](https://www.nature.com/articles/s42004-026-02131-2), [PubMed](https://pubmed.ncbi.nlm.nih.gov/42477424), [ChemRxiv preprint](https://chemrxiv.org/doi/pdf/10.26434/chemrxiv-2025-qt08z) |

## 2. Why This Paper

- Condition recommendation tools are usually judged on named cross-couplings with thousands of precedents. This paper is a **metal-free C–N coupling** whose conditions (base, solvent, temperature, stoichiometry) are non-obvious — the C–N bond forms through an **intramolecular Smiles rearrangement**, not oxidative addition/reductive elimination, so metal-catalyst-centered priors actively mislead.
- It is **open access**, so the complete optimization table (failed/successful condition sets, yields per entry) can be transcribed into machine-readable ground truth without paywall friction.
- Includes substrate scope with yields and a scale-up demonstration → supports a yield-prediction sub-benchmark.

## 3. Ground Truth from the Paper



- Transformation: **benzamide + sulfonamide → arylated/amidated C–N coupled product via Smiles rearrangement**, transition-metal-free.
- Claims: broad substrate scope across functional groups, scalability demonstrated, access to key building blocks.

To extract into `ground_truth/optimization_table.csv` (one row per optimization entry):

| column | content |
|---|---|
| entry | optimization table entry # |
| base | exact base + equivalents |
| solvent | solvent + concentration |
| temp / time | °C, hours |
| additive | if any |
| yield | % (isolated or assay — record which) |
| note | e.g. "SM recovered", "Smiles intermediate observed" |

Also extract: final optimized conditions row (flag `is_optimum`), the mechanistic proposal (Smiles rearrangement pathway), and scope table → `ground_truth/scope.csv`.

## 4. Objective of the Task

The agent scientist, using only the **condition recommendation tool** (paper masked), must:

1. **Recommend conditions** for the model reaction (benzamide + sulfonamide, structures from `input/`): ranked top-10 condition sets spanning base/solvent/temp/additive space.
2. **Predict the mechanism class** (or the mechanistic feature the conditions must enable — e.g., anion formation + intramolecular aryl transfer) to justify the recommendation.
3. **Predict yield** for (a) the tool's own top condition set and (b) the 5 highest-yielding and 5 lowest-yielding literature condition sets, blind (yields stripped).
4. **Predict scope trend:** rank a 10-substrate subset (from scope table, yields stripped) by expected yield.

## 5. Environment Setup

```
sci_paper/
└── env/task3_condition/
    ├── input/
    │   ├── reaction.smi              # reactants + (product, for condition-mode tools)
    │   └── scope_blind.csv           # substrates with yields stripped
    ├── ground_truth/
    │   ├── optimization_table.csv    # fill from open-access paper
    │   ├── scope.csv
    │   └── optimum.yaml              # final conditions + yield
    ├── runs/
    └── scores/
```

Tool interface (adapt):

```
recommend_conditions --reaction input/reaction.smi --topk 10 \
                     --out runs/conds_<timestamp>.json
predict_yield --condition <row> --out runs/yield_<row_id>.json
```

## 6. Expected Results & Scoring

| # | Metric | Expected / pass threshold |
|---|---|---|
| 1 | Paper optimum in tool's top-5 | Pass if the final optimized condition set (or a chemically equivalent variant: same base class + compatible solvent + temp within 20 °C) appears in top 5 |
| 2 | Mechanism awareness | Tool does **not** recommend Pd/Cu catalysts as critical components (the transformation is metal-free; strong metal-catalyst recommendations = mechanism-model failure) |
| 3 | Yield MAE (optimization entries) | Mean absolute error ≤ 15 percentage points across ≥ 10 entries |
| 4 | Yield MAE (scope, blind) | ≤ 12 pp on the 10-substrate blind subset |
| 5 | Yield ranking | Spearman ≥ 0.5 between predicted and actual yields on the blind subset |
| 6 | Condition-space coverage | Top-10 recommendations span ≥ 3 distinct base classes and ≥ 3 solvents (tests diversity, not mode collapse) |

**Expected result profile:** a tool with strong literature priors on SNAr/Smiles chemistry should land a strong base (e.g., carbonate/phosphazene/hydroxide class — exact optimum from paper) but may miss solvent/temperature subtleties; watch for it incorrectly dragging in metal catalysis because "C–N coupling" pattern-matches Buchwald–Hartwig.

## 7. Sources

- [Nature Communications Chemistry article (open access)](https://www.nature.com/articles/s42004-026-02131-2)
- [PubMed 42477424](https://pubmed.ncbi.nlm.nih.gov/42477424)
- [ChemRxiv preprint](https://chemrxiv.org/doi/pdf/10.26434/chemrxiv-2025-qt08z)
- [ResearchGate entry](https://www.researchgate.net/publication/410606515_Metal-free_strategy_for_C-N_cross-coupling_of_benzamide_with_sulfonamide_enabled_by_a_Smiles_rearrangement)
